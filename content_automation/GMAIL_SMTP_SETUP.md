# Gmail SMTP Setup Guide

This guide explains how to switch from SendGrid to Gmail SMTP for sending newsletters.

## Why Use Gmail SMTP?

**Pros:**
- ✅ Shows your G Suite profile picture
- ✅ Emails come directly from Google servers
- ✅ More personal feel for subscribers
- ✅ No third-party service dependency

**Cons:**
- ❌ Sending limit: 2,000 emails/day for G Suite
- ❌ Potential spam issues for bulk sending
- ❌ Less reliable for large newsletters
- ❌ No built-in analytics

## Setup Steps

### Step 1: Create Google App Password

Since you have 2-factor authentication enabled on your G Suite account, you need an app-specific password:

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** in the left sidebar
3. Under "Signing in to Google", click **2-Step Verification**
4. Scroll down and click **App passwords**
5. Select:
   - **App:** Mail
   - **Device:** Other (Custom name)
   - Name it: "Betania Newsletter"
6. Click **Generate**
7. Copy the 16-character password (you'll need this in Step 2)

### Step 2: Update Your `.env` File

Add these lines to your `.env` file:

```bash
# Email Provider (choose: "sendgrid" or "gmail")
EMAIL_PROVIDER=gmail

# Gmail SMTP Configuration
GMAIL_EMAIL=newsletter@betania.io
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx  # Paste the 16-character password from Step 1
GMAIL_FROM_NAME=Betania Tech Newsletter
```

### Step 3: Test It

Run the test email script:

```bash
source venv/bin/activate
cd content_automation
python test_email_detailed.py
```

You should see: `✓ Email service initialized (Gmail SMTP)`

### Step 4: Send a Newsletter

```bash
python functions/weekly_newsletter/__init__.py
```

Now the emails will be sent directly through your G Suite account and will show your profile picture!

## Switching Back to SendGrid

If you want to switch back to SendGrid, just change your `.env`:

```bash
EMAIL_PROVIDER=sendgrid
```

That's it! The code automatically detects which provider to use.

## Troubleshooting

### Error: "Username and Password not accepted"
- Make sure you're using the **App Password**, not your regular Gmail password
- Check that 2-Step Verification is enabled on your Google account

### Error: "SMTPAuthenticationError"
- Verify the email address matches: `newsletter@betania.io`
- Make sure the App Password is entered correctly (16 characters)

### Emails going to spam
- Gmail SMTP may have lower deliverability than SendGrid for bulk emails
- Consider keeping SendGrid for newsletters and using Gmail only for transactional emails

## Deployment to Azure

When deploying to Azure Functions, add these environment variables:

```bash
EMAIL_PROVIDER=gmail
GMAIL_EMAIL=newsletter@betania.io
GMAIL_APP_PASSWORD=your-app-password-here
GMAIL_FROM_NAME=Betania Tech Newsletter
```

## Recommendation

For your use case:
- **Use Gmail SMTP** if you're sending < 500 emails/week
- **Use SendGrid** if you're sending > 500 emails/week or want better analytics

You can even use both:
- Gmail for confirmation emails (personal touch)
- SendGrid for weekly newsletters (better deliverability)

Just switch `EMAIL_PROVIDER` based on which function is running!
