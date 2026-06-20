# Record & Replay Policy For Web QA

Record & Replay is a path-discovery and Skill-learning accelerator. It is not the long-term Web QA execution engine.

## Quality Gate

A recording can produce candidates only when:

- The target workflow is complete from entry to expected checkpoint.
- It does not contain passwords, OTPs, cookies, tokens, private account details, or exact funds data.
- Route, action, and assertion candidates can be identified.
- Key interactions can be mapped to DOM selector, role, text, or route candidates.
- The recording is not dominated by mis-clicks, random drag gestures, or repeated trial-and-error.

## Candidate Outputs

Recordings may produce:

- `recording_summary`
- `flow_seed`
- `route_candidate`
- `selector_candidate`
- `assertion_candidate`
- `test_id_request`
- `do_not_promote`

Only human-confirmed candidates may update `routes/*.yaml`, `flows/*.yaml`, or Skill references.

## Sensitive Data

Raw event streams stay in local evidence only. Do not commit raw recordings or sensitive event payloads to Git.
