---
name: bounty-roi-2026
description: Pre-hunt ROI discipline for bug bounty in 2026 — why hunters find nothing, the mistakes that burn engagements, and the rules that convert effort into paid findings. Load BEFORE starting any new program, and again whenever 10+ leads close with zero findings.
version: 1.0.0
revision_date: 2026-09-09
license: MIT
category: redteam
tags: [methodology, roi, bounty, triage]
---

## When to Use

- Before touching a new program: run the ROI checklist to decide if the program deserves your time.
- After ~10 closed leads with zero findings: stop, load this skill, re-rank the backlog instead of grinding.
- When choosing between two leads: score both with the matrix below.

## Why Hunters Find Nothing (2026)

1. **Mature targets with free-tier accounts.** The easy IDOR/BOLA on core products was burned years ago. What remains sits behind products, payment, SMS identity, or victim interaction — all things a free account cannot reach.
2. **Testing the program's strengths.** Every hour spent re-proving session-scoping on a hardened API is an hour not spent where the program is weak (new features, acquired products, mobile-only flows, staging).
3. **Confusing activity with progress.** 30 closed leads feels productive; the payout function only counts reportable findings. Optimize for findings-per-hour, not requests-per-hour.
4. **Ignoring the scope's exclusion list.** Each non-qualifying class you "confirm" costs time and pays zero by definition. Read exclusions first, route around them.
5. **No product ownership.** Most High/Critical impact (money movement, PII stores, admin functions) lives in paid products. Free-tier hunting caps out at Low/Medium by construction.

## The ROI Matrix (score every lead before testing)

| Factor | +2 | 0 | −2 |
|---|---|---|---|
| Access needed | Have it now | Need a free action (SMS, trial) | Needs money/victim/product |
| Exclusion risk | Clearly qualifying class | Gray area | Listed non-qualifying |
| Freshness | New feature, beta, acquired product, recent CVE family | Stable, old code | Core auth hardened for years |
| Proof cost | Read-only GETs | Own-account writes (reversible) | Cross-account writes, emails, infra |

Test only leads scoring ≥ +2. Park the rest with a named unlock condition.

## Mistakes Made (Real Campaign Log — Infomaniak 2026-09-09, 36 leads, 0 findings)

1. **Hunted BOLA on session-scoped APIs for hours.** The first 401/403 differential should have ended each sub-surface immediately; instead similar endpoints were re-tested across hosts.
2. **Chased the `uri=` redirect through 8 probes** before using the browser, which answered it in one navigation. Browser-first for flow bugs, Burp-first for API bugs.
3. **Burned guest AI quota guessing model slugs.** Enumeration without an oracle (docs, bundle strings, error differentials) is just noise.
4. **Repackaged an APK before confirming the API was reachable.** Static auth-shape analysis (smali `account-id` header) was the cheap win; the 2-hour dynamic pipeline confirmed what static already suggested.
5. **Ignored the exclusion list's spirit.** Integer share-IDs and shortlink enumeration were technically unlisted but obviously the same excluded class — time spent rationalizing instead of moving on.
6. **No stop rule.** The campaign ran 36 leads without a checkpoint. Rule now: after 10 consecutive negatives, mandatory re-rank.

## Tips That Actually Convert (2026)

- **Disclosure-mine first.** CVEs and plugin bug histories for the vendor's ecosystem name the weak product family (here: VOD plugins, OpenID shortcodes). Hunt the same class on adjacent in-scope endpoints.
- **Source maps are free source code.** Always check `.js.map` before any other web technique; one map (chk: 1,053 files) replaced a week of guessing.
- **APK strings are free API docs.** Auth headers (`account-id`), endpoint inventories, and OAuth client shapes come from 10 minutes of static analysis.
- **Repurpose, don't rebuild.** The repackage → CDP-login → heap-dump → smali-log chain built once works on every app from the same vendor.
- **Log negatives with evidence.** A closed lead with proof (own-200/cross-403 differential) prevents all future duplicate work — the log IS the deliverable until a finding lands.
- **Ask for access early.** SMS validation, trials, and API tokens from the operator unblock more than any cleverness. Request them on day one, in parallel with free-tier work.
- **Kill fast.** One clean own-vs-cross differential closes a surface. Never run 6 probes where 2 decide.
