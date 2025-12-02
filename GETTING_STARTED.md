# Getting Started - Complete Workflow

**This guide shows you EXACTLY what to run and in what order.**

---

## 🎯 **Understanding the Setup**

There are **TWO SEPARATE THINGS** you can do:

### **Option A: Local Development** (Start Here!)
Run the automation on your local machine for testing. **NO Azure deployment needed!**

### **Option B: Deploy to Azure** (Later!)
Deploy to Azure for automatic scheduled runs. Requires Terraform and Azure setup.

---

## 🚀 **RECOMMENDED: Start with Option A (Local)**

This gets you up and running in 10 minutes!

---

## 📋 **Option A: Local Development Setup**

### **What This Does:**
- Installs Python dependencies
- Configures your API keys
- Lets you test the system locally
- **NO cloud deployment**
- **NO Terraform needed**

### **Step-by-Step:**

#### **1. Run the master setup script:**

```bash
./SETUP.sh
```

This will:
- ✅ Check Python
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Help you configure credentials

#### **2. Get your API credentials:**

While the script is running, you'll need:

**a) OpenAI API Key** (required)
- Go to: https://platform.openai.com/api-keys
- Sign up / login
- Click "Create new secret key"
- Copy the key (starts with `sk-`)

**b) WordPress Database** (required)
- From your hosting provider:
  - Login to cPanel
  - MySQL Databases
  - Find your WordPress database name, user, password

**c) SendGrid API Key** (optional - can skip for now)
- Go to: https://signup.sendgrid.com
- Sign up (free)
- Settings → API Keys → Create
- Copy the key (starts with `SG.`)

#### **3. Test your setup:**

```bash
source venv/bin/activate
cd content_automation
python test_setup.py
```

You should see:
```
✓ Configuration loaded successfully
✓ Database connection successful
✓ WordPress API connection successful
✓ AI service initialized

Results: 6/6 tests passed
```

#### **4. Test manually running functions:**

```bash
# Test daily content generation (doesn't actually publish, just tests)
python functions/daily_content/__init__.py

# Test weekly newsletter
python functions/weekly_newsletter/__init__.py
```

### **🎉 Done with Local Setup!**

At this point you have a working system locally. You can:
- Test fetching articles
- Test AI generation
- Test WordPress publishing (manually)
- Test email sending

---

## ☁️ **Option B: Deploy to Azure (Optional)**

**Only do this AFTER Option A works locally!**

### **What This Does:**
- Creates Azure infrastructure (Function App, Storage, etc.)
- Deploys your code to Azure
- Runs automatically on schedule:
  - Daily: 9:00 AM (fetch & publish articles)
  - Weekly: Sunday 10:00 AM (send newsletter)

### **When to Do This:**
- ✅ After local testing works
- ✅ When you're ready for automation
- ✅ When you have credentials configured

### **Two Ways to Deploy:**

#### **Method 1: Manual Terraform (Simpler)**

```bash
# 1. Login to Azure
az login

# 2. Deploy infrastructure with Terraform
cd terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # Fill in your credentials
terraform init
terraform apply

# 3. Deploy code to Azure
cd ..
source venv/bin/activate
func azure functionapp publish betania-content-prod-func
```

**Time**: 15-20 minutes

---

#### **Method 2: CI/CD with GitHub Actions (Automated)**

This automatically deploys whenever you push to GitHub.

**Prerequisites:**
- Code pushed to GitHub ✅ (you already did this!)
- Azure credentials

**Steps:**

**1. Create Azure Service Principal:**
```bash
az login
az ad sp create-for-rbac --name "betania-automation" \
  --role contributor \
  --scopes /subscriptions/$(az account show --query id -o tsv) \
  --sdk-auth
```

**2. Copy the JSON output** (you'll need it next)

**3. Add secrets to GitHub:**
- Go to: https://github.com/lemara98/post_automation/settings/secrets/actions
- Click "New repository secret"
- Add these secrets:

| Secret Name | Value |
|------------|-------|
| `AZURE_CREDENTIALS` | The JSON from step 1 |
| `OPENAI_API_KEY` | Your OpenAI key |
| `WORDPRESS_DB_HOST` | Your DB host |
| `WORDPRESS_DB_NAME` | Your DB name |
| `WORDPRESS_DB_USER` | Your DB user |
| `WORDPRESS_DB_PASSWORD` | Your DB password |
| `SENDGRID_API_KEY` | Your SendGrid key |

**4. Push to GitHub:**
```bash
git push origin master
```

**5. Watch deployment:**
- Go to: https://github.com/lemara98/post_automation/actions
- Watch the pipeline run!

**Time**: 10 minutes + 8 minute deployment

**See**: [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md) for detailed guide

---

## 🗺️ **Complete Workflow Map**

```
START HERE
    ↓
┌─────────────────────────────────────────┐
│  1. Run ./SETUP.sh                      │
│     - Installs dependencies             │
│     - Creates .env file                 │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  2. Get API Credentials                 │
│     - OpenAI: platform.openai.com       │
│     - WordPress DB: From cPanel         │
│     - SendGrid: sendgrid.com (optional) │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  3. Run ./fill_env_simple.sh            │
│     - Fills .env with your keys         │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  4. Test Setup                          │
│     python test_setup.py                │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  ✅ LOCAL SETUP COMPLETE                │
│     System works on your machine!       │
└─────────────────────────────────────────┘
    ↓
    Choose deployment method:
    ↓
    ├─→ Manual Run Locally (no Azure needed)
    │   python functions/daily_content/__init__.py
    │
    ├─→ Deploy to Azure (Manual)
    │   terraform apply
    │   func azure functionapp publish
    │
    └─→ Deploy via GitHub Actions (Automated)
        Add secrets to GitHub
        git push → auto-deploy
```

---

## ❓ **Common Questions**

### **Q: Do I need to deploy to Azure to use this?**
**A:** NO! You can run everything locally for testing. Azure is only for automated scheduling.

### **Q: Do I need Terraform?**
**A:** Only if you want to deploy to Azure. For local testing, NO.

### **Q: What's the minimum I need to get started?**
**A:** Just run `./SETUP.sh` and get an OpenAI API key. That's it!

### **Q: Can I test without WordPress database?**
**A:** Partially. You can test RSS fetching and AI generation, but not publishing or newsletters.

### **Q: How much does this cost if I just test locally?**
**A:** $0! You only pay OpenAI when you actually generate content (~$0.15 per article).

### **Q: When should I deploy to Azure?**
**A:** After local testing works and you're ready for daily automation.

---

## 🆘 **Troubleshooting**

### **Setup script fails**
```bash
# Make sure you're in the right directory
cd /home/milanknezevic/Desktop/applications

# Make script executable
chmod +x SETUP.sh

# Run again
./SETUP.sh
```

### **Python not found**
```bash
# Install Python 3.10+
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

### **Can't install dependencies**
```bash
# Activate virtual environment first
source venv/bin/activate

# Then install
cd content_automation
pip install -r requirements.txt
```

### **Tests fail**
Check which specific test failed and see [CREDENTIALS_GUIDE.md](CREDENTIALS_GUIDE.md) for that service.

---

## 📚 **Documentation Index**

**Start Here:**
- **GETTING_STARTED.md** ← You are here!
- **SETUP.sh** ← Run this first

**Configuration:**
- **fill_env_simple.sh** ← Configure credentials
- **CREDENTIALS_GUIDE.md** ← Where to get each credential

**Testing:**
- `python test_setup.py` ← Test your setup

**Deployment (Later):**
- **DEPLOYMENT_QUICKSTART.md** ← Deploy to Azure
- **CICD_SETUP.md** ← Complete CI/CD guide
- **terraform/main.tf** ← Infrastructure code

**Reference:**
- **README_SETUP.md** ← Complete application guide
- **QUICK_REFERENCE.md** ← Command cheatsheet
- **COST_BREAKDOWN.md** ← Pricing details

---

## 🎯 **Quick Commands**

```bash
# Complete local setup
./SETUP.sh

# Configure credentials
./fill_env_simple.sh

# Activate Python environment
source venv/bin/activate

# Test setup
cd content_automation && python test_setup.py

# Test functions manually
python functions/daily_content/__init__.py
python functions/weekly_newsletter/__init__.py

# Deploy to Azure (later)
cd terraform && terraform apply
func azure functionapp publish betania-content-prod-func
```

---

## ✅ **Success Checklist**

- [ ] Ran `./SETUP.sh`
- [ ] Got OpenAI API key
- [ ] Got WordPress database credentials
- [ ] Ran `./fill_env_simple.sh`
- [ ] Ran `python test_setup.py` - all tests pass
- [ ] (Optional) Tested manual run
- [ ] (Optional) Deployed to Azure

---

**Need help?** Check the specific guide for your step above!

**Last Updated:** 2025-11-30
