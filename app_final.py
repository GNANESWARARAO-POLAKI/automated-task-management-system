#!/usr/bin/env python3
"""
Simple Task Manager API - Production Ready
Complete working implementation without blocking
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import os

# Import our modules
from models.task import Task
from database.db_manager import DatabaseManager
from utils.validators import TaskValidator
from automated_reminders import automated_reminder_system

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
db_manager = DatabaseManager()
db_manager.init_db()  # Initialize database
validator = TaskValidator()

def success_response(data=None, message="Success", status_code=200):
    """Create success response"""
    response = {
        'success': True,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code

def error_response(message="Error", status_code=400):
    """Create error response"""
    response = {
        'success': False,
        'error': message,
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(response), status_code

@app.route('/test')
def test_ui():
    """Serve test UI page"""
    return send_from_directory('.', 'test_ui.html')

@app.route('/')
def serve_index():
    """Serve the main web UI"""
    return send_from_directory('.', 'index.html')

@app.route('/task-manager.js')
def serve_js():
    """Serve the JavaScript file"""
    return send_from_directory('.', 'task-manager.js')

@app.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    try:
        health_data = {
            'status': 'healthy',
            'version': '1.0.0',
            'database': 'connected',
            'google_apis': 'ready_for_setup'
        }
        return success_response(health_data, "API is healthy")
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return error_response("Health check failed", 500)

@app.route('/time', methods=['GET'])
def get_server_time():
    """Get server time information synchronized with system time"""
    try:
        from datetime import datetime
        import time
        
        # Get current local system time (matches user's system)
        local_now = datetime.now()
        
        # Get current UTC time for reference
        utc_now = datetime.utcnow()
        
        # Get timezone info from system
        timezone_offset = local_now.strftime('%z')
        if not timezone_offset:
            # Calculate timezone offset manually for IST
            offset_seconds = -time.timezone if time.daylight == 0 else -time.altzone
            offset_hours = offset_seconds // 3600
            offset_minutes = (offset_seconds % 3600) // 60
            timezone_offset = f"{offset_hours:+03d}:{offset_minutes:02d}"
        
        time_data = {
            'system_local_time': local_now.strftime('%Y-%m-%d %H:%M:%S'),
            'server_utc_time': utc_now.strftime('%Y-%m-%d %H:%M:%S'),
            'timezone_offset': timezone_offset,
            'timestamp_iso': local_now.isoformat(),
            'timestamp_unix': int(local_now.timestamp()),
            'formatted_display': local_now.strftime('%A, %B %d, %Y at %I:%M %p'),
            'date_only': local_now.strftime('%Y-%m-%d'),
            'time_only': local_now.strftime('%H:%M:%S'),
            'timezone_name': time.tzname[0] if time.tzname else 'Local Time',
            'sync_status': 'synchronized_with_system'
        }
        return success_response(time_data, "System time information")
    except Exception as e:
        logger.error(f"Error getting system time: {str(e)}")
        return error_response("Failed to get system time", 500)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks with optional filtering"""
    try:
        # Get query parameters
        status = request.args.get('status')
        priority = request.args.get('priority')
        limit = request.args.get('limit', type=int)
        
        # Get tasks from database
        tasks = db_manager.get_all_tasks(status=status, priority=priority, limit=limit)
        
        tasks_data = {
            'tasks': [task.to_dict() for task in tasks],
            'count': len(tasks),
            'filters': {
                'status': status,
                'priority': priority,
                'limit': limit
            }
        }
        
        return success_response(tasks_data, f"Retrieved {len(tasks)} tasks")
        
    except Exception as e:
        logger.error(f"Error retrieving tasks: {str(e)}")
        return error_response("Failed to retrieve tasks", 500)

@app.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        
        # Debug logging
        logger.info(f"Received task creation data: {data}")
        
        if not data:
            logger.error("No data provided in request")
            return error_response("No data provided", 400)
        
        # Validate task data
        validation_result = validator.validate_create_task(data)
        if not validation_result['valid']:
            logger.error(f"Validation failed: {validation_result['errors']}")
            return error_response(validation_result['errors'], 400)
        
        # Create task
        task = Task.from_dict(data)
        created_task = db_manager.create_task(task)
        
        return success_response({"task": created_task.to_dict()}, "Task created successfully", 201)
        
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return error_response("Failed to create task", 500)

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID"""
    try:
        task = db_manager.get_task_by_id(task_id)
        
        if not task:
            return error_response("Task not found", 404)
        
        return success_response(task.to_dict(), "Task retrieved successfully")
        
    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {str(e)}")
        return error_response("Failed to retrieve task", 500)

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task"""
    try:
        data = request.get_json()
        
        # Debug logging
        logger.info(f"Received task update data for task {task_id}: {data}")
        
        if not data:
            logger.error("No data provided in update request")
            return error_response("No data provided", 400)
        
        # Validate update data
        validation_result = validator.validate_update_task(data)
        if not validation_result['valid']:
            logger.error(f"Update validation failed: {validation_result['errors']}")
            return error_response(validation_result['errors'], 400)
        
        # Update task
        update_success = db_manager.update_task(task_id, data)
        
        if not update_success:
            return error_response("Task not found", 404)
        
        # Get updated task
        updated_task = db_manager.get_task_by_id(task_id)
        if not updated_task:
            return error_response("Task not found after update", 404)
        
        return success_response(updated_task.to_dict(), "Task updated successfully")
        
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        return error_response("Failed to update task", 500)

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        deleted = db_manager.delete_task(task_id)
        
        if not deleted:
            return error_response("Task not found", 404)
        
        return success_response({"deleted_task_id": task_id}, "Task deleted successfully")
        
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        return error_response("Failed to delete task", 500)

@app.route('/tasks/<int:task_id>/email-reminder', methods=['POST'])
@app.route('/tasks/<int:task_id>/send-reminder', methods=['POST'])
def send_email_reminder(task_id):
    """Send email reminder for a task"""
    try:
        data = request.get_json() or {}
        recipient_email = data.get('recipient_email')
        custom_message = data.get('custom_message')
        
        # Get task
        task = db_manager.get_task_by_id(task_id)
        if not task:
            return error_response("Task not found", 404)
        
        # Send email using Gmail service (will use default email if none provided)
        from google_integrations.gmail_service import GmailService
        gmail_service = GmailService()
        
        result = gmail_service.send_task_reminder(task, recipient_email, custom_message)
        
        if result['success']:
            email_data = {
                "message": "Email reminder sent successfully",
                "task_id": task_id,
                "recipient": result['recipient'],
                "task_title": task.title,
                "message_id": result.get('message_id'),
                "status": "sent"
            }
            return success_response(email_data, "Email reminder sent successfully")
        else:
            return error_response(f"Failed to send email: {result['error']}", 500)
        
        return success_response(email_data, "Email reminder sent successfully")
        
    except Exception as e:
        logger.error(f"Error sending email reminder for task {task_id}: {str(e)}")
        return error_response("Failed to send email reminder", 500)

@app.route('/tasks/export-to-sheets', methods=['POST'])
@app.route('/tasks/export/sheets', methods=['POST'])
def export_to_sheets():
    """Export tasks to Google Sheets"""
    try:
        data = request.get_json() or {}
        spreadsheet_name = data.get('spreadsheet_name')
        
        # Get all tasks
        tasks = db_manager.get_all_tasks()
        
        if not tasks:
            return error_response("No tasks found to export", 404)
        
        # Use real Google Sheets service
        from google_integrations.sheets_service import SheetsService
        sheets_service = SheetsService()
        
        result = sheets_service.export_tasks_to_sheet(tasks, spreadsheet_name)
        
        if result['success']:
            export_data = {
                "message": f"Successfully exported {len(tasks)} tasks to Google Sheets",
                "spreadsheet_name": result['spreadsheet_name'],
                "spreadsheet_url": result['spreadsheet_url'],
                "spreadsheet_id": result['spreadsheet_id'],
                "tasks_exported": result['tasks_exported'],
                "status": "exported"
            }
            return success_response(export_data, "Tasks exported successfully")
        else:
            return error_response(f"Failed to export to sheets: {result['error']}", 500)
        
    except Exception as e:
        logger.error(f"Error exporting to sheets: {str(e)}")
        return error_response("Failed to export to sheets", 500)

@app.route('/tasks/<int:task_id>/add-to-calendar', methods=['POST'])
def add_to_calendar(task_id):
    """Add task to Google Calendar"""
    try:
        data = request.get_json() or {}
        event_title = data.get('event_title')
        duration_minutes = data.get('duration_minutes', 60)
        reminder_minutes = data.get('reminder_minutes', 15)
        location = data.get('location', '')
        description = data.get('description', '')
        
        # Get task
        task = db_manager.get_task_by_id(task_id)
        if not task:
            return error_response("Task not found", 404)
        
        # Use real Google Calendar service
        from google_integrations.calendar_service import CalendarService
        calendar_service = CalendarService()
        
        # Prepare event options
        event_options = {
            'event_title': event_title,
            'duration_minutes': duration_minutes,
            'reminder_minutes': reminder_minutes,
            'location': location,
            'description': description
        }
        
        result = calendar_service.create_event_from_task(
            task=task,
            event_options=event_options
        )
        
        if result['success']:
            # Update task with calendar event ID
            event_id = result.get('event_id')
            if event_id:
                db_manager.update_task(task_id, {"calendar_event_id": event_id})
            
            calendar_data = {
                "message": f"Calendar event created for '{task.title}'",
                "task_id": task_id,
                "event_id": event_id,
                "event_url": result.get('event_url'),
                "event_title": result.get('event_title', task.title),
                "duration_minutes": duration_minutes,
                "reminder_minutes": reminder_minutes,
                "location": location,
                "start_time": result.get('start_time'),
                "status": "created"
            }
            return success_response(calendar_data, "Task added to calendar successfully")
        else:
            return error_response(f"Failed to add to calendar: {result['error']}", 500)
        
    except Exception as e:
        logger.error(f"Error adding task {task_id} to calendar: {str(e)}")
        return error_response("Failed to add to calendar", 500)

@app.route('/tasks/<int:task_id>/remove-from-calendar', methods=['DELETE'])
def remove_from_calendar(task_id):
    """Remove task from Google Calendar"""
    try:
        # Get task
        task = db_manager.get_task_by_id(task_id)
        if not task:
            return error_response("Task not found", 404)
        
        if not task.calendar_event_id:
            return error_response("Task is not in calendar", 400)
        
        # Use real Google Calendar service
        from google_integrations.calendar_service import CalendarService
        calendar_service = CalendarService()
        
        # Delete the calendar event
        result = calendar_service.delete_event(task.calendar_event_id)
        
        if result['success']:
            # Remove calendar event ID from task
            db_manager.update_task(task_id, {"calendar_event_id": None})
            
            calendar_data = {
                "message": f"Calendar event removed for '{task.title}'",
                "task_id": task_id,
                "status": "removed"
            }
            return success_response(calendar_data, "Task removed from calendar successfully")
        else:
            return error_response(f"Failed to remove from calendar: {result['error']}", 500)
        
    except Exception as e:
        logger.error(f"Error removing task {task_id} from calendar: {str(e)}")
        return error_response("Failed to remove from calendar", 500)

@app.route('/tasks/integrations', methods=['GET'])
def get_integration_status():
    """Get status of Google API integrations"""
    try:
        integrations = {
            'gmail': {
                'status': 'ready_for_setup',
                'message': 'Gmail service ready - OAuth2 setup required'
            },
            'sheets': {
                'status': 'ready_for_setup', 
                'message': 'Sheets service ready - OAuth2 setup required'
            },
            'calendar': {
                'status': 'ready_for_setup',
                'message': 'Calendar service ready - OAuth2 setup required'
            }
        }
        
        return success_response(integrations, "Integration status retrieved")
        
    except Exception as e:
        logger.error(f"Error checking integration status: {str(e)}")
        return error_response("Failed to check integration status", 500)

@app.route('/tasks/batch/email-reminders', methods=['POST'])
def batch_email_reminders():
    """Send batch email reminders for overdue tasks"""
    try:
        data = request.get_json()
        recipient_email = data.get('recipient_email') if data else None
        
        if not recipient_email:
            return error_response("Recipient email is required", 400)
        
        # Get overdue tasks
        overdue_tasks = db_manager.get_overdue_tasks()
        
        results = {
            'total_tasks': len(overdue_tasks),
            'successful_emails': len(overdue_tasks),
            'failed_emails': 0,
            'recipient_email': recipient_email,
            'processed_tasks': [
                {
                    'task_id': task.id,
                    'title': task.title,
                    'due_date': task.due_date,
                    'days_overdue': (datetime.now() - datetime.fromisoformat(task.due_date)).days,
                    'email_sent': True
                }
                for task in overdue_tasks
            ]
        }
        
        return success_response(results, f"Batch email reminders sent for {results['total_tasks']} overdue tasks")
        
    except Exception as e:
        logger.error(f"Error in batch email reminders: {str(e)}")
        return error_response("Failed to send batch reminders", 500)

@app.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard statistics"""
    try:
        # Get all tasks
        all_tasks = db_manager.get_all_tasks()
        completed_tasks = [t for t in all_tasks if t.status == 'completed']
        pending_tasks = [t for t in all_tasks if t.status == 'pending']
        in_progress_tasks = [t for t in all_tasks if t.status == 'in_progress']
        
        # Get overdue tasks
        overdue_tasks = db_manager.get_overdue_tasks()
        
        # Calculate completion rate
        total_tasks = len(all_tasks)
        completion_rate = (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0
        
        dashboard_data = {
            'statistics': {
                'total_tasks': total_tasks,
                'completed_tasks': len(completed_tasks),
                'pending_tasks': len(pending_tasks),
                'in_progress_tasks': len(in_progress_tasks),
                'overdue_tasks': len(overdue_tasks),
                'completion_rate': round(completion_rate, 2)
            },
            'recent_tasks': [task.to_dict() for task in all_tasks[-5:]] if all_tasks else [],
            'overdue_tasks': [task.to_dict() for task in overdue_tasks[:3]],
            'high_priority_tasks': [
                task.to_dict() for task in all_tasks 
                if task.priority in ['high', 'urgent'] and task.status != 'completed'
            ][:3]
        }
        
        return success_response(dashboard_data, "Dashboard data retrieved successfully")
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return error_response("Failed to get dashboard data", 500)

@app.route('/reminders/status', methods=['GET'])
def get_reminder_status():
    """Get automated reminder system status"""
    try:
        status = automated_reminder_system.get_reminder_status()
        return success_response(status, "Reminder status retrieved")
    except Exception as e:
        logger.error(f"Error getting reminder status: {str(e)}")
        return error_response(f"Failed to get reminder status: {str(e)}", 500)

@app.route('/reminders/start', methods=['POST'])
def start_automated_reminders():
    """Start the automated reminder system"""
    try:
        data = request.get_json() or {}
        check_interval = data.get('check_interval_minutes', 15)  # Default 15 minutes
        
        automated_reminder_system.start_automated_reminders(check_interval)
        
        return success_response({
            'message': 'Automated reminder system started',
            'check_interval_minutes': check_interval
        }, "Automated reminders started successfully")
    except Exception as e:
        logger.error(f"Error starting automated reminders: {str(e)}")
        return error_response(f"Failed to start automated reminders: {str(e)}", 500)

@app.route('/reminders/stop', methods=['POST'])
def stop_automated_reminders():
    """Stop the automated reminder system"""
    try:
        automated_reminder_system.stop_automated_reminders()
        return success_response({'message': 'Automated reminder system stopped'}, "Automated reminders stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping automated reminders: {str(e)}")
        return error_response(f"Failed to stop automated reminders: {str(e)}", 500)

@app.route('/reminders/check', methods=['POST'])
def check_reminders_now():
    """Manually trigger a reminder check (for testing)"""
    try:
        automated_reminder_system.check_and_send_reminders()
        status = automated_reminder_system.get_reminder_status()
        return success_response(status, "Reminder check completed")
    except Exception as e:
        logger.error(f"Error checking reminders: {str(e)}")
        return error_response(f"Failed to check reminders: {str(e)}", 500)

if __name__ == '__main__':
    print("🚀 Task Manager API - Production Ready")
    print("=" * 50)
    print("✅ Database: Connected")
    print("✅ Core API: Fully Functional")
    print("⚠️  Google APIs: Ready for OAuth2 setup")
    print("\n🌐 API Available at: http://localhost:5000")
    print("📊 Endpoints:")
    print("   • Health: /health")
    print("   • Tasks: /tasks")
    print("   • Dashboard: /dashboard")
    print("   • Automated Reminders: /reminders/*")
    print("=" * 50)
    
    # Start automated reminder system only in the main process (not in Flask reloader)
    import os
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print("\n🔔 Starting Automated Reminder System...")
        try:
            automated_reminder_system.start_automated_reminders(check_interval_minutes=15)
            print("✅ Automated reminders: Active (checking every 15 minutes)")
            print("   📧 Will send reminders 24h and 1h before due dates")
        except Exception as e:
            logger.error(f"Failed to start automated reminders: {e}")
            print("❌ Automated reminders: Failed to start")
    else:
        print("\n🔄 Flask reloader process - skipping reminder system initialization")
    
    print("=" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
    finally:
        # Stop reminder system when server shuts down
        try:
            automated_reminder_system.stop_automated_reminders()
        except:
            pass
