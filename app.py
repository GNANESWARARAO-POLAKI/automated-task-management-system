"""
Task Manager API with Google APIs Integration
A comprehensive REST API for managing tasks with Gmail, Google Sheets, and Google Calendar integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import sqlite3
import os
import json
from werkzeug.exceptions import BadRequest
import logging

# Import Google API modules
from google_integrations.gmail_service import GmailService
from google_integrations.sheets_service import SheetsService
from google_integrations.calendar_service import CalendarService
from database.db_manager import DatabaseManager
from models.task import Task
from utils.validators import TaskValidator
from utils.responses import APIResponse

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
db_manager = DatabaseManager()
gmail_service = GmailService()
sheets_service = SheetsService()
calendar_service = CalendarService()
task_validator = TaskValidator()

# Initialize database
db_manager.init_db()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return APIResponse.success({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks with optional filtering"""
    try:
        status = request.args.get('status')
        priority = request.args.get('priority')
        
        tasks = db_manager.get_all_tasks(status=status, priority=priority)
        
        return APIResponse.success({
            'tasks': [task.to_dict() for task in tasks],
            'count': len(tasks)
        })
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}")
        return APIResponse.error("Failed to fetch tasks", 500)

@app.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        
        # Validate input
        validation_result = task_validator.validate_create_task(data)
        if not validation_result['valid']:
            return APIResponse.error(validation_result['errors'], 400)
        
        # Create task
        task = Task.from_dict(data)
        task_id = db_manager.create_task(task)
        task.id = task_id
        
        logger.info(f"Created task: {task_id}")
        return APIResponse.success(task.to_dict(), 201)
        
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return APIResponse.error("Failed to create task", 500)

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task"""
    try:
        task = db_manager.get_task(task_id)
        if not task:
            return APIResponse.error("Task not found", 404)
        
        return APIResponse.success(task.to_dict())
    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {str(e)}")
        return APIResponse.error("Failed to fetch task", 500)

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    try:
        # Check if task exists
        existing_task = db_manager.get_task(task_id)
        if not existing_task:
            return APIResponse.error("Task not found", 404)
        
        data = request.get_json()
        
        # Validate input
        validation_result = task_validator.validate_update_task(data)
        if not validation_result['valid']:
            return APIResponse.error(validation_result['errors'], 400)
        
        # Update task
        success = db_manager.update_task(task_id, data)
        if not success:
            return APIResponse.error("Failed to update task", 500)
        
        # Get updated task
        updated_task = db_manager.get_task(task_id)
        
        logger.info(f"Updated task: {task_id}")
        return APIResponse.success(updated_task.to_dict())
        
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        return APIResponse.error("Failed to update task", 500)

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        # Check if task exists
        existing_task = db_manager.get_task(task_id)
        if not existing_task:
            return APIResponse.error("Task not found", 404)
        
        success = db_manager.delete_task(task_id)
        if not success:
            return APIResponse.error("Failed to delete task", 500)
        
        logger.info(f"Deleted task: {task_id}")
        return APIResponse.success({'message': 'Task deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        return APIResponse.error("Failed to delete task", 500)

@app.route('/tasks/<int:task_id>/email-reminder', methods=['POST'])
def send_email_reminder(task_id):
    """Send email reminder for a task via Gmail API"""
    try:
        # Get task
        task = db_manager.get_task(task_id)
        if not task:
            return APIResponse.error("Task not found", 404)
        
        data = request.get_json() or {}
        recipient_email = data.get('recipient_email')
        
        if not recipient_email:
            return APIResponse.error("recipient_email is required", 400)
        
        # Send email
        result = gmail_service.send_task_reminder(task, recipient_email)
        
        if result['success']:
            logger.info(f"Email reminder sent for task {task_id} to {recipient_email}")
            return APIResponse.success({
                'message': 'Email reminder sent successfully',
                'message_id': result.get('message_id')
            })
        else:
            return APIResponse.error(f"Failed to send email: {result.get('error')}", 500)
            
    except Exception as e:
        logger.error(f"Error sending email reminder for task {task_id}: {str(e)}")
        return APIResponse.error("Failed to send email reminder", 500)

@app.route('/tasks/export-to-sheets', methods=['POST'])
def export_to_sheets():
    """Export all tasks to Google Sheets"""
    try:
        data = request.get_json() or {}
        spreadsheet_name = data.get('spreadsheet_name', 'Task Manager Export')
        
        # Get all tasks
        tasks = db_manager.get_all_tasks()
        
        # Export to sheets
        result = sheets_service.export_tasks_to_sheet(tasks, spreadsheet_name)
        
        if result['success']:
            logger.info(f"Tasks exported to Google Sheets: {result.get('spreadsheet_url')}")
            return APIResponse.success({
                'message': 'Tasks exported to Google Sheets successfully',
                'spreadsheet_id': result.get('spreadsheet_id'),
                'spreadsheet_url': result.get('spreadsheet_url'),
                'tasks_count': len(tasks)
            })
        else:
            return APIResponse.error(f"Failed to export to sheets: {result.get('error')}", 500)
            
    except Exception as e:
        logger.error(f"Error exporting to sheets: {str(e)}")
        return APIResponse.error("Failed to export to Google Sheets", 500)

@app.route('/tasks/<int:task_id>/add-to-calendar', methods=['POST'])
def add_to_calendar(task_id):
    """Add task to Google Calendar"""
    try:
        # Get task
        task = db_manager.get_task(task_id)
        if not task:
            return APIResponse.error("Task not found", 404)
        
        if not task.due_date:
            return APIResponse.error("Task must have a due date to add to calendar", 400)
        
        data = request.get_json() or {}
        
        # Add to calendar
        result = calendar_service.create_event_from_task(task, data)
        
        if result['success']:
            # Update task with calendar event ID
            db_manager.update_task(task_id, {'calendar_event_id': result.get('event_id')})
            
            logger.info(f"Task {task_id} added to Google Calendar: {result.get('event_url')}")
            return APIResponse.success({
                'message': 'Task added to Google Calendar successfully',
                'event_id': result.get('event_id'),
                'event_url': result.get('event_url')
            })
        else:
            return APIResponse.error(f"Failed to add to calendar: {result.get('error')}", 500)
            
    except Exception as e:
        logger.error(f"Error adding task {task_id} to calendar: {str(e)}")
        return APIResponse.error("Failed to add to Google Calendar", 500)

@app.route('/tasks/integrations', methods=['GET'])
def get_integration_status():
    """Show integration status for all Google APIs"""
    try:
        gmail_status = gmail_service.check_connection()
        sheets_status = sheets_service.check_connection()
        calendar_status = calendar_service.check_connection()
        
        return APIResponse.success({
            'gmail': {
                'status': 'connected' if gmail_status['success'] else 'disconnected',
                'details': gmail_status.get('details', gmail_status.get('error'))
            },
            'sheets': {
                'status': 'connected' if sheets_status['success'] else 'disconnected',
                'details': sheets_status.get('details', sheets_status.get('error'))
            },
            'calendar': {
                'status': 'connected' if calendar_status['success'] else 'disconnected',
                'details': calendar_status.get('details', calendar_status.get('error'))
            }
        })
    except Exception as e:
        logger.error(f"Error checking integration status: {str(e)}")
        return APIResponse.error("Failed to check integration status", 500)

# Bonus endpoints

@app.route('/tasks/batch/email-reminders', methods=['POST'])
def batch_email_reminders():
    """Send email reminders for all overdue tasks"""
    try:
        data = request.get_json() or {}
        recipient_email = data.get('recipient_email')
        
        if not recipient_email:
            return APIResponse.error("recipient_email is required", 400)
        
        # Get overdue tasks
        overdue_tasks = db_manager.get_overdue_tasks()
        
        if not overdue_tasks:
            return APIResponse.success({'message': 'No overdue tasks found', 'sent_count': 0})
        
        # Send emails
        results = gmail_service.send_batch_reminders(overdue_tasks, recipient_email)
        
        successful_sends = sum(1 for r in results if r['success'])
        
        logger.info(f"Batch email reminders: {successful_sends}/{len(overdue_tasks)} sent successfully")
        return APIResponse.success({
            'message': f'Batch email reminders processed',
            'total_tasks': len(overdue_tasks),
            'successful_sends': successful_sends,
            'failed_sends': len(overdue_tasks) - successful_sends,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error sending batch email reminders: {str(e)}")
        return APIResponse.error("Failed to send batch email reminders", 500)

@app.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Get unified dashboard showing all integrations and statistics"""
    try:
        # Get task statistics
        total_tasks = len(db_manager.get_all_tasks())
        completed_tasks = len(db_manager.get_all_tasks(status='completed'))
        overdue_tasks = len(db_manager.get_overdue_tasks())
        pending_tasks = len(db_manager.get_all_tasks(status='pending'))
        
        # Get integration status
        gmail_status = gmail_service.check_connection()
        sheets_status = sheets_service.check_connection()
        calendar_status = calendar_service.check_connection()
        
        return APIResponse.success({
            'statistics': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': pending_tasks,
                'overdue_tasks': overdue_tasks,
                'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
            },
            'integrations': {
                'gmail': {
                    'status': 'connected' if gmail_status['success'] else 'disconnected',
                    'last_check': datetime.now().isoformat()
                },
                'sheets': {
                    'status': 'connected' if sheets_status['success'] else 'disconnected',
                    'last_check': datetime.now().isoformat()
                },
                'calendar': {
                    'status': 'connected' if calendar_status['success'] else 'disconnected',
                    'last_check': datetime.now().isoformat()
                }
            }
        })
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return APIResponse.error("Failed to get dashboard data", 500)

@app.errorhandler(404)
def not_found(error):
    return APIResponse.error("Endpoint not found", 404)

@app.errorhandler(400)
def bad_request(error):
    return APIResponse.error("Bad request", 400)

@app.errorhandler(500)
def internal_error(error):
    return APIResponse.error("Internal server error", 500)

if __name__ == '__main__':
    print("Starting Task Manager API...")
    print("Available endpoints:")
    print("- GET /health - Health check")
    print("- GET /tasks - List all tasks")
    print("- POST /tasks - Create new task")
    print("- GET /tasks/{id} - Get specific task")
    print("- PUT /tasks/{id} - Update task")
    print("- DELETE /tasks/{id} - Delete task")
    print("- POST /tasks/{id}/email-reminder - Send Gmail notification")
    print("- POST /tasks/export-to-sheets - Export to Google Sheets")
    print("- POST /tasks/{id}/add-to-calendar - Add to Google Calendar")
    print("- GET /tasks/integrations - Show integration status")
    print("- POST /tasks/batch/email-reminders - Batch email reminders")
    print("- GET /dashboard - Unified dashboard")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
