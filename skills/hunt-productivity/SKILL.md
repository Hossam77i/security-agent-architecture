---
name: hunt-productivity
description: The non-technical half of elite hunting. Top hunters (rabhi, hakluke, Bonner, Buerhaus) win on methodology, notes, consistency, report quality, and target economics — not tools. Use at session start (goals, plan, timebox), during (notes, pacing, STUCK), and end (dupe-check, report gate, accounting). Trigger on "plan session", "take notes", "pick a target", "am I productive", "dupe check", "pacing", "goals", "Start of any training or hunt alongside bb-methodology.
version: 1.0.0
revision_date: 2026-09-14
license: MIT
category: redteam
tags: [productivity, notes, methodology, goals, pacing, reporting, target-selection]
---

# Hunt Productivity: the other 50%

Technical skill gets you in the room. These habits decide whether you get paid. Synthesized from HackerOne/Intigriti/YesWeHack interviews (rabhi, hakluke, Buerhaus, Bonner/Roll4CombatUS), Bugcrowd methodology series, bugbounty.info, and competitior skill bundles (shuvonsec/0x1Jar/elementalsouls).

---

## 1. Session contract (first 5 minutes, every session)

Write this down before touching the target. No contract = wandering.

```
Date:        ____  Target: ____  Mode: [training|bounty|redteam]
Goal (time, NOT bugs):  ____ hours on ____  (Bonner rule: time goals, zero expectations)
Vuln classes (1-2): ____  Route: [Wide recon | Deep test]
Stop conditions: 20-min rotation / 45-min rabbit hole / STUCK at 3 fails
Dupe-check done: [ ]  Scope re-read: [ ]
```

Why time-not-bugs: bug goals create frustration tilt; time goals create volume, and volume creates bugs. rabhi: minimum 2h/day, never give up early, intuition compounds over days/weeks on one target.

## 2. Notes & session tracking (never hunt without this)

Digital notes beat memory from day 3 onward. Per target keep ONE file (`~/huntkit/logs/<target>.md`, template in `scripts/note-template.md`):

- **Features list** — every feature + intended behavior in your own words (iBruteSec: edge cases jump out while writing this; low-impact notes become chains later)
- **Interesting params/endpoints/JS** — with one-line why-weird + screenshot/reference
- **Commands run** — wrap long sessions in `script session.log` (ZephrFish: dead sessions, cool one-liners, report evidence)
- **Failed attempts** — what/why, so you never re-test the same way (feeds STUCK)

Rule: if it isn't written, it didn't happen. Review yesterday's notes in the first 10 minutes (pattern recognition needs warm-up).

## 3. Daily reading (15 min, non-negotiable)

Bonner: "read one thing per day — writeups, open reports, tech blogs." rabhi: recon + differentiation come from accumulated patterns. Sources: HackerOne Hacktivity, Intigriti writeups, Bugcrowd mindset, disclosed criticals, framework changelogs. Log one line per read: technique → where you'd use it. This compounds into specialization (below).

## 4. Target selection economics (bounty mode)

Highest bounty table ≠ highest expected payout. Score each candidate 1–5 and hunt the total:

| Factor | Ask |
|---|---|
| Freshness | New program / scope update / just launched? (less competition) |
| Competition | Crowded H1 whale or quiet VDP? (hakluke: hack where there's less competition) |
| Fit | Matches your niche + recent reads? |
| Complexity | Complex features, money/data flows, integrations? (complex = less secure) |
| Response | Triage speed + payout reliability reputation? |

Rotate out when: time budget spent with zero new signals (Bonner: spend the hours, then move on — no sunk-cost), or recon shows a picked-clean, long-running whale outside your niche.

## 5. Recon as a pipeline, not a checklist

One-shot, timestamped output, every target: `scripts/recon.sh <domain>` (subs → resolve → probe → URLs → JS → params → nuclei → report dir). Principles (bugbounty.info, su6osec, Cyber-note):

- Passive before active; deduplicate between stages; every stage feeds files the next stage reads.
- **Diff over time**: re-run on schedule, alert on new assets (new = least competition).
- JS analysis is consistently top-ROI; API docs (Swagger/OpenAPI/Postman) are endpoint lists handed to you.
- 5-minute rule: all 401/403/404 after 5 min probing → move on (shuvonsec bundle).
- Wordlist matters more than the tool (content discovery).

## 6. Specialization tracker

Generalist trap is real: pick ONE niche per quarter (API authz, SSRF/cloud, mobile, OAuth, LLM...). Track in `~/huntkit/MEMORY.md`: niche → reads → labs → findings → payout. Pivot only on data (findings/quarter), never on boredom. Our training labs feed this directly (crAPI → API authz, WebGoat → web, Juice → modern web).

## 7. Kill weak findings fast (triage economics)

- The Only Question (shuvonsec): "Can an attacker do this RIGHT NOW to a real user with NO unusual actions — real harm?" No → STOP, log, move on.
- 7-Question Gate before any report (`triage-validation`). Status-code-only, self-only, and theoretical findings die here.
- **Dupe-check before writing** (missing in most workflows — add it): search disclosed reports + HackerOne Hacktivity + changelog/commits for the same endpoint/class. 10 minutes here saves hours of N/A.
- Chain before submitting: A→B signal (same dev, 20 min siblings) turns mediums into criticals (`vulnerability-chaining`).

## 8. Report quality = pay (the Bonner lesson)

Bonner was fired from his first pentest job for weak reports — then rebuilt on writing. Buerhaus: write for the program owner; quality > quantity (one RCE beats ten self-XSS). Gate every report (`report-writing`): impact-first sentence, exact replayable requests, <600 words, CVSS matching actual impact. While waiting for triage: escalate further, retest fixes (incomplete patch = new bug).

## 9. Pacing & health (performance system, not luxury)

- hakluke's list: health is a top-10 item. rabhi: work-life balance keeps motivation across years. LHE lesson (Vitor Falcao): set daily report-rate goals AND mandatory breaks; pace is a team protocol, cover for each other.
- Session rhythm: 50/10 focus blocks; hard stop at contract hours; rabbit-hole timer visible.
- Tilt protocol: two N/As or one frustrating hour → 15-min break + notes review, never "one more try." Tilt burns more hours than any WAF.

## 10. Collaboration pattern (pair hunting)

"Together you find more" — pair sessions with designated roles, runnable with subagents (`Task` explore/general):
- **Driver**: executes, narrates every request.
- **Skeptic**: owns the 7-Question Gate live, calls out status-only claims, proposes the bypass the driver dismissed.
Swap every 45 min. Log disagreements — they're usually the bug.

## 11. Program communication

Top hunters ask programs questions (office hours, architecture context). Templates: scope-clarification before deep work, impact-clarification on N/A pushback with business-risk framing, retest notes when fixes land. Professional, short, evidence-linked. Disputes: counter with impact math + platform mediation, then walk away fast (sunk-cost applies to arguments too).

## 12. Session close (last 10 minutes)

- [ ] Experiments logged with evidence (dashboard/MEMORY)
- [ ] Evidence gate (`evidence-reporting`): every solved/reported finding has screenshot + raw exchange bundle — text-only findings stay drafts
- [ ] Untested surface list written (opens next session)
- [ ] Time accounting updated (`~/huntkit/MEMORY.md` time log)
- [ ] STUCK invocations reviewed — what pattern keeps recurring?
- [ ] Tomorrow's first 10 minutes defined (notes review + one vuln class)

## Related skills

- `bb-methodology` — technical 5-phase loop (run together at session start)
- `solve-review-cycle` — PEER-COMPARE + STUCK (this skill's enforcement arms)
- `triage-validation`, `report-writing`, `vulnerability-chaining` — gates and escalation
- `recon-and-osint`, `offensive-osint`, `web2-recon` — recon depth behind `scripts/recon.sh`
- `pentest-engagement` — red-team planning/SOW/OPSEC side
