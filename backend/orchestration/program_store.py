"""Program orchestration store for Weeks 7-16 feature tracks."""

from __future__ import annotations

import asyncio
import base64
import hmac
import json
import time
from hashlib import sha256
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from cryptography.fernet import Fernet

from config import settings
from models.builds import BuildCheckpoint
from models.program import (
    CampaignRunIngestRequest,
    GoLiveDecision,
    GoLiveDecisionRequest,
    GoLiveDecisionStatus,
    IdempotentCheckpointResult,
    PlatformWebhookResponse,
    PolicyCheckAction,
    PolicyCheckRequest,
    PolicyCheckResult,
    PolicyProfile,
    PolicyProfileRequest,
    ReleaseChecklist,
    ReleaseChecklistRequest,
    RollbackDrill,
    RollbackDrillRequest,
    SecretCreateRequest,
    SecretMetadata,
    SecretRecord,
    SecretRef,
    SloSummary,
    ValidationCampaign,
    ValidationCampaignRequest,
)
from orchestration.benchmark_harness import ValidationBenchmarkReport, compile_benchmark_report
from orchestration.store import build_store
from orchestration.validation import ValidationRun


class ProgramStore:
    def __init__(self, *, state_path: str | None = None) -> None:
        self._lock = asyncio.Lock()
        self._campaigns: dict[UUID, ValidationCampaign] = {}
        self._campaign_runs: dict[UUID, dict[str, ValidationRun]] = {}
        self._policy_profiles: dict[UUID, PolicyProfile] = {}
        self._secrets: dict[UUID, SecretRecord] = {}
        self._seen_nonces: dict[str, int] = {}
        self._idempotent_checkpoints: dict[tuple[UUID, str], dict[str, Any]] = {}
        self._release_checklists: dict[str, ReleaseChecklist] = {}
        self._rollback_drills: dict[str, RollbackDrill] = {}
        self._go_live_decisions: dict[str, GoLiveDecision] = {}
        self._fernet = Fernet(self._fernet_key_from_secret(settings.supabase_jwt_secret))
        self._platform_secret = settings.supabase_jwt_secret.encode("utf-8")
        self._state_path = Path(state_path).expanduser() if state_path else None
        self._idempotency_ttl_seconds = max(60, int(settings.idempotency_ttl_seconds))
        if self._state_path:
            self._load_state()

    async def create_campaign(
        self,
        *,
        user_id: str,
        request: ValidationCampaignRequest,
    ) -> ValidationCampaign:
        async with self._lock:
            campaign = ValidationCampaign(
                campaign_id=uuid4(),
                name=request.name,
                repos=list(request.repos),
                runs_per_repo=max(1, int(request.runs_per_repo)),
                created_by=user_id,
            )
            self._campaigns[campaign.campaign_id] = campaign
            self._campaign_runs[campaign.campaign_id] = {}
            self._save_state_unlocked()
            return campaign

    async def get_campaign(self, campaign_id: UUID) -> ValidationCampaign | None:
        async with self._lock:
            return self._campaigns.get(campaign_id)

    async def ingest_campaign_run(
        self,
        campaign_id: UUID,
        request: CampaignRunIngestRequest,
    ) -> ValidationRun:
        async with self._lock:
            if campaign_id not in self._campaigns:
                raise KeyError("campaign_not_found")
            run = ValidationRun(
                repo=request.repo,
                language=request.language,
                run_id=request.run_id,
                status=request.status,
                duration_ms=request.duration_ms,
                findings_total=request.findings_total,
            )
            self._campaign_runs[campaign_id][run.run_id] = run
            self._save_state_unlocked()
            return run

    async def campaign_report(self, campaign_id: UUID) -> ValidationBenchmarkReport:
        async with self._lock:
            if campaign_id not in self._campaigns:
                raise KeyError("campaign_not_found")
            runs = list(self._campaign_runs[campaign_id].values())
            return compile_benchmark_report(runs)

    async def create_policy_profile(
        self,
        *,
        user_id: str,
        request: PolicyProfileRequest,
    ) -> PolicyProfile:
        async with self._lock:
            profile = PolicyProfile(
                profile_id=uuid4(),
                name=request.name,
                blocked_commands=[row.strip() for row in request.blocked_commands if row.strip()],
                restricted_paths=[row.strip() for row in request.restricted_paths if row.strip()],
                created_by=user_id,
            )
            self._policy_profiles[profile.profile_id] = profile
            self._save_state_unlocked()
            return profile

    async def evaluate_policy(self, request: PolicyCheckRequest) -> PolicyCheckResult:
        profile = await self.get_policy_profile(request.profile_id)
        if profile is None:
            raise KeyError("policy_profile_not_found")

        command = request.command.strip().lower()
        path = (request.path or "").strip()

        for blocked in profile.blocked_commands:
            token = blocked.lower()
            if token and token in command:
                result = PolicyCheckResult(
                    action=PolicyCheckAction.block,
                    reason=f"blocked_command:{blocked}",
                    violation_code="blocked_command",
                )
                await self._record_policy_violation_if_needed(result=result, request=request)
                return result

        for restricted in profile.restricted_paths:
            if restricted and path.startswith(restricted):
                result = PolicyCheckResult(
                    action=PolicyCheckAction.block,
                    reason=f"restricted_path:{restricted}",
                    violation_code="restricted_path",
                )
                await self._record_policy_violation_if_needed(result=result, request=request)
                return result

        return PolicyCheckResult(action=PolicyCheckAction.allow, reason="policy_pass")

    async def get_policy_profile(self, profile_id: UUID) -> PolicyProfile | None:
        async with self._lock:
            return self._policy_profiles.get(profile_id)

    async def store_secret(
        self,
        *,
        user_id: str,
        request: SecretCreateRequest,
    ) -> SecretRef:
        async with self._lock:
            secret_id = uuid4()
            encrypted = self._fernet.encrypt(request.value.encode("utf-8")).decode("utf-8")
            record = SecretRecord(
                secret_id=secret_id,
                name=request.name,
                encrypted_value=encrypted,
                created_by=user_id,
            )
            self._secrets[secret_id] = record
            self._save_state_unlocked()
            return SecretRef(
                secret_id=secret_id,
                name=record.name,
                masked_value=self._mask_value(request.value),
                cipher_digest=self._cipher_digest(record.encrypted_value),
                created_at=record.created_at,
            )

    async def list_secrets(self, *, user_id: str) -> list[SecretRef]:
        async with self._lock:
            rows = [row for row in self._secrets.values() if row.created_by == user_id]
            rows.sort(key=lambda row: row.created_at, reverse=True)
            return [
                SecretRef(
                    secret_id=row.secret_id,
                    name=row.name,
                    masked_value="***",
                    cipher_digest=self._cipher_digest(row.encrypted_value),
                    created_at=row.created_at,
                )
                for row in rows
            ]

    async def get_secret_metadata(self, *, secret_id: UUID, user_id: str) -> SecretMetadata:
        async with self._lock:
            record = self._secrets.get(secret_id)
            if record is None or record.created_by != user_id:
                raise KeyError("secret_not_found")
            return SecretMetadata(
                secret_id=secret_id,
                name=record.name,
                cipher_digest=self._cipher_digest(record.encrypted_value),
                cipher_length=len(record.encrypted_value),
            )

    async def ingest_platform_webhook(
        self,
        *,
        body: bytes,
        timestamp: int,
        nonce: str,
        signature: str,
    ) -> PlatformWebhookResponse:
        now_ts = int(time.time())
        replay_window = max(60, int(settings.webhook_replay_window_seconds))
        if abs(now_ts - timestamp) > replay_window:
            raise ValueError("timestamp_out_of_window")

        expected = self.build_platform_signature(timestamp=timestamp, nonce=nonce, body=body)
        if not hmac.compare_digest(expected, signature):
            raise ValueError("signature_invalid")

        async with self._lock:
            expired = [
                key for key, seen_ts in self._seen_nonces.items() if (now_ts - seen_ts) > replay_window
            ]
            for key in expired:
                self._seen_nonces.pop(key, None)

            if nonce in self._seen_nonces:
                raise ValueError("nonce_replay_detected")
            self._seen_nonces[nonce] = now_ts
            self._save_state_unlocked()

        return PlatformWebhookResponse(status="accepted", nonce=nonce, timestamp=timestamp)

    async def create_idempotent_checkpoint(
        self,
        *,
        build_id: UUID,
        idempotency_key: str,
        reason: str,
    ) -> IdempotentCheckpointResult:
        key = (build_id, idempotency_key.strip())
        if not key[1]:
            raise ValueError("idempotency_key_required")

        async with self._lock:
            self._prune_idempotency_unlocked()
            cached = self._idempotent_checkpoints.get(key)
        if cached is not None:
            checkpoint = BuildCheckpoint.model_validate(cached["checkpoint"])
            return IdempotentCheckpointResult(
                checkpoint_id=checkpoint.checkpoint_id,
                replayed=True,
                status=checkpoint.status.value,
                reason=checkpoint.reason,
            )

        checkpoint = await build_store.create_checkpoint(build_id, reason=reason)
        async with self._lock:
            self._idempotent_checkpoints[key] = {
                "created_ts": int(time.time()),
                "checkpoint": checkpoint.model_dump(mode="json"),
            }
            self._save_state_unlocked()
        return IdempotentCheckpointResult(
            checkpoint_id=checkpoint.checkpoint_id,
            replayed=False,
            status=checkpoint.status.value,
            reason=checkpoint.reason,
        )

    async def slo_summary(self, *, user_id: str) -> SloSummary:
        rows = await build_store.list_builds(user_id=user_id, limit=500)
        total = len(rows)
        completed = sum(1 for row in rows if row.status.value == "completed")
        failed = sum(1 for row in rows if row.status.value == "failed")
        aborted = sum(1 for row in rows if row.status.value == "aborted")
        running = sum(1 for row in rows if row.status.value in {"running", "paused", "pending"})
        mean_cycle = 0.0
        if rows:
            durations = [
                max((row.updated_at - row.created_at).total_seconds(), 0.0)
                for row in rows
            ]
            mean_cycle = sum(durations) / len(durations)
        success_rate = (completed / total) if total else 0.0
        return SloSummary(
            total_builds=total,
            completed_builds=completed,
            failed_builds=failed,
            aborted_builds=aborted,
            running_builds=running,
            success_rate=round(success_rate, 4),
            mean_cycle_seconds=round(mean_cycle, 4),
        )

    async def upsert_release_checklist(
        self,
        *,
        user_id: str,
        request: ReleaseChecklistRequest,
    ) -> ReleaseChecklist:
        async with self._lock:
            row = ReleaseChecklist(
                release_id=request.release_id,
                security_review=request.security_review,
                slo_dashboard=request.slo_dashboard,
                rollback_tested=request.rollback_tested,
                docs_complete=request.docs_complete,
                runbooks_ready=request.runbooks_ready,
                updated_by=user_id,
            )
            self._release_checklists[request.release_id] = row
            self._save_state_unlocked()
            return row

    async def get_release_checklist(self, release_id: str) -> ReleaseChecklist | None:
        async with self._lock:
            return self._release_checklists.get(release_id)

    async def upsert_rollback_drill(
        self,
        *,
        user_id: str,
        request: RollbackDrillRequest,
    ) -> RollbackDrill:
        async with self._lock:
            row = RollbackDrill(
                release_id=request.release_id,
                passed=request.passed,
                duration_minutes=request.duration_minutes,
                issues_found=list(request.issues_found),
                updated_by=user_id,
            )
            self._rollback_drills[request.release_id] = row
            self._save_state_unlocked()
            return row

    async def get_rollback_drill(self, release_id: str) -> RollbackDrill | None:
        async with self._lock:
            return self._rollback_drills.get(release_id)

    async def decide_go_live(
        self,
        *,
        user_id: str,
        request: GoLiveDecisionRequest,
    ) -> GoLiveDecision:
        checklist = await self.get_release_checklist(request.release_id)
        rollback = await self.get_rollback_drill(request.release_id)

        reasons: list[str] = []
        if checklist is None:
            reasons.append("checklist_missing")
        else:
            if not checklist.security_review:
                reasons.append("security_review_incomplete")
            if not checklist.slo_dashboard:
                reasons.append("slo_dashboard_missing")
            if not checklist.docs_complete:
                reasons.append("docs_incomplete")
            if not checklist.runbooks_ready:
                reasons.append("runbooks_not_ready")
            if not checklist.rollback_tested:
                reasons.append("rollback_not_tested")

        if rollback is None:
            reasons.append("rollback_drill_missing")
        elif not rollback.passed:
            reasons.append("rollback_drill_failed")

        if not request.validation_release_ready:
            reasons.append("validation_not_release_ready")

        status = GoLiveDecisionStatus.go if not reasons else GoLiveDecisionStatus.no_go
        decision = GoLiveDecision(
            release_id=request.release_id,
            status=status,
            reasons=reasons,
            decided_by=user_id,
        )
        async with self._lock:
            self._go_live_decisions[request.release_id] = decision
            self._save_state_unlocked()
        return decision

    async def get_go_live_decision(self, release_id: str) -> GoLiveDecision | None:
        async with self._lock:
            return self._go_live_decisions.get(release_id)

    def _load_state(self) -> None:
        if self._state_path is None or not self._state_path.exists():
            return
        try:
            raw = json.loads(self._state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        if not isinstance(raw, dict):
            return

        campaigns = raw.get("campaigns", {})
        if isinstance(campaigns, dict):
            for key, value in campaigns.items():
                if not isinstance(value, dict):
                    continue
                try:
                    campaign_id = UUID(str(key))
                    self._campaigns[campaign_id] = ValidationCampaign.model_validate(value)
                except (ValueError, TypeError):
                    continue

        campaign_runs = raw.get("campaign_runs", {})
        if isinstance(campaign_runs, dict):
            for key, value in campaign_runs.items():
                if not isinstance(value, dict):
                    continue
                try:
                    campaign_id = UUID(str(key))
                except ValueError:
                    continue
                run_bucket: dict[str, ValidationRun] = {}
                for run_id, run_value in value.items():
                    if not isinstance(run_value, dict):
                        continue
                    try:
                        run_bucket[str(run_id)] = ValidationRun.model_validate(run_value)
                    except (ValueError, TypeError):
                        continue
                self._campaign_runs[campaign_id] = run_bucket

        policy_profiles = raw.get("policy_profiles", {})
        if isinstance(policy_profiles, dict):
            for key, value in policy_profiles.items():
                if not isinstance(value, dict):
                    continue
                try:
                    profile_id = UUID(str(key))
                    self._policy_profiles[profile_id] = PolicyProfile.model_validate(value)
                except (ValueError, TypeError):
                    continue

        secrets = raw.get("secrets", {})
        if isinstance(secrets, dict):
            for key, value in secrets.items():
                if not isinstance(value, dict):
                    continue
                try:
                    secret_id = UUID(str(key))
                    self._secrets[secret_id] = SecretRecord.model_validate(value)
                except (ValueError, TypeError):
                    continue

        seen_nonces = raw.get("seen_nonces", {})
        if isinstance(seen_nonces, dict):
            for key, value in seen_nonces.items():
                if isinstance(key, str) and isinstance(value, int):
                    self._seen_nonces[key] = value

        idempotent = raw.get("idempotent_checkpoints", {})
        if isinstance(idempotent, dict):
            for key, value in idempotent.items():
                if not isinstance(key, str) or not isinstance(value, dict):
                    continue
                parts = key.split("::", 1)
                if len(parts) != 2:
                    continue
                try:
                    build_id = UUID(parts[0])
                except ValueError:
                    continue
                idem_key = parts[1]
                if not idem_key:
                    continue
                checkpoint_raw = value.get("checkpoint")
                created_ts = value.get("created_ts", 0)
                if not isinstance(checkpoint_raw, dict) or not isinstance(created_ts, int):
                    continue
                self._idempotent_checkpoints[(build_id, idem_key)] = {
                    "created_ts": created_ts,
                    "checkpoint": checkpoint_raw,
                }

        release_checklists = raw.get("release_checklists", {})
        if isinstance(release_checklists, dict):
            for key, value in release_checklists.items():
                if isinstance(key, str) and isinstance(value, dict):
                    try:
                        self._release_checklists[key] = ReleaseChecklist.model_validate(value)
                    except (ValueError, TypeError):
                        continue

        rollback_drills = raw.get("rollback_drills", {})
        if isinstance(rollback_drills, dict):
            for key, value in rollback_drills.items():
                if isinstance(key, str) and isinstance(value, dict):
                    try:
                        self._rollback_drills[key] = RollbackDrill.model_validate(value)
                    except (ValueError, TypeError):
                        continue

        decisions = raw.get("go_live_decisions", {})
        if isinstance(decisions, dict):
            for key, value in decisions.items():
                if isinstance(key, str) and isinstance(value, dict):
                    try:
                        self._go_live_decisions[key] = GoLiveDecision.model_validate(value)
                    except (ValueError, TypeError):
                        continue

        self._prune_idempotency_unlocked()

    def _save_state_unlocked(self) -> None:
        if self._state_path is None:
            return
        payload = self._serialize_state_unlocked()
        try:
            parent = self._state_path.parent
            parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self._state_path.with_suffix(f"{self._state_path.suffix}.tmp")
            tmp_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            tmp_path.replace(self._state_path)
        except OSError:
            return

    def _serialize_state_unlocked(self) -> dict[str, Any]:
        campaigns = {
            str(key): value.model_dump(mode="json")
            for key, value in self._campaigns.items()
        }
        campaign_runs = {
            str(key): {
                run_id: run.model_dump(mode="json")
                for run_id, run in bucket.items()
            }
            for key, bucket in self._campaign_runs.items()
        }
        policy_profiles = {
            str(key): value.model_dump(mode="json")
            for key, value in self._policy_profiles.items()
        }
        secrets = {
            str(key): value.model_dump(mode="json")
            for key, value in self._secrets.items()
        }
        idempotent = {
            f"{build_id}::{idem_key}": value
            for (build_id, idem_key), value in self._idempotent_checkpoints.items()
        }
        release_checklists = {
            key: value.model_dump(mode="json")
            for key, value in self._release_checklists.items()
        }
        rollback_drills = {
            key: value.model_dump(mode="json")
            for key, value in self._rollback_drills.items()
        }
        go_live_decisions = {
            key: value.model_dump(mode="json")
            for key, value in self._go_live_decisions.items()
        }
        return {
            "campaigns": campaigns,
            "campaign_runs": campaign_runs,
            "policy_profiles": policy_profiles,
            "secrets": secrets,
            "seen_nonces": self._seen_nonces,
            "idempotent_checkpoints": idempotent,
            "release_checklists": release_checklists,
            "rollback_drills": rollback_drills,
            "go_live_decisions": go_live_decisions,
        }

    def _prune_idempotency_unlocked(self) -> None:
        cutoff = int(time.time()) - self._idempotency_ttl_seconds
        expired_keys = [
            key
            for key, value in self._idempotent_checkpoints.items()
            if int(value.get("created_ts", 0)) < cutoff
        ]
        for key in expired_keys:
            self._idempotent_checkpoints.pop(key, None)

    async def _record_policy_violation_if_needed(
        self,
        *,
        result: PolicyCheckResult,
        request: PolicyCheckRequest,
    ) -> None:
        if request.build_id is None or result.action != PolicyCheckAction.block:
            return
        await build_store.record_policy_violation(
            request.build_id,
            code=result.violation_code or "policy_violation",
            message=result.reason,
            source="policy_profile",
            blocking=True,
        )

    def build_platform_signature(self, *, timestamp: int, nonce: str, body: bytes) -> str:
        payload = f"{timestamp}.{nonce}.".encode("utf-8") + body
        return hmac.new(self._platform_secret, payload, sha256).hexdigest()

    def _fernet_key_from_secret(self, secret: str) -> bytes:
        digest = sha256(secret.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)

    def _mask_value(self, value: str) -> str:
        if not value:
            return "***"
        if len(value) <= 4:
            return "***"
        return f"{value[:2]}***{value[-2:]}"

    def _cipher_digest(self, encrypted_value: str) -> str:
        return sha256(encrypted_value.encode("utf-8")).hexdigest()[:16]


program_store = ProgramStore(state_path=settings.program_store_state_path)
