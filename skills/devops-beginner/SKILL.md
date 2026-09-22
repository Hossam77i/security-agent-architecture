---
name: devops-beginner
description: Use when starting DevOps - Linux, Bash, Git, YAML, Docker basics, GitHub Actions intro. Triggers on devops beginner, learn devops, what is CI/CD, dockerfile help, git workflow.
---

# DevOps Beginner — Zero to Shipping Containers + Green CI

## 0. Objective + prerequisites
Take a developer from 0 to: Linux-confident, Git-fluent, Docker-building, CI-green.
Prereqs: laptop with Docker Desktop or Linux + Docker Engine, GitHub account, Python 3.11+ OR Node 20+.
Success: you can clone a repo, run it in Docker, open a PR, watch CI go green, with zero secrets leaked.

## 1. Mental model (read this first)
DevOps = make the path from `git push` to `running in prod` boring, fast, and safe.
Three loops:
- Inner loop: edit -> run locally (Docker) -> test (<2 min)
- Outer loop: push -> CI (lint/test/build/scan) -> review -> merge (<15 min)
- Safety loop: everything in git, nothing by hand on servers, secrets never in repo.
If you SSH to fix prod by hand, the system failed — fix the pipeline, not the server.

## 2. Linux + Bash survival (30 commands that pay rent)
```bash
pwd && ls -la
cd /home/user && find . -maxdepth 2 -type f | head -20
grep -R "TODO" --include="*.py" .
df -h && free -h && uptime
ps aux | grep docker | head
env | sort | grep -E "PATH|HOME|AWS" | head
chmod 600 ~/.ssh/id_rsa && ssh -i ~/.ssh/id_rsa user@host
tail -100 /var/log/syslog 2>/dev/null || journalctl -n 100 --no-pager | head
```

Rules:
- Every script starts:
```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
```
- Quote vars: `"${MY_VAR}"`, never `$MY_VAR` naked. Default: `"${PORT:-3000}"`.
- Destructive commands need guard: `pwd`, `ls`, then act. Never `rm -rf /tmp/$VAR` — use `rm -rf "/tmp/${VAR:?unset}"`.
- SSH: key only, disable password. `ssh-keygen -t ed25519 -C "dev@laptop"`, add pub to GitHub/AWS.

Lab 1 (15 min): write `scripts/dev.sh` that checks docker, builds image, runs container, tails logs. Must exit non-zero on failure.

## 3. Git like a team (even solo)
```bash
git clone git@github.com:org/repo.git && cd repo
git checkout -b feat/health-endpoint
# edit ...
git status && git diff
git add -p && git commit -m "feat(api): add /health with version"
git push -u origin feat/health-endpoint
# open PR, wait green, squash-merge
git checkout main && git pull --rebase && git log --oneline -10
```
- Branch names: `feat/`, `fix/`, `chore/`, `docs/`. Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`.
- `.gitignore` must have: `.venv/`, `node_modules/`, `.env`, `*.tfstate*`, `.terraform/`, `dist/`, `*.log`.
- Never commit secrets. Pre-commit check:
```bash
git log -p | grep -iE "AKIA|BEGIN.*PRIVATE|password\s*=" | head && echo "LEAK?"
pipx install gitleaks && gitleaks detect --source . -v
```
- Undo safely: `git restore file`, `git reset --soft HEAD~1` (keep changes), never `push --force` to main.

Lab 2: create branch, break a test, push, watch CI red, fix, watch green. Screenshot both.

## 4. YAML without tears
- 2-space indent, no tabs. Lists with `- `, maps with `key: value`. Quote strings with `:` or `#`.
- Validate:
```bash
python3 -c "import yaml,sys; print(yaml.safe_load(open(sys.argv[1])))" .github/workflows/ci.yml
```
- Anchors for CI reuse (`&base` / `*base`) only when 3+ repeats — otherwise explicit is clearer.

## 5. Docker basics — build once, run anywhere
Production-ready starter Dockerfiles:

Python (FastAPI):
```dockerfile
FROM python:3.12-slim AS base
WORKDIR /app
RUN useradd -m appuser
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Node (Express):
```dockerfile
FROM node:20-slim AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . ./
RUN useradd -m appuser && chown -R appuser /app
USER appuser
EXPOSE 3000
CMD ["node", "server.js"]
```

`.dockerignore`:
```
.git
node_modules
.venv
.env
*.log
Dockerfile*
.github
```
Commands:
```bash
docker build -t myapp:dev .
docker run --rm -p 3000:3000 --env-file .env myapp:dev
docker ps && docker logs -f $(docker ps -q --filter ancestor=myapp:dev | head -1)
docker exec -it <id> sh
docker system prune -f  # reclaim space weekly
```
Pin versions (`python:3.12-slim`, `node:20.12-slim`), never `:latest` beyond local scratch. One process per container. Health endpoint `/health` returns 200 + `{"version":"0.1.0"}`.

Lab 3: dockerize a Python CLI that counts words in a file + a Node API with `/health`. Both must `docker build` clean with no warnings.

## 6. CI intro — GitHub Actions that actually helps
`.github/workflows/ci.yml`:
```yaml
name: ci
on:
  push:
  pull_request:
jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: "pip" }
      - uses: actions/setup-node@v4
        with: { node-version: "20", cache: "npm" }
      - run: pip install -r requirements.txt
      - run: npm ci
      - run: ruff check . || true
      - run: npx eslint . || true
      - run: pytest -q
      - run: npm test -- --passWithNoTests
      - run: docker build -t myapp:${{ github.sha }} .
```
Rules: cache deps, `concurrency: cancel-in-progress` on PRs, keep <10 min, required check `build-test` on main branch protection. Artifacts: upload test reports on failure (`if: failure()`).

Lab 4: push PR, make CI red (bad lint), fix, green. Enable branch protection requiring CI.

## 7. Env + Python/Node specifics
- `.env` local only. Commit `.env.example` with empty values + docs. Load via `python-dotenv` / `dotenv`.
- Python: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && pip freeze > requirements.txt`
- Node: commit `package-lock.json`, CI uses `npm ci`, never `npm install` in CI.
- Ports: `${PORT:-3000}` everywhere, documented in README.

## 8. Troubleshooting table
| Symptom | Likely cause | Fix |
|---|---|---|
| `permission denied` on script | missing +x | `chmod +x scripts/dev.sh`, shebang first line |
| Docker `failed to solve: not found` | wrong COPY path / .dockerignore ate it | `docker build --progress=plain`, check WORKDIR |
| Port already in use | stale container | `docker ps`, `docker rm -f <id>`, use `-p 127.0.0.1:3001:3000` |
| CI red only on remote | uncommitted file / case-sensitive path | `git status --ignored`, `git ls-files`, fix case |
| `gitleaks` hit | secret committed | rotate key NOW, `git filter-repo` or BFG, add to `.gitignore` |
| `npm ci` fails | lock out of sync | `npm install` locally, commit lock, re-push |

## 9. Mini-project (ship it)
Build `hello-devops`: FastAPI OR Express with `/` + `/health`, Dockerfile, `scripts/dev.sh`, CI green, README with run/test/deploy. Acceptance: fresh clone -> `docker build` -> `docker run` -> `curl localhost:3000/health` 200 in <5 min following only README.

## 10. Checklist to graduate to Intermediate
- [ ] Explain CI vs CD in 30s, inner vs outer loop
- [ ] Dockerfile builds with no `latest`, runs as non-root, has /health
- [ ] Branch -> PR -> red -> fix -> green, with branch protection on
- [ ] `gitleaks detect` clean, `.env` never committed
- [ ] README lets stranger run project in <5 min
- [ ] Can debug `docker logs`, `docker exec`, CI logs without help

## Anti-patterns (fail the level if you do these)
`chmod 777`, root in container, AWS keys in code, `:latest` in prod docs, manual SSH deploys, 1000-line bash script, committing `.venv`/`node_modules`, force-push to main.
Next: devops-intermediate (Compose, real pipelines, Terraform basics, ECR).
