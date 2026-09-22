---
name: devops-intermediate
description: Use when building real CI/CD, Docker Compose, Terraform basics, AWS ECR/ECS, monitoring. Triggers on docker compose, terraform init, github actions pipeline, ECR push, CI caching, deploy staging.
---

# DevOps Intermediate — Multi-Service + Real Pipelines + IaC

## 0. Objective
Ship a frontend + API + Postgres stack with one `docker compose up`, CI that lints/tests/scans/pushes to ECR, Terraform for ECR/ECS basics, and CloudWatch visibility. No snowflakes, no click-ops.

## 1. Docker Compose production patterns
`compose.yml`:
```yaml
services:
  api:
    build: ./api
    ports: ["3000:3000"]
    env_file: [.env]
    depends_on:
      db: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]
      interval: 10s
      retries: 3
    deploy: { resources: { limits: { cpus: "1", memory: 512M } } }
  web:
    build: ./web
    ports: ["5173:5173"]
    depends_on: [api]
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD:?set DB_PASSWORD}
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 10
volumes: { pgdata: {} }
```
- `docker compose up --build`, `docker compose logs -f api`, `docker compose exec db psql -U postgres`
- Profiles: `profiles: [test]` for ephemeral test DB. Override: `compose.override.yml` for local ports.
- Multi-stage build example (Node):
```dockerfile
FROM node:20-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . ./ && npm run build
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev && useradd -m appuser
COPY --from=build /app/dist ./dist
USER appuser
CMD ["node", "dist/server.js"]
```
Cuts image 70%+. Scan: `trivy image myapp:dev --severity HIGH,CRITICAL --exit-code 1`.

Lab 1: compose stack with healthchecks, `docker compose down -v` then up clean, `curl` all health endpoints green.

## 2. GitHub Actions — matrix, OIDC, SBOM, ECR
`.github/workflows/pipeline.yml`:
```yaml
name: pipeline
on: { push: {}, pull_request: {} }
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
jobs:
  test:
    strategy: { matrix: { node: [20, 22], python: ["3.11", "3.12"] } }
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: ${{ matrix.node }}, cache: npm }
      - uses: actions/setup-python@v5
        with: { python-version: ${{ matrix.python }}, cache: pip }
      - run: npm ci && npm run lint && npm test
      - run: pip install -r requirements.txt && ruff check . && pytest -q
  scan-push:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with: { role-to-assume: arn:aws:iam::123456789012:role/gha-ecr-push, aws-region: eu-west-1 }
      - uses: aws-actions/amazon-ecr-login@v2
      - run: docker build -t $ECR/api:${{ github.sha }} ./api
      - uses: aquasecurity/trivy-action@master
        with: { image-ref: $ECR/api:${{ github.sha }}, severity: HIGH,CRITICAL, exit-code: 1 }
      - run: docker push $ECR/api:${{ github.sha }}
      - uses: anchore/sbom-action@v0
        with: { image: $ECR/api:${{ github.sha }} }
```
- OIDC: no static AWS keys. IAM role trusts `token.actions.githubusercontent.com:sub repo:org/repo:*`.
- Cache: setup-node/npm + setup-python/pip cache, Docker layer cache via `docker/build-push-action` + `cache-from: type=gha`.
- Budget <15 min. Upload JUnit + coverage on failure.

Lab 2: add Trivy blocking, break build with vulnerable base (`node:16`), watch fail, bump to `node:20-slim`, green.

## 3. Terraform basics that don't hurt later
Layout:
```
infra/
  backend.tf  # S3 + DynamoDB lock
  providers.tf # pinned aws ~> 5.0
  variables.tf
  main.tf     # ecr + ecs + logs
  outputs.tf
```
`backend.tf`:
```hcl
terraform {
  backend "s3" {
    bucket         = "my-tfstate-123456"
    key            = "dev/terraform.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "tf-locks"
    encrypt        = true
  }
}
```
Flow: `terraform fmt -recursive && terraform validate && terraform plan -out=tfplan && terraform apply tfplan`. Never `apply` without plan in team. Pin providers, tag everything:
```hcl
tags = { Owner = "platform" Env = var.env CostCenter = "eng" }
```
Secrets: SSM `/dev/api/DB_PASSWORD` (SecureString), ECS `secrets` block, never `environment` plaintext. Check: `tflint`, `checkov -d infra/ --framework terraform`.

Lab 3: `terraform init/plan/apply` creates ECR repo, push image by digest, `terraform destroy` cleans. State in S3, lock works (two applies collide safely).

## 4. ECS delivery + observability
- ECS Fargate service 2 tasks, ALB health `/health`, deregistration 30s, deployment `ECS` rolling.
- Logs: awslogs to CloudWatch `/ecs/api-dev`, JSON lines with `requestId`, `latencyMs`. Dashboard: p95 latency, 5xx%, CPU/mem, ALB target health.
- Alarms: 5xx >1% 5m, p95 >800ms 10m, CPU >80% 15m -> SNS to Slack.
- SSM exec: `aws ecs execute-command --cluster dev --task <id> --container api --interactive --command sh` (no SSH).

## 5. Branching for teams
Trunk-based: short branches <2d, PR <400 lines, CODEOWNERS for `infra/` + `api/`, required `test` + `scan`, squash merge, auto-delete branch. Staging auto-deploy on main, prod manual `workflow_dispatch` with approver.

## 6. Troubleshooting
| Symptom | Fix |
|---|---|
| Compose DB not ready | `depends_on` healthy + retry loop in app, `pg_isready` healthcheck |
| OIDC `AccessDenied` | trust policy sub mismatch, `aud: sts.amazonaws.com`, role session name |
| ECR `denied: push` | `amazon-ecr-login` before build, repo URI region match |
| TF state lock stuck | `terraform force-unlock <ID>` after confirming no apply running, DynamoDB item check |
| Trivy HIGH blocks legit | pin base digest, `trivy --ignore-unfixed`, fix via bump not ignore |
| Pipeline 25 min | split jobs, cache GHA + Docker GHA cache, matrix only on PR not push |

## 7. Project + graduation
Project: full-stack todo (Vite + Express/FastAPI + Postgres) with compose, pipeline matrix+scan+ECR, Terraform ECR+logs, CloudWatch dashboard. Graduate when: compose cold-start <3 min documented, pipeline <15 min with SBOM, `terraform plan` clean on empty diff, dashboard shows p95 + errors, no static AWS keys anywhere.
Anti-patterns: `docker commit`, console edits, local tfstate in git, month-long dev branch, secrets in `environment`.
Next: devops-advanced (K8s, GitOps, zero-downtime).
