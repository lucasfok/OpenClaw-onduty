---
name: onduty-runbook-checker
description: Use this skill when asked to create, update, or execute daily on-duty runbook health checks across environments (prod/staging/dev), including weekly responsible-person rotation, HTTP/TCP/command checks, and result reporting.
---

# On-duty runbook checker

## When to use
Use this skill when the task mentions:
- daily/periodic on-duty checks,
- runbook automation,
- cross-environment health checks,
- weekly ownership rotation for incident/check follow-up,
- verification reports for operations.

## Workflow
1. Open `/etc/onduty/runbook.json` (or `RUNBOOK_PATH`) and validate each check has `name`, `environment`, and `type`.
2. Open `/etc/onduty/rotation-team.json` (or `ROTATION_TEAM_PATH`) to load eligible people.
3. Select the weekly responsible person with persisted state (`ROTATION_STATE_PATH`), avoiding repetition until everyone is selected.
4. Execute checks:
   - `http`: validate status code and optional response substring.
   - `tcp`: validate connection to host/port.
   - `command`: run command and validate exit code/stdout substring.
5. Generate JSON report in `/workspace/reports` with pass/fail summary + `responsible_person`.
6. If failures exist, exit with non-zero status and include details in report.

## Check schema reference
For check fields, see [references/check-types.md](references/check-types.md). For weekly ownership rotation, see [references/rotation.md](references/rotation.md).
