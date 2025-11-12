# Quick Start Guide

Get up and running in 5 minutes!

## Setup Checklist

```bash
# 1. Install dependencies
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Create configuration
cp .env.example .env
# Edit .env with your credentials

# 3. Verify setup
python verify_setup.py

# 4. Test components
python test_email.py
python test_sharepoint.py
python test_review.py

# 5. Run the agent
python main.py --limit 5
```

## Credentials Needed

### Email (Gmail Example)
1. Enable IMAP: [Gmail Settings](https://mail.google.com/mail/u/0/#settings/fwdandpop)
2. Create App Password: [App Passwords](https://myaccount.google.com/apppasswords)
3. Add to `.env`:
   ```env
   EMAIL_ADDRESS=your-email@gmail.com
   EMAIL_PASSWORD=your-16-char-app-password
   ```

### SharePoint
1. Create Azure AD app: [Azure Portal](https://portal.azure.com)
   - Go to: Azure Active Directory → App registrations → New registration
   - Copy: Tenant ID, Client ID
   - Create: Client Secret
   - Grant: Sites.ReadWrite.All permission + admin consent

2. Create SharePoint list with columns:
   - Status (choice)
   - Priority (choice)
   - Category (choice)
   - Notes (text)
   - EmailFrom (text)
   - EmailDate (text)
   - ReferenceID (text)

3. Add to `.env`:
   ```env
   SHAREPOINT_TENANT_ID=your-tenant-id
   SHAREPOINT_CLIENT_ID=your-client-id
   SHAREPOINT_CLIENT_SECRET=your-client-secret
   SHAREPOINT_SITE_NAME=YourSiteName
   SHAREPOINT_LIST_NAME=YourListName
   ```

## Testing Commands

```bash
# Verify everything is set up correctly
python verify_setup.py

# Test email connection only
python test_email.py

# Test SharePoint connection only
python test_sharepoint.py

# Test review logic
python test_review.py

# Test with 3 emails (safe first run)
python main.py --limit 3

# Process 10 emails (default)
python main.py

# Process 20 emails
python main.py --limit 20

# Debug mode
python main.py --debug --limit 5
```

## Common Issues

**"Could not connect to email server"**
- Gmail: Use App Password, not regular password
- Enable IMAP in email settings

**"Could not authenticate with SharePoint"**
- Wait 5-10 minutes after creating Azure AD app
- Verify admin consent was granted
- Check credentials have no extra spaces

**"Could not find site/list"**
- Names are case-sensitive
- Try using IDs instead of names

**"Missing column errors"**
- Ensure all SharePoint columns are created with exact names

## Next Steps

Once working:
1. Customize review rules in `src/email_reviewer.py`
2. Set up scheduled runs (cron/Task Scheduler)
3. Enable AI review (optional):
   ```env
   REVIEW_USE_AI=true
   OPENAI_API_KEY=sk-...
   ```

## Full Documentation

- **Implementation Guide**: `IMPLEMENTATION_GUIDE.md` - Detailed step-by-step setup
- **README**: `README.md` - Full feature documentation
- **Code Reference**: See `src/` directory for source code

## Help

If stuck, check:
1. Run `python verify_setup.py` to diagnose issues
2. Use `--debug` flag for detailed logs
3. Review `IMPLEMENTATION_GUIDE.md` troubleshooting section
