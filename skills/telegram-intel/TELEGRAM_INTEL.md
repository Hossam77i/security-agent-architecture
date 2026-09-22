# Telegram Channel Intelligence — Curated Resources (Auto-Fetched 2026-09-22)

> Source: Public t.me/s/ previews via webfetch. No login required. Deduplicated against existing skills.

---

## CHANNEL INDEX

| Channel | Subscribers | Focus | Key Assets |
|---------|-------------|-------|------------|
| [@bugbountyusa](https://t.me/s/bugbountyusa) | 298 | Daily tips (XSS, SQLi, IDOR, Business Logic) | Tips #77-89 |
| [@GitBook_s](https://t.me/s/GitBook_s) | 8K | PDFs/Guides: ZAP, Hakrawler, HTTP headers, regex, AWK, grep, CSP | 15+ PDFs |
| [@brutsecurity](https://t.me/s/brutsecurity) | 17K | Tips, bypasses, CVEs, tools, coupons | IDN homograph, 403 bypass, secret regex |
| [@bugxplorer](https://t.me/s/bugxplorer) | 9.8K | Research articles, conferences, GitHub repos | HTTP/2 WAF bypass, postMessage, DOMPurify, CSS injection |
| [@bugbountyresources](https://t.me/s/bugbountyresources) | 12.5K | 100 vuln categories, checklists, PDFs, tools | IDOR/2FA/Reset PDFs, APKLeaks, SQL wordlist |
| [@pentestandroid](https://t.me/s/pentestandroid) | 287 | Android/iOS pentest: Frida, SSL bypass, reports, keyhacks | 2 large PDFs, InsecureBankv2, awesome-mobile-security |
| [@Bug0x](https://t.me/s/Bug0x) | 5.3K | Writeups, courses, tools, checklists | RCE writeups, file upload checklist, CVE scanners |

---

## HIGH-VALUE RESOURCES BY CATEGORY

### RECON & CRAWLING
- **Hakrawler** — Ultra-fast web crawler (GitBook_s: `hakrawler1.pdf`, `hakrawler2.pdf`)
- **OWASP ZAP 2026 Setup** — 12 steps, Docker, GitHub Actions (GitBook_s)
- **URL Contexts** — href, src, javascript: bridge (GitBook_s: `url.tg@gitbook_s.pdf`)
- **CSP Recon** — Reading policies like a hunter (GitBook_s: `csp-recon.tg@gitbook_s.pdf`)
- **Awesome Mobile Security** — Android/iOS repo list (pentestandroid: `vaib25vicky/awesome-mobile-security`)
- **KeyHacks** — Verify leaked API keys (pentestandroid: `streaak/keyhacks`)
- **RegExAPI** — Regex patterns for OAuth/API tokens (pentestandroid: `odomojuli/RegExAPI`)

### VULN CLASS CHEATSHEETS / CHECKLISTS
- **100 Web Vulnerabilities Categorized** (bugbountyresources #1064) — Injection, Auth, Data Exposure, Misconfig, XXE, Broken Access Control, Deserialization, API, Crypto, Client-Side, DoS, Other, Mobile, IoT, WoT, Auth Bypass, SSRF, Content Spoofing, Business Logic, Zero-Day
- **IDOR Checklist** (bugbountyresources #1071: `IDOR.pdf`)
- **2FA Bypass** (bugbountyresources #1072: `2FA Bypass.pdf`)
- **Reset Password Checklist** (bugbountyresources #1073)
- **File Upload Cheatsheet** (bugbountyresources #1076: `File Upload Cheatsheet.pdf`)
- **AEM Misconfiguration** (bugbountyresources #1077)
- **Jira Vulnerability Checklist** (bugbountyresources #1078)
- **Admin Panel Bypass** (bugbountyresources #1079)
- **Business Logic Error Cheatsheet** (bugbountyresources #1075)
- **Secure Coding Practice Checklist** (bugbountyresources #1080)
- **Malicious File Upload Checklist** (Bug0x: `aacle.notion.site/Malicious-File-Upload-Checklist`)

### BYPASS TECHNIQUES
- **IDN Homograph → Account Collision** (brutsecurity #3016) — Unicode in email/username fields, test normalization at every stage
- **403/401 Bypass** (brutsecurity #3017, #3025: `iamj0ker/bypass-403`)
- **HTTP/2 WAF Bypass** (bugxplorer #4075: `lab.ctbb.show/research/h2-WAF-Bypasses`)
- **postMessage targetOrigin bypass via IP normalization** (bugxplorer #4082)
- **DOMPurify Attack Classes & Bypass History** (bugxplorer #4084: `cure53/DOMPurify/wiki`)
- **CSS Injection: "The Bomb Inside Your Inbox"** (bugxplorer #4088: PortSwigger research)
- **SSL Pinning Bypass (Android/iOS)** — Frida universal bypass (pentestandroid #5, #11, #16: `Bypassing SSL pinning using Frida.pdf`, `Ultimate_Guide_to_SSL_Pinning_Bypass_RedHunt_Labs.pdf` 37MB)
- **Google Maps API Key Restrictions Bypass** (pentestandroid #14)

### TOOLS & SCANNERS
- **HackTools** — All-in-one RedTeam browser extension (brutsecurity #3023: `LasCC/Hack-Tools`)
- **bypass-403** — Simple 403 bypass script (brutsecurity #3025: `iamj0ker/bypass-403`)
- **geminiHunter** — Hunt exposed Gemini API keys in JS, Wayback, APKs (brutsecurity #3032: `devploit/geminiHunter`)
- **APKLeaks** — Scan APK for URIs, endpoints, secrets (bugbountyresources #1084: `dwisiswant0/apkleaks`)
- **SQL Wordlist** (bugbountyresources #1082: `orwagodfather/SQL-Wordlist`)
- **CVE-2024-38856 Scanner** — Apache OFBiz RCE (Bug0x #172: `securelayer7/CVE-2024-38856_Scanner`)
- **Shuriken** — Android kernel tooling (Bug0x #158: `0xdarkvortex.dev/shuriken`)

### SECRET / CREDENTIAL HUNTING
- **One Regex for All Leaked Keys/Secrets** (brutsecurity #3020, bugbountyresources #1081: `gist.github.com/h4x0r-dz/be69c7533075ab0d3f0c9b97f7c93a59`)
- **KeyHacks** — Quick validation of leaked keys (pentestandroid #6)
- **RegExAPI** — OAuth/API token patterns (pentestandroid #9)

### MOBILE PENTESTING
- **InsecureBankv2 Walkthrough** (pentestandroid #12: Parts 1-3)
- **Android Apps Exploitation Slides** (pentestandroid #13: Google Docs)
- **Android Hacking Fundamentals** (pentestandroid #17)
- **iOS Pentesting Resources** (pentestandroid #18: Cobalt, Corellium, HackTricks, Mobexler, Nviso)
- **B3nac/Android-Reports-and-Resources** — H1 disclosed Android reports (pentestandroid #8)

### WRITEUPS / CASE STUDIES
- **Rate Limit Bypass → 0-Click ATO** (Bug0x #166: `zeroxuf.medium.com`)
- **Two RCEs at EPAM** (Bug0x #167: `0xbartita.medium.com`)
- **$3300 with FFUF** (Bug0x #169: `bit.ly/3300bucks-ffuf`)
- **RCE in Bugcrowd Program** (Bug0x #171: `yousefmoh15.medium.com`)
- **Reverse Engineering Browser Extension → $25k** (Bug0x #177: `theindiannetwork.medium.com`)
- **Chrome Behavior → ATO** (Bug0x #179: YouTube `Pi37YwraPBg`)
- **Click2Shell — WordPress Preauth RCE** (brutsecurity #3021: `pwn.ai/blog/click2shell`)
- **Ni8mare — n8n Unauth RCE (CVE-2026-21858)** (brutsecurity #3026)

### WORDLISTS / REFERENCE
- **SQL Wordlist** (bugbountyresources #1082: `github.com/orwagodfather/SQL-Wordlist/blob/main/sql.txt`)
- **Secret Regex Gist** (brutsecurity #3020)
- **HTTP Headers Every Hunter Should Know** (GitBook_s: `http-headers.tg@gitbook_s.pdf`)
- **Regex for Bug Bounty** (GitBook_s: `regex.tg@gitbook_s.pdf`, `re.cheatsheet.tg@gitbook_s.pdf`)
- **AWK One-Liners** (GitBook_s: `awk.tg@gitbook_s.pdf`)
- **grep Mastery** (GitBook_s: `grep.tg@gitbook_s.pdf`)

### LEARNING / COURSES
- **Bug Bounty Guide 2026** (brutsecurity coupon: `topmate.io/saumadip/2187710?coupon_code=awaw`)
- **Zero to Mobile Pentester** (brutsecurity coupon: `topmate.io/saumadip/2272794?coupon_code=sada`)
- **Brut Offensive Playbook v1** (brutsecurity coupon: `topmate.io/saumadip/2054509?coupon_code=dada`)
- **Claude for Bug Bounty Series** (bugbountyresources #1066)
- **NahamSec Training** (Bug0x references: `bugbounty.nahamsec.training`)

---

## INTEGRATION NOTES FOR SKILLS

### bb-methodology
- Add IDN homograph account collision to "What-If experiments" (developer psychology)
- Add HTTP/2 WAF bypass to "Tactical Thinking → Environment diff"
- Add postMessage IP normalization to "Critical Thinking → Question trust boundaries"

### bountyforge
- Add geminiHunter to credential leak hunting tools
- Add bypass-403 and HackTools to WAF bypass toolkit
- Add mobile pentest resources (InsecureBankv2, SSL pinning bypass PDFs) to mobile section
- Add CVE-2024-38856 scanner to supply chain / known CVE exploitation
- Add DOMPurify bypass history to XSS bypass tables
- Add CSS injection (PortSwigger) to CSS injection class

### web2-vuln-classes
- **IDOR**: Add InsecureBankv2 walkthrough as mobile IDOR example
- **XSS**: Add DOMPurify bypass history, CSS injection research, postMessage bypass
- **Auth Bypass**: Add 2FA bypass checklist, reset password checklist
- **SSRF**: Add geminiHunter for API key exposure leading to SSRF
- **File Upload**: Add malicious file upload checklist, AEM misconfig
- **Business Logic**: Add IDN homograph account collision, rate limit bypass → ATO chain
- **Mobile**: Add SSL pinning bypass (Frida), Android/iOS resource lists
- **API Security**: Add KeyHacks, RegExAPI for token validation

### offensive-osint
- Add geminiHunter for AI API key discovery
- Add Hakrawler for ultra-fast crawling
- Add KeyHaks for credential validation

### recon-and-osint
- Add CSP recon guide
- Add URL contexts guide
- Add secret regex for credential discovery

---

## DEDUPLICATION CHECKLIST (vs Existing Skills)

- [ ] IDOR tips (#79, #83, #87) — merge with bb-methodology IDOR section
- [ ] SQLi tips (#78, #84) — merge with web2-vuln-classes SQLi
- [ ] XSS tips (#77, #80, #81, #86) — merge with web2-vuln-classes XSS
- [ ] Business Logic tips (#80, #85, #89) — merge with web2-vuln-classes Business Logic
- [ ] Enum tips (#82, #88) — merge with web2-vuln-classes Auth/ATO
- [ ] 100 Vuln Categories — cross-ref with web2-vuln-classes 26 classes
- [ ] All PDFs — index by vuln class, add to relevant skill reference files
- [ ] Mobile resources — integrate into web2-vuln-classes mobile section (currently sparse)
- [ ] Bypass techniques — add to web2-vuln-classes bypass tables

---

## NEXT ACTIONS

1. **Download PDFs** from t.me links (requires Telegram login or bot)
2. **Parse PDF content** for actionable techniques
3. **Update skill reference files** with new bypasses, tools, checklists
4. **Create hunting playbooks** for high-value chains (e.g., IDN homograph → ATO, rate limit → ATO, SSL bypass → mobile API access)