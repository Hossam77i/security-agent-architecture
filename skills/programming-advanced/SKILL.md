---
name: programming-advanced
description: Use for performance, concurrency, design patterns, TypeScript advanced, Python advanced. Triggers on optimize slow code, memory leak, race condition, design pattern, typescript generics, python asyncio scale.
---

# Programming Advanced

## 0. Objective

Ship fast, safe, maintainable systems: profile before optimizing, choose the right primitive (multiprocessing vs asyncio vs worker threads), apply patterns only with proven need, write strict TS with generics/branded types, use Python decorators/context managers/dataclasses/Pydantic v2 correctly, validate at the boundary, prove gains with benchmarks + heap diffs. Exit: documented p95 win, stress x1000 clean, `tsc --noEmit` + `pyright` clean, `pip-audit`/`npm audit` clean.
Stack: Python 3.11+ + Node 20 + TS strict, FastAPI/Express, pytest/jest/vitest, pytest-benchmark/k6, cProfile/node --prof/clinic.

## 1. Mental model

Measure, then cut: 90% of time lives in 10% of code — fix the hot path, not the pretty code. Concurrency != parallelism: I/O-bound -> overlap waits (asyncio, async/await); CPU-bound -> parallel cores (multiprocessing, worker threads); mixing them up is the #1 perf bug. Shared mutable state is the enemy: two threads touching it need a lock, queue, or elimination — prefer immutable messages + queues. Patterns are costs (indirection): use only with 3+ real use-cases; default to composition + pure functions. Types are machine-checked design: strict TS + Pydantic v2 at boundaries turn runtime surprises into compile errors; `any` is debt with interest.

## 2. Performance: profile, Big-O, streams, LRU

Baseline benchmark -> profile -> fix hotspot -> re-benchmark -> document p95. Suspect any request-path nested loop (O(n^2)); `list.insert(0)`/`shift()` in a loop is O(n^2) — use `deque`/index pointer. Every cache needs maxsize/TTL or it is a leak.

```python
import cProfile
from functools import lru_cache
@lru_cache(maxsize=1024)
def expensive(key: str) -> int: return hash(key) % 10_000
def count_lines(path: str) -> int:  # generator: O(1) memory
    with open(path, encoding="utf-8") as f:
        return sum(1 for line in f)
cProfile.run("count_lines('big.log')", sort="cumulative")
```

```bash
node --prof app.js && node --prof-process isolate-*.log > processed.txt
npx clinic doctor -- node app.js && npx clinic flame -- node app.js
```

```ts
import { createReadStream } from "node:fs"; import { createInterface } from "node:readline";
export async function countLines(path: string): Promise<number> {
  let n = 0;
  const rl = createInterface({ input: createReadStream(path), crlfDelay: Infinity });
  for await (const _ of rl) n++;
  return n;
}
const cache = new Map<string, number>();
export function memoized(key: string): number {
  const hit = cache.get(key); if (hit !== undefined) return hit;
  const v = key.length * 31;
  if (cache.size > 1000) cache.delete(cache.keys().next().value!);
  cache.set(key, v); return v;
}
```

## 3. Concurrency: CPU vs I/O + locks + stress

| Workload | Python | JS/Node |
|---|---|---|
| I/O-bound (API, DB) | `asyncio` + semaphore | `async/await` + `p-limit` + `AbortSignal.timeout` |
| CPU-bound (hash, parse) | `multiprocessing`/`ProcessPoolExecutor` | `worker_threads`/`Piscina` |
| Mixed | async producers + process-pool consumers | main-thread orchestration + worker pool |

```python
import multiprocessing as mp
from threading import Lock
def cpu_hash(n: int) -> int: return sum(hash(str(i)) for i in range(n))
def run_cpu(items: list[int]) -> list[int]:
    with mp.Pool() as pool: return pool.map(cpu_hash, items)
_counter, _lock = 0, Lock()
def inc() -> None:
    global _counter
    with _lock: _counter += 1
# stress: loop 1000x, assert counter == 1000
```

```ts
import { Worker } from "node:worker_threads"; import pLimit from "p-limit";
export function hashInWorker(n: number): Promise<number> {
  return new Promise((res, rej) => {
    const w = new Worker(`parentPort.postMessage(${JSON.stringify(n)});`, { eval: true });
    w.on("message", (v) => { res(v); w.terminate(); }); w.on("error", rej);
  });
}
const limit = pLimit(8);
export const fanOut = (jobs: number[]) => Promise.all(jobs.map((j) => limit(() => hashInWorker(j))));
```

Rules: no shared mutable without lock/`Atomics`/queue; bound every queue (`maxsize`); stress x1000 in CI before claiming thread-safe.

## 4. Patterns with when-to-use

Default to functions + composition. Each pattern needs 3+ use-cases or inline it.

```python
from typing import Protocol
import time
class Discount(Protocol):
    def apply(self, total: float) -> float: ...
class Vip(Discount):  # STRATEGY: swappable pricing/auth/shipping rules
    def apply(self, total: float) -> float: return total * 0.8
class OrderRepo:  # REPOSITORY: swap Postgres/memory/fake in tests
    def __init__(self): self._db = {}
    def save(self, o: dict) -> None: self._db[o["id"]] = o
    def get(self, i: int) -> dict | None: return self._db.get(i)
class Breaker:  # CIRCUIT BREAKER: flaky downstream
    def __init__(self, fails=3, cool=30.0):
        self.fails, self.cool, self.n, self.open_until = fails, cool, 0, 0.0
    def call(self, fn):
        if time.time() < self.open_until: raise RuntimeError("circuit open")
        try: r = fn(); self.n = 0; return r
        except Exception:
            self.n += 1
            if self.n >= self.fails: self.open_until = time.time() + self.cool
            raise
```

```ts
type Handler = (e: { kind: string }) => void;
export class Bus {  // OBSERVER: >2 decoupled subscribers, else direct call
  private h = new Map<string, Handler[]>();
  on(k: string, f: Handler) { this.h.set(k, [...(this.h.get(k) ?? []), f]); }
  emit(e: { kind: string }) { for (const f of this.h.get(e.kind) ?? []) f(e); }
}
export const handlerFactory = (kind: "a" | "b") =>  // FACTORY: branching creation
  kind === "a" ? { run: () => "A" } : { run: () => "B" };
export const adaptLegacy = (old: { GetVal: () => number }) =>  // ADAPTER: legacy shape
  ({ getValue: () => old.GetVal() });
```

Factory = branching creation; Strategy = swappable algorithms; Observer = decoupled events; Repository = persistence seam; Adapter = legacy shape; CircuitBreaker = flaky downstream.

## 5. TypeScript advanced

`tsconfig`: `strict: true` + `noUncheckedIndexedAccess`. No `any` (use `unknown` + narrow). Branded IDs prevent mixups; `never` enforces exhaustiveness; `satisfies` checks shape without widening.

```ts
type UserId = string & { readonly __brand: "UserId" };
export const asUserId = (s: string): UserId => s as UserId;
type Ok<T> = { ok: true; value: T }; type Err = { ok: false; error: string };
export type Result<T> = Ok<T> | Err;
export function assertNever(x: never): never { throw new Error(`unreachable: ${x}`); }
export function describe(r: Result<number>): string {
  if (r.ok) return `value ${r.value}`;
  return `error ${r.error}`;
}
export function first<T>(xs: readonly T[]): T | undefined { return xs[0]; }
const config = { retries: 3, timeoutMs: 5000 } as const satisfies Record<string, number>;
```

## 6. Python advanced

Prefer `dataclass(frozen=True)`/Pydantic for data, `Protocol` for duck-typing, `@wraps` in decorators, `pyproject.toml` + `pipx` for CLIs.

```python
from dataclasses import dataclass
from contextlib import contextmanager
from functools import wraps
from pydantic import BaseModel, Field, field_validator
import time
def timed(fn):
    @wraps(fn)
    def wrapper(*a, **k):
        t = time.perf_counter()
        try: return fn(*a, **k)
        finally: print(f"{fn.__name__} took {time.perf_counter()-t:.3f}s")
    return wrapper
@contextmanager
def timer(label: str):
    t = time.perf_counter()
    try: yield
    finally: print(f"{label}: {time.perf_counter()-t:.3f}s")
@dataclass(frozen=True)
class Money: cents: int; currency: str = "USD"
class ItemIn(BaseModel):  # Pydantic v2 boundary validation
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v: raise ValueError("name required")
        return v
```

## 7. Safety: boundary validation, secrets, SBOM, fuzz

Validate at boundary (Zod/Pydantic), encode on output, secrets from env/vault only (never logged). Fuzz hand-rolled parsers; property-test (`hypothesis`/`fast-check`).

```python
import os
from pydantic import BaseModel
class Webhook(BaseModel): url: str; event: str
def handle(raw: dict) -> None:
    body = Webhook.model_validate(raw)  # reject here
    token = os.environ["API_TOKEN"]  # never hardcoded
    assert body.url.startswith("https://")
```

```ts
import { z } from "zod";
const Webhook = z.object({ url: z.string().url(), event: z.string().min(1) });
export function handle(raw: unknown) {
  const body = Webhook.parse(raw);
  const token = process.env.API_TOKEN;
  if (!token) throw new Error("API_TOKEN missing");
  if (!body.url.startsWith("https://")) throw new Error("https only");
}
```

```bash
pip-audit && npm audit --audit-level=moderate
pip freeze > sbom.txt && npm sbom --package-lock-only > sbom.json
```

## Labs 1-3

**Lab 1 — Profile and fix a hot loop.** O(n^2) dedup/search + 100k-line fixture: cProfile/clinic baseline, rewrite with set/dict or stream, pytest-benchmark/k6 p95 before/after.
Acceptance: >=5x speedup, flat memory, benchmark committed.
**Lab 2 — Concurrency stress.** I/O fan-out (limit 8, timeout 5s) + CPU pool (workers = cores), guarded counter, stress x1000.
Acceptance: no deadlock/race; unbounded version timing documented as worse.
**Lab 3 — Typed boundary + breaker.** Strict-TS `Result<T>` client, branded IDs, exhaustive `never`, Zod/Pydantic validation, breaker around 50%-500 fake.
Acceptance: `tsc --noEmit` clean, zero `any`; breaker opens after 3 fails, recovers half-open; malformed-JSON fuzz finds no crash.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `append`/`shift` hotspot | O(n) head-insert in loop | `collections.deque` / index pointer; batch `extend` |
| `asyncio` slower than sync | CPU work inside async | CPU -> `ProcessPoolExecutor`; async for I/O + semaphore |
| Py threads slower on CPU | GIL on CPU-bound threads | `multiprocessing.Pool`; threads for I/O only |
| Memory grows unbounded | unbounded cache/queue, open streams | `lru_cache(maxsize=)`, `queue(maxsize=)`, streams, heap-diff |
| `any`/`unknown` sprawl | untyped boundary | Validate once (Zod/Pydantic), propagate narrowed types |
| Breaker stuck open/closed | bad counting, no half-open | Count 5xx+timeout only; `cool` window + single probe |

## Mini-project + graduation

**Fast log analyzer (Python AND Node):** stream 1GB+ access log, top-10 IPs/paths, p95 latency, LRU-cached GeoIP stub, worker-pool parsing, JSON report + benchmark. Strict TS + Pydantic args, SBOM + audit clean, heap-diff shows no leak over 3 runs.
- [ ] cProfile/clinic flame before/after committed; p95 improvement documented
- [ ] CPU vs I/O split correctly; stress x1000 green
- [ ] `tsc --noEmit`, `pyright`/`mypy`, `ruff`, `eslint` clean; zero `any`
- [ ] Boundary validation, env secrets, audits clean; benchmark + heap diff in README (<5 min repro)
- [ ] Every pattern justified (3+ use-cases) or removed

## Anti-patterns + Next

Premature optimization without a profile; clever one-liners; reflection/`eval` magic; unbounded queues/caches/retries; shared mutable without locks; `any` default; SQL concat; pattern bingo (AbstractFactoryFactory); asyncio for CPU hashing; threads for GIL-bound loops.
Next: own a subsystem — SLOs, k6 load tests, chaos/stress in CI, runbook, postmortem template. Revisit beginner/intermediate checklists quarterly.
