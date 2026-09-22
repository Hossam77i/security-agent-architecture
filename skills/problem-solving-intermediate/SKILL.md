---
name: problem-solving-intermediate
description: Use for data structures, Big-O, systematic debugging, LeetCode patterns. Triggers on big-o, hashmap vs array, two pointers, debugging strategy, bisect, recursion vs loop.
---

# Problem Solving Intermediate

## 0. Objective

Pick the right structure in under 2 minutes, estimate Big-O before coding, and debug with hypotheses instead of guesses. Rule: map every problem to one of 7 patterns, write complexity in a comment, and build a minimal failing repro before any fix. Done when 30 mixed problems carry correct O() notes and a hypothesis table converges in ≤3 experiments.

## 1. Mental Model — Constraints → Pattern → Structure → Complexity

```
CONSTRAINTS (n = ?) → PATTERN (which of 7?) → STRUCTURE → O() fits n? → CODE → MEASURE
```

Sizing rules (~1e8 ops/sec):

| n | Must be ≤ | Examples |
|---|---|---|
| ≤500 | O(n^2) | nested loops |
| ≤1e5 | O(n log n) | sort + binary search, heap, DFS/BFS O(V+E) |
| ≥1e5 / many queries | O(n) or O(1)/O(log n) each | two pointers, sliding window, prefix sum, hashmap |

Space tradeoff: hashmap buys O(1) lookup for O(n) memory; sort buys binary search for O(n log n) upfront. State both: `Time O(n), Space O(n)`.

## 2. DSA Core + Costs

| Structure | Lookup | Insert/Delete | Use when |
|---|---|---|---|
| Array/list | O(1) index, O(n) search | O(n) middle, O(1) append | order, scan/slide |
| HashMap/Set | O(1) avg | O(1) avg | dedupe, frequency, lookup |
| Stack/Queue | O(1) top | O(1) push/pop | parens, monotonic, BFS |
| Heap | O(1) peek, O(log n) pop | O(log n) push | top-k, merge k lists |
| Graph adj. list | O(deg) neighbors | O(1) add edge | DFS/BFS, shortest path |
| Trie | O(L) | O(L) | prefix search |

Python: `Counter`, `defaultdict(list)`, `heapq` (min-heap; negate for max), `bisect_left/right`, `deque` (O(1) popleft). JS: `Map/Set` (O(1)), numeric sort `.sort((a,b)=>a-b)` (default is lexicographic!), queue via index pointer not `shift()` (O(n)).

## 3. The 7 Patterns with Templates

Name the pattern in <2 min before coding.

### 3.1 Two pointers — sorted array, pair sum, palindrome

```python
def two_sum_sorted(nums, target):  # O(n), O(1)
    l, r = 0, len(nums) - 1
    while l < r:
        s = nums[l] + nums[r]
        if s == target:
            return [l, r]
        l, r = (l + 1, r) if s < target else (l, r - 1)
    return []
```

```js
function twoSumSorted(nums, target) { // O(n)
  let l = 0, r = nums.length - 1;
  while (l < r) {
    const s = nums[l] + nums[r];
    if (s === target) return [l, r];
    else if (s < target) l++; else r--;
  }
  return [];
}
```

### 3.2 Sliding window — subarray/substring, at most K, longest contiguous

```python
def longest_ones(nums, k):  # O(n), O(1)
    left = zeros = best = 0
    for right, v in enumerate(nums):
        zeros += (v == 0)
        while zeros > k:                 # shrink until valid
            zeros -= (nums[left] == 0)
            left += 1
        best = max(best, right - left + 1)
    return best
```

```js
function minLenWithKDistinct(s, k) { // O(n) shrink-when-valid template
  const win = new Map();
  let left = 0, best = Infinity, distinct = 0;
  for (let r = 0; r < s.length; r++) {
    if (!win.get(s[r])) distinct++;
    win.set(s[r], (win.get(s[r]) || 0) + 1);
    while (distinct === k) {           // shrink until invalid
      best = Math.min(best, r - left + 1);
      win.set(s[left], win.get(s[left]) - 1);
      if (!win.get(s[left++])) distinct--;
    }
  }
  return best === Infinity ? 0 : best;
}
```

### 3.3 Binary search — sorted/rotated, answer-space (capacity, days)

```python
def search_rotated(nums, target):  # O(log n)
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:           # left sorted
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        elif nums[mid] < target <= nums[hi]:  # right sorted
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
# Answer-space search: same loop over feasible(x), return smallest True.
```

### 3.4 DFS / BFS — islands, levels, shortest unweighted path

```python
from collections import deque
def num_islands(grid):  # O(R*C)
    R, C = len(grid), len(grid[0])
    def dfs(r, c):
        if not (0 <= r < R and 0 <= c < C) or grid[r][c] != "1":
            return
        grid[r][c] = "0"
        dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1)
    return sum(grid[r][c] == "1" and not dfs(r, c) for r in range(R) for c in range(C))

def bfs_shortest(adj, start, goal):  # O(V+E)
    q = deque([(start, 0)]); seen = {start}
    while q:
        node, d = q.popleft()
        if node == goal:
            return d
        for nb in adj[node]:
            if nb not in seen:
                seen.add(nb); q.append((nb, d + 1))
    return -1
```

### 3.5 Backtracking — permutations, subsets, N-queens

```python
def subsets(nums):  # O(n * 2^n)
    out = []
    def backtrack(i, path):
        out.append(list(path))
        for j in range(i, len(nums)):
            path.append(nums[j])    # choose
            backtrack(j + 1, path)  # explore
            path.pop()              # unchoose
    backtrack(0, [])
    return out
```
# Prune before recursing; sort + skip duplicates for dedupe; depth >1000 → explicit stack.

### 3.6 Heap top-k — k largest, merge k lists, streaming median

```python
import heapq
from collections import Counter
def top_k_frequent(nums, k):  # O(n log k)
    return [x for x, _ in heapq.nlargest(k, Counter(nums).items(), key=lambda kv: kv[1])]

def merge_k_sorted(lists):  # O(N log k)
    h = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(h); out = []
    while h:
        v, i, j = heapq.heappop(h)
        out.append(v)
        if j + 1 < len(lists[i]):
            heapq.heappush(h, (lists[i][j+1], i, j+1))
    return out
```

JS has no builtin heap — sort is O(n log n) vs heap O(n log k); know the tradeoff.

### 3.7 Prefix sum — subarray sum = K, range queries

```python
def subarray_sum_k(nums, k):  # O(n), O(n)
    pref = {0: 1}; run = ans = 0
    for x in nums:
        run += x
        ans += pref.get(run - k, 0)
        pref[run] = pref.get(run, 0) + 1
    return ans
```

```js
function subarraySum(nums, k) { // O(n)
  const pref = new Map([[0, 1]]);
  let run = 0, ans = 0;
  for (const x of nums) {
    run += x;
    ans += pref.get(run - k) || 0;
    pref.set(run, (pref.get(run) || 0) + 1);
  }
  return ans;
}
```

## 4. Complexity Sizing — Worked Call

"n up to 1e5, pair sums to T": O(n²) = 1e10 ops (~100 s, fails); sort + two pointers O(n log n) ≈ 1.7e6 ops (instant). Comment `# Time O(n log n) — sort dominates`; measure with `timeit`/`cProfile`, never guess. Recursion: test base alone; depth >1000 → explicit stack.

## 5. Debug System — Repro + Hypotheses + Bisect

1. **Minimal repro:** shrink input to smallest still-failing case; save `repro_test.py` (fails now, passes after fix).
2. **Hypothesis table (≤3 rounds):**

| # | Hypothesis | Test | Result → Next |
|---|---|---|---|
| 1 | off-by-one in shrink | log `left/right` on `[1,1,1],k=2` | jumps 2 → fix bound |
| 2 | JS lexicographic sort / stale state | check `[10,9]` order; call twice same input | wrong/differs → comparator / remove mutation |

3. **Bisect regression:** `git bisect start; git bisect bad HEAD; git bisect good <sha>; git bisect run pytest repro_test.py`. Log with request IDs (`req=%s`) so interleaved cases stay separable. No fix without a failing test; after fix, repro + suite green.

## 6. Labs — 30-Problem Plan with Acceptance

O() comment on every solution; each must pass empty/single/duplicates/sorted+reverse edges. Pace 2/day × 15 days; state pattern aloud in 2 min before coding and log wrong calls.

- **Arrays/Strings (10):** two-sum sorted, longest substring w/o repeat, min window, rotated search, subarray = k, product except self, 3sum, container water, trapped rain (stretch), compression.
- **Hash/Stack/Heap (10):** group anagrams, top-k frequent, min-stack, daily temperatures (monotonic), LRU cache, merge k lists, stream median (2 heaps), task scheduler, first missing positive, sliding-window max.
- **DFS/BFS/Backtrack (10):** islands, clone graph, course schedule, word ladder, subsets, permutations II, combination sum, N-queens count, word search, Pacific-Atlantic.

## 7. Troubleshooting Table

| Symptom | Likely cause | Fix |
|---|---|---|
| TLE at n=1e5 | Hidden O(n²) (`in` on list in loop) | Inner scan → set/dict; re-derive O() |
| JS `[10,2]` order | Lexicographic default sort | `.sort((a,b)=>a-b)` for numbers |
| BFS slow/memory blow | `shift()` O(n) or revisits | Index-pointer queue + `seen` at enqueue |
| `RecursionError` | Depth >1000 / no base | Test base alone; explicit stack |
| Binary search hangs | `lo=mid` not `mid+1` | Use answer-space template verbatim |
| Flaky pass/fail | Set order / global mutation | Sort output; copy inputs |

## 8. Mini-Project — Request Log Analyzer

CLI over `requests.csv` (`req_id,timestamp_ms,endpoint,status`): p50/p95 per endpoint, top-5 endpoints (heap), flag any 60 s window >1000 reqs (sliding window). Acceptance: 1M rows <10 s (`time`), O() per function, `repro_test.py` with 3 cases, request-ID error logging.

## 9. Graduation Checklist
- [ ] 1-of-7 pattern call in <2 min, aloud, per problem.
- [ ] Correct Time/Space O() on 30 solutions; rejects O(n²) at n=1e5 pre-code.
- [ ] Failing→passing repro for 3 bugs; `git bisect run` finds regression; hypotheses converge ≤3 rows; log-analyzer hits budget; fluent `Counter/heapq/bisect/deque` + JS `Map/Set`/numeric sort.

## 10. Anti-Patterns
- Memorizing solutions (can't name pattern in 2 min = not learned); ignoring constraints; optimizing before correct.
- Recursion without base/depth check; `in`-list in loop, JS `shift()` in BFS, default `.sort()` on numbers.
- Fixing without failing repro; bulk edits per experiment.

## 11. Next
Graduate to `problem-solving-advanced`: DP with recurrence proofs, union-find / segment tree / Dijkstra-A* / topo / KMP, profile→algorithm→layout→parallelize with p50/p95/p99, sanitizers + idempotency, blameless postmortems + ADR cost math.
