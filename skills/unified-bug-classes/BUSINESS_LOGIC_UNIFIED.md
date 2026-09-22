# BUSINESS LOGIC FLAWS — UNIFIED MASTER REFERENCE
> Merged from: web2-vuln-classes (Section 5), telegram-intel (@bugbountyusa tips, @bugbountyresources #1075), github-x-intel (H1 reports), bountyforge, bb-methodology
> Last updated: 2026-09-22

---

## QUICK START — 5-MINUTE TEST PLAN

```
[ ] 1. Map complete business workflows (purchase, coupon, transfer, refund, registration)
[ ] 2. Test state-skipping (fast path, workflow bypass, missing state updates)
[ ] 3. Test numeric boundaries (negative, zero, overflow, precision)
[ ] 4. Test IDN homograph → account collision (Unicode normalization)
[ ] 5. Test rate limit bypass on auth/critical endpoints
[ ] 6. Test concurrent operations (race conditions on state changes)
[ ] 7. Prove impact: financial loss, free goods, ATO, privilege escalation
```

---

## CORE PATTERNS (Complete Taxonomy)

### Pattern 1: Fast Path Skips State Update
```python
# VULNERABLE
def redeem_coupon(coupon_code, user_id):
    coupon = get_coupon(coupon_code)
    if coupon.balance >= amount:
        transfer(user_id, amount)
        return  # MISSING: never marks coupon as used!
    coupon.mark_used()
    transfer(user_id, amount)

# SECURE
def redeem_coupon(coupon_code, user_id):
    coupon = get_coupon(coupon_code)
    if coupon.balance >= amount and not coupon.used:
        coupon.mark_used()
        transfer(user_id, amount)
```

### Pattern 2: Workflow Step Skip
```
Normal Flow:    Select Plan → Add Payment → Confirm → Activate
Attack Flow:    Skip to /confirm?plan=premium&skip_payment=true
```
**Test**: Direct access to later steps, parameter manipulation (`skip_payment=true`, `step=3`), referrer bypass

### Pattern 3: Negative / Zero Bypass
```
POST /api/transfer {"amount": -100}    → credits attacker, debits victim
POST /api/cart {"quantity": 0}         → adds item free
POST /api/refund {"amount": 99999}     → refunds more than purchased
POST /api/withdraw {"amount": -500}    → deposits instead of withdraws
POST /api/buy {"price": 0}             → free purchase
POST /api/buy {"quantity": -1}         → seller pays buyer
```

### Pattern 4: Race Condition (TOCTOU) — See Race Conditions Unified Skill
```
Thread 1: checks balance (10 credits) → PASS
Thread 2: checks balance (10 credits) → PASS
Thread 1: deducts → 0 remaining
Thread 2: deducts → -10 remaining (DOUBLE SPEND)
```

### Pattern 5: IDN Homograph → Account Collision (BrutSecurity #3016)
**Normalization Mismatch at Scale:**
```
Input → Validation → Database → Token Generation → Email Delivery
```
- Database: `victim@gmail.com` ≡ `victim@gmáil.com` (after NFC/NFKC normalization)
- Application: Finds victim's account by normalized email
- SMTP: Treats as DIFFERENT → sends reset to attacker's `gmáil.com` domain

**Test Vectors:**
| Original | Unicode Variant | Unicode Codepoint |
|----------|-----------------|-------------------|
| `a` | `á` | U+00E1 |
| `a` | `à` | U+00E0 |
| `a` | `ā` | U+0101 |
| `i` | `ı` | U+0131 (dotless i) |
| `i` | `í` | U+00ED |
| `o` | `о` | U+043E (Cyrillic) |
| `e` | `е` | U+0435 (Cyrillic) |
| `c` | `с` | U+0441 (Cyrillic) |
| `p` | `р` | U+0440 (Cyrillic) |

**Verification:** Register `victim@gmáil.com` → request reset for `victim@gmail.com` → check if token sent to attacker

### Pattern 6: Rate Limit Bypass → 0-Click ATO (Bug0x #166)
https://zeroxuf.medium.com/rate-limit-bypass-leads-to-0-click-ato-9f1b29daec42
- Bypass rate limiting on OAuth/password reset/2FA endpoints
- Combine with token leakage or prediction → zero-interaction ATO
- Test: distributed requests, header manipulation (X-Forwarded-For), IP rotation, endpoint confusion

### Pattern 7: Precision / Rounding Errors
```python
# Floating point precision
price = 0.1 + 0.2  # = 0.30000000000000004
# Integer division truncation
discount = total // 3  # loses cents
# Currency conversion rounding
usd = eur * rate  # round half-up vs banker's rounding
```

### Pattern 8: Coupon/Promo Code Abuse
```
- Multiple redemption (fast path skips mark_used)
- Stackable coupons (no mutual exclusion check)
- Expired coupon acceptance (no expiry check)
- Coupon prediction (sequential, timestamp-based, low entropy)
- Coupon sharing (no per-user limit)
```

### Pattern 9: Gift Card / Store Credit Issues
```
- Balance transfer between accounts (no authorization)
- Partial redemption leaves balance accessible
- Gift card prediction (sequential numbers)
- Balance check without rate limit → enumeration
- Refund to different gift card
```

### Pattern 10: Loyalty Points / Rewards
```
- Points transfer between users
- Points purchase with negative amount
- Tier upgrade/downgrade race condition
- Points expiry bypass
- Referral bonus loops (A refers B, B refers A)
```

### Pattern 11: Subscription / Billing Logic
```
- Downgrade without proration (keep premium features)
- Upgrade without payment (skip payment step)
- Trial extension (repeated signups, email + dot)
- Cancellation bypass (reactivate without payment)
- Invoice manipulation (negative line items)
```

### Pattern 12: Inventory / Stock Race
```
- overselling (check stock → decrement, gap allows oversell)
- Reservation without timeout (hold forever)
- Cart hold → checkout race (two users, one item)
```

### Pattern 13: Access Control Logic
```
- Feature flag check only in UI, not API
- Role check: `if user.is_admin` in frontend only
- Resource ownership: `if resource.owner == user` missing
- Time-based access: `if now < expiry` but expiry not enforced server-side
```

---

## BUSINESS LOGIC CHEATSHEET (BugBountyResources #1075)

### Common Flaw Categories
```
1. Authentication Logic     → Session fixation, weak reset, 2FA bypass
2. Authorization Logic      → Horizontal/vertical IDOR, missing checks
3. Transaction Logic        → Race conditions, state skipping, negative values
4. Workflow Logic           → Step skipping, order bypass, completion bypass
5. Pricing/Discount Logic   → Negative prices, coupon stacking, precision
6. Inventory Logic          → Overselling, reservation abuse, stock check bypass
7. Subscription Logic       → Trial abuse, downgrade/upgrade flaws, cancellation
8. Referral/Invite Logic    → Self-referral, loop, fake accounts
9. Loyalty/Rewards Logic    → Points transfer, expiry bypass, tier manipulation
10. File/Upload Logic       → Type confusion, size bypass, processing flaws
```

### Testing Methodology
```
For EACH business function:
1. Document normal flow (happy path)
2. Identify all state changes
3. Identify all validation points
4. Test: skip each step
5. Test: reorder steps
6. Test: repeat steps
7. Test: negative/zero/overflow inputs
8. Test: concurrent execution
9. Test: Unicode/IDN variants
10. Test: rate limit bypass
```

---

## HIGH-VALUE H1 REPORTS (2025)

| Bounty | Title | Program | Pattern |
|--------|-------|---------|---------|
| **$35,000** | ATO via Password Reset without user interactions | GitLab | Reset token misuse (Pattern 2/6) |
| **—** | Race Condition in Folder Creation | Dust | TOCTOU (Pattern 4) |
| **—** | Race Condition in Workspace Limits | SingleStore | TOCTOU (Pattern 4) |
| **—** | Improper Authentication Throttling | Lichess | Rate limit bypass (Pattern 6) |
| **—** | Race Condition on Add Free Domain | Automattic | Coupon/limit (Pattern 4) |
| **—** | Chained Broken Access Control in TikTok Live | TikTok | Workflow skip (Pattern 2) |
| **—** | Unauthorized Reservation Cancellation | Yelp | IDOR + workflow (Pattern 2) |
| **—** | Exceeding Workspace Limit via Race | SingleStore | TOCTOU (Pattern 4) |
| **—** | Bypass Cloudflare Cache Keys via Header Overflow | Cloudflare | Cache poisoning (Related) |

---

## CHAINS THAT PAY

```
Workflow skip + payment bypass                    → Critical (Free premium)
Negative amount + transfer                        → Critical (Financial loss)
Coupon fast path + no mark_used                   → High (Unlimited coupons)
IDN homograph + password reset                    → Critical (ATO)
Rate limit bypass + OTP prediction                → Critical (0-click ATO)
Race condition + double spend                     → High/Critical
Precision error + high-volume transactions        → High (Financial)
Gift card balance transfer                        → High
Subscription downgrade without proration          → High
Loyalty points transfer + cashout                 → High
Referral loop + bonus abuse                       → Medium/High
```

---

## AUTOMATED TESTING (One-Liners)

```bash
# Workflow step skip
for step in 1 2 3 4 5; do
  curl "https://target.com/checkout/step$step?skip_payment=true" -w "Step $step: %{http_code}\n"
done

# Negative/zero testing
for val in -1 0 -100 999999; do
  curl -X POST "https://target.com/api/transfer" -d "{\"amount\": $val}" -w "$val: %{http_code}\n"
done

# Coupon brute force (if low entropy)
ffuf -u "https://target.com/api/coupon/validate" -X POST -d "{\"code\":\"FUZZ\"}" -w coupons.txt -fc 400

# IDN homograph test
for variant in "gmáil.com" "gmàil.com" "gmaıl.com" "gmаil.com"; do
  curl "https://target.com/forgot-password" -d "email=victim@$variant"
done

# Rate limit bypass (distributed)
for ip in $(cat proxies.txt); do
  curl -H "X-Forwarded-For: $ip" "https://target.com/api/verify-otp" -d '{"otp":"123456"}'
done

# Precision testing
curl -X POST "https://target.com/api/price" -d '{"items":[{"price":0.1,"qty":3},{"price":0.2,"qty":1}]}'

# Concurrent testing (race)
for i in {1..20}; do
  curl -X POST "https://target.com/api/redeem" -d '{"code":"COUPON123"}' &
done
wait
```

---

## TRIAGE DECISION TREE

```
1. Does flaw allow unauthorized action?
   NO → Not a business logic bug
   YES → Continue

2. What is the impact?
   - Financial loss (theft, free goods, negative balance)    → Critical
   - Account Takeover                                        → Critical
   - Privilege Escalation                                    → Critical
   - Unlimited resource (coupons, points, trials)            → High
   - DoS / Resource exhaustion                               → Medium
   - Information disclosure (minor)                          → Low
   - UI inconvenience only                                   → N/A

3. Chain potential?
   + IDOR / Auth bypass                                      → Critical
   + Rate limit bypass                                       → Critical
   + SSRF / RCE                                              → Critical
```

---

## KILL LIST (Auto-Reject)

| Pattern | Reason |
|---------|--------|
| "Could exploit if user does X, Y, Z" | Theoretical = N/A |
| Requires victim to click phishing link | Social engineering = N/A |
| Flaw in test/staging only (not prod) | Out of scope = N/A |
| Negative amount but server rejects | Not vulnerable = N/A |
| Workflow skip but redirects to login | Not bypassed = N/A |
| Coupon prediction but rate limited | Not exploitable = N/A |
| Precision error < $0.01 | No material impact = N/A |
| Race condition but atomic DB operations | Not vulnerable = N/A |

---

## TOOLS (Consolidated)

| Tool | Purpose |
|------|---------|
| `ffuf` | Workflow fuzzing, coupon brute force |
| `race-the-web` | HTTP race condition testing |
| `aiohttp` + `asyncio` | Custom race condition scripts |
| `Turbo Intruder` (Burp) | Last-byte sync race testing |
| `Param Miner` (Burp) | Hidden parameter discovery |
| `nuclei` templates | Business logic templates |
| `idna` / `python-idna` | IDN homograph generation |

---

## REFERENCES (All Sources)

- web2-vuln-classes: Section 5 (Patterns 1-6)
- telegram-intel: @bugbountyusa tips #80, #85, #89; @bugbountyresources #1075 (Business Logic Cheatsheet); @brutsecurity #3016 (IDN homograph); @Bug0x #166 (Rate limit → ATO)
- github-x-intel: H1 reports (GitLab $35k, Dust, SingleStore, Lichess, Automattic, TikTok, Yelp, Cloudflare)
- bountyforge: Business logic as #1 under-hunted class, ATO chains
- bb-methodology: What-If experiments (skip checkout, skip 2FA, coupon race), Critical Thinking
- PortSwigger: Business logic labs
- HackTricks: Business logic methodology