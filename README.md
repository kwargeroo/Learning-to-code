# Email Review SharePoint Agent

An intelligent agent that automatically reviews emails and updates status in SharePoint spreadsheets. Perfect for tracking customer inquiries, support tickets, approvals, and more.

## Features

- **Email Processing**: Connects to any IMAP email server (Gmail, Outlook, etc.)
- **Intelligent Review**: Rule-based or AI-powered email analysis
- **SharePoint Integration**: Automatically updates SharePoint lists via Microsoft Graph API
- **Status Tracking**: Extracts priority, category, status, and action items from emails
- **Flexible Configuration**: Environment variables or JSON config file
- **Reference Extraction**: Identifies ticket numbers, order IDs, and other references

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Learning-to-code

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Email Configuration
EMAIL_SERVER=imap.gmail.com
EMAIL_ADDRESS=your-email@example.com
EMAIL_PASSWORD=your-app-specific-password

# SharePoint Configuration
SHAREPOINT_TENANT_ID=your-tenant-id
SHAREPOINT_CLIENT_ID=your-client-id
SHAREPOINT_CLIENT_SECRET=your-client-secret
SHAREPOINT_SITE_NAME=YourSiteName
SHAREPOINT_LIST_NAME=YourListName
```

### 3. Run the Agent

```bash
python main.py --limit 10
```

## Configuration Options

### Email Setup

**Gmail Users:**
1. Enable IMAP in Gmail settings
2. Create an [App Password](https://myaccount.google.com/apppasswords)
3. Use the app password in `EMAIL_PASSWORD`

**Outlook/Office 365:**
- Server: `outlook.office365.com`
- Use your regular password or app password

### SharePoint Setup

**Required: Azure AD App Registration**

1. Go to [Azure Portal](https://portal.azure.com) → Azure Active Directory → App registrations
2. Create a new registration
3. Note the **Tenant ID** and **Client ID**
4. Create a **Client Secret** under Certificates & secrets
5. Add API permissions:
   - Microsoft Graph → Application permissions
   - `Sites.ReadWrite.All`
   - Grant admin consent

**SharePoint List Requirements:**

Your SharePoint list should have these columns:
- `Title` (default, single line text)
- `Status` (choice: Pending Review, Pending Approval, In Progress, Completed, Rejected, On Hold)
- `Priority` (choice: Low, Medium, High, Critical)
- `Category` (choice: General, Finance, Meeting, Reporting, Support, HR, Sales, Technical)
- `Notes` (multiple lines of text)
- `EmailFrom` (single line text)
- `EmailDate` (single line text)
- `ReferenceID` (single line text, optional)

### AI Review (Optional)

Enable AI-powered email analysis with OpenAI:

```env
REVIEW_USE_AI=true
OPENAI_API_KEY=your-openai-api-key
```

## Usage

### Basic Usage

Process the 10 most recent unread emails:

```bash
python main.py
```

### Advanced Usage

```bash
# Process 20 emails
python main.py --limit 20

# Use JSON config file
python main.py --config config.json

# Don't use environment variables
python main.py --config config.json --no-env

# Enable debug logging
python main.py --debug
```

## How It Works

1. **Connect**: Agent connects to your email server and SharePoint
2. **Fetch**: Retrieves unread emails from your inbox
3. **Review**: Analyzes each email to determine:
   - Status (Pending Review, Pending Approval, etc.)
   - Priority (Low, Medium, High, Critical)
   - Category (Finance, Support, Meeting, etc.)
   - Action required (Yes/No)
   - Reference IDs (ticket numbers, order IDs)
4. **Update**: Creates or updates SharePoint list items with the review results
5. **Mark**: Marks processed emails as read (optional)

## Review Logic

### Rule-Based Review (Default)

Analyzes emails using keyword patterns:

**Priority Detection:**
- High: urgent, asap, immediately, critical, emergency
- Low: fyi, for your information, no rush

**Status Detection:**
- Pending Approval: approve, approval needed, please review
- Completed: completed, done, finished, closed
- Rejected: rejected, declined, not approved

**Category Detection:**
- Finance: invoice, payment, billing
- Meeting: meeting, schedule, calendar
- Reporting: report, analytics, data
- Support: support, help, issue, problem

### AI-Powered Review

Uses OpenAI GPT-4 to intelligently analyze email content and context for more accurate categorization.

## Project Structure

```
Learning-to-code/
├── src/
│   ├── __init__.py
│   ├── agent.py              # Main agent orchestrator
│   ├── email_client.py       # Email connection and fetching
│   ├── sharepoint_client.py  # SharePoint API integration
│   ├── email_reviewer.py     # Email analysis logic
│   └── config.py             # Configuration management
├── main.py                   # Entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment variables
├── config.example.json       # Example JSON configuration
└── README.md                 # This file
```

## Troubleshooting

### Email Connection Issues

- **Gmail**: Make sure IMAP is enabled and you're using an App Password
- **2FA**: Use app-specific passwords if 2FA is enabled
- **Firewall**: Ensure port 993 is not blocked

### SharePoint Authentication Issues

- Verify Tenant ID, Client ID, and Client Secret are correct
- Ensure API permissions are granted and admin consent is given
- Check that the app has access to the specific SharePoint site

### Missing SharePoint Columns

If you get errors about missing columns, ensure your SharePoint list has all required columns with the exact names listed in the "SharePoint Setup" section.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for learning and production use.

## Support

For issues, questions, or contributions, please open an issue on GitHub.