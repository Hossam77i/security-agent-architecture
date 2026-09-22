# ALL RESOURCES COLLECTED — MASTER URL INDEX
> Complete historical + current session | Last updated: 2026-09-22

---

## PART 1: HISTORICAL INE LABS & CTF EXPERIENCE (from AGENTS.md)

### INE Lab CTFs Completed

| CTF | Target | Tasks | Key Lessons | Flag Format |
|-----|--------|-------|-------------|-------------|
| **ReconNexus CTF 1** | Web app | 4 tasks | JS tracker → API; backup files (ext matrix); prefetch HTML; SQLitei UNION | FLAG{n}_32hex |
| **Advanced Injection CTF 2** | Various | SQLi, Mongo, LDAP, XXE | LDAP md5-correction cycle; triple-lock essential | FLAG{n}_32hex |
| **API Pen Testing CTF 1 (WebServVault)** | target.ine.local (SOAP:80, REST:1337) | 4 tasks | WSDL hidden op; SQLite SQLi; mass-assignment role; JWT secret forge | FLAG{n}_32hex |
| **Filter Evasion & WAF Bypass CTF 1 (FlowBoard)** | target.ine.local | 4 tasks | Direct POST bypass; event-handler XSS; regex fuzzing; mobile UA gate | FLAG{n}_32hex |
| **Server-Side Attacks CTF 1 (ServerVault)** | target.ine.local (Apache+PHP-FPM) | 4 tasks | SSRF→internal:7777; XXE file://; PHP deserialization; SSRF→RCE | FLAG{n}_32hex |
| **Mobile App Sec CTF 1 (SecureBank)** | APK com.securebank.app, IPA SecureBank.ipa | 4 tasks | dexdump Constants; emergency backdoor JSON; IPA dylib grep | Hex only |
| **Mobile Pen-Testing CTF 1 (CampusConnect)** | APK com.campusconnect.app, IPA | IN PROGRESS 0/5 | Endpoints mapped; PIN brute failed; login contract unknown | — |
| **Mobile Pen-Testing CTF 2 (OrbitHR)** | APK com.orbithr.app | 4/4 | Login SQLi JSON; X-User-Role header; IDOR employee; wordlist paths | FLAG{n}_32hex |

### INE Lab Infrastructure Rules (from AGENTS.md)

| Rule | Detail |
|------|--------|
| **Flag verification** | Triple-lock: spaced hex → byte table → LEN 38 + remote md5sum + string compare |
| **Terminal channel** | Right-click desktop → Open in Terminal; `page.keyboard.type`; 12ms delay; leading space; `echo MARKER` |
| **Screenshot/OCR** | `~/.local/tess/usr/bin/tesseract <img> stdout --tessdata-dir ~/.local/tessdata`; never Read images |
| **Image budget** | Max 50/request; zero-image mode after ~15; rm screenshots after OCR |
| **Channels that DON'T work** | webhook.site (no outbound); clipboard (RDP X sync fails); local DNS/ping target.ine.local |

### Pre-installed Tools on INE Student VMs
| Tool | Location |
|------|----------|
| frida client/server | Preinstalled |
| dexdump | `~/Android/Sdk/build-tools/*/` |
| adb | Standard |
| Tesseract | `~/.local/tess/usr/bin/tesseract` |

---

## PART 2: SKILLS LOADED FROM PREVIOUS SESSIONS

### Core Methodology Skills
| Skill | Path | Description |
|-------|------|-------------|
| **bb-methodology** | `/home/user/.config/opencode/skills/bb-methodology/SKILL.md` | Master orchestrator: 5-phase workflow + critical thinking (developer psychology, anomaly detection, What-If experiments) |
| **bountyforge** | `/home/user/.config/opencode/skills/bountyforge/SKILL.md` | All-round bug bounty: smart contracts, web/API, CI/CD, LLM/AI, reporting (7-Question Gate, 4 validation gates) |
| **offensive-osint** | `/home/user/.config/opencode/skills/offensive-osint/SKILL.md` | Authorized external recon: subdomain enum, GraphQL/REST, identity fabric, cloud buckets, CDN/WAF bypass, vendor fingerprinting, CI/CD exposure, secret-scan catalog |
| **pentest-engagement** | `/home/user/.config/opencode/skills/pentest-engagement/SKILL.md` | Professional pentest: WEB mode (apex domains) + NETWORK mode (IPs/CIDRs) |
| **recon-and-osint** | `/home/user/.config/opencode/skills/recon-and-osint/SKILL.md` | Attack surface discovery: subdomains, hosts, endpoints, technologies, exposed services, leaked credentials |
| **recon-scope-triage** | `/home/user/.config/opencode/skills/recon-scope-triage/SKILL.md` | Separate target assets from namespace-collision noise (common word brands) |
| **report-writing** | `/home/user/.config/opencode/skills/report-writing/SKILL.md` | Bug bounty reports for H1/Bugcrowd/Intigriti/Immunefi |
| **triage-validation** | `/home/user/.config/opencode/skills/triage-validation/SKILL.md` | 7-Question Gate, 4 pre-submission gates, always-rejected list, CVSS 3.1 |
| **vulnerability-chaining** | `/home/user/.config/opencode/skills/vulnerability-chaining/SKILL.md` | Combine findings into end-to-end attack paths |
| **web2-vuln-classes** | `/home/user/.config/opencode/skills/web2-vuln-classes/SKILL.md` | 26 web2 bug classes with root causes, detection, bypass tables, exploit techniques |

### Specialized Skills (Loaded This Session)
| Skill | Path | Description |
|-------|------|-------------|
| **ine-rdp-lab** | `/home/user/.config/opencode/skills/ine-rdp-lab/SKILL.md` | INE lab operator: terminal channel, OCR pipeline, flag verification, mobile playbook |
| **telegram-intel** | `/home/user/.config/opencode/skills/telegram-intel/TELEGRAM_INTEL.md` | 8 Telegram channels curated |
| **github-x-intel** | `/home/user/.config/opencode/skills/github-x-intel/GITHUB_X_INTEL.md` | GitHub repos, X accounts, H1 reports, writeups |
| **unified-bug-classes** (18 skills) | `/home/user/.config/opencode/skills/unified-bug-classes/` | Merged references for each vuln class |

---

## PART 3: CURRENT SESSION RESOURCES (Auto-fetched)

### Telegram Channels (Public t.me/s/ previews)
| Channel | URL | Subscribers | Focus |
|---------|-----|-------------|-------|
| @bugbountyusa | https://t.me/s/bugbountyusa | 298 | Daily tips (XSS, SQLi, IDOR, Business Logic) |
| @GitBook_s | https://t.me/s/GitBook_s | 8K | PDFs: ZAP, Hakrawler, HTTP headers, regex, AWK, grep, CSP |
| @brutsecurity | https://t.me/s/brutsecurity | 17K | Tips, bypasses, CVEs, tools, coupons |
| @bugxplorer | https://t.me/s/bugxplorer | 9.8K | Research articles, conferences, GitHub repos |
| @bugbountyresources | https://t.me/s/bugbountyresources | 12.5K | 100 vuln categories, checklists, PDFs, tools |
| @bugbounty_tech | https://t.me/s/bugbounty_tech | — | Bug bounty techniques |
| @pentestandroid | https://t.me/s/pentestandroid | 287 | Android/iOS: Frida, SSL bypass, reports, keyhacks |
| @Bug0x | https://t.me/s/Bug0x | 5.3K | Writeups, courses, tools, checklists |

### GitHub Repositories
| Repo | URL | Stars | Focus |
|------|-----|-------|-------|
| Awesome-Bugbounty-Writeups | https://github.com/devanshbatham/Awesome-Bugbounty-Writeups | 6.1K | Categorized writeups by vuln class |
| HolyTips | https://github.com/HolyBugx/HolyTips | 2K | Checklists: API Security, Auth, File Upload, OAuth |
| daily-bugbounty-writeups | https://github.com/securitycipher/daily-bugbounty-writeups | 112 | Daily updates (1000+ commits) |
| bug-bounty-writeups | https://github.com/kh4sh3i/bug-bounty-writeups | 83 | WebSocket, cache poisoning, IDOR, 2FA, SSRF, RCE |
| awesome-bug-bounty | https://github.com/djadmin/awesome-bug-bounty | 5.8K | Meta-list: programs, platforms, methodology |
| HackerOne-Disclosed-Reports | https://github.com/ajaysenr/HackerOne-Disclosed-Reports | — | 587 reports (2025) sorted by bounty |
| awesome-msrc-writeups | https://github.com/bribes/awesome-msrc-writeups | 36 | Microsoft MSRC writeups |
| BountyHound | https://github.com/iamthefrogy/BountyHound | 81 | Auto-weekly tracker of top repos |
| apkleaks | https://github.com/dwisiswant0/apkleaks | 6.2K | APK scanner for URIs, endpoints, secrets |
| awesome-bugbounty-tools | https://github.com/awesome-bugbounty-tools | 6.1K | Curated tool list |
| scan4all | https://github.com/hktalent/scan4all | 6.1K | 15000+ PoCs, 23 vuln types |
| commix | https://github.com/commixproject/commix | 5.8K | Automated OS command injection |
| can-i-take-over-xyz | https://github.com/EdOverflow/can-i-take-over-xyz | 5.7K | Subdomain takeover service list |
| GarudRecon | https://github.com/GarudRecon | 266 | Automated domain recon |
| bbrecon | https://github.com/bbrecon | 229 | Python lib for Bug Bounty Recon API |
| contact.sh | https://github.com/rezadkim/contact.sh | 268 | OSINT contact finder |
| Some-BugBounty-Tips-from-my-Twitter-feed | https://github.com/emadshanab/Some-BugBounty-Tips-from-my-Twitter-feed | — | Twitter tips: Symfony RCE, Struts, AEM, LFI, SSRF |
| KingOfBugBountyTips | https://github.com/KingOfBugbounty/KingOfBugBountyTips | — | One-liner bug bounty scripts |
| OneLiner_BugBounty | https://github.com/Krishnathakur063/OneLiner_BugBounty | — | One-liners |
| One-Liner-Scripts | https://github.com/0xlittleboy/One-Liner-Scripts | — | Bash one-liners |
| Bug-Hunting-With-Bash | https://github.com/notmarshmllow/Bug-Hunting-With-Bash | — | Bash hunting scripts |
| 31-days-of-API-Security-Tips | https://github.com/inonshk/31-days-of-API-Security-Tips | — | Daily API security tips |
| AllThingsSSRF | https://github.com/jdonsec/AllThingsSSRF | — | SSRF writeups, cheatsheets, videos |

### Payload Collections
| Repo | URL | Type |
|------|-----|------|
| sql-injection-payload-list | https://github.com/payloadbox/sql-injection-payload-list | SQLi |
| xxe-injection-payload-list | https://github.com/payloadbox/xxe-injection-payload-list | XXE |
| ssrf-parameters | https://github.com/lutfumertceylan/top25-parameter/blob/master/ssrf-parameters.txt | SSRF params |
| LFI-files | https://github.com/hussein98d/LFI-files | LFI files |
| Adobe-Experience-Manager | https://github.com/emadshanab/Adobe-Experience-Manager | AEM paths |
| fuzz4bounty | https://github.com/0xPugal/fuzz4bounty | 1337 wordlists |

### Mobile Security Repos
| Repo | URL | Focus |
|------|-----|-------|
| awesome-mobile-security | https://github.com/vaib25vicky/awesome-mobile-security | Curated Android/iOS resources |
| Android-Reports-and-Resources | https://github.com/B3nac/Android-Reports-and-Resources | H1 disclosed Android reports |
| keyhacks | https://github.com/streaak/keyhaks | Verify leaked API keys |
| RegExAPI | https://github.com/odomojuli/RegExAPI | OAuth/API token regex patterns |
| geminiHunter | https://github.com/devploit/geminiHunter | Hunt exposed Gemini API keys |

### HolyTips Checklists (PDFs)
| Checklist | URL | Size |
|-----------|-----|------|
| API Security | https://raw.githubusercontent.com/HolyBugx/HolyTips/main/Checklist/API%20Security.md | 2.7MB |
| Auth | https://raw.githubusercontent.com/HolyBugx/HolyTips/main/Checklist/Auth.md | 785KB |
| File Upload | https://raw.githubusercontent.com/HolyBugx/HolyTips/main/Checklist/File%20Upload.md | 340KB |
| OAuth | https://raw.githubusercontent.com/HolyBugx/HolyTips/main/Checklist/OAuth.md | 790KB |

### Top 2025 HackerOne Reports
| Bounty | Title | Program | Technique |
|--------|-------|---------|-----------|
| $35,000 | ATO via Password Reset | GitLab | Reset token misuse |
| $25,000 | `/reports/:id.json` discloses user data | HackerOne | IDOR on reports |
| $25,000 | PolicyPageAssetGroup via GraphQL | HackerOne | GraphQL introspection |
| $15,000 | Groups module DoS | Cosmos | Governance DoS |
| $12,500 | Internal Access to Confluence | HackerOne | SSRF/misconfig |
| $10,000 | Arbitrary Read of Private Repo | GitHub | AuthZ bypass |
| $10,000 | Kernel stack free | PlayStation | Kernel exploit |
| $8,000 | Apache Airflow Format String | Internet Bug Bounty | Format string RCE |
| $7,500 | Exposed proxy → internal Reddit | Reddit | SSRF/proxy misconfig |
| $6,000 | Mozilla VPN RCE | Mozilla | Path traversal → RCE |
| $5,580 | Mint OAuth2 access token | GitLab | OAuth token theft |
| $5,000 | Blu-ray Java Sandbox Escape | PlayStation | Sandbox escape |
| $4,323 | Session Info Leak | IBB | Session leakage |
| $4,323 | CVE-2025-24813 RCE | IBB | Deserialization/RCE |
| $3,800 | Cache Poisoning DoS | Shopify | Cache poisoning |
| $3,500 | Privilege Escalation | Shopify | AuthZ bypass |

### X/Twitter Accounts
| Handle | URL | Focus |
|--------|-----|-------|
| @m0chan98 | https://x.com/m0chan98 | Volume hunter (2,679 vulns, 165 critical), scope aggregator |
| @Behi_Sec | https://x.com/Behi_Sec | Beginner roadmap, tools, IDOR→$5k, path traversal→$40k |
| @bountywriteups | https://x.com/bountywriteups | Automated writeup aggregation |
| @harshinsecurity | https://x.com/harshinsecurity | State of Bug Bounty 2026 |
| @bugbounty_tips | https://x.com/bugbounty_tips | Beginner tips, writeups, jobs |
| @3th1c_yuk1 | https://x.com/3th1c_yuk1 | CTF + bounty, CVE-2025-0133 |
| @heckintosh_ | https://x.com/heckintosh_ | GhostLock CVE-2026-43499 → $92,337 |
| @Alra3ees | https://x.com/Alra3ees | Symfony/Struts/AEM/RCE |

### Reference Articles & Research
| Title | URL | Source |
|-------|-----|--------|
| DOMPurify Attack Classes & Bypass History | https://github.com/cure53/DOMPurify/wiki/Attack-Classes-&-Bypass-History | Cure53 |
| CSS Injection: The Bomb Inside Your Inbox | https://portswigger.net/research/css-the-bomb-inside-your-inbox | PortSwigger |
| postMessage targetOrigin Bypass | https://lab.ctbb.show/research/postmessage-targetorigin-bypass-via-ip-normalization | BugXplorer |
| HTTP/2 WAF Bypasses | https://lab.ctbb.show/research/h2-WAF-Bypasses | BugXplorer |
| Rate Limit Bypass → 0-Click ATO | https://zeroxuf.medium.com/rate-limit-bypass-leads-to-0-click-ato-9f1b29daec42 | Bug0x |
| GhostLock CVE-2026-43499 | https://aydinnyunus.github.io/2026/06/ | heckintosh_ |
| Malicious File Upload Checklist | https://aacle.notion.site/Malicious-File-Upload-Checklist-3cd2b85ff7494efdac47d646b98cdce4 | Bug0x |
| Click2Shell — WordPress Preauth RCE | https://pwn.ai/blog/click2shell | BrutSecurity |
| Ni8mare — n8n Unauth RCE | https://pwn.ai/blog/ni8mare | BrutSecurity |
| IDN Homograph → Account Collision | https://t.me/s/brutsecurity/3016 | BrutSecurity |
| 403/401 Bypass | https://github.com/iamj0ker/bypass-403 | BrutSecurity |
| HackTools Extension | https://github.com/LasCC/Hack-Tools | BrutSecurity |

### Tools & Utilities
| Tool | URL | Purpose |
|------|-----|---------|
| ysoserial | https://github.com/frohoff/ysoserial | Java gadget generation |
| ysoserial.net | https://github.com/pwntester/ysoserial.net | .NET ViewState/BinaryFormatter |
| phpggc | https://github.com/ambionics/phpggc | PHP POP chain generation |
| flask-unsign | https://github.com/Paradoxis/flask-unsign | Flask session sign/unsign |
| marshalsec | https://github.com/marshalsec/marshalsec | Java JNDI/LDAP/RMI server |
| PadBuster | https://github.com/AonCyberLabs/PadBuster | Padding oracle decrypt/forge |
| sisakulint | https://github.com/sisakulint/sisakulint | GitHub Actions security audit |
| trufflehog | https://github.com/trufflesecurity/trufflehog | Secret scanning |
| gitleaks | https://github.com/gitleaks/gitleaks | Secret scanning |
| ffuf | https://github.com/ffuf/ffuf | Fast fuzzing |
| nuclei | https://github.com/projectdiscovery/nuclei | Template-based scanning |
| httpx | https://github.com/projectdiscovery/httpx | Fast HTTP toolkit |
| katana | https://github.com/projectdiscovery/katana | Fast crawling |
| subfinder | https://github.com/projectdiscovery/subfinder | Subdomain enumeration |
| dnsx | https://github.com/projectdiscovery/dnsx | DNS toolkit |
| gau | https://github.com/lc/gau | URL discovery |
| waybackurls | https://github.com/tomnomnom/waybackurls | Wayback URLs |
| qsreplace | https://github.com/tomnomnom/qsreplace | Query param replacement |
| dalfox | https://github.com/hahwul/dalfox | XSS scanning |
| graphql-cop | https://github.com/dolevf/graphql-cop | GraphQL security audit |
| graphw00f | https://github.com/dolevf/graphw00f | GraphQL fingerprinting |
| inql | https://github.com/dolevf/inql | GraphQL Burp extension |
| apkleaks | https://github.com/dwisiswant0/apkleaks | APK secret scanning |
| apktool | https://github.com/iBotPeaches/Apktool | APK decompilation |
| jadx | https://github.com/skylot/jadx | APK decompiler |
| objection | https://github.com/sensepost/objection | Mobile runtime exploration |
| frida | https://github.com/frida/frida | Dynamic instrumentation |
| interactsh | https://github.com/projectdiscovery/interactsh | OOB interaction server |

### Wordlists & Payloads
| Wordlist | URL |
|----------|-----|
| SecLists | https://github.com/danielmiessler/SecLists |
| PayloadsAllTheThings | https://github.com/swisskyrepo/PayloadsAllTheThings |
| fuzz4bounty (1337 lists) | https://github.com/0xPugal/fuzz4bounty |
| SQLi payloads | https://github.com/payloadbox/sql-injection-payload-list |
| XXE payloads | https://github.com/payloadbox/xxe-injection-payload-list |
| SSRF params | https://github.com/lutfumertceylan/top25-parameter/blob/master/ssrf-parameters.txt |
| LFI files | https://github.com/hussein98d/LFI-files |
| AEM paths | https://github.com/emadshanab/Adobe-Experience-Manager |

### CVEs Referenced Across Skills
| CVE | Description | Referenced In |
|-----|-------------|---------------|
| CVE-2015-7501 | Apache Commons Collections deserialization | Deserialization |
| CVE-2016-7124 | PHP __wakeup property-count bypass | Deserialization |
| CVE-2017-5941 | node-serialize IIFE RCE | Deserialization |
| CVE-2021-41277 | CVE-2021-41277 LFI | File Upload / LFI |
| CVE-2022-40604 | Apache Airflow format string | H1 Reports |
| CVE-2024-38856 | Apache OFBiz RCE | Bug0x |
| CVE-2024-45230 | Django DoS | H1 Reports |
| CVE-2024-53908 | Django SQL injection | H1 Reports |
| CVE-2024-56374 | IPv6 validation DoS | H1 Reports |
| CVE-2025-24813 | Deserialization/RCE | H1 Reports, IBB |
| CVE-2025-49596 | MCP Inspector RCE | AI/LLM, MCP |
| CVE-2025-5273 | Markdownify MCP file read | AI/LLM, MCP |
| CVE-2025-53109/53110 | Anthropic Filesystem MCP "EscapeRoute" | AI/LLM, MCP |
| CVE-2025-68143 | Git MCP path traversal | AI/LLM, MCP |
| CVE-2026-21858 | n8n Unauth RCE (Ni8mare) | BrutSecurity |
| CVE-2026-43499 | GhostLock | heckintosh_ |

### Skills Created This Session
| Skill | Path |
|-------|------|
| telegram-intel | `/home/user/.config/opencode/skills/telegram-intel/TELEGRAM_INTEL.md` |
| github-x-intel | `/home/user/.config/opencode/skills/github-x-intel/GITHUB_X_INTEL.md` |
| unified-bug-classes (18 skills) | `/home/user/.config/opencode/skills/unified-bug-classes/` |
| MASTER_INDEX | `/home/user/.config/opencode/skills/unified-bug-classes/MASTER_INDEX.md` |

---

## PART 4: ALL AVAILABLE SKILLS IN OPENCODE

### Total Skills: 200+ (including 18 unified + 10 core + 2 new + 170+ specialized)

Key skill categories:
- **Core Methodology** (10): bb-methodology, bountyforge, offensive-osint, pentest-engagement, recon-and-osint, recon-scope-triage, report-writing, triage-validation, vulnerability-chaining, web2-vuln-classes
- **INE Labs** (1): ine-rdp-lab
- **New Intelligence** (3): telegram-intel, github-x-intel, unified-bug-classes (18)
- **Specialized** (170+): All skills in `/home/user/.config/opencode/skills/` covering web, mobile, API, cloud, AI/LLM, crypto, supply chain, red team, blue team, etc.