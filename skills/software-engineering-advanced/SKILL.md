---
name: software-engineering-advanced
description: Use for distributed systems, DDD, event-driven, tech leadership. Triggers on distributed design, event-driven, saga, DDD bounded context, tech debt strategy, platform engineering.
---

# Software Engineering Advanced

## 0. Objective

Design evolvable platforms and lead execution under uncertainty.
You will: choose consistency tradeoffs explicitly, make workflows idempotent,
ship events with schemas+DLQ+replay, model domains before tables,
scale statelessly with cache/shard/backpressure, and lead via RFCs, strangler
migrations, debt math, SLOs, and mentoring. Stack: FastAPI/Express, Postgres,
Redis, Kafka/SQS/EventBridge, Lambda/ECS, AWS.

## 1. Mental Model

Distributed systems fail partially — design for timeout, retry, duplicate, reorder.
CAP: partition happens, pick consistency vs availability per operation.
PACELC: else (no partition) pick latency vs consistency.
Idempotency turns at-least-once delivery into exactly-once effect.
Outbox turns dual-write (DB+queue) into one atomic write + relay.
Saga turns distributed transaction into compensable steps; 2PC is rarely worth it.
DDD: language first, then bounded contexts, then aggregates, then code.
Events are facts (`OrderPlaced v1`), not commands. Schema evolves additively.
Scale: stateless app, state in Postgres/Redis/queue; shed load with 429+Retry-After.
Leadership: write the RFC, price the debt, protect the SLO, grow people.

## 2. Workflow — Deep Dive with Copy-Paste

### 2.1 CAP/PACELC + idempotency + outbox/Kafka/SQS + saga vs 2PC + CQRS

Decision snippet for RFC:

```markdown
Operation: charge + create shipment.
P (partition): choose availability for reads (cached), consistency for charge.
E (else): choose consistency for charge (p99 +80ms OK), latency for feed.
```

Idempotency key (FastAPI):

```python
@app.post("/v1/charges")
def charge(req: ChargeIn, idempotency_key: str = Header(...)):
    if seen(idempotency_key): return cached_result(idempotency_key)
    res = stripe.charge(req); store(idempotency_key, res); return res
```

Outbox table + relay:

```sql
CREATE TABLE outbox(id uuid PRIMARY KEY, topic text, payload jsonb, sent_at timestamptz);
-- tx: INSERT order + INSERT outbox in ONE Postgres tx; relay polls WHERE sent_at IS NULL
```

Kafka/SQS producer reads outbox, publishes, marks sent. Consumer is idempotent on `eventId`.
Saga vs 2PC: use saga (choreography via events or orchestration via step function)
with compensations (`refund`, `cancel_shipment`); use 2PC only inside one DB.
CQRS: write model (normalized Postgres) + read model (materialized view/ES) rebuilt
from events where contention high. Timeouts/retries with jitter + deadlines:

```python
@retry(stop_after(3), wait_jitter(0.1, 1.0), deadline=2.0)
def call_ship(): ...
```

### 2.2 DDD — bounded contexts + aggregates + ACL

Context map before code (`docs/context-map.md`):

```markdown
Contexts: Billing | Shipping | Trials.
Billing -> Shipping: customer/supplier (events: OrderPaid v1).
Legacy CRM -> Trials: ACL translates legacy XML -> domain Trial.
Language: Trial {expiresAt, owner} — never "user data blob".
```

Aggregate with invariant (Python):

```python
@dataclass
class Trial:
    id: str; expires_at: datetime; unsubscribed: bool = False
    def schedule(self, kind: str, now: datetime):
        if self.unsubscribed: raise DomainError("unsubscribed")
        if now > self.expires_at: raise DomainError("expired")
        return Reminder(trial_id=self.id, kind=kind)
```

ACL adapter: `legacy_crm_adapter.py` converts legacy fields, isolates cruft;
domain never imports legacy SDK. One aggregate per transaction; reference others by ID.

### 2.3 Event-driven — EventBridge -> Lambda/ECS + registry + DLQ/replay + lag alarms

Event schema `events/OrderPaid.v1.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "OrderPaid.v1",
  "type": "object",
  "required": ["eventId", "occurredAt", "actor", "orderId", "amountCents"],
  "properties": {
    "eventId": { "type": "string", "format": "uuid" },
    "occurredAt": { "type": "string", "format": "date-time" },
    "actor": { "type": "string" },
    "orderId": { "type": "string" },
    "amountCents": { "type": "integer", "minimum": 1 }
  }
}
```

Rule: additive only; `v2` new file; consumers accept `v1+v2` for 2 versions.
EventBridge rule -> Lambda (fast) or ECS (long); SQS queue + DLQ per consumer:

```yaml
# terraform sketch
resource "aws_sqs_queue" "reminders" { visibility_timeout_seconds = 60 }
resource "aws_sqs_queue" "reminders_dlq" { message_retention_seconds = 1209600 }
```

Replay: redrive DLQ to source after fix (`aws sqs start-message-move-task`).
Alarms: consumer lag (ApproximateAgeOfOldestMessage >300s), DLQ depth >0,
failed invocations rate. Dashboard per service: throughput, lag, error%, p99.

### 2.4 Scale — stateless + Redis stampede + sharding + backpressure 429

Stateless: no local sessions/uploads; sticky-free ALB; config from env/Secrets Manager.
Redis stampede protection (TS):

```ts
const v = await redis.get(key);
if (v) return JSON.parse(v);
const lock = await redis.set(`lock:${key}`, "1", "NX", "EX", 5);
if (!lock) return await waitForValue(key); // singleflight
const fresh = await db.load(key);
await redis.set(key, JSON.stringify(fresh), "EX", 60);
return fresh;
```

Sharding: choose key by query pattern (e.g., `owner_id` for trials dashboard);
avoid cross-shard joins; document hot-key plan. Postgres: read replica for feed,
partition `reminder_log` by month.
Backpressure: queue depth metric -> 429 with `Retry-After`:

```ts
res.set("Retry-After", "5").status(429).json({ error: "busy", retryInSec: 5 });
```

Bulkhead + concurrency limits per downstream; load-shed non-critical first.

### 2.5 Leadership — RFCs + strangler + debt math + SLOs + mentoring

RFC template `docs/rfc/0007-charge-flow.md`:

```markdown
# RFC: async charge flow
Options: A sync chain (simple, fragile) | B outbox+saga (chosen) | C 2PC (rejected: ops cost).
Cost: +2 weeks, -80% double-charge. Rollout: strangler route 5% -> 50% -> 100%.
SLO: 99.9% charge success, p99 <800ms. Rollback: flag off.
```

Strangler: facade routes old/new by flag or path; migrate slice by slice; delete legacy last.
Debt math: `principal (fix cost) vs interest (hrs/wk * team rate)`; prioritize if
interest > principal in <3 months. SLOs drive priority: burn-rate alert pages,
feature freeze when error budget <10%.
Mentoring: pair weekly, review rubric (explain tradeoffs, suggest one alternative),
delegate RFC sections to mentees with tight feedback loop.

### 2.6 Golden paths + paved-road observability + failure injection + runbooks

Golden path template: `service-fastapi` (FastAPI+Dockerfile+CI+Terraform+Otel)
and `service-express`; `cookiecutter` or Backstage scaffold in <10 min.
Paved road: structured JSON logs (`traceId`, `eventId`), Otel traces, Prometheus
metrics, default dashboards + alerts provisioned by template.
Runbook `docs/runbook-charge.md`:

```markdown
# Charge flow on-call
Symptoms: DLQ depth rising. Triage: check lag dashboard -> replay sample ->
flag off new flow? Mitigate: redrive DLQ, scale consumer. Escalate: payments on-call.
```

Failure injection monthly in staging: kill broker, partition AZ, expire cert,
saturate Redis. Assert: no double-charge, DLQ+replay works, 429 sheds gracefully.
Each new service ships ADR + runbook + dashboard or it does not ship.

## 3. Labs with Acceptance

Lab 1 — Idempotent charge: implement key-based dedupe + test double-POST. Accept: two identical POSTs charge once.
Lab 2 — Outbox relay: write order+outbox in one tx, relay to SQS/Kafka. Accept: kill relay mid-run, no lost/double event.
Lab 3 — Saga: orchestrate charge->ship with `refund` compensation on ship fail. Accept: chaos kill of ship yields refunded state.
Lab 4 — Schema evolution: publish `OrderPaid v2` additive, old consumer still passes. Accept: registry CI green for both.
Lab 5 — Scale + chaos: stampede test (1k concurrent cold key = 1 DB hit), backpressure 429 under load, DLQ replay drill. Accept: dashboards show lag alarm + clean replay.

## 4. Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Double charge on retry | Missing idempotency key | Key on header, store result, return cached on repeat `eventId` |
| Lost event after DB commit | Dual-write DB then queue | Outbox in same tx + relay; never publish before commit |
| Poison message blocks queue | No DLQ / infinite retry | MaxReceiveCount 3 -> DLQ, alarm on depth, fix + redrive |
| Consumer lag spikes at deploy | Cold cache + thundering herd | Singleflight lock, warm cache, rolling deploy, scale consumers first |
| Cross-service sync timeout chain | 5-service sync call graph | Convert to events/saga, set deadlines + jitter, bulkhead |
| Hot shard (one owner_id huge) | Bad shard key | Split hot key, add read replica/cache, re-shard by `trial_id` hash |
| Schema breakage downs consumer | Renamed/removed field | Revert, additive `v2`, consumer tolerates unknown fields, registry check in CI |

## 5. Mini-Project + Graduation Checklist

Build `billing-pipeline`: FastAPI charges API (idempotent) -> outbox -> Kafka/SQS/EventBridge
-> Lambda/ECS consumer -> Postgres + read model, schema registry, DLQ+replay, lag alarms,
strangler migration from sync legacy, RFC+ADR+runbook+dashboard.
Graduation checklist:
- [ ] PACELC choice documented per operation; deadlines+jitter configured
- [ ] Outbox relay proven lossless under kill; consumer idempotent on `eventId`
- [ ] Saga with compensations tested; 2PC avoided with written reason
- [ ] Bounded contexts + aggregate invariants + ACL for legacy
- [ ] Versioned event schema, DLQ+replay drill recorded, lag alarms live
- [ ] Stateless deploy, stampede guard, shard key justified, 429+Retry-After verified
- [ ] RFC merged, strangler plan executed, debt priced, SLOs wired to alerts
- [ ] Golden-path scaffold used; runbook + chaos drill completed; mentee review done

## 6. Anti-Patterns + Next

Anti-patterns: distributed monolith, sync chain of 5 services, event without schema,
rewrite without strangler, shared mutable DB across contexts, cache without TTL/singleflight,
2PC across regions, SLO without error budget.
Next: platform mastery — Backstage templates, policy-as-code, cost-aware autoscaling,
multi-region active-passive, game-days quarterly, staff-level scope (org-wide RFCs).
