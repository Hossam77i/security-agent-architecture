---
name: evidence-reporting
description: No finding ships without proof. Every reported finding gets an evidence bundle: UI screenshot(s), raw HTTP exchange transcript, and a note. Runs on EVERY target (training labs and hunts) as part of reporting — a report without PoC screenshots is a draft, not a deliverable. Trigger on "capture evidence", "PoC screenshots", "report", end of any hunt, or "evidence".
version: 1.0.0
revision_date: 2026-09-14
license: MIT
category: redteam
tags: [evidence, poc, screenshots, reporting, playwright, verification]
---

# Evidence Reporting: proof with every finding

A text-only report is a claim. An evidence bundle is a finding. Standard applies to **every target** — training labs and live hunts alike.

## The bundle (per finding, no exceptions)

```
<lab>/evidence/<finding>/
  shot-*.png        # UI screenshots proving visible impact/state
  exchange.http     # raw request + response transcript (status, headers, body)
  note.md           # what/where/impact + links to shots + transcript
<lab>/evidence/index.md   # manifest of all bundles
```

Minimum per finding: **1 screenshot + 1 raw exchange**. RCE/data-theft claims need both plus the exact command/output in `exchange.http`.

## Capture pattern (Playwright, verified 2026-09-14 on crAPI)

`scripts/capture_poc.py` per lab: API login for tokens + **real UI login for screenshots** (never rely on token injection alone), one function per finding, manifest writer. Lessons baked in from failures:

1. **SPA token injection bounces.** crAPI's React app ignores `localStorage` tokens set pre-load and redirects to `/login`. Always perform a real form login in the capture script. If injection is ever needed, set storage then `reload()` and verify URL — never assume.
2. **Strict-mode buttons.** Pages have duplicate labels (nav + form). Scope selectors: `page.locator('form').get_by_role('button', name='Login')`, never bare `get_by_role` when 2+ match.
3. **Already-authenticated contexts.** Later captures in one browser session skip login (no form present). Guard: `if placeholder.count() == 0: return`.
4. **Verify uniqueness.** Identical file hashes across shots = same render = broken capture. Assert distinct hashes before accepting a run.
5. **System chromium works.** `launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])` avoids the ~170MB Playwright browser download.
6. **Transcripts are live replays.** Re-fire the exact PoC request during capture (fresh timestamps, fresh IDs) — never paste old terminal output.

## Wiring (every target)

- Training labs: `scripts/capture_poc.py` + `evidence/` next to `progress-site/`. Link bundles from the dashboard finding rows and from `note.md` files.
- Live hunts: `~/huntkit/logs/<target>/evidence/` with the same layout. Redact PII/tokens before storing (see `evidence-hygiene`); keep full-fidelity copies only in the encrypted report package.
- Session close gate (see `hunt-productivity`): no finding marked solved/reported without its bundle. `capture_poc.py --only <name>` for single-finding refresh.

## Related skills

- `hunt-productivity` — session-close gate enforces this standard
- `report-writing` — evidence bundles are the attachments to impact-first reports
- `triage-validation` — 7-Question Gate decides IF it reports; this skill decides HOW it's proven
- `evidence-hygiene` — redaction before any screenshot/transcript leaves the lab
