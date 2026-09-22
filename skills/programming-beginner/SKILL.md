---
name: programming-beginner
description: Use when learning to code in Python and JavaScript, variables, loops, functions, debugging. Triggers on learn python, learn javascript, first function, for loop help, syntax error, how to debug.
---

# Programming Beginner (Python + JS)

## 0. Objective

Write small correct scripts in Python 3.11+ and Node 20 JS that run first try, handle bad input with a message, and are debuggable by someone else. Master: venv/node setup, variables/types, control flow, functions, collections, f-strings/template literals, file/JSON I/O, try/except, pdb/inspect debugging. Exit: 5 katas passing + 1 JSON-backed todo CLI + clean `ruff`/`eslint`. Non-goals: OOP, async, frameworks, DBs (see programming-intermediate).

## 1. Mental model

Think like the interpreter: **program = input -> transform -> output**. Every script reads (args, file, API), transforms (loop/function), writes (print, file). Know the type on every line: Python is strongly typed (`"5" + 5` fails); JS coerces (`"5" + 5 === "55"`). Trace execution line by line — play computer for 3 loop iterations on paper. Read errors bottom-up: last line = what failed, lines above = call chain. One function = one job (`verb_noun`, <20 lines); if you cannot name it in 3 words, split it.
Map: `list <-> Array`, `dict <-> Object`, `f"{}" <-> `${}``, `try/except <-> try/catch`, `None <-> null/undefined`, `venv+pip <-> node+npm`.

## 2. Setup: venv + Node (do first)

Python 3.11+, Node 20+, VS Code + Ruff + ESLint. Plain JS with ESM for now (`"type": "module"`).

```bash
python3 --version # >=3.11
python3 -m venv .venv && source .venv/bin/activate
pip install ruff requests pytest && python3 app.py
node --version # v20.x
npm init -y && npm pkg set type=module && npm i -D eslint && node app.js
```

```json
{ "type": "module", "scripts": { "start": "node app.js", "lint": "eslint ." } }
```

Rule: one project = one `.venv` + one `package.json`. Never `pip install` globally. Commit `requirements.txt`/`package.json`; never commit `.venv/` or `node_modules/`.

## 3. Variables, types, control flow, functions

Prefer `const` in JS; type-hint everything in Python. Python falsy: `[] {} "" 0 None`. JS falsy: `0 "" null undefined NaN false` — but `[]` and `{}` are TRUTHY (classic trap). Python `and/or/not` vs JS `&&/||/!`.

```python
name: str = "ada"; age: int = 36; ratio: float = 3.14; active: bool = True
def grade(score: int) -> str:
    """Return A/B/C/invalid for 0-100 score."""
    if not 0 <= score <= 100: return "invalid"
    if score >= 90: return "A"
    if score >= 70: return "B"
    return "C"
for i in range(3): print(f"try {i}: {grade(85)}")
n = 0
while n < 3: n += 1
print("done", n)
def add(a: int, b: int) -> int:
    """Return sum; raise TypeError on bad type."""
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError(f"expected ints, got {type(a)} {type(b)}")
    return a + b
if __name__ == "__main__": print(add(2, 3))
```

```js
const name = "ada"; let age = 36; const ratio = 3.14; const active = true;
export function grade(score) {
  if (!Number.isInteger(score) || score < 0 || score > 100) return "invalid";
  if (score >= 90) return "A";
  if (score >= 70) return "B";
  return "C";
}
for (let i = 0; i < 3; i++) console.log(`try ${i}: ${grade(85)}`);
let n = 0; while (n < 3) n++;
console.log("done", n);
/** Return sum of two numbers. @throws {TypeError} */
export function add(a, b) {
  if (typeof a !== "number" || typeof b !== "number")
    throw new TypeError(`expected numbers, got ${typeof a} ${typeof b}`);
  return a + b;
}
```

Rules: docstring/JSDoc on every function, early-return on invalid input, no `print` inside logic (return values; let `main` print).

## 4. Collections + strings

`map/filter` for transforms, `for` for side effects. Python `dict.get(k, dflt)` = JS `obj.k ?? dflt`. Never `+`-concat in a loop — Python `"".join(parts)`, JS `parts.join("")`.

```python
nums = [1, 2, 3, 4, 5]
squares = [x * x for x in nums if x % 2 == 1]  # [1, 9, 25]
user = {"name": "ada", "tags": ["admin", "dev"]}
print(user.get("missing", "default"), nums[:2])
for k, v in user.items(): print(f"{k}={v}")
name, score = "ada", 95
print(f"{name} scored {score}/100 ({score/100:.0%})")
print(f"{'name':<10} | {'score':>5}")
```

```js
const nums = [1, 2, 3, 4, 5];
const squares = nums.filter((x) => x % 2 === 1).map((x) => x * x);
const user = { name: "ada", tags: ["admin", "dev"] };
console.log(user.missing ?? "default", nums.slice(0, 2));
for (const [k, v] of Object.entries(user)) console.log(`${k}=${v}`);
const name = "ada", score = 95;
console.log(`${name} scored ${score}/100 (${score}%)`);
console.log(`${"name".padEnd(10)} | ${"score".padStart(5)}`);
```

## 5. File/JSON I/O + errors

Always `pathlib.Path` / `node:path`, always `encoding="utf-8"`, `indent=2` for human-edited JSON. Catch narrow, add context, never bare `except: pass`.

```python
import json
from pathlib import Path
def load_users(path: str) -> list[dict]:
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
def save_users(path: str, users: list[dict]) -> None:
    Path(path).write_text(json.dumps(users, indent=2), encoding="utf-8")
def parse_age(raw: str) -> int:
    try: age = int(raw.strip())
    except (ValueError, AttributeError) as e:
        raise ValueError(f"bad age {raw!r}: digits only") from e
    if not 0 <= age <= 130: raise ValueError(f"age {age} out of range")
    return age
```

```js
import { readFile, writeFile } from "node:fs/promises";
export async function loadUsers(path) {
  try { return JSON.parse(await readFile(path, "utf-8")); }
  catch (e) { if (e.code === "ENOENT") return []; throw e; }
}
export async function saveUsers(path, users) {
  await writeFile(path, JSON.stringify(users, null, 2), "utf-8");
}
export function parseAge(raw) {
  const age = Number(String(raw).trim());
  if (!Number.isInteger(age)) throw new Error(`bad age ${JSON.stringify(raw)}`);
  if (age < 0 || age > 130) throw new Error(`age ${age} out of range`);
  return age;
}
```

## 6. Debugging + 5 katas

Process: read traceback bottom-up, reproduce with smallest input, add labelled prints, rubber-duck input->expected->actual, fix one thing, rerun.

```python
print(f"[debug] nums={nums!r}")
import pdb; pdb.set_trace()  # n=next, c=continue, p <var>; or python3 -m pdb app.py
def fizzbuzz(n: int) -> list[str]:
    return [(("Fizz" * (i % 3 == 0) + "Buzz" * (i % 5 == 0)) or str(i)) for i in range(1, n + 1)]
def reverse(s: str) -> str: return s[::-1]
def word_count(path: str) -> dict[str, int]:
    from collections import Counter
    text = open(path, encoding="utf-8").read().lower()
    return dict(Counter("".join(c if c.isalnum() else " " for c in text).split()))
```

```js
console.log("[debug] nums=", nums); console.table(users);
// node --inspect app.js -> chrome://inspect; or VS Code F5 auto-attach
const res = await fetch("https://api.github.com/zen", { signal: AbortSignal.timeout(5000) });
if (!res.ok) throw new Error(`HTTP ${res.status}`);
console.log(await res.text());
```

Katas: FizzBuzz, reverse-string, word-count-in-file, fetch-JSON-API, todo-CLI-storing-JSON. Do all five before intermediate.

## Labs 1-3

**Lab 1 — Word counter.** Read `.txt`, print top-10 words with counts. Missing file -> `File not found: <path>`, exit 1.
Acceptance: empty file prints nothing, exit 0; `ruff check` clean.
**Lab 2 — JSON todo CLI.** `add "buy milk"`, `list`, `done 1` persisted to `todo.json`. Bad index prints error, never crashes.
Acceptance: round-trip survives restart; malformed JSON resets with warning, not traceback.
**Lab 3 — Fetch and save.** Fetch public JSON API (5s timeout), save pretty JSON, print record count. No-network -> friendly message.
Acceptance: timeout path verified offline; output is valid JSON.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: requests` | venv inactive / wrong interpreter | `source .venv/bin/activate && pip install requests`; fix VS Code interpreter |
| `SyntaxError` on f-string | Python <3.8 or quote mismatch | `python3 --version`; match quotes, upgrade to 3.11+ |
| `undefined is not a function` | typo / `[]`-truthy assumption | `console.log(typeof x)`; ESM imports need `.js` suffix |
| `ENOENT: no such file` | CWD vs script dir mismatch | Python `Path(__file__).parent / f`; JS `path.join(process.cwd(), f)` |
| `JSON parse error` | empty file / trailing comma | Guard empty -> `[]`; write only via `JSON.stringify`/`json.dumps` |
| Infinite `while` | counter never updated | Increment first; add max-iteration guard while debugging |
| `Cannot use import outside module` | missing ESM flag | `npm pkg set type=module`; use `import`, not `require` |

## Mini-project + graduation

**Finance tracker CLI:** `add 12.50 groceries`, monthly totals, `expenses.json`. Validate positive amount, non-empty category. Ship `README.md` (run commands for Py + JS), `requirements.txt`/`package.json`, 3 sample commands with expected output.
- [ ] `python3 finance.py ...` and `node finance.js ...` run clean
- [ ] Bad input -> actionable message, exit != 0, no raw traceback
- [ ] `ruff check .` and `npx eslint .` pass
- [ ] Functions <20 lines, docstring/JSDoc each; README runs in <2 min
- [ ] Can explain every line without notes (no blind copy-paste)

## Anti-patterns + Next

Global mutable state; 200-line `main` (split `parse/format/save`); `eval`/`exec` on input; hardcoded `/home/you/...` paths (use args + `Path`); bare `except: pass`; permanent `console.log` error handling; SO copy-paste untested.
Next: `programming-intermediate` — OOP/composition, FastAPI/Express REST, asyncio, pytest/jest, Postgres.
