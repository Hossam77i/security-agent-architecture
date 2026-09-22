---
name: programming-intermediate
description: Use for OOP, APIs, async, testing, Node/Python backend work. Triggers on build REST api, async await, pytest, jest test, class design, fetch data, express/fastapi.
---

# Programming Intermediate (Full-stack Python/JS)

## 0. Objective

Build tested full-stack features: paginated REST in FastAPI + Express with Pydantic/Zod, async I/O with timeouts + concurrency caps, AAA tests with mocks + 70% coverage, structured logs with retry/backoff, Postgres via SQLAlchemy/Prisma with migrations. Exit: Vite -> API -> DB works locally, CORS locked, `pytest + jest --coverage` green, zero string-concat SQL.
Stack: Python 3.11+ + Node 20 + TS basics, FastAPI/Express, pytest/jest-or-vitest, Postgres 15+.

## 1. Mental model

Layers, not spaghetti: request -> validation -> service (pure logic) -> repository (DB) -> response. Controllers stay thin; logic lives in testable functions. Composition over inheritance — inject dependencies so tests substitute fakes; inheritance depth >1 is a smell. Validate once at the HTTP boundary (Pydantic/Zod), trust typed objects inside. Async overlaps I/O waits, it does not speed CPU — never block the event loop. Tests are executable specs: mock at the network/DB seam, never mock your own logic; unasserted behavior is broken behavior you have not found yet.

## 2. OOP, composition, modules

One class = one responsibility. Python packages need `__init__.py` + absolute imports; JS ESM needs `.js` suffix under NodeNext.

```python
from dataclasses import dataclass
@dataclass
class Order: id: int; total: float; status: str = "pending"
class Pricer:
    def total(self, items: list[dict]) -> float:
        return round(sum(i["price"] * i["qty"] for i in items), 2)
class OrderService:  # composition + injection
    def __init__(self, pricer: Pricer) -> None: self.pricer = pricer
    def create(self, items: list[dict]) -> Order:
        if not items: raise ValueError("items required")
        return Order(id=1, total=self.pricer.total(items))
```

```ts
export interface Item { price: number; qty: number }
export class Pricer {
  total(items: Item[]): number {
    return Math.round(items.reduce((s, i) => s + i.price * i.qty, 0) * 100) / 100;
  }
}
export class OrderService {
  constructor(private pricer: Pricer = new Pricer()) {}
  create(items: Item[]) {
    if (!items.length) throw new Error("items required");
    return { id: 1, total: this.pricer.total(items), status: "pending" as const };
  }
}
```

## 3. REST: FastAPI + Express, validation, pagination

Contract first: 200/201/400/404/422/500, envelope `{ data, page }`, bounded `limit`. Never trust client `limit`.

```python
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
app = FastAPI()
class ItemIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
DB: list[dict] = []
@app.post("/items", status_code=201)
def create_item(body: ItemIn) -> dict:
    item = {"id": len(DB) + 1, **body.model_dump()}
    DB.append(item); return {"data": item}
@app.get("/items")
def list_items(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)) -> dict:
    s = (page - 1) * limit
    return {"data": DB[s:s + limit], "page": {"page": page, "limit": limit, "total": len(DB)}}
```

```ts
import express from "express"; import { z } from "zod";
const app = express(); app.use(express.json());
const ItemIn = z.object({ name: z.string().min(1).max(100), price: z.number().positive() });
const DB: Array<{ id: number; name: string; price: number }> = [];
app.post("/items", (req, res) => {
  const p = ItemIn.safeParse(req.body);
  if (!p.success) return res.status(422).json({ error: p.error.flatten() });
  const item = { id: DB.length + 1, ...p.data }; DB.push(item);
  return res.status(201).json({ data: item });
});
app.get("/items", (req, res) => {
  const page = Math.max(1, Number(req.query.page ?? 1));
  const limit = Math.min(100, Math.max(1, Number(req.query.limit ?? 20)));
  const s = (page - 1) * limit;
  res.json({ data: DB.slice(s, s + limit), page: { page, limit, total: DB.length } });
});
app.listen(3000);
```

Save a `.http`/Postman collection; verify `422` on `price: -1` and slice correctness on page 2.

## 4. Async + timeouts + concurrency caps

Every outbound I/O gets a timeout; every fan-out gets a cap. Bare `Promise.all` on 100 URLs = self-DDoS.

```python
import asyncio, aiohttp
async def fetch_one(s: aiohttp.ClientSession, url: str) -> dict:
    async with s.get(url, timeout=aiohttp.ClientTimeout(total=5)) as r:
        r.raise_for_status(); return await r.json()
async def fetch_all(urls: list[str]) -> list[dict]:
    sem = asyncio.Semaphore(5)
    async with aiohttp.ClientSession() as s:
        async def one(u: str):
            async with sem: return await fetch_one(s, u)
        return await asyncio.gather(*[one(u) for u in urls])
```

```ts
import pLimit from "p-limit";
const limit = pLimit(5);
async function fetchOne(url: string) {
  const res = await fetch(url, { signal: AbortSignal.timeout(5000) });
  if (!res.ok) throw new Error(`HTTP ${res.status} ${url}`);
  return res.json();
}
export const fetchAll = (urls: string[]) =>
  Promise.all(urls.map((u) => limit(() => fetchOne(u))));
```

## 5. Testing: AAA + mocks + coverage

One behavior per test. Mock network/DB (`responses`, `msw`/`vi.spyOn`), never your own logic. Real route contract test with test DB per suite.

```python
import pytest
from app.services.orders import OrderService, Pricer
def test_create_totals_items():
    svc = OrderService(Pricer())  # arrange
    order = svc.create([{"price": 10.0, "qty": 2}])  # act
    assert order.total == 20.0  # assert
def test_create_rejects_empty():
    with pytest.raises(ValueError, match="items required"):
        OrderService(Pricer()).create([])
```

```ts
import { describe, it, expect } from "vitest"; import { OrderService } from "./orders.js";
describe("OrderService", () => {
  it("totals items", () => {
    const svc = new OrderService({ total: () => 20 } as any);
    expect(svc.create([{ price: 10, qty: 2 }]).total).toBe(20);
  });
  it("rejects empty", () => {
    expect(() => new OrderService().create([])).toThrow("items required");
  });
});
```

```bash
pytest -q --cov=app --cov-fail-under=70
npm test -- --coverage --coverageThreshold='{"global":{"lines":70}}'
```

## 6. Errors, logs, retry-backoff

Custom errors carry status; logs are JSON with request IDs; retry 5xx/timeouts only, never 4xx, with jitter.

```python
import logging, time, uuid, random
class AppError(Exception):
    def __init__(self, msg: str, status: int = 500): super().__init__(msg); self.status = status
class NotFound(AppError):
    def __init__(self, msg="not found"): super().__init__(msg, 404)
logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("api")
def retry_5xx(fn, tries=3):
    for i in range(tries):
        try: return fn()
        except AppError as e:
            if e.status < 500 or i == tries - 1: raise
            time.sleep(0.2 * (2 ** i) + random.uniform(0, 0.1))
```

```ts
export class AppError extends Error { constructor(m: string, public status = 500) { super(m); } }
export class NotFound extends AppError { constructor(m = "not found") { super(m, 404); } }
export async function retry5xx<T>(fn: () => Promise<T>, tries = 3): Promise<T> {
  for (let i = 0; i < tries; i++) {
    try { return await fn(); } catch (e: any) {
      if (!(e?.status >= 500) || i === tries - 1) throw e;
      await new Promise((r) => setTimeout(r, 200 * 2 ** i + Math.random() * 100));
    }
  }
  throw new Error("unreachable");
}
```

## 7. Postgres: parameterized only + migrations

```python
from sqlalchemy import create_engine, text
eng = create_engine("postgresql+psycopg://app:secret@localhost:5432/app")
def get_user(user_id: int) -> dict | None:
    with eng.connect() as c:
        row = c.execute(text("SELECT id, name FROM users WHERE id = :id"),
                        {"id": user_id}).mappings().first()
        return dict(row) if row else None
# alembic revision --autogenerate -m "add users" && alembic upgrade head
```

```ts
import { PrismaClient } from "@prisma/client";
const prisma = new PrismaClient();
export const getUser = (id: number) => prisma.user.findUnique({ where: { id } });
// npx prisma migrate dev --name add_users
```

Never `"WHERE id = " + userId`. Lint with `ruff S` / `eslint-plugin-security`. One migration per deploy; never hand-edit prod.

## 8. Full-stack tie: Vite -> API -> DB + CORS

```ts
const res = await fetch(`${import.meta.env.VITE_API_URL}/items?page=1`, {
  signal: AbortSignal.timeout(5000) });
if (!res.ok) throw new Error(`API ${res.status}`);
const { data } = await res.json();
```

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_methods=["GET", "POST"], allow_headers=["Content-Type", "Authorization"])
```

```ts
import cors from "cors";
app.use(cors({ origin: "http://localhost:5173", methods: ["GET", "POST"] }));
```

Env per stage (`.env.development/.env.production` + `VITE_API_URL`). Frontend never holds DB credentials.

## Labs 1-3

**Lab 1 — Paginated items API (both stacks).** `POST/GET /items` in FastAPI AND Express with validation + `{ data, page }`.
Acceptance: `422` on `price: -1`; `?page=2&limit=2` slices correctly; collection committed.
**Lab 2 — Capped fetcher.** 20 URLs, concurrency 5, 5s timeout; per-URL success/error without aborting batch.
Acceptance: 1 slow URL times out while 19 succeed; max-concurrency assertion in test.
**Lab 3 — Tested service + DB read.** Injected `Pricer`, 70%+ coverage, mocked DB, one bound-param query.
Acceptance: both coverage gates pass; `get_user` uses params; migration file exists.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `422` from FastAPI | Pydantic rejected body | Read `detail` array; match names/types; retry minimal JSON |
| CORS in browser, curl fine | origin not allowlisted | Exact `http://localhost:5173`, no `*` with creds; restart API |
| `Promise.all` hangs / 429s | unbounded fan-out, no timeout | `p-limit(5)` + `AbortSignal.timeout(5000)`; per-item catch |
| `Event loop is closed` | unclosed `ClientSession` | `async with ClientSession()`; single `asyncio.run(main())` |
| Green tests, prod bug | mocked own logic, no contract test | Add route-level test on test DB; assert status + shape |
| `relation "users" does not exist` | migration not applied | `alembic upgrade head` / `prisma migrate dev`; check `DATABASE_URL` |

## Mini-project + graduation

**Bookmarks API + Vite UI:** `POST /bookmarks {url, title}`, `GET /bookmarks?page=&limit=` newest-first, `DELETE /bookmarks/:id`. URL-validated, title 1-120, Postgres-backed. Vite lists/adds, inline API errors. JSON logs with request IDs; one frontend retry on 5xx.
- [ ] `pytest -q` + `npm test -- --coverage` green, logic >= 70%
- [ ] `ruff`, `mypy`/`pyright`, `eslint`, `tsc --noEmit` clean
- [ ] Contract test (status + shape + pagination) passes in CI
- [ ] No SQL concat; migration rebuilds DB from scratch
- [ ] CORS = frontend origin only; `.env` never committed; README has `compose up`, migrate, seed, curl examples

## Anti-patterns + Next

God routers (500-line `main.py`); N+1 list queries (eager-load/batch); swallowed errors (`except: return None`); `any` everywhere (type boundary, narrow inward); timeout-less `fetch`; unbounded `Promise.all`; committed `.env`; coverage of getters but not failure paths.
Next: `programming-advanced` — profiling, concurrency at scale, patterns with when-to-use, strict TS, supply-chain safety, benchmarks.
