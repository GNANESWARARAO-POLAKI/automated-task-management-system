# Task Manager API Setup Guide

## Prerequisites

1. Python 3.8 or higher
2. Google Cloud Console account
3. Git (for version control)

## Installation Steps

### 1. Clone and Setup Environment

```bash
# Navigate to project directory
cd "d:/Rompit Technologies/22-July"

# Create virtual environment (recommended)
python -m venv task_manager_env

# Activate virtual environment
# On Windows:
task_manager_env\Scripts\activate
# On macOS/Linux:
source task_manager_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Google Cloud Console Setup

#### A. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your project ID

#### B. Enable APIs

Enable the following APIs in your Google Cloud project:

1. Gmail API: https://console.cloud.google.com/apis/library/gmail.googleapis.com
2. Google Sheets API: https://console.cloud.google.com/apis/library/sheets.googleapis.com
3. Google Calendar API: https://console.cloud.google.com/apis/library/calendar-json.googleapis.com

#### C. Create Service Account (Option 1 - Recommended)

1. Go to IAM & Admin > Service Accounts
2. Click "Create Service Account"
3. Fill in details:
   - Name: `task-manager-service`
   - Description: `Service account for Task Manager API`
4. Click "Create and Continue"
5. Grant roles:
   - `Editor` (or specific API roles)
6. Click "Continue" then "Done"
7. Click on the created service account
8. Go to "Keys" tab
9. Click "Add Key" > "Create New Key"
10. Choose JSON format
11. Download the key file

#### D. Create OAuth 2.0 Credentials (Option 2 - Alternative)

1. Go to APIs & Services > Credentials
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop Application"
4. Name it "Task Manager API"
5. Download the JSON file

### 3. Credential Setup

Create a `credentials` folder in the project root and add your credential files:

```
d:/Rompit Technologies/22-July/
├── credentials/
│   ├── gmail_credentials.json      # OAuth credentials for Gmail
│   ├── sheets_credentials.json     # OAuth credentials for Sheets
│   ├── calendar_credentials.json   # OAuth credentials for Calendar
│   └── service_account.json        # Service account key (if using)
```

**Important:**

- For OAuth: Download the OAuth JSON file and rename/copy it for each service
- For Service Account: Use the downloaded service account JSON file
- Never commit these files to version control!

### 4. Environment Variables (Optional)

Create a `.env` file in the project root:

```env
# Google Cloud Project
GOOGLE_CLOUD_PROJECT_ID=your-project-id

# Database
DATABASE_PATH=task_manager.db

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### 5. Database Initialization

The database will be automatically created when you first run the application.

### 6. First Run and OAuth Setup

```bash
# Run the application
python app.py
```

On first run, you'll be prompted to authenticate with Google for each service:

1. Gmail API authentication
2. Google Sheets API authentication
3. Google Calendar API authentication

Follow the browser prompts to grant permissions.

### 7. Test the Setup

```bash
# Test API health
curl http://localhost:5000/health

# Test integrations status
curl http://localhost:5000/tasks/integrations
```

## API Endpoints

### Core CRUD Operations

- `GET /tasks` - List all tasks
- `POST /tasks` - Create new task
- `GET /tasks/{id}` - Get specific task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

### Google API Integrations

- `POST /tasks/{id}/email-reminder` - Send Gmail notification
- `POST /tasks/export-to-sheets` - Export to Google Sheets
- `POST /tasks/{id}/add-to-calendar` - Add to Google Calendar
- `GET /tasks/integrations` - Show integration status

### Bonus Features

- `POST /tasks/batch/email-reminders` - Batch email reminders
- `GET /dashboard` - Unified dashboard

## Usage Examples

### Create a Task

```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive API documentation",
    "due_date": "2024-12-31T23:59:59",
    "priority": "high",
    "status": "pending"
  }'
```

### Send Email Reminder

```bash
curl -X POST http://localhost:5000/tasks/1/email-reminder \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "user@example.com"
  }'
```

### Export to Google Sheets

```bash
curl -X POST http://localhost:5000/tasks/export-to-sheets \
  -H "Content-Type: application/json" \
  -d '{
    "spreadsheet_name": "My Tasks Export"
  }'
```

### Add to Google Calendar

```bash
curl -X POST http://localhost:5000/tasks/1/add-to-calendar \
  -H "Content-Type: application/json" \
  -d '{
    "duration_minutes": 90,
    "reminder_minutes": 30,
    "location": "Office Conference Room"
  }'
```

## Troubleshooting

### Common Issues

1. **Import errors for Google libraries**

   ```bash
   pip install google-auth google-auth-oauthlib google-api-python-client
   ```

2. **Credentials not found**

   - Ensure credential files are in the `credentials/` folder
   - Check file names match the expected names
   - Verify file permissions

3. **OAuth authentication fails**

   - Check that APIs are enabled in Google Cloud Console
   - Verify OAuth consent screen is configured
   - Try deleting token files and re-authenticating

4. **Database errors**

   - Ensure write permissions in project directory
   - Delete database file to reset if corrupted

5. **API connection issues**
   - Check internet connectivity
   - Verify Google Cloud project settings
   - Confirm API quotas aren't exceeded

### Testing Individual Services

Test each Google service separately:

```python
# Test Gmail service
from google_integrations.gmail_service import GmailService
gmail = GmailService()
print(gmail.check_connection())

# Test Sheets service
from google_integrations.sheets_service import SheetsService
sheets = SheetsService()
print(sheets.check_connection())

# Test Calendar service
from google_integrations.calendar_service import CalendarService
calendar = CalendarService()
print(calendar.check_connection())
```

## Security Notes

1. **Never commit credential files to version control**
2. **Use service accounts for production**
3. **Implement proper authentication for API endpoints**
4. **Use HTTPS in production**
5. **Regularly rotate API keys**

## Production Deployment

For production deployment:

1. Use environment variables for credentials
2. Implement proper logging
3. Add rate limiting
4. Use a production WSGI server (e.g., Gunicorn)
5. Set up proper monitoring
6. Use a production database (PostgreSQL/MySQL)

## Support

If you encounter issues:

1. Check the logs in the console
2. Verify all prerequisites are met
3. Test individual components
4. Review Google Cloud Console for API usage and errors
5. Check the project documentation
