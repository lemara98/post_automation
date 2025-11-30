# CI/CD Setup Guide

Complete guide for deploying the Betania Content Automation with Infrastructure as Code (Terraform) and automated CI/CD pipelines.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Terraform Setup](#terraform-setup)
4. [CI/CD Options](#cicd-options)
   - [Option A: GitHub Actions](#option-a-github-actions-recommended)
   - [Option B: Azure DevOps](#option-b-azure-devops)
5. [Deployment Steps](#deployment-steps)
6. [Troubleshooting](#troubleshooting)

---

## Overview

### What Gets Deployed

```
Terraform creates:
├── Resource Group
├── Storage Account (for Functions)
├── Application Insights (monitoring)
├── App Service Plan (Consumption - serverless)
└── Linux Function App (Python 3.11)

CI/CD Pipeline:
├── Build: Install dependencies, run tests
├── Infrastructure: Terraform apply
└── Deploy: Push code to Azure Functions
```

### Benefits

✅ **Repeatable deployments** - Same infrastructure every time
✅ **Version controlled** - All changes tracked in git
✅ **Automated** - Push to main → auto-deploy
✅ **Safe** - Review changes before applying
✅ **Rollback ready** - Revert to any previous commit

---

## Prerequisites

### Required Tools (Local Development)

```bash
# Install Terraform
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Verify installations
terraform --version  # Should be 1.6.0+
az --version
```

### Azure Prerequisites

1. **Azure Subscription** (free tier works)
2. **Service Principal** (for automation)

Create service principal:

```bash
# Login to Azure
az login

# Create service principal
az ad sp create-for-rbac --name "betania-content-automation" \
  --role contributor \
  --scopes /subscriptions/{subscription-id} \
  --sdk-auth

# Save the output - you'll need this for secrets!
```

### Required Secrets

Gather these credentials:

- ✅ OpenAI API key
- ✅ WordPress admin username + application password
- ✅ WordPress database credentials
- ✅ SendGrid API key
- ✅ Azure service principal credentials (from above)

---

## Terraform Setup

### 1. Configure Terraform Variables

```bash
cd terraform

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

**terraform.tfvars** (NEVER commit this file!):

```hcl
environment = "prod"
location    = "eastus"
project_name = "betania-content"

openai_api_key         = "sk-..."
wordpress_username     = "your_username"
wordpress_password     = "xxxx xxxx xxxx xxxx"
wordpress_db_host      = "localhost"
wordpress_db_name      = "wordpress_db"
wordpress_db_user      = "db_user"
wordpress_db_password  = "db_password"
sendgrid_api_key       = "SG...."
```

### 2. Initialize Terraform

```bash
cd terraform

# Initialize
terraform init

# Validate configuration
terraform validate

# Preview changes
terraform plan

# Apply (creates resources in Azure)
terraform apply
```

### 3. Verify Infrastructure

```bash
# Check outputs
terraform output

# Should show:
# function_app_name = "betania-content-prod-func"
# resource_group_name = "betania-content-prod-rg"
```

### 4. Manual Deployment (Optional)

If you want to deploy code manually first:

```bash
# Go back to project root
cd ..

# Deploy using Azure CLI
func azure functionapp publish betania-content-prod-func
```

---

## CI/CD Options

Choose **ONE** of these options based on where your code is hosted.

---

## Option A: GitHub Actions (Recommended)

Best for: GitHub repositories, simpler setup, free for public repos

### 1. Push Code to GitHub

```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/betania-content-automation.git
git branch -M main
git push -u origin main
```

### 2. Configure GitHub Secrets

Go to: **Repository → Settings → Secrets and variables → Actions**

Add these secrets:

| Secret Name | Value | Where to get |
|------------|-------|--------------|
| `AZURE_CREDENTIALS` | Service principal JSON | Output from `az ad sp create-for-rbac` |
| `OPENAI_API_KEY` | `sk-...` | OpenAI dashboard |
| `WORDPRESS_USERNAME` | Your WP username | WordPress admin |
| `WORDPRESS_PASSWORD` | Application password | WordPress → Users → Profile |
| `WORDPRESS_DB_HOST` | Database host | Hosting provider |
| `WORDPRESS_DB_NAME` | Database name | Hosting provider |
| `WORDPRESS_DB_USER` | Database user | Hosting provider |
| `WORDPRESS_DB_PASSWORD` | Database password | Hosting provider |
| `SENDGRID_API_KEY` | `SG....` | SendGrid dashboard |

**AZURE_CREDENTIALS format:**
```json
{
  "clientId": "xxx",
  "clientSecret": "xxx",
  "subscriptionId": "xxx",
  "tenantId": "xxx"
}
```

### 3. Enable GitHub Actions

The workflow file is already created at `.github/workflows/deploy.yml`

To trigger deployment:

```bash
# Push to main branch
git push origin main

# Or manually trigger
# GitHub → Actions → Deploy to Azure → Run workflow
```

### 4. Monitor Deployment

1. Go to **Actions** tab in GitHub
2. Click on the running workflow
3. Watch each step complete
4. Check for ✅ or ❌

### 5. Verify Deployment

After successful deployment:

```bash
# Check function app
curl https://betania-content-prod-func.azurewebsites.net

# Check logs in Azure Portal
az functionapp log tail --name betania-content-prod-func \
  --resource-group betania-content-prod-rg
```

---

## Option B: Azure DevOps

Best for: Azure DevOps users, enterprise environments

### 1. Create Azure DevOps Project

1. Go to: https://dev.azure.com
2. Create new project: "Betania Content Automation"

### 2. Push Code to Azure Repos

```bash
# Get repo URL from Azure DevOps
git remote add origin https://dev.azure.com/YOUR_ORG/betania-content-automation/_git/betania-content-automation

git push -u origin main
```

### 3. Create Variable Group

1. Go to **Pipelines → Library**
2. Create variable group: `betania-content-secrets`
3. Add these variables (mark as secret):

   - `OPENAI_API_KEY`
   - `WORDPRESS_USERNAME`
   - `WORDPRESS_PASSWORD`
   - `WORDPRESS_DB_HOST`
   - `WORDPRESS_DB_NAME`
   - `WORDPRESS_DB_USER`
   - `WORDPRESS_DB_PASSWORD`
   - `SENDGRID_API_KEY`

### 4. Create Service Connection

1. Go to **Project Settings → Service connections**
2. Create **Azure Resource Manager** connection
3. Name it: `Azure-ServiceConnection`
4. Use Service Principal authentication
5. Select your subscription

### 5. Create Pipeline

1. Go to **Pipelines → Create Pipeline**
2. Select **Azure Repos Git**
3. Select your repository
4. Choose **Existing Azure Pipelines YAML file**
5. Select `/azure-pipelines.yml`
6. Click **Run**

### 6. Monitor Pipeline

Watch the pipeline run through stages:
1. Build → 2. Infrastructure → 3. Deploy → 4. Post-Deployment

---

## Deployment Steps (Complete Workflow)

### First-Time Setup

```bash
# 1. Configure Terraform locally
cd terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # Fill in secrets

# 2. Create infrastructure
terraform init
terraform plan
terraform apply

# 3. Setup CI/CD (choose GitHub Actions OR Azure DevOps)
# Follow steps above for your chosen platform

# 4. Push code
git add .
git commit -m "Setup CI/CD"
git push origin main

# 5. Watch deployment
# GitHub: Actions tab
# Azure DevOps: Pipelines tab
```

### Regular Deployments

After initial setup, deployments are automatic:

```bash
# 1. Make changes
nano services/rss_aggregator.py

# 2. Commit and push
git add .
git commit -m "Add new RSS feed"
git push origin main

# 3. Automatic deployment triggers
# ✅ Build → ✅ Infrastructure → ✅ Deploy
```

### Manual Terraform Updates

If you only need to update infrastructure:

```bash
cd terraform

# Edit configuration
nano main.tf

# Apply changes
terraform plan
terraform apply
```

---

## Terraform State Management

### Option 1: Local State (Default)

Terraform state is stored locally in `terraform/terraform.tfstate`

⚠️ **Not recommended for teams** - state conflicts possible

### Option 2: Remote State (Recommended for Production)

Store state in Azure Storage:

```bash
# 1. Create storage account for state
az storage account create \
  --name betaniatfstate \
  --resource-group betania-terraform-state \
  --sku Standard_LRS

# 2. Create container
az storage container create \
  --name tfstate \
  --account-name betaniatfstate

# 3. Uncomment backend in terraform/main.tf
# Lines 13-18

# 4. Re-initialize
cd terraform
terraform init -migrate-state
```

Benefits:
- ✅ Team collaboration
- ✅ State locking
- ✅ No local state files

---

## Environment Management

### Multiple Environments (Dev/Prod)

Create separate workspaces:

```bash
cd terraform

# Create dev environment
terraform workspace new dev
terraform apply -var="environment=dev"

# Create prod environment
terraform workspace new prod
terraform apply -var="environment=prod"

# Switch between environments
terraform workspace select dev
terraform workspace select prod
```

Or use separate `.tfvars` files:

```bash
# dev.tfvars
environment = "dev"
project_name = "betania-content-dev"

# prod.tfvars
environment = "prod"
project_name = "betania-content"

# Apply
terraform apply -var-file="dev.tfvars"
terraform apply -var-file="prod.tfvars"
```

---

## Monitoring & Logging

### Application Insights

View logs in Azure Portal:

1. Go to Function App → Application Insights
2. Click "Logs"
3. Query examples:

```kusto
// All logs from past hour
traces
| where timestamp > ago(1h)
| order by timestamp desc

// Errors only
traces
| where severityLevel >= 3
| where timestamp > ago(24h)

// Function executions
requests
| where name contains "daily_content"
| summarize count() by bin(timestamp, 1h)
```

### Cost Monitoring

Track Azure costs:

```bash
# Check current costs
az consumption usage list \
  --start-date 2025-11-01 \
  --end-date 2025-11-30

# Set budget alerts in Azure Portal
# Cost Management → Budgets → Create
```

---

## Troubleshooting

### Terraform Errors

**Error: Resource already exists**
```bash
# Import existing resource
terraform import azurerm_resource_group.main /subscriptions/{sub-id}/resourceGroups/betania-content-prod-rg

# Or destroy and recreate
terraform destroy
terraform apply
```

**Error: State lock**
```bash
# Force unlock (use with caution!)
terraform force-unlock <lock-id>
```

### Pipeline Failures

**Build fails: "Module not found"**
- Check `requirements.txt` is complete
- Verify Python version matches (3.11)

**Terraform fails: "Invalid credentials"**
- Verify service principal hasn't expired
- Check secret values in GitHub/Azure DevOps

**Deploy fails: "Function app not found"**
- Verify Terraform apply completed successfully
- Check function app name matches in pipeline

### Deployment Issues

**Functions not triggering**
```bash
# Check function status
az functionapp function show \
  --name betania-content-prod-func \
  --resource-group betania-content-prod-rg \
  --function-name daily_content

# Enable function
az functionapp config appsettings set \
  --name betania-content-prod-func \
  --resource-group betania-content-prod-rg \
  --settings "AzureWebJobsStorage=<connection-string>"
```

**Logs not showing**
- Wait 5-10 minutes for Application Insights to sync
- Check connection string is set correctly
- Verify instrumentation key in app settings

---

## Best Practices

### Security

1. ✅ Never commit `.tfvars` files
2. ✅ Use Azure Key Vault for production secrets
3. ✅ Rotate service principal credentials quarterly
4. ✅ Enable MFA on Azure account
5. ✅ Use managed identities where possible

### Git Workflow

```bash
# Use feature branches
git checkout -b feature/new-rss-feed
# Make changes
git commit -m "Add new RSS feed"
git push origin feature/new-rss-feed
# Create PR → Review → Merge to main → Auto-deploy
```

### Cost Optimization

1. Use Consumption Plan (Y1) for Function App
2. Set max scale-out limit to prevent unexpected costs
3. Use free tier Application Insights
4. Monitor monthly spending in Azure Portal

### Testing

```bash
# Always test locally first
python test_setup.py

# Test individual functions
python functions/daily_content/__init__.py

# Then deploy to production
```

---

## Cleanup / Teardown

To remove all Azure resources:

```bash
cd terraform

# Preview what will be destroyed
terraform plan -destroy

# Destroy all resources
terraform destroy

# Confirm with 'yes'
```

**Warning**: This will delete:
- Function App
- Application Insights (including logs)
- Storage Account
- All data

---

## Next Steps

After successful deployment:

1. ✅ Monitor first few runs in Application Insights
2. ✅ Adjust schedule if needed (`function.json`)
3. ✅ Set up Azure Monitor alerts for errors
4. ✅ Configure auto-scaling limits
5. ✅ Document any custom changes

---

## Support & Resources

- **Terraform Docs**: https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs
- **Azure Functions**: https://learn.microsoft.com/azure/azure-functions/
- **GitHub Actions**: https://docs.github.com/actions
- **Azure DevOps**: https://learn.microsoft.com/azure/devops/

---

**Last Updated**: 2025-11-30
**Version**: 1.0
