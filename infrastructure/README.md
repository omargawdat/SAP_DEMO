# PII Shield - AWS Infrastructure

Deploy the FastAPI backend to AWS App Runner. The Streamlit UI deploys separately to Streamlit Cloud (free).

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit Cloud (FREE)                  │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │  UI: your-app.streamlit.app                    │     │
│  └──────────────────────┬─────────────────────────┘     │
└─────────────────────────┼───────────────────────────────┘
                          │ API_URL
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  AWS (eu-central-1)                      │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │  App Runner: pii-shield-api                    │     │
│  │  URL: https://xxx.eu-central-1.awsapprunner.com│     │
│  │  Port: 8000 | Auto-HTTPS | Auto-scale          │     │
│  └──────────────────────┬─────────────────────────┘     │
│                         │                                │
│           ┌─────────────┴─────────────┐                 │
│           ▼                           ▼                 │
│  ┌─────────────────┐        ┌─────────────────┐        │
│  │      ECR        │        │ Secrets Manager │        │
│  │ pii-shield-api  │        │ ANTHROPIC_API_KEY│       │
│  └─────────────────┘        └─────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **Terraform** >= 1.5
2. **AWS CLI** configured

## Quick Start

**Important:** App Runner requires an ECR image to exist. Use two-stage deployment:

```bash
cd infrastructure/terraform

# 1. Initialize Terraform
terraform init

# 2. Create ECR + IAM only (no App Runner yet)
terraform apply -target=aws_ecr_repository.api \
                -target=aws_ecr_lifecycle_policy.api \
                -target=aws_iam_role.apprunner_ecr \
                -target=aws_iam_role_policy_attachment.apprunner_ecr \
                -target=aws_iam_role.apprunner_instance \
                -target=aws_iam_role_policy.secrets_access

# 3. Create secret (one-time)
aws secretsmanager create-secret \
    --name pii-shield/anthropic-api-key \
    --secret-string "sk-ant-your-key-here" \
    --region eu-central-1

# 4. Create IAM user for GitHub Actions
aws iam create-user --user-name github-actions-ecr
aws iam attach-user-policy --user-name github-actions-ecr \
    --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser
aws iam create-access-key --user-name github-actions-ecr

# 5. Add GitHub Secrets (Settings → Secrets → Actions)
#    - AWS_ACCESS_KEY_ID
#    - AWS_SECRET_ACCESS_KEY
#    - AWS_REGION_NAME (eu-central-1)
#    - ECR_REPOSITORY_NAME (pii-shield-api)

# 6. Push to main branch → GitHub Actions builds and pushes image to ECR

# 7. Create App Runner (image now exists)
terraform apply

# 8. Get API URL
terraform output api_url
```

## Deploy UI to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. Set main file: `demo/app.py`
4. Add secret in Settings → Secrets:
   ```toml
   API_URL = "https://xxx.eu-central-1.awsapprunner.com"
   ```

## Terraform Files

| File | Purpose |
|------|---------|
| `versions.tf` | Terraform + AWS provider |
| `variables.tf` | project_name, region, environment |
| `ecr.tf` | Docker image repository |
| `iam.tf` | App Runner IAM roles |
| `apprunner.tf` | App Runner service |
| `outputs.tf` | URLs and commands |

## Outputs

```bash
terraform output api_url          # FastAPI URL
terraform output api_docs_url     # Swagger docs
terraform output ecr_api_url      # ECR repository
terraform output ecr_login_command # Login to ECR
```

## Cost Estimate

| Service | Monthly Cost |
|---------|--------------|
| App Runner | ~$15-25 |
| ECR | ~$1 |
| Secrets Manager | ~$0.40 |
| **Total** | **~$17-27** |

## Cleanup

```bash
terraform destroy
```

## Troubleshooting

### Check App Runner logs

```bash
aws apprunner describe-service \
    --service-arn $(terraform output -raw service_arn) \
    --region eu-central-1
```

### Force redeploy

Push a new image to ECR - App Runner auto-deploys on push.
