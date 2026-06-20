# QA Learning Loop

Use this reference after every automated QA run. The goal is to preserve useful execution knowledge without turning one-off failures into permanent Skill behavior.

## Required Artifacts

Each run should produce these files in its evidence directory:

- `qa-experience-summary.md`
- `qa-skill-optimization-candidates.json`
- `qa-skill-optimization-confirm.template.json`
- `flows-used/`

## What Can Be Promoted

- Stable selectors proven by DOM evidence.
- Flow timing or failure classification fixes that are repeatable.
- Requirement notes that clarify an already reviewed PRD/Lark behavior.
- Environment setup knowledge such as health gate thresholds or WS freshness windows.
- Browser strategy improvements (e.g., viewport selection, CDP connection tips).
- Web test ID requests that help remove coordinate/fallback selectors.

## What Must Not Be Promoted

- Unconfirmed product bugs.
- One-off network, market data, or session timing problems.
- Account credentials, cookies, tokens, or private login details.
- CAPTCHA/login-state details.
- Real-asset or production trading side effects.

## Human Confirmation

Set `confirmed: true` only when the candidate should update the QA Skill. Keep product bugs in `confirmed-bugs.template.json` and follow the Zentao workflow.

After confirming candidates:

```bash
python3 scripts/skill_learning_review.py --apply-confirmed /tmp/onebullex-web-qa/<run>
python3 scripts/skill_learning_review.py --apply-confirmed --write-skill /tmp/onebullex-web-qa/<run>
scripts/sync-onebullex-web-qa-skill.sh
```

Codex and Cursor directories are generated mirrors. Edit the repo source under `workflow/skills/qa/onebullex-web-qa`, then sync.

## Record & Replay Candidate Promotion

Record & Replay outputs are candidate-only. Promote only human-confirmed items from:

- `qa-recording-summary.md`
- `flow-seed-candidates/`
- `route-seed-candidates/`
- `selector-hardening-candidates.json`
- `assertion-candidates.json`
- `test-id-requests.md`

Do not promote raw recordings, sensitive event payloads, one-off network/VPN behavior, or manual-only observations without a stable oracle.

## Professional QA Learning Types

Valid Skill learnings include test-level metadata corrections, oracle coverage fixes, route/selector hardening, anti-flaky waiting improvements, Clash gate documentation, and release-readiness gaps. Product bugs remain in `confirmed-bugs.template.json`.
