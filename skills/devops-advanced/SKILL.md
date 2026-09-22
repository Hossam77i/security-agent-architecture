---
name: devops-advanced
description: Use for Kubernetes, GitOps, advanced Terraform, DevSecOps, zero-downtime, observability. Triggers on kubernetes deploy, gitops, argocd, helm, terraform workspace, k8s security, blue-green, canary.
---

# DevOps Advanced — Production K8s + GitOps + DevSecOps at Scale

## 0. Objective
Run EKS prod with GitOps, signed images, policy-guarded deploys, SLO burn-rate alerts, and zero-downtime DB-safe releases. Survive pod kill, AZ loss, bad deploy without paging customers.

## 1. Kubernetes production spec (EKS)
Deployment baseline:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: api, labels: { app: api } }
spec:
  replicas: 3
  strategy:
    rollingUpdate: { maxSurge: 1, maxUnavailable: 0 }
    type: RollingUpdate
  template:
    spec:
      serviceAccountName: api-irsa
      securityContext: { runAsNonRoot: true, runAsUser: 10000, fsGroup: 10000, seccompProfile: { type: RuntimeDefault } }
      containers:
      - name: api
        image: 123456789012.dkr.ecr.eu-west-1.amazonaws.com/api@sha256:<digest>
        ports: [{ containerPort: 3000 }]
        readinessProbe: { httpGet: { path: /health, port: 3000 }, periodSeconds: 5 }
        livenessProbe: { httpGet: { path: /health, port: 3000 }, periodSeconds: 15 }
        resources: { requests: { cpu: 250m, memory: 256Mi }, limits: { cpu: 1000m, memory: 512Mi } }
        lifecycle: { preStop: { exec: { command: ["sh","-c","sleep 15"] } } }
        env: [{ name: PORT, value: "3000" }]
```
- HPA on CPU 60% + custom p95 >500ms (KEDA/Prometheus adapter). PDB `minAvailable: 2` for 3 replicas. Topology spread across AZs.
- IRSA: ServiceAccount annotates `eks.amazonaws.com/role-arn`, no node-wide AWS creds. RBAC: CI gets `role-deployer` (deploy in ns only), devs `view`, on-call `admin` via SSO.
- Secrets: External Secrets Operator syncs AWS Secrets Manager -> K8s Secret, rotation every 30d. Never plain Secret YAML in git unencrypted.
- Helm: `Chart.yaml` version pinned, `values-dev.yaml`/`values-prod.yaml`, `helm lint && helm template . -f values-prod.yaml | kubeconform`. Or Kustomize overlays if team hates templating.

Ops:
```bash
kubectl rollout status deploy/api -n prod
kubectl describe pod -l app=api -n prod | tail -80
stern -n prod api --since 5m | head -200
kubectl top pods -n prod
kubectl auth can-i create deploy --as=system:serviceaccount:ci:deployer -n prod
```

Lab 1: deploy 3-replica API with probes+HPA+PDB, `kubectl delete pod` -> zero 5xx on `k6` smoke, `kubectl rollout undo` works.

## 2. GitOps (ArgoCD) done right
- Repo layout: `apps/api/overlays/prod` (Kustomize) or `charts/api`. Argo Application per env, app-of-apps root.
- Sync: auto-sync + prune ON for dev, manual approve for prod (require `argocd app sync prod/api` + Slack approval). selfHeal ON, `retryLimit 3`.
- Image Updater pinned to digest, only `main` branch, allowlist `api` image. Every sync = commit SHA visible in Argo UI + Slack.
- Drift: `argocd app diff` in CI fails PR if live vs git diverges unexpectedly.

## 3. Terraform advanced — envs without copy-paste
- Choose workspaces for simple OR Terragrunt `live/dev|staging|prod` for real teams. DRY modules: `modules/vpc`, `modules/eks`, `modules/ecr`.
- State per env: `s3://tfstate/prod/eks.tfstate`, DynamoDB lock. `terraform plan -detailed-exitcode` nightly cron -> Slack if drift (exit 2).
- Policy as code: `conftest` + OPA `deny public S3`, `deny *: * IAM`, `require tags`. `tflint --init`, `tfsec`, `checkov`.
- Import safely: `terraform import aws_ecr_repository.api api`, then `plan` empty. Move: `terraform state mv old new`, never hand-edit state JSON.

## 4. Zero-downtime releases + DB safety
- App: `/health` fails during shutdown drain, `preStop sleep 15` + ALB dereg 30s + `terminationGracePeriodSeconds: 60`.
- Strategy: RollingUpdate first, Canary (Argo Rollouts 10% -> 50% -> 100% with analysis on 5xx/p95) for risky, Blue-Green only for schema-incompatible frontend.
- DB expand-contract: migration 1 adds nullable column + dual-write, deploy, backfill job, migration 2 makes NOT NULL + drops old. Rollback = deploy previous image, no down-migration on prod data. Test restore: `pg_restore` to scratch weekly.

## 5. Observability — SLOs not CPU graphs
- Stack: Prometheus + Grafana (or CloudWatch Container Insights), Loki/CloudWatch Logs JSON, Tempo/X-Ray traces via OpenTelemetry (Python `opentelemetry-instrumentation-fastapi`, Node `@opentelemetry/auto-instrumentations-node`).
- RED per service: Rate/Errors/Duration p50/p95/p99. USE per node. SLO: 99.9% 28d (43m budget), alerts on burn 14x fast / 6x slow, not `CPU>80%`.
- Runbooks linked in alert: `kubectl rollout restart`, `helm rollback api 3`, DB failover steps. Game day monthly: kill AZ (cordon), expire secret, fill disk.

## 6. DevSecOps gates
Pipeline: SAST (Semgrep) -> SCA (`npm audit`, `pip-audit`) -> build -> Trivy HIGH/CRITICAL block -> sign (`cosign sign --key awskms://... $DIGEST`) -> verify in cluster (Kyverno `verifyImages`) -> deploy.
Kyverno baseline (deny root, require limits/probes, require digest, default-deny NetworkPolicy):
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: require-basics }
spec:
  validationFailureAction: Enforce
  rules:
  - name: no-root
    match: { resources: { kinds: [Pod] } }
    validate:
      message: runAsNonRoot required
      pattern: { spec: { securityContext: { runAsNonRoot: true } } }
```
- NetworkPolicy default-deny + allow DNS + ALB -> api + api -> db/redis only. `kube-bench` CIS, `kube-hunter` quarterly. Secrets rotation drill.

## 7. Troubleshooting
| Symptom | Fix |
|---|---|
| CrashLoopBackOff | `kubectl logs --previous`, probe path wrong, OOM (raise limit, check `dmesg`), bad env |
| ImagePullBackOff | ECR policy/IRSA, digest typo, PrivateLink missing |
| HPA thrash | stabilizationWindow 300s, raise request to match p50, check p95 not CPU only |
| Argo OutOfSync loop | ignore `replicas` (HPA owns), `ignoreDifferences` for webhook timestamps |
| TF `Error acquiring lock` | confirm no apply, `force-unlock`, DynamoDB `LockID` inspection |
| 5xx on deploy | preStop too short, readiness gate missing, migration not backward-compat |

## 8. Graduation project
EKS dev+prod via Terraform, ArgoCD sync, signed canary release with analysis, SLO dashboard + burn alerts, Kyverno Enforce, kill-pod/AZ drill report. Done when: bad image auto-halted at 10% canary, `cosign verify` enforced, drift alert fires in <1h, rollback <5 min with runbook.
Anti-patterns: `kubectl edit` prod, cluster-admin CI, public ECR, unversioned chart, migration without expand-contract.
