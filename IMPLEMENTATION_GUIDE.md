# Implementation & Testing Guide

This guide will walk you through setting up and testing the Email Review SharePoint Agent step-by-step.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Environment Setup](#step-1-environment-setup)
3. [Step 2: Email Configuration](#step-2-email-configuration)
4. [Step 3: SharePoint Setup](#step-3-sharepoint-setup)
5. [Step 4: Testing Components](#step-4-testing-components)
6. [Step 5: Running the Agent](#step-5-running-the-agent)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Python 3.7 or higher
- A Gmail or Outlook email account
- A Microsoft 365 account with SharePoint access
- Azure AD admin permissions (to create app registration)

---

## Step 1: Environment Setup

### 1.1 Create Python Virtual Environment

```bash
cd Learning-to-code

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows
```

### 1.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 1.3 Verify Setup

```bash
python verify_setup.py
```

This will check that all dependencies are installed. Don't worry if configuration checks fail - we'll fix that next.

---

## Step 2: Email Configuration

### 2.1 Create Configuration File

```bash
cp .env.example .env
```

### 2.2 Configure Gmail (Recommended for Testing)

**Step 2.2.1: Enable IMAP**
1. Go to [Gmail Settings](https://mail.google.com/mail/u/0/#settings/fwdandpop)
2. Click "Forwarding and POP/IMAP" tab
3. Enable IMAP
4. Save changes

**Step 2.2.2: Create App Password**
1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
2. If you don't see this option, enable 2-Step Verification first
3. Select "Mail" and your device
4. Click "Generate"
5. Copy the 16-character password (remove spaces)

**Step 2.2.3: Update .env File**

Edit `.env` and set:

```env
EMAIL_SERVER=imap.gmail.com
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
EMAIL_PORT=993
```

### 2.3 Configure Outlook (Alternative)

Edit `.env` and set:

```env
EMAIL_SERVER=outlook.office365.com
EMAIL_ADDRESS=your-email@outlook.com
EMAIL_PASSWORD=your-password-or-app-password
EMAIL_PORT=993
```

### 2.4 Test Email Connection

```bash
python test_email.py
```

**Expected output:**
```
EMAIL CONNECTION TEST
============================================================

1. Testing connection to imap.gmail.com:993
   Email: your-email@gmail.com

2. Attempting to connect...
✓ Connected successfully!

3. Fetching recent emails (max 5)...
✓ Found 3 emails

Recent emails:
------------------------------------------------------------
1. From: sender@example.com
   Subject: Test Email

✓ EMAIL TEST PASSED
```

If this fails, check the [Troubleshooting](#troubleshooting) section.

---

## Step 3: SharePoint Setup

### 3.1 Create Azure AD App Registration

**Step 3.1.1: Register the App**
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to: **Azure Active Directory** → **App registrations**
3. Click **"New registration"**
4. Enter:
   - **Name**: `Email Review Agent` (or any name)
   - **Supported account types**: `Accounts in this organizational directory only`
   - **Redirect URI**: Leave empty
5. Click **"Register"**

**Step 3.1.2: Get Tenant ID and Client ID**
1. On the app's Overview page, copy:
   - **Application (client) ID** → This is your `SHAREPOINT_CLIENT_ID`
   - **Directory (tenant) ID** → This is your `SHAREPOINT_TENANT_ID`

**Step 3.1.3: Create Client Secret**
1. Click **"Certificates & secrets"** in the left menu
2. Click **"New client secret"**
3. Description: `Email Agent Secret`
4. Expires: Choose duration (recommended: 12 months)
5. Click **"Add"**
6. **IMPORTANT**: Copy the **Value** immediately → This is your `SHAREPOINT_CLIENT_SECRET`
   - You won't be able to see this again!

**Step 3.1.4: Grant API Permissions**
1. Click **"API permissions"** in the left menu
2. Click **"Add a permission"**
3. Choose **"Microsoft Graph"**
4. Choose **"Application permissions"**
5. Search for and select:
   - `Sites.ReadWrite.All`
6. Click **"Add permissions"**
7. Click **"Grant admin consent for [Your Organization]"**
8. Click **"Yes"** to confirm

### 3.2 Create SharePoint List

**Step 3.2.1: Go to SharePoint Site**
1. Navigate to your SharePoint site (e.g., `https://yourtenant.sharepoint.com/sites/YourSite`)
2. Note the site name from the URL

**Step 3.2.2: Create New List**
1. Click **"New"** → **"List"**
2. Name: `Email Tracking` (or any name you prefer)
3. Click **"Create"**

**Step 3.2.3: Add Required Columns**

The list already has `Title` by default. Add these columns:

| Column Name | Type | Choices (if applicable) |
|------------|------|------------------------|
| Status | Choice | Pending Review, Pending Approval, In Progress, Completed, Rejected, On Hold |
| Priority | Choice | Low, Medium, High, Critical |
| Category | Choice | General, Finance, Meeting, Reporting, Support, HR, Sales, Technical |
| Notes | Multiple lines of text | - |
| EmailFrom | Single line of text | - |
| EmailDate | Single line of text | - |
| ReferenceID | Single line of text | - |

**To add a column:**
1. Click **"+ Add column"**
2. Select column type
3. Enter name and options
4. Click **"Save"**

### 3.3 Update .env File

Edit `.env` and add:

```env
SHAREPOINT_TENANT_ID=your-tenant-id-from-step-3.1.2
SHAREPOINT_CLIENT_ID=your-client-id-from-step-3.1.2
SHAREPOINT_CLIENT_SECRET=your-client-secret-from-step-3.1.3
SHAREPOINT_SITE_NAME=YourSite
SHAREPOINT_LIST_NAME=Email Tracking
```

### 3.4 Test SharePoint Connection

```bash
python test_sharepoint.py
```

**Expected output:**
```
SHAREPOINT CONNECTION TEST
============================================================

1. Testing authentication
   Tenant ID: 12345678...
   Client ID: abcdef12...

2. Attempting to authenticate with Microsoft Graph...
✓ Authentication successful!

3. Testing site access...
   Looking up site by name: YourSite
   ✓ Found site ID: yourtenant.sharepoint.com,abc-123...

4. Testing list access...
   Looking up list by name: Email Tracking
   ✓ Found list ID: def-456...

5. Testing list read access...
✓ Successfully read list (found 0 items)

✓ SHAREPOINT TEST PASSED
```

---

## Step 4: Testing Components

### 4.1 Verify Complete Setup

```bash
python verify_setup.py
```

All checks should pass:
```
✓ PASS: Environment
✓ PASS: Configuration

✓ SETUP VERIFICATION PASSED
```

### 4.2 Test Review Logic

```bash
python test_review.py
```

This tests the email analysis rules with sample data:
```
EMAIL REVIEW TEST
============================================================

Testing rule-based email review...

Test 1: URGENT: Payment approval needed for Invoice #12345
------------------------------------------------------------
  ✓ priority: High ✓
  ✓ status: Pending Approval ✓
  ✓ category: Finance ✓
  ✓ Reference ID: 12345
  ✓ TEST PASSED

Results: 4 passed, 0 failed out of 4 tests
✓ ALL REVIEW TESTS PASSED
```

### 4.3 Individual Component Tests

Run each test individually to ensure everything works:

```bash
# Test email
python test_email.py

# Test SharePoint
python test_sharepoint.py

# Test review logic
python test_review.py
```

All should show `✓ PASSED` at the end.

---

## Step 5: Running the Agent

### 5.1 First Test Run (Limited)

Start with a small number of emails:

```bash
python main.py --limit 3
```

**Expected output:**
```
2024-01-15 10:30:00 - INFO - Loading configuration...
2024-01-15 10:30:00 - INFO - Starting Email Review SharePoint Agent...
2024-01-15 10:30:01 - INFO - Successfully connected to imap.gmail.com
2024-01-15 10:30:02 - INFO - Successfully authenticated with Microsoft Graph
2024-01-15 10:30:03 - INFO - Fetched 3 emails from INBOX
2024-01-15 10:30:04 - INFO - Email reviewed: Test Subject -> Pending Review
2024-01-15 10:30:05 - INFO - Created new SharePoint item: 123
2024-01-15 10:30:06 - INFO - Successfully processed 3/3 emails
✓ Agent completed successfully!
  Processed 3 emails
```

### 5.2 Check SharePoint

1. Go to your SharePoint list
2. Refresh the page
3. You should see new items created from your emails with:
   - Title (email subject)
   - Status (detected status)
   - Priority (detected priority)
   - Category (detected category)
   - EmailFrom, EmailDate, etc.

### 5.3 Production Run

Once verified, you can process more emails:

```bash
# Process 10 emails (default)
python main.py

# Process 20 emails
python main.py --limit 20

# Enable debug logging for troubleshooting
python main.py --debug --limit 5
```

### 5.4 Schedule Automatic Runs (Optional)

**Linux/Mac (cron):**
```bash
# Edit crontab
crontab -e

# Add line to run every hour
0 * * * * cd /path/to/Learning-to-code && /path/to/venv/bin/python main.py --limit 20
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily or hourly
4. Action: Start a program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `main.py --limit 20`
   - Start in: `C:\path\to\Learning-to-code`

---

## Troubleshooting

### Email Connection Issues

**Problem: "Could not connect to email server"**

Solutions:
- **Gmail**: Ensure IMAP is enabled and you're using an App Password
- **2FA**: You must use app-specific passwords if 2FA is enabled
- **Less secure apps**: Gmail no longer supports this - use App Passwords
- **Firewall**: Check that port 993 is not blocked
- **VPN**: Some VPNs block IMAP connections

**Problem: "No emails found"**

This is normal if:
- Your inbox is empty
- All emails are already read (set `unread_only=false` in config)

### SharePoint Authentication Issues

**Problem: "Could not authenticate with SharePoint"**

Solutions:
1. Verify credentials are correct (no extra spaces)
2. Check that the app registration is complete
3. Ensure API permissions are granted AND admin consent is given
4. Wait 5-10 minutes after creating the app registration
5. Try revoking and re-granting admin consent

**Problem: "Could not find site"**

Solutions:
1. Use the exact site name from the URL (case-sensitive)
2. Try using `SHAREPOINT_SITE_ID` directly instead:
   - Go to: `https://yourtenant.sharepoint.com/sites/YourSite/_api/site/id`
   - Copy the ID value
   - Set `SHAREPOINT_SITE_ID` in `.env`

**Problem: "Could not find list"**

Solutions:
1. Use the exact list name (case-sensitive)
2. Try using `SHAREPOINT_LIST_ID` directly instead:
   - Go to list Settings → Copy the list ID from URL (`List=%7B...%7D`)
   - URL decode the value
   - Set `SHAREPOINT_LIST_ID` in `.env`

**Problem: "Missing column" errors**

Solutions:
1. Ensure all columns are created with exact names (case-sensitive)
2. Check column types match the requirements
3. For Choice columns, ensure they allow custom values or have the right choices

### Review Logic Issues

**Problem: Emails categorized incorrectly**

Solutions:
1. Review the keyword patterns in `src/email_reviewer.py`
2. Customize the keywords for your use case
3. Enable AI review for better accuracy:
   ```env
   REVIEW_USE_AI=true
   OPENAI_API_KEY=your-openai-api-key
   ```

### General Issues

**Problem: Import errors**

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Problem: "Configuration error"**

```bash
# Check all required variables are set
python verify_setup.py
```

**Problem: Need more detailed logs**

```bash
# Run with debug logging
python main.py --debug --limit 5
```

---

## Advanced Configuration

### Using JSON Config Instead of .env

```bash
# Copy example
cp config.example.json config.json

# Edit config.json with your settings

# Run with config file
python main.py --config config.json --no-env
```

### Customizing Review Rules

Edit `src/email_reviewer.py` and modify the keyword lists:

```python
# Add your custom keywords
urgent_keywords = ["urgent", "asap", "immediately", "critical", "emergency", "rush"]
```

### Processing Specific Folders

Edit `.env`:

```env
# Process from a specific folder
EMAIL_FOLDER=Work
```

Or edit the folder in `config.json`.

---

## Next Steps

Once everything is working:

1. Customize review rules for your needs
2. Set up automated scheduling
3. Add more SharePoint columns if needed
4. Enable AI review for better accuracy
5. Monitor and adjust the configuration

## Getting Help

If you encounter issues:

1. Check this guide's troubleshooting section
2. Run with `--debug` flag for detailed logs
3. Review the test scripts to isolate the problem
4. Check the README.md for additional information
