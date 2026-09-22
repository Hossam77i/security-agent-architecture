# COMPLETE HANDS-ON TRAINING GUIDE — 44-STEP MASTER PLAN
> User's full curriculum mapped to unified skills, resources, labs, and progression | 2026-09-22

---

## USER'S FULL CURRICULUM (44 STEPS)

### PHASE 1: WEB APPLICATION SECURITY (Steps 1-7)
| # | Target | Status | Unified Skills | Primary Resources |
|---|--------|--------|----------------|-------------------|
| 1 | **OWASP Juice Shop** | ✅ COMPLETED | All web skills | https://github.com/juice-shop/juice-shop |
| 2 | **DVWA** | 🔲 | SQLI, XSS, FILE_UPLOAD, AUTH_BYPASS, IDOR | https://github.com/digininja/DVWA |
| 3 | **OWASP WebGoat** | 🔲 | All web skills (guided) | https://github.com/WebGoat/WebGoat |
| 4 | **OWASP crAPI** | 🔲 | API_SECURITY, OAUTH_OIDC, AUTH_BYPASS | https://github.com/OWASP/crAPI |
| 5 | **VAmPI** | 🔲 | API_SECURITY, AUTH_BYPASS, MASS_ASSIGNMENT | https://github.com/erev0s/VAmPI |
| 6 | **WebSploit Labs** | 🔲 | All web skills | https://github.com/WebSploit/WebSploit |
| 7 | **OWASP VWAD** | 🔲 | All (directory of vuln apps) | https://github.com/OWASP/VWAD |

### PHASE 2: MOBILE APPLICATION SECURITY (Steps 8-18)
| # | Target | Status | Unified Skills | Primary Resources |
|---|--------|--------|----------------|-------------------|
| 8 | **Mobile App Sec Fundamentals** | 🔲 | MOBILE_PENTESTING | OWASP MASVS/MASTG |
| 9 | **Android Security Labs** | 🔲 | MOBILE_PENTESTING | https://github.com/asvid/Android-Security-Labs |
| 10 | **iOS Security Fundamentals & Labs** | 🔲 | MOBILE_PENTESTING | https://github.com/OWASP/iGoat |
| 11 | **OWASP MASTG** | 🔲 | MOBILE_PENTESTING (methodology) | https://github.com/OWASP/owasp-mstg |
| 12 | **OWASP MASVS** | 🔲 | MOBILE_PENTESTING (requirements) | https://github.com/OWASP/owasp-masvs |
| 13 | **Android Reverse Engineering Labs** | 🔲 | MOBILE_PENTESTING | https://github.com/AndroBugs/InsecureApp |
| 14 | **Mobile API & Backend Security** | 🔲 | MOBILE_PENTESTING + API_SECURITY | crAPI, VAmPI |
| 15 | **Mobile Auth & Authorization** | 🔲 | MOBILE_PENTESTING + AUTH_BYPASS | InsecureBankv2, DIVA |
| 16 | **Mobile Storage, Crypto & IPC** | 🔲 | MOBILE_PENTESTING | InsecureBankv2, DIVA, MSTG |
| 17 | **Mobile Network Security** | 🔲 | MOBILE_PENTESTING + SSRF | Frida SSL bypass, mitmproxy |
| 18 | **Mobile Binary/Native Code Analysis** | 🔲 | MOBILE_PENTESTING | Ghidra, JADX, Frida, radare2 |

### PHASE 3: WEB3 / SMART CONTRACT SECURITY (Steps 19-30)
| # | Target | Status | Unified Skills | Primary Resources |
|---|--------|--------|----------------|-------------------|
| 19 | **Web3 Security Fundamentals** | 🔲 | Web3 skills (web3-* skills) | https://github.com/patdoyle/SmartContractSecurity |
| 20 | **Solidity Security Labs** | 🔲 | web3-solidity-audit, web3-bug-classes | https://github.com/crytic/slither |
| 21 | **Smart Contract Vulnerability Labs** | 🔲 | web3-bug-classes, web3-hunt-foundation | https://github.com/crytic/echidna |
| 22 | **Ethereum Security Labs** | 🔲 | web3-*, web3-hunt-zksync-era | https://github.com/trailofbits/eth-security-toolbox |
| 23 | **DeFi Security Labs** | 🔲 | web3-bug-classes, web3-case-study | https://github.com/sunsec/DeFi-Attack |
| 24 | **Web3 Auth & Wallet Security** | 🔲 | web3-auth, web3-wallet | https://github.com/ethereum/EIPs |
| 25 | **Smart Contract Auditing** | 🔲 | web3-solidity-audit-mcp, web3-start-here | https://github.com/trailofbits/publications |
| 26 | **Smart Contract Source-Code Analysis** | 🔲 | web3-grep-arsenal, sast-* | Slither, Mythril, Foundry |
| 27 | **Blockchain Transaction & State Analysis** | 🔲 | web3-hunt-foundation | https://github.com/ethereum/go-ethereum |
| 28 | **Cross-Contract/Protocol Interaction** | 🔲 | web3-bug-classes, vulnerability-chaining | Foundry, Hardhat, Tenderly |
| 29 | **Web3 Business Logic & Economic Security** | 🔲 | web3-bug-classes, web3-case-study | DeFi attack vectors |
| 30 | **Historical Smart Contract Vuln Labs** | 🔲 | web3-case-study-role-misconfig | https://github.com/sunsec/DeFi-Attack |

### PHASE 4: SOURCE CODE REVIEW & CVE REPRODUCTION (Steps 31-35)
| # | Target | Status | Unified Skills | Primary Resources |
|---|--------|--------|----------------|-------------------|
| 31 | **Source-Code Vulnerability Analysis** | 🔲 | sast-*, web2-vuln-classes | CodeQL, Semgrep, SonarQube |
| 32 | **Secure Code Review Labs** | 🔲 | sast-*, securecoder-* | OWASP Code Review Guide |
| 33 | **Historical CVE Reproduction Labs** | 🔲 | web2-vuln-classes, vulnerability-chaining | https://github.com/ARPSyndicate/cvemon |
| 34 | **CyberGym** | 🔲 | pentest-engagement, pentest-* | https://cybergym.io/ |
| 35 | **CyberGym-E2E** | 🔲 | pentest-engagement (full chain) | https://cybergym.io/ |

### PHASE 5: ADVANCED RESEARCH & CHAINING (Steps 36-44)
| # | Target | Status | Unified Skills | Primary Resources |
|---|--------|--------|----------------|-------------------|
| 36 | **Advanced Multi-Step Vuln Chains** | 🔲 | vulnerability-chaining, bb-methodology | H1 disclosed chains |
| 37 | **Cross-Domain Vulnerability Research** | 🔲 | vulnerability-chaining, bb-methodology | Cross-platform bugs |
| 38 | **Novel Vulnerability Research Labs** | 🔲 | bb-methodology, bountyforge | 0-day research |
| 39 | **Hidden Holdout Labs** | 🔲 | bb-methodology, bountyforge | Blind spots |
| 40 | **Cross-Environment Generalization** | 🔲 | bb-methodology, pentest-engagement | Multi-env testing |
| 41 | **Mixed-Domain Security Challenges** | 🔲 | vulnerability-chaining | Web+Mobile+Cloud+Web3 |
| 42 | **Adaptive Weakness-Driven Training** | 🔲 | bb-methodology (What-If) | Adaptive learning |
| 41 | **Continuous Evaluation & Self-Improvement** | 🔲 | triage-validation, report-writing | Metrics-driven |
| 44 | **Research-to-Responsible-Disclosure Sim** | 🔲 | report-writing, triage-validation | Full disclosure flow |

---

## DOCKER QUICK-START FOR ALL WEB TARGETS (Steps 1-7)

```bash
# Core web apps (run simultaneously)
docker run -d -p 3000:3000 bkimminich/juice-shop              # 1. Juice Shop (DONE)
docker run -d -p 8080:80 vulnerables/web-dvwa                # 2. DVWA
docker run -d -p 8082:8082 -p 9090:9090 webgoat/goatandwolf  # 3. WebGoat + WebWolf
docker run -d -p 8888:8888 cr-api/crapi                       # 4. crAPI
docker run -d -p 5000:5000 erev0s/vampi                       # 5. VAmPI
docker run -d -p 9000:9000 web-sploit/labs                    # 6. WebSploit Labs

# VWAD - download the directory index
git clone https://github.com/OWASP/VWAD ~/VWAD
```

---

## MOBILE SETUP (Steps 8-18)

### Android Lab Setup
```bash
# 1. Start emulator
nohup ~/Android/Sdk/emulator/emulator -avd pixel_api_33 -no-snapshot-load > /dev/null 2>&1 &

# 2. Wait for boot, then install apps
adb install ~/Downloads/InsecureBankv2.apk          # Step 15, 16
adb install ~/Downloads/DIVA.apk                    # Step 9, 13, 16
adb install ~/Downloads/InsecureApp.apk             # Step 13

# 3. Frida setup (preinstalled on INE VMs)
pip install frida-tools objection
frida-ps -U
```

### iOS Lab Setup (macOS or Corellium)
```bash
# Corellium cloud (recommended for iOS)
# https://www.corellium.com/ - rent iOS device

# Or local macOS with Xcode
# Install iGoat, SwiftShield via Xcode
```

### Mobile Tools (all preinstalled on INE VMs)
```bash
# Static analysis
jadx -d ~/jadx_out app.apk
apktool d app.apk -o ~/apk_out

# Dynamic analysis
objection -g com.app explore
frida -U -f com.app -l ~/scripts/ssl_bypass.js --no-pause

# Automated scanning
pip install mobsf
mobsf scan app.apk
```

---

## WEB3 / SMART CONTRACT SETUP (Steps 19-30)

### Foundry + Hardhat + Slither
```bash
# Foundry (fastest for testing)
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Hardhat (standard)
npm init -y && npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox

# Slither (static analysis)
pip install slither-analyzer

# Echidna (fuzzing)
# Download binary from https://github.com/crytic/echidna/releases

# Mythril (symbolic execution)
pip install mythril

# Tenderly (debugging) - web UI
# https://tenderly.co/
```

### Web3 Practice Repos
```bash
# Solidity Security Labs
git clone https://github.com/crytic/slither && cd slither && make

# DeFi Attack Vectors
git clone https://github.com/sunsec/DeFi-Attack

# Ethereum Security Toolbox
docker run -it trailofbits/eth-security-toolbox

# Smart Contract Vulnerability Labs
git clone https://github.com/patdoyle/SmartContractSecurity

# Cross-Contract Testing
git clone https://github.com/foundry-rs/foundry
# forge test --fork-url $RPC_URL
```

---

## SOURCE CODE REVIEW SETUP (Steps 31-33)

### SAST Tools
```bash
# CodeQL (GitHub's engine)
# https://github.com/github/codeql-cli-binaries/releases
codeql database create mydb --language=javascript
codeql query run query.ql --database=mydb

# Semgrep (fast, rules-based)
pip install semgrep
semgrep --config=auto /path/to/code

# SonarQube (comprehensive)
docker run -d -p 9000:9000 sonarqube:latest

# Gosec (Go)
go install github.com/securego/gosec/v2/cmd/gosec@latest

# Bandit (Python)
pip install bandit
bandit -r /path/to/code

# Gosec (Go)
go install github.com/securego/gosec/v2/cmd/gosec@latest
```

### CVE Reproduction
```bash
# cvemon - CVE monitoring
go install github.com/ARPSyndicate/cvemon/cmd/cvemon@latest
cvemon -k "CVE-2024-38856" -t "RCE"

# Vulhub - vulnerable docker environments
git clone https://github.com/vulhub/vulhub
cd vulhub/activemq/CVE-2023-46604 && docker-compose up -d

# CVE-2024-38856 (Apache OFBiz)
cd vulhub/ofbiz/CVE-2024-38856 && docker-compose up -d

# CVE-2025-24813 (Spring)
cd vulhub/spring/CVE-2025-24813 && docker-compose up -d
```

---

## CYBERGYM SETUP (Steps 34-35)

```bash
# CyberGym - requires account
# https://cybergym.io/
# Offers: web, mobile, cloud, AD, network labs

# CyberGym-E2E - full engagement simulation
# Requires subscription
```

---

## ADVANCED RESEARCH SETUP (Steps 36-44)

### Vulnerability Chaining Framework
```bash
# Create chaining workspace
mkdir -p ~/research/chains/{web,mobile,cloud,web3,cross-domain}
cd ~/research/chains

# Document each chain
# Format: vuln1 -> vuln2 -> impact
```

### Novel Research Tools
```bash
# Fuzzing
pip install aflplusplus
git clone https://github.com/AFLplusplus/AFLplusplus

# Symbolic execution
pip install angr
# angr for binary analysis

# Custom research
# Build your own: grammar-based fuzzer, differential testing, etc.
```

---

## MAPPING: YOUR 44 STEPS → UNIFIED SKILLS

| Step Range | Primary Unified Skills | Secondary Skills |
|------------|----------------------|------------------|
| 1-7 (Web) | All 13 web unified skills | bb-methodology, bountyforge |
| 8-18 (Mobile) | MOBILE_PENTESTING_UNIFIED | API_SECURITY, SSRF, AUTH_BYPASS |
| 19-30 (Web3) | web3-* skills (10 skills) | sast-*, vulnerability-chaining |
| 31-33 (Code Review) | sast-*, web2-vuln-classes | CodeQL, Semgrep, securecoder-* |
| 34-35 (CyberGym) | pentest-engagement, pentest-* | All skills (full engagement) |
| 36-44 (Research) | vulnerability-chaining, bb-methodology, bountyforge | All skills |

---

## PROGRESSION TRACKER

### Phase Completion Criteria

| Phase | Criteria | Est. Time |
|-------|----------|-----------|
| **Phase 1: Web** | All 7 apps → can chain 3+ vulns for Critical | 4-6 weeks |
| **Phase 2: Mobile** | InsecureBankv2 + DIVA 100% + MSTG coverage | 4-6 weeks |
| **Phase 3: Web3** | 20+ Slither findings, 5+ DeFi exploits, 1 audit report | 6-8 weeks |
| **Phase 4: Code Review** | 10+ CodeQL/Semgrep custom rules, 3 CVE repros | 4-6 weeks |
| **Phase 5: Research** | 3+ novel chains documented, 1 responsible disclosure | Ongoing |

---

## DAILY EXECUTION TEMPLATE

```markdown
## YYYY-MM-DD — Phase X, Step Y

### Target: [App/Lab Name]
### Time: [X] hours

### Pre-Req Check
- [ ] Environment running (docker/adb/emulator)
- [ ] Unified skill loaded (skill name)
- [ ] Quick-start test plan reviewed

### Execution
**Recon (15 min)**
- Endpoints/entry points:
- Tech stack:
- Unified skill quick-start:

**Exploitation (60-90 min)**
- Vuln class:
- Payload/bypass used:
- Chain potential:
- Proof (screenshot/log):

**Post-Exploitation (15 min)**
- Triage: 7Q Gate PASS/FAIL
- 4 Gates: □□□□
- Chain documented: YES/NO

### Next Session
- [ ] Next sub-step:
- [ ] Chain with:
- [ ] Writeup to read:
```

---

## WEEKLY REVIEW METRICS

| Metric | Target | This Week |
|--------|--------|-----------|
| Steps completed | 2-3 | |
| Unified skills practiced | 5+ | |
| Chains documented | 2+ | |
| Writeups studied | 5+ | |
| Custom tools/scripts written | 1+ | |
| CVE reproduced | 1 | |
| Responsible disclosure drafted | 0-1 | |

---

## RESOURCE INDEX (Quick Links)

### Web Apps
- Juice Shop: https://github.com/juice-shop/juice-shop
- DVWA: https://github.com/digininja/DVWA
- WebGoat: https://github.com/WebGoat/WebGoat
- crAPI: https://github.com/OWASP/crAPI
- VAmPI: https://github.com/erev0s/VAmPI
- WebSploit: https://github.com/WebSploit/WebSploit
- VWAD: https://github.com/OWASP/VWAD

### Mobile
- InsecureBankv2: https://github.com/dineshshetty/Android-InsecureBankv2
- DIVA: https://github.com/payatu/diva-android
- MASTG: https://github.com/OWASP/owasp-mstg
- MASVS: https://github.com/OWASP/owasp-masvs
- iGoat: https://github.com/OWASP/iGoat
- Android-Security-Labs: https://github.com/asvid/Android-Security-Labs

### Web3
- SmartContractSecurity: https://github.com/patdoyle/SmartContractSecurity
- slither: https://github.com/crytic/slither
- echidna: https://github.com/crytic/echidna
- eth-security-toolbox: https://github.com/trailofbits/eth-security-toolbox
- DeFi-Attack: https://github.com/sunsec/DeFi-Attack
- Foundry: https://github.com/foundry-rs/foundry
- Hardhat: https://hardhat.org/

### Code Review
- CodeQL: https://github.com/github/codeql-cli-binaries
- Semgrep: https://github.com/returntocorp/semgrep
- sast-* skills in opencode

### CVE Reproduction
- vulhub: https://github.com/vulhub/vulhub
- cvemon: https://github.com/ARPSyndicate/cvemon

### CyberGym
- https://cybergym.io/

### Research
- H1 Disclosed: https://github.com/ajaysenr/HackerOne-Disclosed-Reports
- vulnerability-chaining skill
- bb-methodology skill