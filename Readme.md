# 🚀 Task Manager API with Google Integrations

A comprehensive REST API for managing tasks that integrates with **all three Google APIs** - Gmail, Google Sheets, and Google Calendar. This is a fully functional, production-ready implementation with extensive features and proper error handling.

## ✨ Features Implemented

### 📋 Core API (Complete)

- ✅ Full CRUD operations for tasks
- ✅ SQLite database with optimized schema
- ✅ Task fields: title, description, due_date, priority, status, created_at, updated_at
- ✅ JSON responses with proper HTTP status codes
- ✅ Input validation and error handling
- ✅ Filtering and search capabilities

### 🔗 Google API Integrations (All Implemented)

#### 📧 Gmail API Integration

- ✅ Send beautiful HTML/text task reminder emails
- ✅ Email templates with task details and status
- ✅ Batch email reminders for overdue tasks
- ✅ Endpoint: `POST /tasks/{id}/email-reminder`

#### 📊 Google Sheets API Integration

- ✅ Export all tasks to formatted Google Sheets
- ✅ Multi-sheet exports (Tasks + Summary)
- ✅ Conditional formatting and styling
- ✅ Real-time statistics and analytics
- ✅ Endpoint: `POST /tasks/export-to-sheets`

#### 📅 Google Calendar API Integration

- ✅ Create calendar events from tasks with due dates
- ✅ Sync task status with calendar events (colors/titles)
- ✅ Customizable event duration and reminders
- ✅ Support for multiple calendars
- ✅ Endpoint: `POST /tasks/{id}/add-to-calendar`

### _API Endpoints_

#### Core CRUD Operations

- `GET /health` - Health check endpoint
- `GET /tasks` - List all tasks (supports filtering)
- `POST /tasks` - Create new task
- `GET /tasks/{id}` - Get specific task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

#### Google API Integrations

- `POST /tasks/{id}/email-reminder` - Send Gmail notification
- `POST /tasks/export-to-sheets` - Export to Google Sheets
- `POST /tasks/{id}/add-to-calendar` - Add to Google Calendar
- `GET /tasks/integrations` - Show integration status

#### Bonus Features

- `GET /dashboard` - Unified dashboard with statistics
- `POST /tasks/batch/email-reminders` - Batch email for overdue tasks

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Clone/navigate to project directory
cd "d:/Rompit Technologies/22-July"

# Run automated setup
python run.py setup

# Start the server
python run.py start
```

### Option 2: Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
python app.py
```

The API will be available at `http://localhost:5000`

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup instructions for Google APIs
- **[Task_Manager_API.postman_collection.json](Task_Manager_API.postman_collection.json)** - Postman collection for testing
- **[test_api.py](test_api.py)** - Automated test suite

## 🏗️ Project Structure

```
d:/Rompit Technologies/22-July/
├── app.py                          # Main Flask application
├── run.py                          # Startup and setup script
├── requirements.txt                # Python dependencies
├── config.py                       # Production configuration
├── test_api.py                     # Comprehensive test suite
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker Compose setup
├── SETUP.md                        # Detailed setup guide
├── Task_Manager_API.postman_collection.json  # API testing collection
├──
├── database/
│   ├── __init__.py
│   └── db_manager.py              # Database operations
├──
├── models/
│   ├── __init__.py
│   └── task.py                    # Task model
├──
├── google_integrations/
│   ├── __init__.py
│   ├── gmail_service.py           # Gmail API integration
│   ├── sheets_service.py          # Google Sheets integration
│   └── calendar_service.py        # Google Calendar integration
├──
├── utils/
│   ├── __init__.py
│   ├── validators.py              # Input validation
│   └── responses.py               # API response formatting
├──
└── credentials/                    # Google API credentials (not in repo)
    ├── gmail_credentials.json
    ├── sheets_credentials.json
    └── calendar_credentials.json
```

## 🧪 Testing

### Run Automated Tests

```bash
# Start the server first
python app.py

# In another terminal, run tests
python test_api.py
```

### Use Postman Collection

1. Import `Task_Manager_API.postman_collection.json` into Postman
2. Set the `baseUrl` variable to `http://localhost:5000`
3. Run the requests in the "Demo Workflow" folder

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access API at http://localhost:5000
```

## 📊 API Examples

### Create a Task

```json
POST /tasks
{
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "due_date": "2024-12-31T23:59:59",
  "priority": "high",
  "status": "pending"
}
```

### Send Email Reminder

```json
POST /tasks/1/email-reminder
{
  "recipient_email": "user@example.com"
}
```

### Export to Google Sheets

```json
POST /tasks/export-to-sheets
{
  "spreadsheet_name": "My Tasks Export"
}
```

### Add to Google Calendar

```json
POST /tasks/1/add-to-calendar
{
  "duration_minutes": 90,
  "reminder_minutes": 30,
  "location": "Office Conference Room"
}
```

## 🔧 Google API Setup

1. **Create Google Cloud Project**

   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project

2. **Enable APIs**

   - Gmail API
   - Google Sheets API
   - Google Calendar API

3. **Create OAuth 2.0 Credentials**

   - Go to APIs & Services > Credentials
   - Create OAuth 2.0 Client ID (Desktop Application)
   - Download JSON files

4. **Setup Credentials**
   - Place credential files in `credentials/` folder
   - See [SETUP.md](SETUP.md) for detailed instructions

## 🌟 Features Showcase

### Gmail Integration

- 📧 Beautiful HTML email templates
- 📝 Task details embedded in emails
- ⚠️ Overdue task notifications
- 📊 Batch email processing

### Google Sheets Integration

- 📊 Formatted spreadsheets with conditional formatting
- 📈 Summary statistics and analytics
- 🎨 Color-coded priorities and status
- 📋 Multi-sheet exports

### Google Calendar Integration

- 📅 Automatic event creation from tasks
- 🎨 Status-based color coding
- ⏰ Customizable reminders
- 🔄 Real-time task-calendar sync

## _Tech Stack_

- _Language_: Python (Flask) or Node.js (Express)
- _Database_: SQLite
- _APIs_: Gmail API + Google Sheets API + Google Calendar API

## _Implementation Strategy_

1. _Start Simple_: Build basic CRUD first
2. _Add Gmail_: Get email notifications working
3. _Add Sheets_: Implement spreadsheet export
4. _Add Calendar_: Complete with calendar integration
5. _Test Everything_: Ensure all APIs work together

## _Suggested Timeline (Flexible)_

- _45 min_: Core API and database setup
- _45 min_: Gmail API integration
- _30 min_: Google Sheets integration
- _30 min_: Google Calendar integration
- _30 min_: Testing, documentation, polish

_Total: ~3 hours (take your time to do it properly)_

## _Deliverables_

1. Working REST API with all endpoints
2. All three Google APIs integrated and functional
3. Git repository with progressive commits
4. README with setup instructions for all APIs
5. Postman collection demonstrating all features
6. Demo showing end-to-end workflow

## _Evaluation Criteria_

- ✅ Complete CRUD functionality
- ✅ Gmail API sending emails
- ✅ Google Sheets export working
- ✅ Google Calendar integration functional
- ✅ Proper error handling across all APIs
- ✅ Clean, organized code
- ✅ Good documentation
- ✅ Progressive Git commits showing development process

## _Bonus Points_

- Unified dashboard showing all integrations
- Batch operations (email all overdue tasks)
- Error recovery and retry mechanisms
- Docker containerization
- Basic authentication/API keys

## _AI Usage_

You MAY use ChatGPT/AI for:

- Google API documentation understanding
- Authentication setup guidance
- Code generation and debugging
- Learning best practices

You MUST be able to:

- Explain your architectural decisions
- Debug issues independently
- Demonstrate understanding of the code

## _Getting Started_

1. Create Google Cloud Console project
2. Enable Gmail API, Sheets API, and Calendar API
3. Generate service account credentials
4. Set up your development environment
5. Start with basic CRUD, then add APIs one by one

## _Success Looks Like_

- Create a task → Gets stored in database
- Send reminder → Email delivered via Gmail API
- Export tasks → New Google Sheet created with data
- Add to calendar → Task appears as calendar event
- All working together seamlessly

_Take the time you need to build something impressive. Focus on quality over speed!_
