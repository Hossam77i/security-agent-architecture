---
name: software-engineering-intermediate
description: Use for architecture, testing pyramid, code review, CI quality gates. Triggers on system design small, testing pyramid, code review checklist, clean architecture, API versioning.
---

# Software Engineering Intermediate

## 0. Objective

Ship maintainable services a team can evolve without fear.
You will: structure code in layers with inward dependencies, version APIs safely,
balance the 70/20/10 test pyramid with contracts, run ruthless reviews,
and gate releases on lint+typecheck+SCA+SAST. Stack: Python FastAPI + TS Express,
Postgres, AWS, monorepo optional, OpenAPI as contract.

## 1. Mental Model

Architecture is about direction of dependencies, not folders.
Layers: API -> Service (use cases) -> Repo/Domain -> Infra. Nothing inner knows outer.
Hexagonal variant: core domain in center, adapters (HTTP, Postgres, SQS, SES) at edges.
C4: Context (who uses system) -> Container (services/DBs) -> Component (modules) -> Code.
Testing pyramid: many fast units, fewer integration, few e2e. Contracts protect seams.
Quality gates shift left: catch injection, typing, vuln deps before merge, not in prod.
Config: code moves, config varies per env. Flags decouple deploy from release.

## 2. Workflow — Deep Dive with Copy-Paste

### 2.1 Layered / hexagonal layout + C4 + /v1 versioning

Python src layout:

```text
src/
  api/v1/reminders.py      # FastAPI routers, DTOs only
  service/reminders.py     # use cases, no SQL/HTTP
  domain/models.py         # dataclasses + invariants
  repo/postgres.py         # SQLAlchemy queries only
  infra/ses.py             # email adapter
tests/unit|integration|e2e/
```

Dependency rule: `api` may import `service`; `service` may import `domain`+ports;
`repo` implements ports. Enforce with import-linter or ESLint boundaries.

FastAPI versioned router:

```python
from fastapi import APIRouter
router = APIRouter(prefix="/v1/reminders", tags=["reminders"])

@router.post("/preview")
def preview(payload: PreviewIn): ...
# v2 adds field with default; keep /v1 for 2 versions
```

Express equivalent:

```ts
import { Router } from "express";
export const v1 = Router();
v1.post("/reminders/preview", previewHandler);
app.use("/v1", v1);
```

C4 L1-L2 in `docs/c4.md`: one Context diagram (users, SES, Postgres, EventBridge)
+ one Container diagram (api, worker, db, queue). Keep PNG + mermaid source.
Backward-compat rule: additive only for 2 versions; never rename/remove without `/v2`.

### 2.2 Testing pyramid 70/20/10 + contracts + coverage gates

Unit (fast, mocked) — Python:

```python
def test_build_reminders_skips_unsubscribed():
    trials = [Trial(id="1", unsubscribed=True), Trial(id="2", unsubscribed=False)]
    assert [t.id for t in build_reminders(trials, days=3)] == ["2"]
```

TS unit with vitest:

```ts
import { describe, it, expect } from "vitest";
import { isExpired } from "./expiry.js";
describe("isExpired", () => {
  it("flags past date", () => expect(isExpired(new Date("2020-01-01"))).toBe(true));
});
```

Integration with testcontainers (Postgres):

```python
from testcontainers.postgres import PostgresContainer
def test_repo_roundtrip():
    with PostgresContainer("postgres:15") as pg:
        repo = PgRepo(pg.get_connection_url())
        repo.save(Trial(id="1")); assert repo.get("1").id == "1"
```

Contract test (Pact / schemathesis): assert OpenAPI response matches schema on every CI run:

```bash
schemathesis run http://localhost:8000/openapi.json --checks all
```

Coverage gates in `pyproject.toml` / CI: `--cov-fail-under=70 --cov-fail-under-diff` style;
simpler: `pytest --cov=src --cov-report=term --fail-under=70`.
Mutation spot-check monthly: `mutmut run --paths-to-mutate src/service`.

### 2.3 Review checklist (correctness / edges / security / perf / tests)

Copy into PR description or `.github/review-checklist.md`:

```markdown
- [ ] correctness: logic matches AC, no dead code
- [ ] edges: null/empty/auth-expired/timezone/pagination
- [ ] security: injection (SQL/f-string), authZ check, no secret in logs
- [ ] perf: no N+1 (check query count), pagination + index
- [ ] tests: unit+integration, contract updated if API changed
- [ ] docs: README/ADR/changelog touched if needed
Approve only if you could on-call it at 3am.
```

N+1 example to reject:

```python
# BAD: 1 + N queries
for t in trials: send(t.owner.email)
# GOOD: batch fetch + bulk insert into reminder_log
```

### 2.4 CI gates — lint + typecheck + SCA + SAST

`.github/workflows/ci.yml`:

```yaml
name: ci
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env: { POSTGRES_PASSWORD: postgres }
        ports: ["5432:5432"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: pip install -r requirements.txt && ruff check . && mypy src
      - run: pytest -q --cov=src --fail-under=70
      - run: npm ci && npm run lint && npm run typecheck && npm test
      - run: pip-audit; npm audit --audit-level=high
      - uses: returntocorp/semgrep-action@v1
```

`CODEOWNERS`:

```text
* @team-lead
/src/service/ @backend-team
openapi.yaml @api-team @backend-team
```

Block merge unless green + 1 approval + no `npm audit high`.

### 2.5 Twelve-factor + flags with expiry + backward-compat migrations

12-factor: env-based config (`DATABASE_URL`, `SES_REGION`), stateless processes,
logs to stdout, backing services attached resources. `.env.example` documents all keys.

Flag with expiry (Unleash-style):

```ts
if (flags.isEnabled("reminders-v2", { userId })) { /* new path */ }
// flags.yaml: { reminders-v2: { expires: "2026-11-01", owner: "@ana" } }
```

Cron scans flags past expiry and fails CI with `flag expired: reminders-v2`.
Backward-compat migration (Alembic):

```python
# expand first (nullable col), backfill, then constrain — never rename in one go
op.add_column("trials", sa.Column("unsub_reason", sa.String(), nullable=True))
```

Deploy order: migrate (expand) -> deploy code reading both -> backfill -> deploy constrain.

### 2.6 Monorepo + OpenAPI contract

npm workspaces `package.json`:

```json
{ "workspaces": ["apps/api", "apps/worker", "packages/contracts"] }
```

Turborepo `turbo.json`: `{ "pipeline": { "build": { "dependsOn": ["^build"] }, "test": {} } }`.
`packages/contracts/openapi.yaml` is source of truth; generate clients:

```bash
npx @openapitools/openapi-generator-cli generate -i packages/contracts/openapi.yaml -g typescript-axios -o packages/client
npx schemathesis run apps/api/openapi.json --checks all
```

API diff check in CI fails on breaking change without `/v2` bump.

## 3. Labs with Acceptance

Lab 1 — Slice layers: refactor a fat route into api/service/repo. Accept: import-linter passes, route file <80 lines.
Lab 2 — Pyramid: add 5 unit + 2 integration + 1 e2e (Playwright) for one flow. Accept: `pytest` <10s for unit, integration uses testcontainers.
Lab 3 — Contract: change response field, watch schemathesis fail, fix spec. Accept: breaking change detected before merge.
Lab 4 — Gates: introduce `npm audit high` vuln + Semgrep `exec()` sink, watch CI red. Accept: fix + CI green, debt note filed.
Lab 5 — Flag + migration: ship dark feature behind expiring flag + expand/backfill migration. Accept: rollback safe, flag expiry CI check passes.

## 4. Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Circular import service<->repo | Layer violation | Extract port interface in `domain/ports.py`, repo implements it |
| Flaky integration tests | Shared dev DB / ordering | Use testcontainers per run, truncate + seed fixtures, no test interdependence |
| Coverage 90% but bugs ship | Snapshot-only / no edges | Add property/edge tests (empty, tz, auth), mutation spot-check |
| `/v1` breakage for mobile clients | Renamed field | Revert, add additive field, serve both for 2 versions, add contract test |
| Migration locks prod table | `ALTER ... NOT NULL` on big table | Expand/backfill constrain in 3 deploys; use `CONCURRENTLY` index |
| Flag left on for months | No expiry/owner | Add `expires` + owner, CI expiry scan, cleanup ticket auto-filed |
| Monorepo CI slow (20 min) | No caching / all packages rebuild | Turborepo remote cache, `npm ci --prefer-offline`, path-filtered workflows |

## 5. Mini-Project + Graduation Checklist

Build `notifications-platform`: FastAPI `/v1` + Express worker share OpenAPI contract,
Postgres + Alembic migrations, flag-gated send, pyramid tests, CI gates, C4 docs.
Graduation checklist:
- [ ] Layered/hexagonal layout, dependency rule enforced
- [ ] C4 L1-L2 committed; API versioned `/v1` with compat policy
- [ ] 70/20/10 split visible; contract test in CI; coverage gate >=70%
- [ ] Review checklist used on 3 PRs; at least one N+1 caught
- [ ] CI runs lint+typecheck+tests+SCA+SAST; merge blocked on red
- [ ] Flags have expiry+owner; migration is expand/backfill/constrain
- [ ] Monorepo builds from root; OpenAPI generates client

## 6. Anti-Patterns + Next

Anti-patterns: microservices for 2 devs, shared DB across services, flag without cleanup,
snapshot-only testing, God service, version bump on breaking change without migration path.
Next: `software-engineering-advanced` — CAP/PACELC, outbox+saga+CQRS, DDD, EventBridge+DLQ,
Redis stampede, sharding, backpressure, RFCs, strangler, SLOs, golden paths, chaos.
