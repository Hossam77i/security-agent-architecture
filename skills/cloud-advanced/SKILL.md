---
name: cloud-advanced
description: Use for EKS, Lambda advanced, multi-region, landing zones, cost/security at scale. Triggers on EKS cluster, lambda vpc, multi-region failover, organizations SCP, cost optimization, transit gateway.
---

# Cloud Advanced (AWS)

## 0. Objective + Success Criteria

**Objective:** Run a resilient, secure, cost-efficient multi-account platform: multi-region failover with defined RTO/RPO, private EKS with IRSA, advanced serverless sagas, Organizations landing zone, TGW/PrivateLink networking, and continuous cost + security loops. Tech focus: AWS + Python/Linux + Full-stack JS/Python.

**You are done when:**
- [ ] RTO/RPO documented (e.g. RTO 15m / RPO 5m) and Route53 failover drill passes
- [ ] EKS is private-endpoint, IRSA-only, autoscaled, PSS `restricted` enforced
- [ ] Serverless flows use EventBridge+SQS+DLQ, idempotency keys, Step Functions sagas (no 15-min Lambda batch abuse)
- [ ] Org has OUs + SCPs + SSO permission sets + org CloudTrail + GuardDuty + Security Hub
- [ ] TGW hub-spoke + PrivateLink (S3/Dynamo/ECR) + WAF/Shield on edge
- [ ] CUR/Athena attributes unit cost; GP3/Savings Plans/idle-kill list executed monthly
- [ ] KMS CMKs per env, Macie + Inspector + Prowler clean, backup restore drill quarterly with measured RTO

## 1. Mental Model / Architecture (Text Diagram)

```text
  Route53 (health checks) ──▶ ACTIVE us-east-1 ──╳──▶ PASSIVE us-west-2 (pilot-light)
    failover routing            | ALB+WAF/Shield      | scaled-down ALB/ASG/RDS replica
                                | EKS private / Lambda VPC   Aurora Global / DynamoDB Global Tables
                                v                             ▲ async replication (RPO clock)
                         [ TGW hub: shared-services VPC ]─────┘
                           ├─ PrivateLink: S3, DynamoDB, ECR (no NAT $)
                           ├─ Org: mgmt / security / workloads OUs + SCPs + SSO
                           └─ Security: CloudTrail org-trail, Config aggregator,
                              GuardDuty + Security Hub, KMS CMK, Macie, Inspector, Prowler CI
  Data plane: EventBridge ─▶ SQS (DLQ) ─▶ Lambda (provisioned concurrency, VPC) ─▶ Step Functions saga
  Cost plane: CUR ─▶ Athena ─▶ unit-cost dashboard ─▶ Savings Plans + GP3 + idle-kill loop
```

Rule of thumb: region failure is a ROUTING event (Route53), not a rebuild event. Data layer decides your RPO (Global Tables / Aurora Global); everything else follows.

## 2. Multi-Region RTO/RPO + Route53 Failover

Define targets first, then build to them. Pilot-light keeps a cheap replica warm:

```bash
export PRIMARY=us-east-1 SECONDARY=us-west-2 APP=myapp
# Health check on primary ALB + failover records (PRIMARY + SECONDARY alias)
aws route53 create-health-check --caller-reference $APP-$(date +%s) \
  --health-check-config file://hc-primary.json --region $PRIMARY
aws route53 change-resource-record-sets --hosted-zone-id Z1234567890 \
  --change-batch file://failover-records.json
cat failover-records.json
# {"Changes":[
#  {"Action":"CREATE","ResourceRecordSet":{"Name":"api.myapp.com","Type":"A",
#   "SetIdentifier":"primary","Failover":"PRIMARY","AliasTarget":{"HostedZoneId":"Z35SXDOTRQ7X7K","DNSName":"alb-primary.elb.amazonaws.com","EvaluateTargetHealth":true}}},
#  {"Action":"CREATE","ResourceRecordSet":{"Name":"api.myapp.com","Type":"A",
#   "SetIdentifier":"secondary","Failover":"SECONDARY","AliasTarget":{"HostedZoneId":"Z1H1FL5HABSF5","DNSName":"alb-secondary.elb.amazonaws.com","EvaluateTargetHealth":true}}}]}
```

Data replication sets RPO — pick ONE and test conflict handling:

```bash
# DynamoDB Global Table (active-active, last-writer-wins — design idempotent writes)
aws dynamodb create-global-table --global-table-name myapp-orders \
  --replication-group RegionName=$PRIMARY RegionName=$SECONDARY --region $PRIMARY
# Aurora Global (1 writer + cross-region reader; planned failover < 1 min typical)
aws rds create-global-cluster --global-cluster-identifier myapp-global \
  --engine aurora-postgresql --region $PRIMARY
aws rds describe-global-clusters --region $PRIMARY
```

Python RTO probe (run from CI after failover drill):

```python
# scripts/failover_probe.py — assert secondary serves traffic within RTO
import time, requests, sys
t0 = time.time()
for _ in range(60):
    try:
        r = requests.get("https://api.myapp.com/health", timeout=5)
        if r.status_code == 200:
            print(f"RECOVERED in {time.time()-t0:.1f}s"); sys.exit(0)
    except Exception as e: print("probe:", e)
    time.sleep(15)
print("FAIL: RTO breached"); sys.exit(1)
```

## 3. EKS Private / IRSA / Autoscaler / PSS + Serverless Advanced

EKS private endpoint, managed nodes + Fargate burst, IRSA (no node keys), autoscaler, PSS restricted:

```bash
eksctl create cluster --name myapp-prod --region $PRIMARY --version 1.29 \
  --vpc-private-subnets subnet-aaa,subnet-bbb --private-endpoint-access --public-endpoint-access=false \
  --managed-node-groups --node-type m5.large --nodes 2 --nodes-min 2 --nodes-max 8 \
  --fargate --with-oidc
# IRSA: serviceaccount -> IAM role (least privilege, e.g. S3 + SQS only)
eksctl create iamserviceaccount --cluster myapp-prod --region $PRIMARY \
  --namespace app --name api --attach-policy-arn arn:aws:iam::123456789012:policy/myapp-api \
  --approve --override-existing-serviceaccounts
kubectl top nodes; kubectl get sa api -n app -o yaml | grep -i role-arn
# Autoscaler: Karpenter (preferred) or Cluster Autoscaler
helm upgrade --install karpenter oci://public.ecr.aws/karpenter/karpenter --namespace karpenter --create-namespace
kubectl apply -f k8s/pss-restricted.yaml  # enforce: runAsNonRoot, seccomp, drop ALL caps
kubectl label namespace app pod-security.kubernetes.io/enforce=restricted
```

Lambda in VPC with provisioned concurrency + EventBridge/SQS DLQ + idempotency (Dynamo lock):

```bash
aws lambda create-function --function-name myapp-orders \
  --runtime python3.12 --handler orders.handler --role arn:aws:iam::123456789012:role/myapp-lambda-vpc \
  --vpc-config SubnetIds=subnet-aaa,subnet-bbb,SecurityGroupIds=sg-app \
  --memory-size 512 --timeout 30 --region $PRIMARY
aws lambda put-provisioned-concurrency-config --function-name myapp-orders \
  --qualifier prod --provisioned-concurrency-units 10 --region $PRIMARY
# Queue with DLQ: main + redrive after 5 receives, 14-day retention on DLQ
aws sqs create-queue --queue-name myapp-orders --attributes file://queue-attrs.json --region $PRIMARY
aws sqs create-queue --queue-name myapp-orders-dlq --region $PRIMARY
```

```python
# orders.py — idempotent consumer: DynamoDB conditional write on event_id
import boto3
ddb = boto3.resource("dynamodb", region_name="us-east-1")
locks = ddb.Table("myapp-idempotency")
def handler(event, ctx):
    for rec in event["Records"]:
        eid = rec["messageAttributes"]["event_id"]["stringValue"]
        try:
            locks.put_item(Item={"pk": eid, "ttl": 86400},
                           ConditionExpression="attribute_not_exists(pk)")
        except locks.meta.client.exceptions.ConditionalCheckFailedException:
            continue  # duplicate delivery — skip
        process(rec["body"])  # business logic here
```

Step Functions saga (compensate, never 2PC); Node cold-start slim:

```json
{ "Comment": "order saga", "StartAt": "Charge",
  "States": { "Charge": { "Type": "Task", "Resource": "arn:aws:lambda:us-east-1:123456789012:function:charge",
  "Catch": [{ "ErrorEquals": ["States.ALL"], "Next": "Refund" }], "Next": "Ship" },
  "Ship": { "Type": "Task", "Resource": "arn:aws:lambda:us-east-1:123456789012:function:ship",
  "Catch": [{ "ErrorEquals": ["States.ALL"], "Next": "Refund" }], "End": true },
  "Refund": { "Type": "Task", "Resource": "arn:aws:lambda:us-east-1:123456789012:function:refund", "End": true } } }
```

```bash
aws stepfunctions create-state-machine --name myapp-order-saga \
  --definition file://saga.json --role-arn arn:aws:iam::123456789012:role/myapp-sfn --region $PRIMARY
# Node: esbuild bundle <5MB to cut cold start
npx esbuild src/handler.ts --bundle --minify --platform=node --target=node20 --outfile=dist/handler.js && ls -lh dist/
```

## 4. Landing Zone: OUs / SCPs / SSO / CloudTrail / GuardDuty / SecurityHub

OUs isolate blast radius; SCPs guardrail even admins; SSO gives short-lived access:

```bash
ORG=$(aws organizations describe-organization --query Organization.Id --output text)
aws organizations create-organizational-unit --parent-id r-xxxx --name workloads
aws organizations create-organizational-unit --parent-id r-xxxx --name security
# SCP: deny leaving org, unencrypted S3, public EBS snapshots (attach to workloads OU)
aws organizations create-policy --name deny-risky --type SERVICE_CONTROL_POLICY \
  --content file://scp-deny.json --description "guardrails"
aws organizations attach-policy --policy-id p-xxxx --target-id ou-workloads-yyyy
cat scp-deny.json
# {"Version":"2012-10-17","Statement":[
#  {"Effect":"Deny","Action":["organizations:LeaveOrganization","ec2:ShareSnapshot"],
#   "Resource":"*"},
#  {"Effect":"Deny","Action":["s3:PutObject"],"Resource":"*",
#   "Condition":{"StringNotEquals":{"s3:x-amz-server-side-encryption":"aws:kms"}}}]}
```

Detective controls org-wide (delegate to security account):

```bash
aws cloudtrail create-trail --name org-trail --is-organization-trail \
  --s3-bucket-name myapp-org-trail --is-multi-region-trail --enable-log-file-validation
aws guardduty create-detector --enable --finding-publishing-frequency FIFTEEN_MINUTES
aws securityhub enable-security-hub --enable-default-standards
aws configservice put-configuration-aggregator --configuration-aggregator-name org \
  --account-aggregation-sources file://agg.json
aws organizations list-policies --filter SERVICE_CONTROL_POLICY
```

## 5. Network/Cost/Security: TGW + PrivateLink + WAF/Shield, CUR/Athena + GP3 + Savings Plans + Idle-Kill, KMS/Macie/Inspector/Prowler

TGW hub-spoke + PrivateLink kills NAT spend; WAF/Shield on edge:

```bash
TGW=$(aws ec2 create-transit-gateway --description myapp-hub \
  --query TransitGateway.TransitGatewayId --output text --region $PRIMARY)
aws ec2 create-transit-gateway-vpc-attachment --transit-gateway-id $TGW \
  --vpc-id vpc-workload --subnet-ids subnet-aaa subnet-bbb --region $PRIMARY
# PrivateLink endpoints (S3 gateway + ECR/Dynamo interface — traffic never hits NAT)
aws ec2 create-vpc-endpoint --vpc-id vpc-workload --service-name com.amazonaws.$PRIMARY.s3 \
  --route-table-ids $RT_PRIV --vpc-endpoint-type Gateway --region $PRIMARY
aws ec2 create-vpc-endpoint --vpc-id vpc-workload \
  --service-name com.amazonaws.$PRIMARY.ecr.api --vpc-endpoint-type Interface \
  --subnet-ids subnet-aaa subnet-bbb --security-group-ids sg-app --region $PRIMARY
aws shield create-protection --name myapp-alb --resource-arn $ALB_ARN
```

Cost loop — CUR + Athena unit cost, then GP3 + Savings Plans + idle-kill:

```sql
-- Athena on CUR: unit cost per request per service (run monthly)
SELECT line_item_product_code, sum(line_item_unblended_cost) AS cost,
       sum(line_item_unblended_cost) / nullif(sum(usage_amount),0) AS unit_cost
FROM cur_db.cur_table WHERE month = '2026-09' GROUP BY 1 ORDER BY cost DESC;
```

```bash
# GP3 migration (cheaper + faster than GP2), Savings Plans baseline, idle-kill sweep
aws ec2 modify-volume --volume-id vol-abc --volume-type gp3 --iops 3000 --throughput 125
aws savingsplans describe-savings-plans --states active
aws ec2 describe-nat-gateways --filter Name=state,Values=available \
  --query 'NatGateways[*].[NatGatewayId,VpcId,State]'  # flag idle/orphaned
aws ec2 describe-addresses --query 'Addresses[?AssociationId==null]'  # unattached EIPs $$
aws ec2 describe-volumes --filters Name=status,Values=available  # orphaned EBS $$
```

KMS/Macie/Inspector/Prowler + quarterly restore drill:

```bash
aws kms create-key --description myapp-prod --key-usage ENCRYPT_DECRYPT --origin AWS_KMS
aws kms enable-key-rotation --key-id alias/myapp-prod
aws macie2 enable-macie; aws macie2 create-classification-job --job-type ONE_TIME --s3-job-definition file://macie.json
aws inspector2 enable --account-ids 123456789012 --resource-types EC2 ECR LAMBDA
pip install prowler && prowler aws --compliance cis_5.0 -M html -o prowler-report/
# Restore drill: snapshot -> new instance -> connect -> measure RTO
SNAP=$(aws rds describe-db-snapshots --db-instance-identifier myapp-prod \
  --query 'reverse(sort_by(DBSnapshots,&InstanceCreateTime))[0].DBSnapshotIdentifier' --output text)
time aws rds restore-db-instance-from-db-snapshot --db-instance-identifier myapp-restore-test \
  --db-snapshot-identifier $SNAP --no-multi-az
```

## Lab 1/2/3 (Hands-On, Acceptance Checks)

**Lab 1 — Failover drill.** Deploy ALB in 2 regions + Route53 failover records + Global Table (§2). Acceptance: stop primary targets, `scripts/failover_probe.py` returns `RECOVERED` within RTO 15m; record measured RTO/RPO in drill log; fail back cleanly with zero split-brain writes (idempotency table shows no dupes).

**Lab 2 — Private EKS + IRSA + saga.** `eksctl` private cluster per §3; deploy `app/api` with IRSA role (verify `kubectl exec` can `aws s3 ls` scoped bucket but NOT `iam:*`); PSS `restricted` blocks a `runAsRoot` test pod; Step Functions saga order->refund path executes with one forced failure. Acceptance: `kubectl auth can-i` + saga execution history screenshot.

**Lab 3 — Landing-zone guardrail + cost/security sweep.** Attach `scp-deny.json` to a sandbox OU and prove `s3:PutObject` without KMS is denied; run Prowler CIS + Inspector and file the top 5 findings; run CUR/Athena query and produce idle-kill list (NAT/EIP/EBS) with $ saved. Acceptance: denied-action CloudTrail event + Prowler HTML + cost report committed.

## Troubleshooting (Symptom -> Fix)

| Symptom | Fix |
|---|---|
| Failover never triggers / flapping | Health check path/port wrong (must be `HTTPS:443/health` on ALB alias); `EvaluateTargetHealth=true` missing on alias; threshold too tight — 3x30s before declaring unhealthy; check `aws route53 get-health-check-status` |
| Global Table write conflicts / lost updates | Last-writer-wins is by design — add idempotency keys + conditional writes (§3 Python); avoid cross-region counters; use single-writer (Aurora Global) for money movement |
| EKS pods `Unauthorized` / IRSA not working | OIDC provider missing (`eksctl utils associate-iam-oidc-provider`); SA annotation `eks.amazonaws.com/role-arn` typo; trust policy `aud/sts` mismatch; check `aws sts get-caller-identity` from pod via debug job |
| Karpenter/CA never scales / pending pods | No capacity in private subnets (AZ imbalance); SG blocks node->API; instance-type/nodepool mismatch; `kubectl describe pod` events + `kubectl logs -n karpenter` |
| Lambda VPC timeouts / cold starts p99 | ENI exhaustion in small subnets (add /24s); missing PrivateLink so traffic hairpins via NAT (add S3/Dynamo endpoints); enable provisioned concurrency for p99 path; slim bundle (esbuild/layers), raise memory (CPU scales with it) |
| SCP blocks legit deploy / break-glass locked out | SCP attached too high (root vs OU); add explicit break-glass role ARN exception in SCP `Condition`; keep org-management break-glass creds in sealed envelope + test quarterly |
| CUR/Athena query empty / Prowler noisy | CUR delivery lag 24h + wrong Athena table partition (run `MSCK REPAIR TABLE`); Prowler fails on benign rules — baseline with `--severity-critical` first, then expand; Inspector needs SSM agent on EC2 |

## Mini-Project + Graduation Checklist

**Mini-project:** `myapp-global` — todo API (Python or Node) running active-passive across 2 regions: Route53 failover -> ALB+WAF/Shield -> private EKS (IRSA, autoscaled, PSS restricted) + Lambda async worker (VPC, provisioned concurrency, SQS DLQ, idempotency) + Step Functions saga; data on DynamoDB Global Table; landing-zone OUs+SCP+SSO with org CloudTrail/GuardDuty/SecurityHub; CUR unit-cost dashboard; Prowler CIS report; documented failover + restore drills with measured RTO/RPO.

**Graduation checklist:**
- [ ] RTO/RPO doc + passing failover drill log (probe output + timeline)
- [ ] EKS private-only, IRSA proof, autoscaler scales 2->N under load, PSS blocks privileged pod
- [ ] SQS DLQ redrive verified (poison message lands in DLQ, replay works); saga compensates on failure
- [ ] SCP denies test violation; SSO permission sets used (no shared IAM users); org-trail + GuardDuty findings flow to Security Hub
- [ ] TGW attachments + PrivateLink for S3/Dynamo/ECR verified (`traceroute`/VPC Flow Logs show no NAT for endpoint traffic)
- [ ] CUR/Athena unit-cost query saved; GP3 + Savings Plans applied; idle NAT/EIP/EBS killed with $ figure
- [ ] KMS rotation ON, Macie job ran, Inspector + Prowler reports filed, restore drill RTO measured this quarter

## Anti-Patterns + Next

**Anti-patterns:** cross-region sync without conflict/idempotency design; Lambda 15-min timeout abused as batch (use Fargate/Batch); single account for prod+dev; SCPs with no break-glass exception; public EKS endpoint `0.0.0.0/0`; NAT for S3/Dynamo traffic (use PrivateLink); WAF in Count-only; Savings Plans covering spiky burst; backups never restore-tested; KMS wildcard grants.

**Next:** platform mastery — GitOps (ArgoCD + policy-as-code), chaos/failover game-days, FinOps chargeback per team, zero-trust service mesh (mTLS + per-route authz), supply-chain signing (Sigstore) in the deploy pipeline.
