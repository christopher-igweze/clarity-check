"""POST /api/primer — run or reuse Agent_Primer artifact for a repository."""

from __future__ import annotations

import json
import logging
from uuid import UUID, uuid4

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, HttpUrl

from config import settings
from models.scan import PrimerResult
from sandbox.manager import SandboxManager
from services import supabase_client as db
from services.github import get_head_sha, get_repo_info, parse_repo_url

logger = logging.getLogger(__name__)
router = APIRouter()


class PrimerRequest(BaseModel):
    repo_url: HttpUrl


class PrimerResponse(BaseModel):
    project_id: UUID
    cached: bool
    primer: PrimerResult
    suggested_flows: list[str]


@router.post("/primer", response_model=PrimerResponse)
async def run_primer(request_body: PrimerRequest, request: Request) -> PrimerResponse:
    user_id: str = request.state.user_id

    github_token = await db.get_github_access_token(user_id)
    owner, repo = await parse_repo_url(str(request_body.repo_url))

    try:
        repo_info = await get_repo_info(owner, repo, github_token)
        repo_sha = await get_head_sha(
            owner, repo, repo_info.default_branch, github_token
        )
    except Exception as exc:
        logger.exception("Failed to resolve repo info for primer")
        raise HTTPException(status_code=400, detail=f"Repository access failed: {exc}")

    project_id = await db.get_or_create_project(
        user_id=user_id,
        repo_url=str(request_body.repo_url),
        repo_name=repo_info.full_name,
    )

    cached = await db.get_project_primer(project_id, repo_sha)
    if cached:
        primer = PrimerResult(
            primer_json=cached.get("primer_json") or {},
            summary=cached.get("summary") or "",
            repo_sha=cached.get("repo_sha") or repo_sha,
            confidence=int(cached.get("confidence") or 0),
            failure_reason=cached.get("failure_reason"),
        )
        return PrimerResponse(
            project_id=project_id,
            cached=True,
            primer=primer,
            suggested_flows=_suggest_flows(primer.primer_json),
        )

    scan_id = uuid4()
    sandbox_mgr = SandboxManager()

    primer_json: dict = {}
    summary = ""
    confidence = 0
    failure_reason: str | None = None

    try:
        await sandbox_mgr.provision(scan_id, repo_info.clone_url)
        tree = await sandbox_mgr.exec(
            scan_id,
            "find . -type f -not -path './.git/*' -not -path './node_modules/*' | head -350 | sort",
            timeout=30,
        )
        top_dirs = await sandbox_mgr.exec(scan_id, "ls -1", timeout=15)
        head = await sandbox_mgr.exec(scan_id, "git rev-parse HEAD", timeout=15)
        package_raw = ""
        try:
            package_raw = await sandbox_mgr.read_file(scan_id, "/home/daytona/repo/package.json")
        except Exception:
            package_raw = ""

        package_data = {}
        scripts: list[str] = []
        dependencies: list[str] = []
        if package_raw:
            try:
                package_data = json.loads(package_raw)
                scripts = sorted(list((package_data.get("scripts") or {}).keys()))[:12]
                deps = (package_data.get("dependencies") or {}) | (
                    package_data.get("devDependencies") or {}
                )
                dependencies = sorted(list(deps.keys()))[:20]
            except Exception:
                package_data = {}

        primer_json = {
            "repo_full_name": repo_info.full_name,
            "default_branch": repo_info.default_branch,
            "repo_sha": (head.stdout or repo_sha).strip(),
            "is_private": repo_info.private,
            "file_tree_sample": (tree.stdout or "").splitlines()[:200],
            "top_level_entries": (top_dirs.stdout or "").splitlines()[:40],
            "npm_scripts": scripts,
            "dependency_sample": dependencies,
        }
        summary = await _summarize(primer_json)
        confidence = 85
    except Exception as exc:
        failure_reason = str(exc)
        logger.exception("Primer generation failed")
        primer_json = {
            "repo_full_name": repo_info.full_name,
            "default_branch": repo_info.default_branch,
            "repo_sha": repo_sha,
            "is_private": repo_info.private,
        }
        summary = (
            "Primer could not complete all extraction steps. "
            "Proceeding with fallback intake prompts."
        )
        confidence = 35
    finally:
        await sandbox_mgr.destroy(scan_id)

    primer = PrimerResult(
        primer_json=primer_json,
        summary=summary,
        repo_sha=repo_sha,
        confidence=confidence,
        failure_reason=failure_reason,
    )

    await db.save_project_primer(
        project_id=project_id,
        user_id=user_id,
        repo_sha=repo_sha,
        primer_json=primer.primer_json,
        summary=primer.summary,
        confidence=primer.confidence,
        failure_reason=primer.failure_reason,
    )

    return PrimerResponse(
        project_id=project_id,
        cached=False,
        primer=primer,
        suggested_flows=_suggest_flows(primer_json),
    )


def _suggest_flows(primer_json: dict) -> list[str]:
    tree = "\n".join(primer_json.get("file_tree_sample") or [])
    deps = " ".join(primer_json.get("dependency_sample") or [])
    scripts = " ".join(primer_json.get("npm_scripts") or [])
    haystack = f"{tree}\n{deps}\n{scripts}".lower()

    suggestions: list[str] = []
    if any(x in haystack for x in ["clerk", "next-auth", "auth", "jwt"]):
        suggestions.append("Authentication and sign-in journey")
    if any(x in haystack for x in ["stripe", "checkout", "webhook"]):
        suggestions.append("Payment checkout and webhook flow")
    if any(x in haystack for x in ["dashboard", "analytics", "report"]):
        suggestions.append("Dashboard data load and refresh flow")
    if any(x in haystack for x in ["/api/", "fastapi", "express", "trpc"]):
        suggestions.append("Primary API request/response flow")
    if any(x in haystack for x in ["supabase", "postgres", "prisma", "typeorm"]):
        suggestions.append("Database write/read consistency flow")
    if not suggestions:
        suggestions.append("Core user journey from entry to successful outcome")
    return suggestions[:5]


async def _summarize(primer_json: dict) -> str:
    prompt = (
        "You are Agent_Primer. Summarize this repository context in 4 short bullets:\n"
        "1) likely product purpose\n"
        "2) likely core user flows\n"
        "3) likely deployment/runtime shape\n"
        "4) top immediate audit risk areas\n"
        "Keep it concise and factual.\n\n"
        f"{json.dumps(primer_json)[:15000]}"
    )
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"{settings.openrouter_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.model_scanner,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 280,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            if content:
                return content
    except Exception:
        logger.exception("Primer summary fallback to deterministic text")

    scripts = primer_json.get("npm_scripts") or []
    deps = primer_json.get("dependency_sample") or []
    return (
        f"Repo appears to use scripts: {', '.join(scripts[:5]) or 'unknown'}. "
        f"Dependency sample: {', '.join(deps[:6]) or 'none detected'}. "
        "Audit should prioritize auth, data integrity, and runtime reliability paths."
    )
