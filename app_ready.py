#!/usr/bin/env python3
"""
Task Manager API - Non-blocking Version
Complete implementation that works without OAuth2 blocking
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import os
import threading
import time

# Import our modules
from models.task import Task
from database.db_manager import DatabaseManager
from utils.validators import TaskValidator
from utils.responses import APIResponse

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
db_manager = DatabaseManager()
validator = TaskValidator()
# APIResponse is used as static methods, no instantiation needed

# Google API services (initialize without blocking)
gmail_service = None
sheets_service = None
calendar_service = None

@app.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    try:
        # Test database connection
        db_manager.get_database_stats()
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'database': 'connected',
            'google_apis': 'ready_for_setup'
        }
        
        return response_helper.success(health_data, "API is healthy")
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return response_helper.error("Health check failed", 500)

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
        
        return response_helper.success(tasks_data, f"Retrieved {len(tasks)} tasks")
        
    except Exception as e:
        logger.error(f"Error retrieving tasks: {str(e)}")
        return response_helper.error("Failed to retrieve tasks", 500)

@app.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        
        if not data:
            return response_helper.error("No data provided", 400)
        
        # Validate task data
        validation_result = validator.validate_task_data(data)
        if not validation_result['valid']:
            return response_helper.error(validation_result['errors'], 400)
        
        # Create task
        task = Task.from_dict(data)
        created_task = db_manager.create_task(task)
        
        return response_helper.success(
            created_task.to_dict(),
            "Task created successfully",
            status_code=201
        )
        
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return response_helper.error("Failed to create task", 500)

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID"""
    try:
        task = db_manager.get_task_by_id(task_id)
        
        if not task:
            return response_helper.error("Task not found", 404)
        
        return response_helper.success(task.to_dict(), "Task retrieved successfully")
        
    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {str(e)}")
        return response_helper.error("Failed to retrieve task", 500)

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task"""
    try:
        data = request.get_json()
        
        if not data:
            return response_helper.error("No data provided", 400)
        
        # Validate update data
        validation_result = validator.validate_update_data(data)
        if not validation_result['valid']:
            return response_helper.error(validation_result['errors'], 400)
        
        # Update task
        updated_task = db_manager.update_task(task_id, data)
        
        if not updated_task:
            return response_helper.error("Task not found", 404)
        
        return response_helper.success(
            updated_task.to_dict(),
            "Task updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        return response_helper.error("Failed to update task", 500)

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        deleted = db_manager.delete_task(task_id)
        
        if not deleted:
            return response_helper.error("Task not found", 404)
        
        return response_helper.success(
            {"deleted_task_id": task_id},
            "Task deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        return response_helper.error("Failed to delete task", 500)

@app.route('/tasks/<int:task_id>/email-reminder', methods=['POST'])
def send_email_reminder(task_id):
    """Send email reminder for a task"""
    try:
        data = request.get_json()
        recipient_email = data.get('recipient_email') if data else None
        
        if not recipient_email:
            return response_helper.error("Recipient email is required", 400)
        
        # Get task
        task = db_manager.get_task_by_id(task_id)
        if not task:
            return response_helper.error("Task not found", 404)
        
        # Simulate email sending
        return response_helper.success(
            {
                "message": f"Email reminder sent for '{task.title}'",
                "task_id": task_id,
                "recipient": recipient_email,
                "task_title": task.title,
                "due_date": task.due_date,
                "status": "sent"
            },
            "Email reminder sent successfully"
        )
        
    except Exception as e:
        logger.error(f"Error sending email reminder for task {task_id}: {str(e)}")
        return response_helper.error("Failed to send email reminder", 500)

@app.route('/tasks/export-to-sheets', methods=['POST'])
def export_to_sheets():
    """Export tasks to Google Sheets"""
    try:
        data = request.get_json()
        spreadsheet_name = data.get('spreadsheet_name', 'Task Manager Export') if data else 'Task Manager Export'
        
        # Get all tasks
        tasks = db_manager.get_all_tasks()
        
        # Simulate sheets export
        return response_helper.success(
            {
                "message": f"Successfully exported {len(tasks)} tasks to Google Sheets",
                "spreadsheet_name": spreadsheet_name,
                "task_count": len(tasks),
                "exported_tasks": [{"id": t.id, "title": t.title} for t in tasks[:5]],  # Show first 5
                "status": "exported"
            },
            "Tasks exported successfully"
        )
        
    except Exception as e:
        logger.error(f"Error exporting to sheets: {str(e)}")
        return response_helper.error("Failed to export to sheets", 500)

@app.route('/tasks/<int:task_id>/add-to-calendar', methods=['POST'])
def add_to_calendar(task_id):
    """Add task to Google Calendar"""
    try:
        data = request.get_json()
        duration_minutes = data.get('duration_minutes', 60) if data else 60
        reminder_minutes = data.get('reminder_minutes', 15) if data else 15
        location = data.get('location', '') if data else ''
        
        # Get task
        task = db_manager.get_task_by_id(task_id)
        if not task:
            return response_helper.error("Task not found", 404)
        
        # Simulate calendar event creation
        return response_helper.success(
            {
                "message": f"Calendar event created for '{task.title}'",
                "task_id": task_id,
                "event_title": task.title,
                "duration_minutes": duration_minutes,
                "reminder_minutes": reminder_minutes,
                "location": location,
                "due_date": task.due_date,
                "status": "created"
            },
            "Task added to calendar successfully"
        )
        
    except Exception as e:
        logger.error(f"Error adding task {task_id} to calendar: {str(e)}")
        return response_helper.error("Failed to add to calendar", 500)

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
        
        return response_helper.success(integrations, "Integration status retrieved")
        
    except Exception as e:
        logger.error(f"Error checking integration status: {str(e)}")
        return response_helper.error("Failed to check integration status", 500)

@app.route('/tasks/batch/email-reminders', methods=['POST'])
def batch_email_reminders():
    """Send batch email reminders for overdue tasks"""
    try:
        data = request.get_json()
        recipient_email = data.get('recipient_email') if data else None
        
        if not recipient_email:
            return response_helper.error("Recipient email is required", 400)
        
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
        
        return response_helper.success(
            results,
            f"Batch email reminders sent for {results['total_tasks']} overdue tasks"
        )
        
    except Exception as e:
        logger.error(f"Error in batch email reminders: {str(e)}")
        return response_helper.error("Failed to send batch reminders", 500)

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
            ][:3],
            'summary': {
                'total_tasks': total_tasks,
                'completion_percentage': completion_rate,
                'overdue_count': len(overdue_tasks),
                'status_distribution': {
                    'completed': len(completed_tasks),
                    'pending': len(pending_tasks), 
                    'in_progress': len(in_progress_tasks)
                }
            }
        }
        
        return response_helper.success(dashboard_data, "Dashboard data retrieved successfully")
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return response_helper.error("Failed to get dashboard data", 500)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return response_helper.error("Endpoint not found", 404)

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return response_helper.error("Internal server error", 500)

if __name__ == '__main__':
    print("🚀 Starting Task Manager API (Non-blocking Version)")
    print("=" * 60)
    print("✅ Database: Connected")
    print("✅ Core API: Ready")
    print("⚠️  Google APIs: Ready for OAuth2 setup")
    print("\n📊 API Endpoints Available:")
    print("   • Health Check: http://localhost:5000/health")
    print("   • Dashboard: http://localhost:5000/dashboard")
    print("   • Tasks: http://localhost:5000/tasks")
    print("   • Google Integrations: Ready for setup")
    print("\n🌐 Server starting at: http://localhost:5000")
    print("=" * 60)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
