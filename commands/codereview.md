---
description: Full security source-code review: threat model, per-class audit, verified findings register, remediation. Usage: /codereview <path-or-repo> [language-focus]
---

Run a deep security-focused source code review of $ARGUMENTS following `secure-code-review`, `security-code-audit`, and `source-code-scanning` skills. If the path is unknown or ambiguous, ask before proceeding.

1. **Scope** — Inventory the codebase: language, framework, dependency manifest, entry points (HTTP handlers, CLI, message consumers), auth layer. State the attack surface and 1-3 highest-risk data flows (money, auth, file I/O, user data).
2. **Taint-first audit** — Trace user input → sink, prioritizing: auth/authorization, SQL/ORM, command exec, SSRF/URL fetch, path/file ops, deserialization, template rendering, ORM mass-assignment. Use the `sast-*` skills by class.
3. **Deep dive** — for the top 3 risk areas do a multi-file flow review (component → handler → service → DB), not just single-function checks. Check business logic + state machines, not only classic injection.
4. **Tool pass** — if tools are available (semgrep, bandit, gitleaks, trivy, osv-scanner, npm/pip audit), run them and reconcile their output with manual findings.
5. **Deliverable** — a severity-ranked findings register:
   - each finding: `title | severity (CVSS 3.1) | file:line | vuln class | preconditions | reproduction | impact`
   - mark confirmed vs theoretical; for confirmed, provide a minimal proof (curl/request or small repro) when safe
   - remediation per finding (fix, why it works, test)
   - a "clean" checklist confirming what was checked and found clean
6. **Output** — save the report as `CODE_REVIEW_<project>.md` and give a 5-line executive summary with the top 3 fixes.

Rules: only review code you own or are authorized to test. Never execute malicious payloads against live systems. Do not invent file:line references — verify with Read/Grep before citing.