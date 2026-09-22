---
name: problem-solving-advanced
description: Use for hard optimization, DP/graph advanced, incident root cause, postmortems. Triggers on dynamic programming, optimize O(n^2), deadlock, incident root cause, postmortem, scale bottleneck.
---

# Problem Solving Advanced

## 0. Objective

Solve under tight constraints (time, memory, concurrency, cost) and prevent recurrence through RCA and postmortems. When this skill is active: prove the recurrence before coding DP, profile with p50/p95/p99 before optimizing, reproduce concurrency bugs under sanitizers before fixing, and close every incident with timeline + 5 Whys + owned actions.

Done when you can: implement memo + tabulation + state-compressed DP from a written recurrence, run Dijkstra/A*/topo/union-find/segment-tree/KMP from templates, cut p95 by fixing the algorithmic bottleneck (not micro-tweaks), and ship a blameless postmortem with detection + prevention actions within 48 h.

## 1. Mental Model — Prove, Profile, Harden, Prevent

```
PROVE (recurrence / invariant) → CODE (template + proof sketch) → PROFILE (p50/p95/p99)
   → ALGORITHM fix → LAYOUT fix → PARALLELIZE → HARDEN (sanitizers, idempotency)
   → PREVENT (timeline, 5 Whys, ADR, chaos test)
```

Two loops: the **optimization loop** (profile → algorithm → layout → parallelize) and the **reliability loop** (timeline → root cause → fix + detection + prevention). Never parallelize unprofiled code; never close an incident with only a fix.

## 2. Advanced DSA — Recurrences, Templates, Proofs

Rule: write the recurrence + base cases in a comment BEFORE code. If you cannot state optimal substructure, you are not ready for DP.

### 2.1 DP: memo + tabulation + compression

Classic: 0/1 knapsack. Recurrence: `dp[i][w] = max(dp[i-1][w], dp[i-1][w-wt[i]] + val[i])`. Base: `dp[0][*] = 0`. Proof sketch: item `i` is either taken or not; both subproblems are optimal on fewer items → optimal substructure; overlapping because many `(i,w)` repeat.

```python
from functools import lru_cache
def knapsack_memo(wt, val, W):  # O(n*W) time, O(n*W) space
    # Recurrence: dp(i,w) = max(dp(i+1,w), dp(i+1,w-wt[i]) + val[i])
    @lru_cache(maxsize=None)
    def dp(i, w):
        if i == len(wt) or w <= 0:
            return 0
        skip = dp(i + 1, w)
        if wt[i] > w:
            return skip
        return max(skip, dp(i + 1, w - wt[i]) + val[i])
    return dp(0, W)

def knapsack_tab(wt, val, W):  # O(n*W) time, O(W) space (compressed)
    dp = [0] * (W + 1)
    for i in range(len(wt)):
        for w in range(W, wt[i] - 1, -1):  # backwards = reuse 1 row
            dp[w] = max(dp[w], dp[w - wt[i]] + val[i])
    return dp[W]
```

```js
function knapsackTab(wt, val, W) { // O(n*W) time, O(W) space
  const dp = new Array(W + 1).fill(0);
  for (let i = 0; i < wt.length; i++)
    for (let w = W; w >= wt[i]; w--)
      dp[w] = Math.max(dp[w], dp[w - wt[i]] + val[i]);
  return dp[W];
}
```

LCS recurrence: `if a[i]==b[j]: 1+dp(i+1,j+1) else max(dp(i+1,j), dp(i,j+1))`. Edit distance adds replace cost. State compression: keep 1–2 rows when transition uses only previous row.

### 2.2 Union-find (disjoint set) — **components, Kruskal, cycle detect**

```python
class DSU:  # amortized ~O(α(n)) per op
    def __init__(self, n):
        self.p = list(range(n)); self.r = [0]*n
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]  # path halving
            x = self.p[x]
        return x
    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b: return False
        if self.r[a] < self.r[b]: a, b = b, a
        self.p[b] = a
        if self.r[a] == self.r[b]: self.r[a] += 1
        return True
```

### 2.3 Segment tree — **range sum/min + point update in O(log n)**

```python
class SegTree:  # build O(n), query/update O(log n)
    def __init__(self, a):
        n = 1
        while n < len(a): n *= 2
        self.n = n; self.t = [0]*(2*n)
        self.t[n:n+len(a)] = a
        for i in range(n-1, 0, -1): self.t[i] = self.t[2*i] + self.t[2*i+1]
    def update(self, i, v):
        i += self.n; self.t[i] = v; i //= 2
        while i: self.t[i] = self.t[2*i] + self.t[2*i+1]; i //= 2
    def query(self, l, r):  # [l, r)
        l += self.n; r += self.n; s = 0
        while l < r:
            if l & 1: s += self.t[l]; l += 1
            if r & 1: r -= 1; s += self.t[r]
            l //= 2; r //= 2
        return s
```

### 2.4 Dijkstra / A* + topological sort

```python
import heapq
def dijkstra(adj, src):  # O((V+E) log V), non-negative weights
    INF = float("inf")
    dist = {src: 0}
    h = [(0, src)]
    while h:
        d, u = heapq.heappop(h)
        if d != dist[u]: continue  # stale entry
        for v, w in adj[u]:
            nd = d + w
            if nd < dist.get(v, INF):
                dist[v] = nd
                heapq.heappush(h, (nd, v))
    return dist
# A*: priority = g + heuristic(v); heuristic must be admissible (never overestimate).
# Proof sketch: popped node has smallest tentative distance; any alt path is ≥ via non-negative edges.

from collections import deque, defaultdict
def topo_sort(n, edges):  # O(V+E); returns [] if cycle (Kahn)
    indeg = [0]*n; g = defaultdict(list)
    for u, v in edges: g[u].append(v); indeg[v] += 1
    q = deque([i for i in range(n) if indeg[i] == 0])
    order = []
    while q:
        u = q.popleft(); order.append(u)
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0: q.append(v)
    return order if len(order) == n else []
```

### 2.5 KMP — **substring search O(n+m)**

```python
def kmp_prefix(p):  # failure function O(m)
    pi = [0]*len(p)
    for i in range(1, len(p)):
        j = pi[i-1]
        while j > 0 and p[i] != p[j]: j = pi[j-1]
        if p[i] == p[j]: j += 1
        pi[i] = j
    return pi

def kmp_search(t, p):  # O(n+m)
    if not p: return 0
    pi = kmp_prefix(p); j = 0
    for i, c in enumerate(t):
        while j > 0 and c != p[j]: j = pi[j-1]
        if c == p[j]: j += 1
        if j == len(p): return i - len(p) + 1
    return -1
```

## 3. Optimization Loop — Profile → Algorithm → Layout → Parallelize

1. **Profile first.** Capture p50/p95/p99 + flamegraph before/after. Python: `cProfile`, `py-spy`, `time.perf_counter` histograms. JS: `--prof`, clinic.js, `performance.now()` buckets. Load test: `k6 run load.js`. The bottleneck is the top frame covering ~80/20 — fix that, ignore the rest.
2. **Algorithmic fix (10–1000x).** O(n²)→O(n log n): sort + heap instead of nested scan; repeated range queries → prefix sum / segment tree; repeated search → index (dict). Document before/after p95 in the PR.
3. **Data layout (2–10x).** Cache locality: arrays over pointer-chasing, batch I/O (read 1000 rows/call, not 1), avoid N+1 queries, compress hot structs, reuse buffers. Example: batch DB fetch cut p95 800 ms → 120 ms before any threading.
4. **Parallelize last (÷cores, with overhead).** Multiprocess/threads for CPU/IO respectively; measure speedup vs cores — if 8 cores give 2x, stop (lock contention). JS: worker threads for CPU, async batching for IO.

Record: `before p50/p95/p99 = 40/800/2100 ms → after = 35/120/300 ms, n=1e6, commit <sha>`.

## 4. Concurrency Bugs — Sanitize, Order, Idempotency

- **Reproduce under stress first:** thread sanitizer (`-fsanitize=thread`, `go run -race`, `pytest -n auto --stress`), 10k-iteration loop, fault injection (kill -9, disk full via `fallocate`, clock skew via `faketime`).
- **Lock ordering:** global order (e.g. `user_lock` before `order_lock`), hold shortest time, never call out while holding. Deadlock proof: lock graph acyclic → no deadlock.
- **Idempotency:** idempotency keys + dedupe table for exactly-once effects; retries with exponential backoff + jitter (`sleep = rand(0, min(cap, base*2^attempt))`) + circuit breaker. No fix without a failing stress test that now passes.

```python
import time, random
def with_retry(fn, attempts=5, base=0.1, cap=5.0):
    for i in range(attempts):
        try:
            return fn()
        except TransientError:
            if i == attempts - 1: raise
            time.sleep(random.uniform(0, min(cap, base * 2**i)))
```

## 5. Incident RCA — Timeline + 5 Whys + Blameless Postmortem

**Timeline (UTC, every entry):** `14:02:11Z alert p99>2s fired → 14:05 deploy v1.4.2 → 14:09 retry storm 10x → 14:15 circuit breaker added, recovered.` Distinguish contributing causes (high traffic) from root cause (unbounded retries, no jitter).

**5 Whys worked example (retry storm):**

1. Why p99 2 s? → downstream slow + 10x retry amplification.
2. Why amplification? → retry with no backoff/jitter, 3 clients × 3 retries instantly.
3. Why no backoff? → retry helper lacked jitter; no review checklist item.
4. Why undetected? → no dashboard on retry rate; alert only on latency.
5. Why? → action gap. Root cause: unbounded synchronized retries. Fixes: jitter + breaker (fix), retry-rate dashboard + alert (detection), load-test with downstream slowness (prevention).

**Postmortem template:** Summary, Impact (reqs failed, $/SLA), Timeline, Root vs contributing causes, Actions table (fix/detection/prevention × owner × date), Lessons. Blameless: "how did the system allow it", never "who". Review within 48 h.

**ADR cost math:** `cost/1M reqs = (ms_per_req/1000) × $/vCPU-s × replicas + $DB. Decision: cache (consistency: 60 s stale) vs scale-out — cache cuts $420→$38/1M reqs, rollback = flag off.` Always include rollback plan.

## 6. Labs + Chaos Tests

- **Lab A — DP:** knapsack + edit distance, memo and tabbed, with recurrence comment + proof sketch. Acceptance: passes brute-force cross-check on 100 random small cases.
- **Lab B — Graphs:** Dijkstra on 10k-node graph vs Bellman-Ford timing; topo sort with cycle detection. Acceptance: correct distances + O() comment + timing table.
- **Lab C — Optimize:** take an O(n²) report endpoint (n=1e5) to O(n log n); show p50/p95/p99 before/after + flamegraph screenshot. Acceptance: p95 down ≥5x.
- **Lab D — Chaos:** kill -9 mid-write, disk-full, clock-skew +5 min. Acceptance: no corrupt state (dedupe table holds), retries converge, dashboard catches it.

## 7. Troubleshooting Table

| Symptom | Likely cause | Fix |
|---|---|---|
| DP wrong answer, memo passes small but fails large | Recurrence missing case / bad base | Cross-check vs brute force on small n; print dp table for n=3 |
| DP MLE (memory blow) | Full n×W table kept | Compress to 1–2 rows (iterate backwards); store short/int32 |
| Dijkstra wrong with negative edge | Violated non-negative assumption | Use Bellman-Ford / SPFA; assert weights ≥ 0 at load |
| A* slower than Dijkstra | Inadmissible/weak heuristic | Prove h ≤ true cost; benchmark both, keep faster with data |
| Topo returns [] on valid DAG | Wrong indegree / missing nodes | Log indegrees; ensure all n nodes initialized |
| KMP misses overlap matches | Reset `j = pi[j-1]` skipped | Use template verbatim; test `AAAA` in `AAAAAAAA` |
| p95 unchanged after threading | Lock contention / GIL / IO-bound misjudged | Profile lock wait; switch to batching or multiprocess |
| Flaky concurrency test | No sanitizer / too few iters | `-race`/TSan + 10k iters + fault injection; seed RNG |
| Deadlock in prod only | Lock order inversion under load | Enforce global order; dump stacks (`py-spy`, `jstack`) at hang |
| Retry storm after deploy | No jitter/breaker | Add jitter + breaker + retry-rate alert; chaos-test slow downstream |
| Postmortem actions rot | No owner/date | Every action: owner + due date + verification (dashboard link) |

## 8. Mini-Project — Bottleneck + Postmortem Package

Take a slow endpoint (or synthetic 1M-row pipeline): (1) profile and record p50/p95/p99 + flamegraph; (2) apply algorithm fix then layout fix, re-measure; (3) add idempotent retry with jitter + dedupe table, chaos-test kill-9/disk-full; (4) write 1-page ADR with $/1M-reqs math + rollback; (5) write blameless postmortem for an injected incident (retry storm) with timeline, 5 Whys, fix/detection/prevention actions. Acceptance: p95 improved ≥5x with numbers, chaos tests pass, postmortem reviewed within 48 h, ADR merged.

## 9. Graduation Checklist

- [ ] Writes recurrence + base + proof sketch before any DP code.
- [ ] Implements DP memo + tabulation + compressed from templates.
- [ ] Runs union-find / segment tree / Dijkstra-A* / topo / KMP from memory of template shape.
- [ ] Records p50/p95/p99 + flamegraph before/after every optimization.
- [ ] Applies profile→algorithm→layout→parallelize in order with measured gains.
- [ ] Reproduces concurrency bug under sanitizer/stress before fixing; fix includes lock ordering + idempotency.
- [ ] Ships timeline (UTC) + 5 Whys distinguishing root vs contributing causes.
- [ ] Ships blameless postmortem in 48 h with owned/dated fix+detection+prevention.
- [ ] Writes ADR with $/1M-reqs cost math + rollback plan.
- [ ] Passes chaos tests (kill-9, disk-full, clock-skew).

## 10. Anti-Patterns

- DP without recurrence (guessing transitions until tests pass).
- Sharding/caching/parallelizing before profiling (scaling the wrong bottleneck).
- Fixing symptoms (restarting cron) instead of root cause (unbounded retries).
- Postmortem without action items, owners, or dates.
- Greedy without exchange-argument proof; Dijkstra with negative weights.
- Locks in inconsistent order; retries without jitter/breaker; non-idempotent handlers.
- Reporting averages only (mean hides p99 pain) — always p50/p95/p99.

## 11. Next

Maintain mastery: monthly chaos drill, quarterly p95 review per service, ADR for every consistency/latency/cost tradeoff. Teach back: mentor an intermediate through the 30-problem plan, review their O() comments and hypothesis tables. Revisit when constraints change (10x scale, new consistency requirement, new incident class).

