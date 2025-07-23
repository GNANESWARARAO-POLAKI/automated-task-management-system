#!/usr/bin/env python3
"""
Automated Task Reminder System
Sends email reminders for tasks based on due dates:
- 1 day before due date
- 1 hour before due date
"""

import sqlite3
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import os

# Import our modules
from database.db_manager import DatabaseManager
from google_integrations.gmail_service import GmailService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomatedReminderSystem:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.gmail_service = None
        self.recipient_email = "chandu0polaki@gmail.com"  # Default recipient
        self.running = False
        self.reminder_thread = None
        
        # Track sent reminders to avoid duplicates
        self.sent_reminders = {
            '24h': set(),  # Task IDs that got 24h reminders
            '1h': set()    # Task IDs that got 1h reminders
        }
        
    def initialize_gmail(self):
        """Initialize Gmail service"""
        try:
            self.gmail_service = GmailService()
            logger.info("Gmail service initialized for automated reminders")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gmail service: {str(e)}")
            return False
    
    def get_tasks_needing_reminders(self) -> List[Dict[str, Any]]:
        """Get tasks that need reminders (24h or 1h before due date)"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all pending and in_progress tasks with due dates
            cursor.execute("""
                SELECT id, title, description, due_date, status, priority
                FROM tasks 
                WHERE status IN ('pending', 'in_progress') 
                AND due_date IS NOT NULL 
                AND due_date != ''
                ORDER BY due_date ASC
            """)
            
            tasks = []
            for row in cursor.fetchall():
                task_dict = dict(row)
                tasks.append(task_dict)
            
            conn.close()
            return tasks
            
        except Exception as e:
            logger.error(f"Error fetching tasks for reminders: {str(e)}")
            return []
    
    def parse_due_date(self, due_date_str: str) -> datetime:
        """Parse due date string to datetime object"""
        try:
            # Try different formats
            formats = [
                '%Y-%m-%dT%H:%M:%S.%f',    # 2025-07-23T21:53:17.406242
                '%Y-%m-%d %H:%M:%S.%f',    # 2025-07-23 21:53:17.406242
                '%Y-%m-%d %H:%M:%S',       # 2025-07-23 21:53:17
                '%Y-%m-%dT%H:%M:%S',       # 2025-07-23T21:53:17
                '%Y-%m-%dT%H:%M',          # 2025-07-23T21:53
                '%Y-%m-%d',                # 2025-07-23
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(due_date_str, fmt)
                except ValueError:
                    continue
            
            # If no format works, log and return None
            logger.warning(f"Could not parse due date: {due_date_str}")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing due date {due_date_str}: {str(e)}")
            return None
    
    def should_send_reminder(self, task: Dict[str, Any], reminder_type: str) -> bool:
        """Check if a reminder should be sent for this task"""
        task_id = task['id']
        due_date_str = task['due_date']
        
        if not due_date_str:
            return False
        
        due_date = self.parse_due_date(due_date_str)
        if not due_date:
            return False
        
        # Use system local time for all calculations (synchronized with user's system)
        now = datetime.now()  # This gets the system's local time
        time_until_due = due_date - now
        
        # Check if reminder was already sent
        if task_id in self.sent_reminders[reminder_type]:
            return False
        
        # 24 hour reminder: send if between 23-25 hours before due
        if reminder_type == '24h':
            hours_until = time_until_due.total_seconds() / 3600
            return 23 <= hours_until <= 25
        
        # 1 hour reminder: send if between 0.5-1.5 hours before due
        elif reminder_type == '1h':
            hours_until = time_until_due.total_seconds() / 3600
            return 0.5 <= hours_until <= 1.5
        
        return False
    
    def send_automated_reminder(self, task: Dict[str, Any], reminder_type: str) -> bool:
        """Send automated email reminder for a task"""
        try:
            if not self.gmail_service:
                logger.error("Gmail service not initialized")
                return False
            
            # Create a simple Task-like object for the Gmail service
            class SimpleTask:
                def __init__(self, task_data):
                    self.id = task_data['id']
                    self.title = task_data['title']
                    self.description = task_data.get('description', 'No description')
                    self.priority = task_data.get('priority', 'medium')
                    self.status = task_data.get('status', 'pending')
                    
                    # Parse due_date
                    self.due_date = None
                    if task_data['due_date']:
                        try:
                            self.due_date = datetime.strptime(task_data['due_date'], '%Y-%m-%dT%H:%M')
                        except:
                            self.due_date = None
                    
                    # Parse created_at
                    self.created_at = datetime.now()
                    if task_data.get('created_at'):
                        try:
                            self.created_at = datetime.fromisoformat(task_data['created_at'])
                        except:
                            self.created_at = datetime.now()
                
                def is_overdue(self):
                    """Check if task is overdue"""
                    if not self.due_date:
                        return False
                    return self.due_date < datetime.now() and self.status != 'completed'
                
                def days_until_due(self):
                    """Calculate days until due date"""
                    if not self.due_date:
                        return 0
                    delta = self.due_date - datetime.now()
                    return delta.days
            
            task_obj = SimpleTask(task)
            
            # Create custom message for automated reminder
            if reminder_type == '24h':
                custom_message = f"🔔 AUTOMATED REMINDER: This task is due tomorrow! Please review and complete '{task['title']}' by {task['due_date']}."
            else:  # 1h
                custom_message = f"⏰ URGENT AUTOMATED REMINDER: This task is due in 1 hour! Please complete '{task['title']}' immediately. Due: {task['due_date']}"
            
            # Send email using existing Gmail service
            result = self.gmail_service.send_task_reminder(
                task=task_obj,
                recipient_email=self.recipient_email,
                custom_message=custom_message
            )
            
            if result.get('success'):
                # Mark reminder as sent
                self.sent_reminders[reminder_type].add(task['id'])
                logger.info(f"✅ Automated {reminder_type} reminder sent for task {task['id']}: {task['title']}")
                return True
            else:
                logger.error(f"❌ Failed to send {reminder_type} reminder for task {task['id']}: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending automated reminder for task {task.get('id', 'unknown')}: {str(e)}")
            return False
    
    def check_and_send_reminders(self):
        """Check all tasks and send reminders as needed"""
        logger.info("🔍 Checking for tasks needing automated reminders...")
        
        tasks = self.get_tasks_needing_reminders()
        if not tasks:
            logger.info("📭 No tasks with due dates found")
            return
        
        reminders_sent = 0
        
        for task in tasks:
            # Check for 24h reminder
            if self.should_send_reminder(task, '24h'):
                if self.send_automated_reminder(task, '24h'):
                    reminders_sent += 1
            
            # Check for 1h reminder  
            if self.should_send_reminder(task, '1h'):
                if self.send_automated_reminder(task, '1h'):
                    reminders_sent += 1
        
        if reminders_sent > 0:
            logger.info(f"📧 Sent {reminders_sent} automated reminders")
        else:
            logger.info("✅ All reminders up to date")
    
    def start_automated_reminders(self, check_interval_minutes: int = 15):
        """Start the automated reminder system"""
        if self.running:
            logger.warning("Automated reminder system is already running")
            return
        
        if not self.initialize_gmail():
            logger.error("Cannot start automated reminders - Gmail service failed to initialize")
            return
        
        self.running = True
        logger.info(f"🚀 Starting automated reminder system (checking every {check_interval_minutes} minutes)")
        
        def reminder_loop():
            while self.running:
                try:
                    self.check_and_send_reminders()
                    # Wait for the specified interval
                    time.sleep(check_interval_minutes * 60)
                except Exception as e:
                    logger.error(f"Error in reminder loop: {str(e)}")
                    time.sleep(60)  # Wait 1 minute before retrying
        
        self.reminder_thread = threading.Thread(target=reminder_loop, daemon=True)
        self.reminder_thread.start()
        logger.info("✅ Automated reminder system started successfully")
    
    def stop_automated_reminders(self):
        """Stop the automated reminder system"""
        if not self.running:
            logger.warning("Automated reminder system is not running")
            return
        
        self.running = False
        logger.info("🛑 Stopping automated reminder system...")
        
        if self.reminder_thread:
            self.reminder_thread.join(timeout=5)
        
        logger.info("✅ Automated reminder system stopped")
    
    def get_reminder_status(self) -> Dict[str, Any]:
        """Get status of the automated reminder system"""
        return {
            'running': self.running,
            'gmail_initialized': self.gmail_service is not None,
            'recipient_email': self.recipient_email,
            'reminders_sent_24h': len(self.sent_reminders['24h']),
            'reminders_sent_1h': len(self.sent_reminders['1h']),
            'total_reminders_sent': len(self.sent_reminders['24h']) + len(self.sent_reminders['1h'])
        }

# Global instance
automated_reminder_system = AutomatedReminderSystem()

if __name__ == "__main__":
    # For testing - run the reminder check once
    system = AutomatedReminderSystem()
    if system.initialize_gmail():
        system.check_and_send_reminders()
    else:
        print("❌ Could not initialize Gmail service")
