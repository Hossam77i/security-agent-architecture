---
name: software-engineering-beginner
description: Use when learning SDLC, version control hygiene, code style, PRs. Triggers on what is SDLC, how to PR, code style, git commit message, agile basics.
---

# Software Engineering Beginner

## 0. Objective

Work like a team of one that others can read, review, and release safely.
You will: turn vague ideas into a 1-pager, sketch a design, branch/commit cleanly,
open a small reviewable PR, keep style green (Ruff/Black + Prettier/ESLint),
and document so the next person can run, test, and change your code.
Stack: Python (FastAPI) + JS/TS (Express), Postgres, AWS basics, monorepo optional.
Done = CI green, reviewer can merge in <15 min, README lets a stranger run the app.

## 1. Mental Model

Think SDLC as a loop, not a waterfall: Clarify -> Slice -> Build -> Review -> Release -> Learn.
Small batches beat big bangs. Every change has four questions:
What? Why? How tested? What if it breaks?
Git is your timeline: main is always releasable, branches are drafts, commits are sentences.
Style is not taste — it is reduced cognitive load. Linters are robots that nag so humans don't have to.
Docs answer: how do I run it, why is it this way, what did we decide not to do.
Agile is just: visible work, small tickets, fast feedback.

## 2. Workflow — Deep Dive with Copy-Paste

### 2.1 Requirements 1-pager (15 min before code)

Create `docs/1pager-<feature>.md` for anything >half a day:

```markdown
# 1-pager: Expiry reminders for trial users
Problem: 30% of trials lapse without login in last 3 days.
Users: trial owners (primary), support (secondary).
Goal: +5% trial->paid in 6 weeks.
Non-goals: SMS, custom schedules, churn winback.
Proposed: nightly job -> email T-3/T-1, unsubscribe link, metrics logged.
Alternatives: in-app banner only (cheaper, less reach).
Acceptance: email sent at 09:00 UTC, <1% bounce, dashboard shows sent/opened.
Risks: SES reputation, timezone bugs.
```

Rule: if you cannot write Problem/Users/Non-goals/Acceptance, you are not ready to code.

### 2.2 Design sketch (napkin first)

For a FastAPI + Postgres feature, sketch in `docs/design-<feature>.md`:

```markdown
Flow: POST /v1/reminders/preview -> service.build_reminders() -> repo.get_trials()
Tables: trials(id, owner_email, expires_at), reminder_log(trial_id, sent_at, kind)
API: POST /v1/reminders/send {dry_run: bool} -> {sent: int}
Edge: idempotent on (trial_id, kind, date); skip unsubscribed.
Test: unit build_reminders, integration with pg testcontainer.
```

Draw ASCII if no whiteboard: `[cron] -> [api] -> [postgres] -> [SES]`.
Keep it <1 page. Link it in the PR.

### 2.3 Branch + commit conventions

```bash
git checkout main && git pull --rebase origin main
git checkout -b feat/trial-reminder-email
# work in slices, commit early
git add src/reminders/service.py
git commit -m "feat(reminders): build T-3/T-1 reminder list"
git commit -m "test(reminders): cover expiry edge at midnight UTC"
git push -u origin feat/trial-reminder-email
```

Conventional commits: `feat|fix|docs|test|refactor|chore(scope): imperative summary`.
Good: `fix(auth): reject expired JWT with 401 not 500`.
Bad: `wip`, `stuff`, `final final v2`.
Never commit: `.env`, `*.pem`, `node_modules/`, `__pycache__/`, dumps.
Use `.gitignore` + `git status` before every commit. Rebase feature onto main, never merge main into feature.

Suggested `.gitignore` additions:

```gitignore
.env
.env.*
*.pem
dist/
.coverage
.pytest_cache/
```

### 2.4 PR template (copy-paste)

Save as `.github/pull_request_template.md`:

```markdown
## What
<!-- 1-2 sentences -->

## Why
<!-- ticket link + problem -->

## How tested
- [ ] `pytest -q` green
- [ ] `npm test` green (if touched)
- [ ] manual: curl /v1/reminders/preview output pasted below

## Risk / Rollback
<!-- migration? flag? revert commit? -->

## Screenshots / Logs
```

Keep PRs <400 lines. One concern per PR. Link ticket: `Closes #123`.
PR title = commit style: `feat(reminders): send T-3 expiry email`.

`CODEOWNERS` starter (`.github/CODEOWNERS`):

```text
* @team-lead
/src/reminders/ @backend-team
/infra/ @platform-team
```

### 2.5 Style gates — Ruff/Black + Prettier/ESLint

Python `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
select = ["E","F","I","UP","B"]
[tool.black]
line-length = 88
[tool.pytest.ini_options]
addopts = "-q"
```

```bash
ruff check src tests
ruff format --check src tests
black --check src tests
pytest -q
```

JS/TS — `package.json` scripts:

```json
{
  "scripts": {
    "lint": "eslint src --max-warnings 0",
    "format:check": "prettier --check src",
    "test": "vitest run"
  }
}
```

Limits to enforce: functions <30 lines, files <300 lines, nesting <=3,
params <=4 (else introduce object), 88-col soft (Python) / 100-col (TS).
Names reveal intent: `getUserById`, `isTrialExpired`, not `getData`, `handleStuff`.
No magic numbers: `TRIAL_WINDOW_DAYS = 3`.

### 2.6 README / ADR / comments-why

`README.md` minimum:

```markdown
# reminders-svc
## Run
cp .env.example .env && docker compose up --build
## Test
pytest -q; npm test
## Env
DATABASE_URL=postgres://... SES_REGION=us-east-1
## Deploy
git push origin main -> CI -> staging -> prod (manual approve)
```

ADR template `docs/adr/0001-use-postgres-not-dynamo.md`:

```markdown
# ADR 0001: Use Postgres for reminders
Status: accepted | Date: 2026-09-10
Context: need joins on trials + audit log.
Decision: Postgres with Prisma/SQLAlchemy.
Consequences: + simpler queries, - must manage migrations.
```

Comments explain why:

```python
# WHY: SES dedupes on (trial_id, date); do not add time or we double-send.
key = f"{trial_id}:{kind}:{date_str}"
```

### 2.7 Agile tickets with acceptance criteria

Ticket format:

```markdown
Title: [reminders] Send T-3 email
AC:
- [ ] Given trial expires in 3d, when job runs, then email queued
- [ ] Given unsubscribed, when job runs, then skipped + logged
- [ ] p95 job <30s for 10k trials
Size: M. Labels: backend, email.
```

Daily standup: yesterday / today / blocker (30 sec each). Point in T-shirt sizes XS-XL.

## 3. Labs with Acceptance

Lab 1 — 1-pager + sketch: pick a TODO feature, write 1-pager + design sketch. Accept: peer understands it without asking you.
Lab 2 — Clean history: create branch, make 3 conventional commits, push, open PR with template. Accept: `git log --oneline` reads like sentences, CI runs.
Lab 3 — Style green: introduce a long function, then split + rename until Ruff/ESLint pass. Accept: `ruff check` + `npm run lint` zero warnings.
Lab 4 — Docs: write README run/test/env + one ADR. Accept: fresh clone can run via README alone.
Lab 5 — Ticket slice: break a 5-day task into 4 tickets each with AC. Accept: each ticket shippable in <1 day.

## 4. Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `git push` rejected non-fast-forward | main moved ahead | `git pull --rebase origin main`, resolve, `git push` |
| Committed `.env` with secrets | Missing gitignore | Rotate secret, `git rm --cached .env`, add to `.gitignore`, force-push branch only |
| Ruff/Black fight each other | Conflicting line length | Set both to 88 in `pyproject.toml`, run `ruff format` then `black` |
| ESLint passes locally, fails CI | Node version drift | Pin `node-version` in CI yaml, run `npm ci` not `npm install` |
| PR too big to review | Mixed concerns | Split: refactor PR + feat PR + test PR; use stacked branches |
| Tests pass locally, fail CI | Missing env / Postgres service | Add `DATABASE_URL` secret + `services: postgres:15` in CI yaml |
| Merge conflicts on every PR | Long-lived branch | Rebase daily, keep branches <2 days, slice smaller |

## 5. Mini-Project + Graduation Checklist

Build `trial-reminders` (FastAPI or Express + Postgres): preview endpoint, nightly send (dry-run flag), log table, README + ADR + CI.
Graduation checklist:
- [ ] 1-pager + design sketch linked in PR
- [ ] Branch naming + conventional commits, <400-line PR
- [ ] Ruff/Black and Prettier/ESLint green in CI
- [ ] README runs fresh clone; one ADR merged
- [ ] Tickets all had AC; demo shows acceptance met
- [ ] No secrets committed; `.env.example` present
- [ ] Reviewer approved without major rework

## 6. Anti-Patterns + Next

Anti-patterns: force-push to main, 2000-line PRs, `WIP` commits to main, no README, TODO without ticket, commenting what (`# increment i`), formatting by hand.
Next: `software-engineering-intermediate` — layered architecture, testing pyramid, review rubrics, quality gates, 12-factor config, OpenAPI contracts.
