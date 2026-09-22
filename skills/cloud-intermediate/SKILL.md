---
name: cloud-intermediate
description: Use for VPC, ALB, RDS, Auto Scaling, IAM policies, CloudWatch, Terraform on AWS. Triggers on VPC subnet, ALB setup, RDS connect, autoscaling group, IAM policy json, cloudwatch alarm.
---

# Cloud Intermediate (AWS)

## 0. Objective + Success Criteria

**Objective:** Build and operate a secure 3-tier app (ALB -> private compute -> private RDS) with Terraform, least-privilege IAM, CloudWatch. Focus: AWS + Python/Linux + JS/Python.

**You are done when:**
- [ ] VPC `10.0.0.0/16` 2 AZs (2 public + 2 private), IGW + NAT routing verified
- [ ] ALB (public) -> ASG/ECS (private) healthy; RDS Postgres private Multi-AZ + rotation works
- [ ] No `*:*`; EC2/ECS use roles; `simulate-principal-policy` passes
- [ ] Terraform S3+DynamoDB backend + modules + tags; `plan` clean
- [ ] CloudWatch alarms (5xx, CPU, RDS) + dashboard fire to SNS; WAF on ALB `/api*`

## 1. Mental Model / Architecture (Text Diagram)

```text
                    +------------------ CloudWatch + SNS ------------------+
                    |  metrics: ALB 5xx, TargetResponseTime, CPU, RDS     |
                    v                                                     |
  Internet --> [ WAF ] --> [ ALB: public A+B (443, ACM) ]                 |
                                v                                         |
                       [ Target Group :80 /health ]                       |
                          /                    \                         |
            [ ASG/ECS private-A ]        [ ASG/ECS private-B ] <-- IAM role
                         \                    /                           |
                   [ RDS Postgres Multi-AZ : private-A+B ]                |
                     ^  Secrets Manager rotation + snapshots 7d + del-protect
  [ S3 ] <-- [ CloudFront OAC ]     [ NAT GW ] <-- private route          |
  [ IGW ] <-- public route          user-data: NO secrets                |
```

Key invariants: ALB is the ONLY public compute entry. DB has NO public access, NO `0.0.0.0/0` SG. Private subnets egress via NAT. All secrets come from Secrets Manager / SSM Parameter Store at runtime.

## 2. VPC /16 2AZ: Public + Private, IGW / NAT / Routes

Copy-paste baseline with AWS CLI:

```bash
export AWS_REGION=us-east-1 PREFIX=myapp ENV=dev
VPC=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
  --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=$PREFIX-$ENV}]" \
  --query Vpc.VpcId --output text --region $AWS_REGION)

IGW=$(aws ec2 create-internet-gateway --query InternetGateway.InternetGatewayId \
  --output text --region $AWS_REGION)
aws ec2 attach-internet-gateway --vpc-id $VPC --internet-gateway-id $IGW --region $AWS_REGION

# Subnets: public .0/.1, private .10/.11
aws ec2 create-subnet --vpc-id $VPC --cidr-block 10.0.0.0/24 \
  --availability-zone ${AWS_REGION}a --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=myapp-dev-public-a}]' --region $AWS_REGION
aws ec2 create-subnet --vpc-id $VPC --cidr-block 10.0.1.0/24 \
  --availability-zone ${AWS_REGION}b --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=myapp-dev-public-b}]' --region $AWS_REGION
aws ec2 create-subnet --vpc-id $VPC --cidr-block 10.0.10.0/24 \
  --availability-zone ${AWS_REGION}a --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=myapp-dev-private-a}]' --region $AWS_REGION
aws ec2 create-subnet --vpc-id $VPC --cidr-block 10.0.11.0/24 \
  --availability-zone ${AWS_REGION}b --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=myapp-dev-private-b}]' --region $AWS_REGION
```

NAT + routes (single NAT for dev, one-per-AZ for prod):

```bash
# Dev: one NAT GW in public-a + EIP
EIP=$(aws ec2 allocate-address --domain vpc --query AllocationId --output text --region $AWS_REGION)
PUB_A=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=myapp-dev-public-a" \
  --query Subnets[0].SubnetId --output text --region $AWS_REGION)
NAT=$(aws ec2 create-nat-gateway --subnet-id $PUB_A --allocation-id $EIP \
  --query NatGateway.NatGatewayId --output text --region $AWS_REGION)
aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT --region $AWS_REGION

# Public route table -> IGW
RT_PUB=$(aws ec2 create-route-table --vpc-id $VPC --query RouteTable.RouteTableId --output text --region $AWS_REGION)
aws ec2 create-route --route-table-id $RT_PUB --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW --region $AWS_REGION
# Private route table -> NAT
RT_PRIV=$(aws ec2 create-route-table --vpc-id $VPC --query RouteTable.RouteTableId --output text --region $AWS_REGION)
aws ec2 create-route --route-table-id $RT_PRIV --destination-cidr-block 0.0.0.0/0 --nat-gateway-id $NAT --region $AWS_REGION
aws ec2 describe-route-tables --route-table-ids $RT_PUB $RT_PRIV --region $AWS_REGION
```

## 3. ALB -> ASG/ECS (Private) + RDS Postgres Private + Secrets Manager

ALB in public, targets in private. Health check `/health`, deregistration 30s, ASG min 2 / max 4 on CPU 60%:

```bash
# Security groups: ALB allows 80/443 world; app allows 80 ONLY from ALB SG; DB allows 5432 ONLY from app SG
ALB_SG=$(aws ec2 create-security-group --group-name myapp-alb --description "alb" --vpc-id $VPC \
  --query GroupId --output text --region $AWS_REGION)
aws ec2 authorize-security-group-ingress --group-id $ALB_SG --protocol tcp --port 443 --cidr 0.0.0.0/0 --region $AWS_REGION
APP_SG=$(aws ec2 create-security-group --group-name myapp-app --description "app" --vpc-id $VPC \
  --query GroupId --output text --region $AWS_REGION)
aws ec2 authorize-security-group-ingress --group-id $APP_SG --protocol tcp --port 80 \
  --source-group $ALB_SG --region $AWS_REGION
DB_SG=$(aws ec2 create-security-group --group-name myapp-db --description "db" --vpc-id $VPC \
  --query GroupId --output text --region $AWS_REGION)
aws ec2 authorize-security-group-ingress --group-id $DB_SG --protocol tcp --port 5432 \
  --source-group $APP_SG --region $AWS_REGION

# ALB + target group
ALB_ARN=$(aws elbv2 create-load-balancer --name myapp-dev --subnets $PUB_A $PUB_B \
  --security-groups $ALB_SG --scheme internet-facing --type application \
  --query LoadBalancers[0].LoadBalancerArn --output text --region $AWS_REGION)
TG_ARN=$(aws elbv2 create-target-group --name myapp-dev-tg --protocol HTTP --port 80 \
  --vpc-id $VPC --health-check-path /health --health-check-interval-seconds 15 \
  --deregistration-delay-timeout-seconds 30 --target-type instance \
  --query TargetGroups[0].TargetGroupArn --output text --region $AWS_REGION)
aws elbv2 describe-target-health --target-group-arn $TG_ARN --region $AWS_REGION
```

RDS Postgres private Multi-AZ + Secrets Manager (never put password in user-data):

```bash
aws secretsmanager create-secret --name myapp/dev/db \
  --secret-string '{"username":"appuser","password":"CHANGE_ME_32CHAR"}' --region $AWS_REGION
aws rds create-db-instance --db-instance-identifier myapp-dev \
  --db-instance-class db.t3.micro --engine postgres --engine-version 15.4 \
  --allocated-storage 20 --no-publicly-accessible --multi-az \
  --db-subnet-group-name myapp-dev --vpc-security-group-ids $DB_SG \
  --manage-master-user-password --backup-retention-period 7 \
  --deletion-protection --region $AWS_REGION
aws rds describe-db-instances --db-instance-identifier myapp-dev \
  --query 'DBInstances[0].[PubliclyAccessible,MultiAZ,BackupRetentionPeriod]' --region $AWS_REGION
```

Python (boto3) connect via Secrets Manager + Node snippet:

```python
# app/db.py — Python: fetch creds at runtime, SSL required
import json, boto3, psycopg2
sm = boto3.client("secretsmanager", region_name="us-east-1")
sec = json.loads(sm.get_secret_value(SecretId="myapp/dev/db")["SecretString"])
conn = psycopg2.connect(host="myapp-dev.xyz.us-east-1.rds.amazonaws.com",
    dbname="appdb", user=sec["username"], password=sec["password"], sslmode="require")
```

```js
// app/db.js — Node (pg): same pattern, no hardcoded password
const { SecretsManagerClient, GetSecretValueCommand } = require("@aws-sdk/client-secrets-manager");
const { Client } = require("pg");
const sm = new SecretsManagerClient({ region: "us-east-1" });
async function dbClient() {
  const s = await sm.send(new GetSecretValueCommand({ SecretId: "myapp/dev/db" }));
  const c = JSON.parse(s.SecretString);
  const client = new Client({ host: process.env.DB_HOST, database: "appdb",
    user: c.username, password: c.password, ssl: { rejectUnauthorized: true } });
  await client.connect(); return client;
}
```

## 4. IAM Least-Privilege + Simulate + Roles, Terraform Backend/Modules/Tags

Least-privilege policy (scoped, no `*:*`), then validate + simulate:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::myapp-dev-uploads/*" },
    { "Effect": "Allow", "Action": ["secretsmanager:GetSecretValue"],
      "Resource": "arn:aws:secretsmanager:us-east-1:123456789012:secret:myapp/dev/*" },
    { "Effect": "Allow", "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": "arn:aws:logs:us-east-1:123456789012:log-group:/myapp/*" }
  ]
}
```

```bash
aws iam access-analyzer validate-policy --policy-document file://pol.json
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::123456789012:role/myapp-dev-app \
  --action-names s3:PutObject secretsmanager:GetSecretValue \
  --resource-arns arn:aws:s3:::myapp-dev-uploads/a arn:aws:secretsmanager:us-east-1:123456789012:secret:myapp/dev/db-AbCdEf
# EC2/ECS uses instance/task role — never bake keys:
aws iam create-role --role-name myapp-dev-app --assume-role-policy-document file://trust-ec2.json
aws iam attach-role-policy --role-name myapp-dev-app --policy-arn arn:aws:iam::123456789012:policy/myapp-dev-app
```

Terraform S3+DynamoDB backend + modules + mandatory tags:

```hcl
# backend.tf — remote state with locking
terraform {
  required_version = ">= 1.6"
  backend "s3" {
    bucket         = "myapp-tfstate-123456789012"
    key            = "dev/network.tfstate"
    region         = "us-east-1"
    dynamodb_table = "myapp-tflock"
    encrypt        = true
  }
}
provider "aws" { region = "us-east-1" default_tags { tags = {
  Project = "myapp" Env = "dev" Owner = "platform" ManagedBy = "terraform" } } }

# main.tf — compose modules, pin versions
module "vpc" { source = "terraform-aws-modules/vpc/aws" version = "~> 5.0"
  name = "myapp-dev" cidr = "10.0.0.0/16" azs = ["us-east-1a", "us-east-1b"]
  public_subnets = ["10.0.0.0/24", "10.0.1.0/24"] private_subnets = ["10.0.10.0/24", "10.0.11.0/24"]
  enable_nat_gateway = true single_nat_gateway = true }
module "alb" { source = "./modules/alb" vpc_id = module.vpc.vpc_id public_subnets = module.vpc.public_subnets }
module "rds" { source = "./modules/rds" vpc_id = module.vpc.vpc_id private_subnets = module.vpc.private_subnets }
```

```bash
terraform init && terraform fmt -check && terraform validate
terraform plan -out=tfplan && terraform show -json tfplan | head -c 2000
# PR comment flow: post plan summary, require 1 approval before apply
terraform apply tfplan
```

## 5. CloudWatch Alarms/Dashboards + WAF Basics

Alarms that page a human (SNS), plus a one-screen dashboard:

```bash
export ALB_FULL="app/myapp-dev/abc123" TG_FULL="targetgroup/myapp-dev-tg/def456"
aws cloudwatch put-metric-alarm --alarm-name myapp-dev-alb-5xx \
  --metric-name HTTPCode_Target_5XX_Count --namespace AWS/ApplicationELB --statistic Sum \
  --period 300 --evaluation-periods 1 --threshold 10 --comparison-operator GreaterThanThreshold \
  --dimensions Name=LoadBalancer,Value=$ALB_FULL --alarm-actions arn:aws:sns:us-east-1:123456789012:myapp-dev
aws cloudwatch put-metric-alarm --alarm-name myapp-dev-cpu-high \
  --metric-name CPUUtilization --namespace AWS/EC2 --statistic Average \
  --period 900 --evaluation-periods 1 --threshold 80 --comparison-operator GreaterThanThreshold \
  --dimensions Name=AutoScalingGroupName,Value=myapp-dev --alarm-actions arn:aws:sns:us-east-1:123456789012:myapp-dev
aws cloudwatch put-dashboard --dashboard-name myapp-dev --dashboard-body file://dashboard.json
aws logs create-log-group --log-group-name /myapp/dev --region $AWS_REGION
```

WAF on ALB for `/api*` (rate-limit + AWS managed rules):

```bash
WAF_ARN=$(aws wafv2 create-web-acl --name myapp-dev --scope REGIONAL \
  --default-action Allow={} --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=myapp-dev \
  --rules file://waf-rules.json --query Summary.ARN --output text --region $AWS_REGION)
aws wafv2 associate-web-acl --web-acl-arn $WAF_ARN --resource-arn $ALB_ARN --region $AWS_REGION
# waf-rules.json: AWSManagedRulesCommonRuleSet + RateBasedStatement limit 2000 on /api*
```

## Lab 1/2/3 (Hands-On, Acceptance Checks)

**Lab 1 — VPC + routing proof.** Build the VPC per §2 (dev single NAT). Acceptance: `aws ec2 describe-route-tables` shows public `0.0.0.0/0->IGW` and private `0.0.0.0/0->NAT`; private instance reaches internet via NAT (`curl ifconfig.me` works) but has no public IP in `describe-instances`.

**Lab 2 — ALB->private + RDS private + rotation.** Deploy ALB + 2 targets + RDS per §3, enable Secrets Manager rotation (30d). Acceptance: `describe-target-health` shows 2x `healthy`; `describe-db-instances` shows `PubliclyAccessible=false`; Python `app/db.py` connects with `sslmode=require`; rotation test creates a new version and app still connects.

**Lab 3 — Terraform + alarms + WAF.** `terraform plan` clean with S3 backend + DynamoDB lock; apply creates tagged resources; trigger 5xx (bad deploy) and confirm SNS alarm fires; `curl` flood against `/api*` gets 403 rate-limited by WAF. Acceptance: dashboard screenshot + alarm history `OK->ALARM->OK`.

## Troubleshooting (Symptom -> Fix)

| Symptom | Fix |
|---|---|
| Targets `unhealthy`, ALB 502 | Check app SG allows 80 ONLY from ALB SG; verify `/health` returns 200 locally; confirm deregistration delay not masking; `aws elbv2 describe-target-health --target-group-arn $TG_ARN` |
| Private instance has no internet | Private route table missing `0.0.0.0/0->NAT`; NAT in wrong subnet (must be public); NACL blocking ephemeral 1024-65535; check `describe-nat-gateways` state |
| RDS `connection timed out` from app | DB SG must allow 5432 from APP_SG (not CIDR); app and DB in same VPC; `PubliclyAccessible=false` + connect via private DNS; test with `psql "sslmode=require"` from app host |
| `AccessDenied` on S3/Secrets at runtime | Role attached? `curl 169.254.169.254/latest/meta-data/iam/info`; run `simulate-principal-policy` to find missing action/resource; fix ARN scope (no typos in secret suffix) |
| `terraform init` backend error / state lock stuck | Bucket + DynamoDB table must pre-exist in same region; check `encrypt=true`; stuck lock: `terraform force-unlock <id>` only after confirming no running apply |
| Alarm never fires / always ALARM | Wrong dimension (`LoadBalancer` needs FULL `app/...` name); period/threshold mismatch (5xx Sum vs Average); SNS subscription unconfirmed — confirm email/Slack hook |
| WAF blocks legit traffic | Check sampled requests in WAF console; scope rule to `/api*` path statement, not `/*`; raise rate limit or add IP allow-list for office/VPN egress |

## Mini-Project + Graduation Checklist

**Mini-project:** Ship `myapp` todo API (Python FastAPI or Node Express) to the 3-tier stack fully via Terraform: ALB(443)+WAF -> ASG min2 (private) -> RDS Postgres private; secrets via Secrets Manager; logs to CloudWatch; dashboard + 3 alarms. Include `README` with architecture diagram, `terraform plan` output, and restore test (snapshot -> new instance -> connect).

**Graduation checklist:**
- [ ] `describe-vpcs/subnets/route-tables` matches §2 design, tags present on every resource
- [ ] ALB 443 only (80 redirects), targets healthy, WAF associated and logging
- [ ] RDS Multi-AZ (prod flag), snapshots 7d, deletion protection ON, rotation ON
- [ ] Zero `*:*` policies; `validate-policy` + `simulate-principal-policy` evidence saved
- [ ] `terraform plan` in PR, state in S3 + lock in DynamoDB, no local `.tfstate` committed
- [ ] Alarms tested end-to-end (induced 5xx pages SNS), dashboard covers ALB+ASG+RDS
- [ ] Restore drill documented: snapshot restored, app reconnected, RTO measured

## Anti-Patterns + Next

**Anti-patterns:** single-AZ prod; SG `0.0.0.0/0` to DB/5432; IAM `*:*` or long-lived keys on EC2; passwords in user-data / git; no RDS deletion protection or snapshots; ALB HTTP-only; NAT per dev shared with prod; CloudWatch alarms with no SNS action; WAF in `Count` mode forever.

**Next:** `cloud-advanced` — multi-region failover, EKS private/IRSA, serverless sagas, Organizations/SCPs, TGW/PrivateLink, cost + security at scale.
