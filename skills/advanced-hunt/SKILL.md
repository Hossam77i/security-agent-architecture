---
name: advanced-hunt
description: Advanced bug-hunting methodology — auth-matrix differentials, JS/APK-driven API discovery, OOB discipline, primitive chaining, and YWH-grade reporting. Load when core vulnerability classes are exhausted and you must manufacture findings from architecture, not scanners.
version: 1.0.0
revision_date: 2026-09-09
license: MIT
category: redteam
tags: [methodology, advanced, chaining, differential, bounty]
---

## When to Use

- Core classes (IDOR, XSS, redirect, SSRF) all closed with no finding.
- You have two test accounts + sessions and need to squeeze the last findings out.
- Before touching a new product surface: run the mapping phases first.

## Phase 1 — Auth Matrix (the differential engine)

Every endpoint gets a 4-cell matrix. A finding exists ONLY where cells differ unexpectedly:

|  | No auth | User A | User B |
|---|---|---|---|
| Own object | — | 200 (baseline) | 200 (baseline) |
| Other's object | expect 401/302/404 | expect 403/404 | expect 403/404 |

Rules:
- Own-200 vs cross-403/404 with identical shape = closed. Move on after ONE clean differential per endpoint family — never re-prove the same middleware.
- `200-but-empty` vs `200-with-data` across users = investigate (silent authz failure).
- Validation-before-authz (422 pre-auth) is normal; only a 200 with чужі data counts.
- Record the exact error codes per family (`not_authorized` vs `access_denied` vs `object_not_found`) — code changes between own/cross are oracles.

## Phase 2 — API Discovery (never guess)

1. **JS bundles + source maps** before any fuzzing. `.js.map` files are full source: routes, API shapes, validation logic, env keys.
2. **APK strings** for mobile-backed APIs: endpoint paths, custom headers (`account-id`), OAuth shapes, deeplink hosts.
3. **Docs indexes** (developer portals often embed full endpoint JSON): extract the complete method+path inventory offline.
4. **Live XHR capture** in an authenticated browser to learn the real call shapes (query params, `with=` expansions, version prefixes like `/v3/api/3/`).
5. Only then: targeted probes. Blind fuzzing is banned — every request must test a named hypothesis.

## Phase 3 — Auth Shape Recovery

When an API rejects your session cookie:
1. Read the error progression: `401 (header)` → `401 (missing X)` → `403/404` tells you each passed control.
2. Recover custom headers/tokens from the client that owns the flow (APK smali: search `const-string` near `header(`, or log via repackaged debuggable build).
3. Recover CSRF models: encrypted-cookie-echo (send cookie value back as header), per-response rotation (always use the latest pair).
4. Mobile-class tokens come from heap dumps (`am dumpheap` on debuggable builds) or AccountManager-adjacent storage — never from guessing.

## Phase 4 — OOB Discipline

- Every blind claim (SSRF fetch, reset-link host, redirect target) needs a Collaborator payload generated BEFORE the probe, and a poll AFTER.
- Server-side fetch with attacker-controlled URL + empty follow-through (no metadata, no redirect-chain abuse) = pingback-only = do not report. Know your program's line before testing.
- Clean up every OOB artifact you create (posts, pastes, teams, links). Verify deletion.

## Phase 5 — Primitive Chaining

Single primitives rarely pay on mature targets. Chain table:

| Have | Need | Yields |
|---|---|---|
| Read-IDOR on profile | Email-change without re-auth | ATO |
| Open redirect | OAuth `redirect_uri` acceptance | Code theft → ATO |
| Server-side fetch | IMDS/internal reach or redirect-follow | SSRF |
| Mass-assignment field | Privileged attribute (`role`, `account_id`) honored | Priv-esc |
| Write API on own objects | Cross-account ID acceptance | BOLA-write |
| Mobile token | Wrong-scope acceptance on another backend | Cross-product authz |

If a primitive composes with nothing, log it as intel, not a finding.

## Phase 6 — YWH-Grade Reporting Bar

- Discovery methodology is mandatory: how you found the endpoint (bundle, APK, docs, fuzz) — reports without it are delayed.
- Gate 0: attacker action NOW + victim loss (CIA) + 10-minute repro from scratch. Fail any → kill the finding.
- PII in evidence must be redacted; test accounts only; no чужі data ever opened beyond the minimum differential.
- One-Fix-One-Reward: same codebase + single fix = one report. Group, don't spray.

## Stop Rules

- 10 consecutive negatives → mandatory backlog re-rank (see bounty-roi-2026).
- No guessing чужі UUIDs/tokens/links — excluded class AND ethical line.
- Validation errors are not vulnerabilities. 422s map schemas; only completed cross-account state changes count.
