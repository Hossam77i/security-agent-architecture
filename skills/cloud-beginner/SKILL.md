---
name: cloud-beginner
description: Use when learning cloud fundamentals, AWS EC2/S3/IAM, regions, CLI setup. Triggers on what is cloud, EC2 launch, S3 bucket, IAM user, aws cli configure, cloud regions.
---

# Cloud Beginner — AWS Foundations Without Surprise Bills

## 0. Objective
Explain cloud in 60s, secure your account, launch EC2 + S3 via console AND CLI, set billing guardrails. Kill everything to avoid charges.

## 1. Mental model
Cloud = rented computers with APIs + pay-per-second. Region = geographic cluster (eu-west-1), AZ = isolated datacenter inside region (eu-west-1a/b/c). Deploy across 2+ AZs for survival. Shared responsibility: AWS secures hardware/hypervisor, YOU secure data/IAM/SGs/encryption. Tag everything (`Project, Env, Owner`) or cost reports are useless.

## 2. Secure the account first (15 min, do not skip)
1. Root MFA ON (virtual MFA app), no root keys ever: `aws iam get-credential-report` must show root `access_key_1_active=false`.
2. Create admin via IAM Identity Center (SSO): `aws configure sso`, user `dev-admin` in group `Admins`. Stop using root.
3. Password policy + CloudTrail ON (org trail to locked S3). Enable Billing alerts.
```bash
aws sts get-caller-identity --profile dev
aws iam get-account-password-policy --profile dev || echo "set via console"
```

## 3. EC2 — first server the safe way
- AMI Amazon Linux 2023, type `t3.micro` (free-tier eligible), key pair ed25519, SG: `22/tcp from MyIP/32` only, `80/443` open if web. No `0.0.0.0/0` on 22.
```bash
aws ec2 run-instances --profile dev \
 --image-id resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
 --instance-type t3.micro --key-name dev-key --security-group-ids sg-xxx --subnet-id subnet-xxx \
 --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=dev-01},{Key=Env,Value=dev}]'
aws ec2 describe-instances --profile dev --query 'Reservations[].Instances[].[InstanceId,State.Name,PublicIpAddress]' --output table
# prefer SSM over SSH (no open 22 at all):
aws ssm start-session --profile dev --target i-0abc123
```
User-data minimal, no secrets:
```bash
#!/bin/bash
dnf update -y && dnf install -y nginx && systemctl enable --now nginx
echo "ok $(hostname)" > /usr/share/nginx/html/health
```
Cleanup: `aws ec2 terminate-instances --instance-ids i-xxx --profile dev`. Verify terminated.

Lab 1: launch, `curl http://<ip>/health` 200, SSH or SSM in, `nginx` logs, terminate. Record instance ID + cost in Cost Explorer ($0 expected free-tier).

## 4. S3 — private by default
```bash
aws s3api create-bucket --bucket my-learn-user-78312 --region eu-west-1 \
 --create-bucket-configuration LocationConstraint=eu-west-1 --profile dev
aws s3api put-public-access-block --bucket my-learn-user-78312 --profile dev \
 --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws s3api put-bucket-versioning --bucket my-learn-user-78312 --profile dev --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket my-learn-user-78312 --profile dev \
 --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
echo hello > hello.txt && aws s3 cp hello.txt s3://my-learn-user-78312/ --profile dev
aws s3 ls s3://my-learn-user-78312/ --profile dev
```
Lifecycle (console or CLI): transition to Glacier after 90d for learning bucket. Static website only via CloudFront OAC, never public bucket policy for PII.

Python tie-in (boto3, no hardcoded keys — uses SSO profile via `AWS_PROFILE=dev`):
```python
import boto3
s3 = boto3.client("s3", region_name="eu-west-1")
print([b["Name"] for b in s3.list_buckets()["Buckets"]])
s3.upload_file("hello.txt", "my-learn-user-78312", "hello.txt")
```

Lab 2: versioning ON, upload v1/v2, `aws s3api list-object-versions`, restore v1, `aws s3 rm` + delete bucket to avoid clutter.

## 5. CLI + billing guardrails
```bash
aws configure sso --profile dev
export AWS_PROFILE=dev
aws sts get-caller-identity
aws ce get-cost-and-usage --time-period Start=$(date -d '30 days ago' +%F),End=$(date +%F) --granularity MONTHLY --metrics BlendedCost --profile dev
```
Console: Budgets -> $5 actual + $10 forecast alerts to email. Tag policy: `Env` required. Check daily first week.

## 6. Troubleshooting
| Symptom | Fix |
|---|---|
| `Unable to locate credentials` | `aws configure sso`, `AWS_PROFILE=dev`, `aws sso login --profile dev` |
| EC2 no SSH | SG source not MyIP (IP changed), use SSM + instance role `AmazonSSMManagedInstanceCore` |
| S3 `AccessDenied` | Block Public Access vs policy conflict, bucket owner mismatch, KMS key deny |
| Surprise $2 NAT | NAT Gateway hourly — delete if learning, use public subnet + IGW for dev |
| `InvalidBucketName` | globally unique, lowercase, no underscores |

## 7. Project + graduation
Project: `cloud-hello` — EC2 nginx `/health` + private versioned S3 with `hello.txt` via CLI AND boto3, budget $5 alarm, all tagged, then full cleanup with termination proof. Graduate when: explain AZ vs Region, least privilege, launch/terminate EC2 locked-down, private S3 versioned/encrypted, `credential-report` shows no root keys, budget alarm set.
Anti-patterns: root keys, `0.0.0.0/0` SSH, public S3 PII, untagged, leaving EC2/NAT running.
Next: cloud-intermediate (VPC/ALB/RDS/ASG).
