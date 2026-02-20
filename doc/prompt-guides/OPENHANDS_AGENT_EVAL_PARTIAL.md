# OpenHands Configured-Agent Evaluation (Partial Matrix Stop)

## Scope
- Run mode: sequential (`1` worker), high sandbox resources (`4 vCPU / 8 GiB / 10 GiB`)
- Stop condition: user-directed stop after completing the current combo
- Data sources:
  - `doc/runs/daytona-openhands-matrix-checkpoint.json`
  - `doc/runs/manual-current-combo-eval.json`

## Completed Combos Used for Evaluation
| Repo | Model | Status | Total | Hard Gate | Notes |
|---|---|---|---:|---|---|
| `express-hard` | `openai/gpt-5.2-codex` | Infra fail | n/a | n/a | Clone failed (`Connection reset by peer`) |
| `uuid-easy` | `google/gemini-2.5-pro` | Completed | 67.25 | Yes | Failed gate requirements |
| `uuid-easy` | `openai/gpt-5.2-codex` | Completed | 100.00 | No | Full criteria pass (C1..C5 all 100) |

## Configured OpenHands Agent Readout (OpenAI / Codex)
- Strong execution on `uuid-easy` in one-shot mode:
  - C1 one-shot compliance: `100`
  - C2 execution quality: `100`
  - C3 regression prevention: `100`
  - C4 scan delta quality: `100`
  - C5 delivery discipline: `100`
- Observed scan delta on this run: actionable findings `1 -> 0`.
- Branch/doc/user-loop contract passed.

## Reliability Caveats Found
- Infra sensitivity remains high on harder repos:
  - `express-hard` OpenAI run failed before agent execution due repo clone transport reset.
- Branch naming quality issue:
  - branch observed as `codex/uuid-easy-fix-` (missing concrete run-id suffix).
- Daytona FS read API instability persists:
  - `download_file` errors required fallback to `cat`.

## Practical Conclusion
- For the configured OpenHands + OpenAI Codex path, agent behavior is good when execution reaches the model loop.
- Current largest blocker is environment/network robustness, not prompt completeness for easy tasks.

## Immediate Hardening Actions
1. Add clone retry/backoff before marking hard fail (at least 2 retries with jitter).
2. Replace `${RUN_ID}` placeholder with concrete value before prompting.
3. Keep sequential mode for heavy repos under Tier 1 and only increase parallelism after stable preflight.
4. Keep checkpoint resume enabled to prevent rerunning completed combos.
