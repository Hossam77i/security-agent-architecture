---
name: solve-review-cycle
description: Mandatory after every training lab or hunting session AND whenever stuck. Two protocols: (1) PEER-COMPARE — search community solutions, analyze, plan, compare against your own, list mistakes honestly, enhance and re-verify; (2) STUCK — when grinding without progress, STOP, deep-search, analyze, plan, resolve again. Trigger on "compare solutions", "what did I miss", "I'm stuck", "review my work", end of any lab/hunt, or 3 failed approaches on one problem.
version: 1.0.0
revision_date: 2026-09-14
license: MIT
category: redteam
tags: [review, peer-compare, stuck-protocol, training, hunting, methodology]
---

# Solve–Review Cycle: Compare + STUCK Protocols

Two mandatory loops. Run PEER-COMPARE at the end of **every** training lab and hunting session. Run STUCK **during** work the moment grinding replaces thinking.

---

## Protocol 1: PEER-COMPARE (end of session, always)

**Purpose:** other hunters see what you don't. Community writeups convert your blind spots into checklist items and your untested surface into findings.

### Steps

1. **SEARCH** — query community solutions for the exact target/class:
   - `<target> writeup walkthrough <vuln>` (blogs, GitHub, PortSwigger, CTF writeups)
   - `<target> secret/hidden challenges solution`
   - Official solution docs in-repo (`challengeSolutions.md`, `docs/`) — read to the last line
   - Minimum 2 queries, 2 sources each. Record URLs.
2. **ANALYZE** — for each community vector, extract: endpoint, method, payload shape, prerequisite, impact claim.
3. **PLAN** — build a table with three columns: `community-only` | `both` | `mine-only`.
4. **COMPARE live** — reproduce every `community-only` vector against the lab **yourself**:
   - If it works and you missed it → genuine miss. Chain it further if possible.
   - If it fails → verify why (version diff? patched? wrong precondition?). A refuted vector is still a logged learning (negative control).
   - If it works but yours is stronger → keep yours, note the alternative as alt-way.
5. **MISTAKES (write them down, honestly)** — mandatory section, no softening:
   - Process mistakes (stale envs, self-killing commands, shell quoting, unverified assumptions)
   - Attribution mistakes (claimed mechanism X, evidence actually shows Y — re-test per-service/per-endpoint)
   - Coverage mistakes (name every untested endpoint/flow explicitly — that list opens the next session)
6. **ENHANCE** — for each closed gap: exploit it, escalate it (chain/blind-exfil/boundary), log it with evidence, update the scoreboard. Re-run snapshot/verification.

### Worked example (crAPI, 2026-09-14, 18 challenges)

| Community-only (verified live) | Both (independently found) | Mine-only |
|---|---|---|
| Vendor `POST /products` negative price → chained +$500 | BOLA×2, OTP brute-force, users-all, video internals, neg-qty, BFLA delete, SSRF, NoSQL `$ne`, SQLi re-redeem, unauth endpoint, JWT 4-ways, echo injection, shell chain | Blind `$regex` exfil, amount-lie $1M, no-QR returns, per-service JWT differential, verify-topology, PUT-matrix, RCE-as-root + revert, DoS timing + 101 cap, v3 control |
| Signup role-field test → **negative** (hardcoded `ROLE_USER`, line-verified — still worth logging) | | |

Mistakes logged that day: stale-container saga (fix: boot-marker check + `--force-recreate`), `pkill -f` self-kill ×2 (fix: kill by PID), zsh glob on `===`/URLs (fix: quote), HS256 misattribution (fix: per-service differential before theorizing), late STUCK trigger on chatbot, untested surface named (change-phone OTP, posts/comments, pictures, secrets, `video_name`).

---

## Protocol 2: STUCK (mandatory circuit-breaker, during work)

**Trigger — ANY of these, no exceptions:**
- 3 failed approaches on one problem, **or**
- 45 minutes on one parameter/endpoint with no new signal, **or**
- Catching yourself re-running a failed command with tiny tweaks, **or**
- Blaming the target ("must be patched") without evidence.

**The cycle — STOP means stop (hands off keyboard for the current path):**

1. **S — STOP.** Freeze the current approach. Write one line: what you tried 3× and what each attempt returned (exact status/body, not vibes).
2. **T — TRIAGE the evidence.** Re-read the last errors literally. Check the boring causes first, in order:
   - Stale environment (container/process restarted? patch loaded? boot markers fresh?)
   - Self-inflicted (killed own shell? quoting/glob? wrong file? wrong port/service?)
   - Wrong layer (gateway vs direct? which microservice actually answered? diff the responders)
3. **U — UNDERSTAND one level deeper.** Read the source/config of the exact failing hop (not docs, not memory). One function, one route, one filter.
4. **C — CONSULT (deep search).** Two targeted searches: `<exact error/behavior> <tech>` and `<target> <vuln> writeup`. Someone has met this wall.
5. **K — KILL or re-PLAN.** Either kill the path with a logged reason (negative result, unblock later) or write a NEW plan with a different mechanism — never a 4th tweak of the same mechanism. Then resolve again.

**Anti-patterns that trigger an immediate STOP:** re-firing the same request hoping, enlarging the rabbit hole (new tools before new understanding), framework debugging past 20 minutes without a logged hypothesis, theorizing without a per-service/per-endpoint differential test.

---

## Integration rules (every training / hunt)

- PEER-COMPARE runs before the session is declared done. Scoreboard is not final until community vectors are dispositioned (reproduced / refuted / stronger-alt).
- STUCK runs mid-session on trigger. Log each STUCK invocation as an experiment entry (`way: STUCK-<n>`) with what it changed.
- Both protocols write to the session log: comparison table + mistakes list + enhancements with evidence. verbal summaries don't count.
- Carry-forward: every session ends with an explicit `untested surface` list. Next session starts there.

## Related skills

- `bb-methodology` — the 5-phase hunt loop these protocols bolt onto (PEER-COMPARE ≈ Phase 5 extension, STUCK ≈ navigation guard).
- `triage-validation` — 7-Question Gate for findings surfaced by comparison.
- `report-writing` — enhanced findings still go through platform reporting shape.
