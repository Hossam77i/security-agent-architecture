---
name: ine-rdp-lab
description: Operate INE skill-check labs through the browser Guacamole RDP channel. Use when solving any INE lab (CTF or otherwise) via attackdefensecloudlabs.com links — terminal interaction, screenshot OCR pipeline, image budget, flag verification, and lab-type playbooks (web, API, mobile APK/IPA).
version: 1.0.0
revision_date: 2026-09-17
license: MIT
category: redteam
tags: [ine, ctf, guacamole, rdp, mobile, apk, ocr]
---

# INE RDP Lab Operator

Solve INE labs through the Guacamole-in-browser channel. The lab VM is reachable ONLY inside the RDP session; this machine has no route to lab targets. All work happens by typing into the remote terminal and reading back screenshots.

## 0. Session bootstrap (every lab)

1. **Fresh chat per lab.** The provider caps at 50 images/request; screenshots/`Read`s accumulate permanently. Never continue a lab across chats — restate target + task, pull methods from `AGENTS.md`, values from `opencode.db` (`part` table).
2. Navigate to the lab URL, `snapshot` (text, free) to confirm connection.
3. **Guacamole `internal error` = dead VM.** ONE Reconnect attempt → ask the user to Stop/Start the lab. Never debug it from the client.
4. Screenshot once; if wallpaper-only on a fresh VM, right-click to test aliveness before waiting.

## 1. Terminal channel (inviolable order)

1. Open: right-click desktop → Open in Terminal. (Hotkeys/taskbar icons fail through Guacamole — don't experiment.)
2. If keystrokes stop landing: left-click canvas to refocus, retype.
3. Type via `page.keyboard.type`, Enter to submit.
4. Screenshot with `filename` → OCR locally via `~/.local/tess/usr/bin/tesseract <img> stdout --tessdata-dir ~/.local/tessdata`. NEVER `Read` an image.
5. Proactive switch: after ~15 images in a session, zero-image mode is mandatory. `rm` screenshots after OCR.

### Typing protocol (Guacamole mangles input)
- Short lines (<~150 chars), leading space, delay ≥12ms.
- In tool calls: ALWAYS `const cmds = "..."` double-quoted JS. Single-quoted JS + backslashes = SyntaxError. Test: if a call errors, the shell got nothing.
- NEVER type hashes/tokens/flags/paths-with-hashes. Pipe through files: `pm path ... > f`, `xargs`, `cut`, `$(...)`.
- No nested quotes: `sh -c '... "..." ...'` breaks (`\"` stays literal inside single quotes). Restructure instead: drop the space (`-H Content-Type:application/json`), use template files + `sed s/A/B/` unquoted, or heredocs.
- Every command ends with an `echo MARKER`; every background job writes markers + results to files. Verify the echoed command is on screen before trusting output (stale-screen trap).
- `===` bare on a line breaks zsh — quote it.

## 2. Flag verification (triple-lock, no exceptions)
1. Extract as spaced hex (`od -An -tx1 -v`), NOT raw text.
2. Decode via explicit byte table (`0x30`=`0`, `0x64`=`d` — NEVER from memory).
3. LEN check (38 for `FLAGn_`+32hex) + remote `md5sum` + `[ "$X" = "<candidate>" ] && echo MATCH`.
4. Disambiguate lookalikes with decimal dump (`od -An -tu1`).
5. On MISMATCH: bisect with `cut -c` + OK/FAIL words (halves → quarters), never re-read full strings.
6. Values go to session history only — never into notes files.

## 3. Pre-flight (ONE batch, ONE screenshot — before anything else)
`ls ~/Desktop/ ~/Desktop/Tools/`, locate `*.apk`/`*.ipa`, `adb devices`, `curl -m 5` backend check. Decides tools/internet/emulator state. Student VMs have no pip internet — use what's installed (frida client/server are preinstalled; `dexdump` lives in `~/Android/Sdk/build-tools/*/`).

## 4. Brute-force discipline (the 10k-PIN lesson)
NEVER loop before ALL of these hold:
1. Request format confirmed from app code (`dexdump` const-strings), not guessed.
2. Positive control known: what does SUCCESS look like? Match on its distinctive key (e.g. `token`), never generic `true`.
3. Harness validated: run the loop body ONCE with a literal value first; confirm failure shape, then launch.
4. Loop in background (`nohup ... &`), poll the results file. Parallelize with `xargs -P`.
5. If full space finds nothing → the FORMAT is wrong (keys/username), not the PIN. Read code; don't re-run.

## 5. Mobile playbook (APK/IPA)
1. Boot emulator FIRST (`nohup startemulator.sh`), static work while it boots.
2. APK: `adb root` → `pm path <pkg>` to file → `xargs` pull.
3. Static order: `unzip -l` → `classes*.dex` → per-dex `strings` → app class list → 32-hex grep → `dexdump -d` for `Constants`/URLs/request shapes → curl.
4. API probes: JSON + `Content-Type: application/json` FIRST. Tokens may ROTATE per call — re-fetch the full chain piped, never hand-carry.
5. IPA: `unzip` + `grep -a` (leftovers: `.dylib`, `.bak`, `DS_Store`); `strings` the main binary for headers/keys/URLs.
6. Raw `grep FLAG` on APK/IPA misses dex-stored strings — always check decompiled/dexdumped output.

## 6. Conduct
- Fail fast on infra; report 0-flag status proactively instead of grinding.
- Sequential labs chain off one auth — unblock the critical path via code reading, not repeated attempts.
- Keep user updated when blocked >2 min; ask for Stop/Start, credentials, or task-box checks crisply.
- Respect user rate limits (sleeps ≤5s, batched requests).
