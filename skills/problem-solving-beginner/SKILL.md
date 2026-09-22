---
name: problem-solving-beginner
description: Use when breaking down coding problems, pseudocode, rubber-ducking, first debugging. Triggers on how to solve, stuck on problem, pseudocode help, break down task, beginner algorithm.
---

# Problem Solving Beginner

## 0. Objective

Turn any vague coding task into executable steps you finish in one sitting. Rule: never jump straight to code — restate the problem, plan in plain English, build the smallest slice first, and reproduce every bug before changing anything.

Done when you can: write pseudocode before code for any easy problem, test 3 cases per function (normal/edge/empty), explain your solution aloud in 1 minute, and fix bugs one change at a time.

## 1. Mental Model — UPR: Understand, Plan, Run

Most beginner bugs come from skipping step 1. Loop until checks pass:

```
Understand (5 min) → Plan (5 min) → Run (15 min slice) → Check → repeat
       ↑                                                      |
       └──────────── if check fails, go back one step ────────┘
```

- **Understand:** What goes in? What comes out? What are 3 concrete examples?
- **Plan:** What are the ≤5 steps in plain English? Simplest container (list? dict?)?
- **Run:** Smallest slice I can code + test in 15 minutes? One function = one job.
- 25-minute timebox per attempt — when it rings, explain aloud (rubber-duck) before continuing.

## 2. Understand — Restate I/O + 3 Examples

Write this comment block before touching logic:

```
PROBLEM (own words):
INPUT:  type + range (e.g. list[int], 0..1000, may be empty?)
OUTPUT: type + format (e.g. int, or None if missing)
EXAMPLES: 1. normal  2. edge (first/last, duplicates, single)  3. empty/weird
FIXED vs VARIABLE: ...
```

**Worked example — "find max":**

```
PROBLEM: return the largest number in a list.
INPUT:  list[int], length 0..10000, may contain negatives.
OUTPUT: int (the max), or None if empty — decide UP FRONT, don't crash.
EXAMPLES: [3,1,4,1,5]->5 | [-9,-3,-20]->-3 | []->None
FIXED: must scan every element once. VARIABLE: None vs raise on empty.
```

Always ask: empty/None input? duplicates? order matters? limits? exact output format?

## 3. Plan — Pseudocode Chunks

Plain English, no syntax, ≤5 steps, each testable. List for order, dict/set for lookup, counter for running answers. If a step needs three "and then"s, split it and name each chunk a helper.

**Count vowels:**

```
1. SET count = 0, DEFINE vowels = {a,e,i,o,u}
2. FOR each ch in text (lowercased): IF ch in vowels: count += 1
3. RETURN count
```

**Validate parentheses:**

```
1. MAP closing->opening: {')':'(', ']':'[', '}':'{'}; CREATE empty stack
2. FOR each c: IF opening: PUSH; ELSE: IF stack empty or POP != expected -> False
3. RETURN True if stack empty else False
```

## 4. Run — Smallest-Slice Coding

Code slice 1, test it, then slice 2. Never write 50 lines then run.

**Python — find max, slice by slice:**

```python
def find_max(nums):
    """Return max of nums, or None if empty."""
    if not nums:          # slice 1: guard — test with []
        return None
    best = nums[0]        # slice 2: init — test with [7]
    for x in nums[1:]:    # slice 3: scan — test with [3,1,4,1,5]
        if x > best:
            best = x
    return best

assert find_max([]) is None
assert find_max([7]) == 7
assert find_max([3, 1, 4, 1, 5]) == 5
assert find_max([-9, -3, -20]) == -3
```

**JS — same problem:**

```js
function findMax(nums) {
  if (!nums || nums.length === 0) return null;
  let best = nums[0];
  for (let i = 1; i < nums.length; i++) {
    if (nums[i] > best) best = nums[i];
  }
  return best;
}
console.assert(findMax([]) === null);
console.assert(findMax([7]) === 7);
console.assert(findMax([3, 1, 4, 1, 5]) === 5);
```

**Python — reverse without reverse():**

```python
def reverse_list(items):
    out = []
    for i in range(len(items) - 1, -1, -1):
        out.append(items[i])
    return out

assert reverse_list([]) == []
assert reverse_list([1, 2, 3]) == [3, 2, 1]
```

**JS — count vowels:**

```js
function countVowels(text) {
  const vowels = new Set(['a', 'e', 'i', 'o', 'u']);
  let count = 0;
  for (const ch of (text || '').toLowerCase()) {
    if (vowels.has(ch)) count++;
  }
  return count;
}
console.assert(countVowels('hello') === 2);
console.assert(countVowels('') === 0);
console.assert(countVowels('AEIOUxyz') === 5);
```

## 5. Debugging Starter — Reproduce 3x, One Change at a Time

1. **Reproduce 3x.** Same failing case three times. Note exact error + line + input.
2. **Print inputs at entry:** `print(f"ENTER f: x={x!r}")` / `console.log('ENTER f:', x)`. Most beginner bugs are wrong input, not wrong logic.
3. **Check the big 5:** typo? off-by-one (`<` vs `<=`)? wrong type (str vs int)? empty input? missing `return`?
4. **One change at a time.** `cp app.py app.bak.py`, edit once, re-run 3 cases. Worse → revert.
5. **25m timebox.** Still stuck → explain line-by-line aloud, then ask for help with UPR notes + error text.

**Example bugs:**

```python
def count_vowels_buggy(text):
    count = 0
    for ch in text.lower():
        if ch in "aeiou":
            count += 1
    # forgot return! -> returns None
```

```js
function lastChar(s) { return s[s.length]; }        // wrong: out of bounds
function lastCharFixed(s) { return s[s.length - 1]; } // right
```

## 6. Labs — 4 Guided Problems with Solutions

For each: UPR block → pseudocode → code → 3 asserts. Acceptance: asserts pass + explain without looking.

**Lab 1 — Reverse list.** Acceptance: `[]`, `[1]`, `[1,2,3]`. Solution in Section 4.
**Lab 2 — Count vowels.** Acceptance: `'hello'->2`, `''->0`, `'AEIOUxyz'->5`. Solution in Section 4.
**Lab 3 — Find max.** Acceptance: `[]->None`, `[7]->7`, negatives work. Solution in Section 4.

**Lab 4 — Validate parentheses with stack:**

```python
def valid_parens(s):
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for c in s:
        if c in '([{':
            stack.append(c)
        elif c in pairs:
            if not stack or stack.pop() != pairs[c]:
                return False
    return not stack

assert valid_parens("()[]{}") is True
assert valid_parens("(]") is False
assert valid_parens("") is True
assert valid_parens("([)]") is False
assert valid_parens("{[]}") is True
```

```js
function validParens(s) {
  const pairs = { ')': '(', ']': '[', '}': '{' };
  const stack = [];
  for (const c of s) {
    if ('([{'.includes(c)) stack.push(c);
    else if (c in pairs && stack.pop() !== pairs[c]) return false;
  }
  return stack.length === 0;
}
```

## 7. Troubleshooting Table

| Symptom | Likely cause | Fix (one change) |
|---|---|---|
| `IndexError` / `undefined` at loop end | Off-by-one (`<=` vs `<`, `s[len]`) | Print `i` and `len`; shift bound by 1 |
| `TypeError` / `NaN` | Wrong type (str vs int) | Print `type(x)`; convert at entry |
| `None` / `undefined` returned | Missing `return` | Add `return`; trace every branch |
| Crashes only on `[]` | No empty guard | Add `if not nums: return <default>` first |
| `KeyError` / missing property | Dict key absent | Use `d.get(k)` / `?? default`; print keys |
| Infinite loop | Loop var never changes | Print var each iter; check exit reachable |
| Passes once, fails next run | Mutated input / stale state | Copy input (`list(x)` / `[...x]`); re-run 3x |

## 8. Mini-Project — Word Counter CLI

Build `wordcount.py` (or `.js`): read a text file, print total lines, total words, top-3 frequent words. Acceptance: `empty.txt` → zeros, no crash; `sample.txt` matches hand count; helpers `count_words(text)` + `top_n(freq, n)` each with 3 asserts; UPR block at top of file.

Pseudocode: READ file (friendly msg if missing) → SPLIT lowercase words → COUNT via dict → PRINT lines/words/top-3.

## 9. Graduation Checklist

- [ ] UPR block (I/O + 3 examples) before code, every time.
- [ ] Pseudocode in ≤5 chunks before coding.
- [ ] Smallest slice first; test after each slice; `.bak` of last working copy.
- [ ] Every bug reproduced 3x with exact error + line noted.
- [ ] One change at a time; revert when worse.
- [ ] All 4 labs pass + mini-project handles empty file.
- [ ] Explains any solution aloud in under 1 minute; honors 25m timebox.

## 10. Anti-Patterns

- Coding before understanding; 50+ lines before first run; 3 edits at once.
- Jumping to advanced DP/recursion when loop + dict works.
- Copying solutions without trace-through; testing happy path only.
- Debugging by staring instead of printing inputs at entry.

## 11. Next

Graduate to `problem-solving-intermediate`: the 7 patterns (two-pointers, sliding window, binary search, DFS/BFS, backtracking, heap top-k, prefix sum), Big-O sizing rules, and hypothesis tables + `git bisect`.
