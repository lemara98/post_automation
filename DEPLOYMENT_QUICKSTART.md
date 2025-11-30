# Deployment Quickstart

⚡ **Fast-track guide to get your CI/CD pipeline running**

## Choose Your Path

### 🚀 Path A: GitHub Actions (15 minutes)

**Best for**: GitHub users, fastest setup

```bash
# 1. Create GitHub repo
git init
git add .
git commit -m "Initial commit"
gh repo create betania-content-automation --public
git push -u origin main

# 2. Create Azure service principal
az ad sp create-for-rbac --name "betania-sp" \
  --role contributor \
  --scopes /subscriptions/$(az account show --query id -o tsv) \
  --sdk-auth > azure-credentials.json

# 3. Add GitHub secrets (copy values from azure-credentials.json and your .env)
gh secret set AZURE_CREDENTIALS < azure-credentials.json
gh secret set OPENAI_API_KEY --body "sk-..."
gh secret set WORDPRESS_USERNAME --body "your_username"
gh secret set WORDPRESS_PASSWORD --body "your_app_password"
gh secret set WORDPRESS_DB_HOST --body "localhost"
gh secret set WORDPRESS_DB_NAME --body "wordpress_db"
gh secret set WORDPRESS_DB_USER --body "db_user"
gh secret set WORDPRESS_DB_PASSWORD --body "db_password"
gh secret set SENDGRID_API_KEY --body "SG...."

# 4. Push and deploy
git push origin main

# 5. Watch deployment
gh run watch
```

**Done!** ✅ Check Azure Portal for your deployed Function App

---

### 🔧 Path B: Manual Terraform (10 minutes)

**Best for**: No CI/CD yet, just want infrastructure

```bash
# 1. Setup Terraform
cd terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # Fill in your secrets

# 2. Deploy infrastructure
terraform init
terraform apply -auto-approve

# 3. Deploy code manually
cd ..
func azure functionapp publish $(terraform -chdir=terraform output -raw function_app_name)
```

**Done!** ✅ Your functions are running in Azure

---

### 🏢 Path C: Azure DevOps (20 minutes)

**Best for**: Enterprise, existing Azure DevOps setup

```bash
# 1. Push to Azure Repos
git remote add origin https://dev.azure.com/YOUR_ORG/betania/_git/betania
git push -u origin main

# 2. Create Variable Group (Azure DevOps Portal)
# Pipelines → Library → + Variable group
# Name: betania-content-secrets
# Add all secrets (OPENAI_API_KEY, etc.)

# 3. Create Service Connection
# Project Settings → Service connections
# Name: Azure-ServiceConnection

# 4. Create Pipeline
# Pipelines → New pipeline → Azure Repos Git
# Select azure-pipelines.yml

# 5. Run pipeline
```

**Done!** ✅ Pipeline running, check Pipelines tab

---

## Minimal Setup (Just to Test)

Don't want full CI/CD yet? Deploy manually:

```bash
# 1. Install Azure CLI & Terraform
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform azure-functions-core-tools-4

# 2. Login to Azure
az login

# 3. Create infrastructure
cd terraform
terraform init
terraform apply

# 4. Deploy functions
cd ..
func azure functionapp publish betania-content-prod-func

# 5. Test
az functionapp log tail --name betania-content-prod-func --resource-group betania-content-prod-rg
```

---

## Verification Checklist

After deployment, verify:

```bash
# ✅ Function App exists
az functionapp show --name betania-content-prod-func --resource-group betania-content-prod-rg

# ✅ Functions are listed
az functionapp function list --name betania-content-prod-func --resource-group betania-content-prod-rg

# ✅ App settings configured
az functionapp config appsettings list --name betania-content-prod-func --resource-group betania-content-prod-rg | grep OPENAI

# ✅ Logs are flowing
az functionapp log tail --name betania-content-prod-func --resource-group betania-content-prod-rg

# ✅ Functions are enabled
az functionapp function show --name betania-content-prod-func --resource-group betania-content-prod-rg --function-name daily_content
```

---

## Quick Troubleshooting

**Problem**: Terraform fails with "Error: Insufficient permissions"

**Solution**:
```bash
# Give service principal Owner role
az role assignment create --assignee <service-principal-id> --role Owner --scope /subscriptions/<subscription-id>
```

**Problem**: Pipeline fails with "AZURE_CREDENTIALS not found"

**Solution**:
```bash
# Recreate service principal with --sdk-auth flag
az ad sp create-for-rbac --name "betania-sp" --role contributor --scopes /subscriptions/$(az account show --query id -o tsv) --sdk-auth
```

**Problem**: Functions deployed but not triggering

**Solution**:
```bash
# Check timer status
az functionapp function show --name betania-content-prod-func --resource-group betania-content-prod-rg --function-name daily_content

# Manually trigger
az functionapp function invoke --name betania-content-prod-func --resource-group betania-content-prod-rg --function-name daily_content
```

---

## Cost Estimate

```
Monthly costs with CI/CD:
├─ Function App (Consumption): $0-5
├─ Application Insights: $0-2
├─ Storage Account: $0-1
├─ OpenAI API: $15-25
├─ SendGrid: $0 (free tier)
└─ GitHub Actions: $0 (2000 min/month free)

Total: ~$15-30/month
```

---

## Next Steps After Deployment

1. **Monitor logs** - Azure Portal → Function App → Log Stream
2. **Test functions** - Wait for scheduled trigger or invoke manually
3. **Check Application Insights** - View metrics and logs
4. **Set up alerts** - Azure Monitor → Alerts → New alert rule
5. **Review costs** - Cost Management + Billing

---

## Emergency Rollback

If something breaks:

```bash
# GitHub Actions - revert to previous commit
git revert HEAD
git push origin main

# Manual - redeploy previous version
git checkout <previous-commit>
func azure functionapp publish betania-content-prod-func

# Terraform - destroy and rebuild
cd terraform
terraform destroy
terraform apply
```

---

## Full Documentation

For complete details, see:
- [CICD_SETUP.md](CICD_SETUP.md) - Complete CI/CD guide
- [README_SETUP.md](README_SETUP.md) - Application setup
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Command reference

---

**Choose your path above and start deploying!** 🚀
