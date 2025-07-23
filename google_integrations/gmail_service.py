"""
Gmail Service Integration for Task Manager API
Handles sending task reminder emails via Gmail API
"""

import os
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, List
import logging

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google.auth.exceptions import RefreshError
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from models.task import Task

logger = logging.getLogger(__name__)

class GmailService:
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Gmail service with authentication"""
        if not GOOGLE_AVAILABLE:
            logger.warning("Google API libraries not available. Install with: pip install google-auth google-auth-oauthlib google-api-python-client")
            return
        
        try:
            # Load credentials
            if os.path.exists('credentials/gmail_token.json'):
                self.credentials = Credentials.from_authorized_user_file('credentials/gmail_token.json', self.SCOPES)
            
            # If there are no (valid) credentials available, let the user log in
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    try:
                        self.credentials.refresh(Request())
                    except RefreshError:
                        logger.error("Failed to refresh Gmail credentials")
                        return
                else:
                    if os.path.exists('credentials/gmail_credentials.json'):
                        flow = InstalledAppFlow.from_client_secrets_file('credentials/gmail_credentials.json', self.SCOPES)
                        # Use fixed port for OAuth redirect
                        self.credentials = flow.run_local_server(port=8080)
                    else:
                        logger.warning("Gmail credentials file not found at credentials/gmail_credentials.json")
                        return
                
                # Save the credentials for the next run
                os.makedirs('credentials', exist_ok=True)
                with open('credentials/gmail_token.json', 'w') as token:
                    token.write(self.credentials.to_json())
            
            self.service = build('gmail', 'v1', credentials=self.credentials)
            logger.info("Gmail service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gmail service: {str(e)}")
            self.service = None
    
    def check_connection(self) -> Dict[str, Any]:
        """Check Gmail API connection status"""
        if not GOOGLE_AVAILABLE:
            return {
                'success': False,
                'error': 'Google API libraries not installed. Run: pip install google-auth google-auth-oauthlib google-api-python-client'
            }
        
        if not self.service:
            return {
                'success': False,
                'error': 'Gmail service not initialized. Check credentials setup.'
            }
        
        try:
            # Test the connection by getting user profile
            profile = self.service.users().getProfile(userId='me').execute()
            return {
                'success': True,
                'details': f'Connected as {profile.get("emailAddress", "Unknown")}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Gmail connection failed: {str(e)}'
            }
    
    def send_task_reminder(self, task: Task, recipient_email: str = "chandu0polaki@gmail.com", custom_message: str = None) -> Dict[str, Any]:
        """Send task reminder email"""
        # Use default email if none provided
        if not recipient_email:
            recipient_email = "chandu0polaki@gmail.com"
            
        if not self.service:
            return {
                'success': False,
                'error': 'Gmail service not available. Please check credentials setup.'
            }
        
        try:
            # Create email message
            message = self._create_reminder_message(task, recipient_email, custom_message)
            
            # Send email
            result = self.service.users().messages().send(userId='me', body=message).execute()
            
            logger.info(f"Email reminder sent for task {task.id} to {recipient_email}")
            
            return {
                'success': True,
                'message_id': result.get('id'),
                'task_id': task.id,
                'recipient': recipient_email
            }
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return {
                'success': False,
                'error': f'Gmail API error: {error}'
            }
        except Exception as e:
            logger.error(f"Error sending email reminder: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to send email: {str(e)}'
            }
    
    def send_batch_reminders(self, tasks: List[Task], recipient_email: str) -> List[Dict[str, Any]]:
        """Send batch email reminders for multiple tasks"""
        if not tasks:
            return []
        
        results = []
        
        # Send individual reminders
        for task in tasks:
            result = self.send_task_reminder(task, recipient_email)
            result['task_id'] = task.id
            result['task_title'] = task.title
            results.append(result)
        
        # Also send summary email
        summary_result = self._send_batch_summary_email(tasks, recipient_email)
        if summary_result['success']:
            results.append({
                'success': True,
                'type': 'summary',
                'message': f'Batch summary email sent for {len(tasks)} overdue tasks'
            })
        
        return results
    
    def _create_reminder_message(self, task: Task, recipient_email: str, custom_message: str = None) -> Dict[str, str]:
        """Create email message for task reminder"""
        msg = MIMEMultipart('alternative')
        
        # Email headers
        msg['To'] = recipient_email
        msg['Subject'] = f"Task Reminder: {task.title}"
        
        # Create text content
        text_content = self._generate_text_content(task, custom_message)
        
        # Create HTML content
        html_content = self._generate_html_content(task, custom_message)
        
        # Attach content
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        
        return {'raw': raw_message}
    
    def _generate_text_content(self, task: Task, custom_message: str = None) -> str:
        """Generate plain text email content"""
        overdue_text = ""
        if task.is_overdue():
            days_overdue = abs(task.days_until_due())
            overdue_text = f"\n⚠️  This task is {days_overdue} day(s) overdue!"
        elif task.due_date:
            days_until = task.days_until_due()
            if days_until == 0:
                overdue_text = "\n📅 This task is due today!"
            elif days_until > 0:
                overdue_text = f"\n📅 This task is due in {days_until} day(s)."
        
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "🟡")
        
        content = f"""
Task Reminder

{overdue_text}

Task Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Title: {task.title}
{priority_emoji} Priority: {task.priority.title()}
📊 Status: {task.status.replace('_', ' ').title()}

"""
        
        if task.description:
            content += f"📝 Description:\n{task.description}\n\n"
        
        if task.due_date:
            content += f"📅 Due Date: {task.due_date.strftime('%B %d, %Y at %I:%M %p')}\n"
        
        content += f"🕐 Created: {task.created_at.strftime('%B %d, %Y at %I:%M %p')}\n"
        
        if custom_message:
            content += f"\n💬 Additional Message:\n{custom_message}\n"
        
        content += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is an automated reminder from your Task Manager system.

Best regards,
Task Manager API
"""
        
        return content
    
    def _generate_html_content(self, task: Task, custom_message: str = None) -> str:
        """Generate HTML email content"""
        overdue_html = ""
        if task.is_overdue():
            days_overdue = abs(task.days_until_due())
            overdue_html = f'<div style="background-color: #ffebee; border-left: 4px solid #f44336; padding: 10px; margin: 10px 0;"><strong>⚠️ This task is {days_overdue} day(s) overdue!</strong></div>'
        elif task.due_date:
            days_until = task.days_until_due()
            if days_until == 0:
                overdue_html = '<div style="background-color: #fff3e0; border-left: 4px solid #ff9800; padding: 10px; margin: 10px 0;"><strong>📅 This task is due today!</strong></div>'
            elif days_until > 0:
                overdue_html = f'<div style="background-color: #e8f5e8; border-left: 4px solid #4caf50; padding: 10px; margin: 10px 0;"><strong>📅 This task is due in {days_until} day(s).</strong></div>'
        
        priority_colors = {"high": "#f44336", "medium": "#ff9800", "low": "#4caf50"}
        priority_color = priority_colors.get(task.priority, "#ff9800")
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Task Reminder</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <h1 style="color: #2c3e50; margin-top: 0;">📋 Task Reminder</h1>
        {overdue_html}
    </div>
    
    <div style="background-color: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
        <h2 style="color: #34495e; margin-top: 0; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px;">Task Details</h2>
        
        <div style="margin-bottom: 15px;">
            <strong style="color: #2c3e50;">📋 Title:</strong>
            <div style="font-size: 18px; font-weight: bold; color: #2c3e50; margin-top: 5px;">{task.title}</div>
        </div>
        
        <div style="display: flex; gap: 20px; margin-bottom: 15px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 150px;">
                <strong style="color: #2c3e50;">Priority:</strong>
                <span style="display: inline-block; background-color: {priority_color}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px; margin-left: 5px;">{task.priority.upper()}</span>
            </div>
            <div style="flex: 1; min-width: 150px;">
                <strong style="color: #2c3e50;">📊 Status:</strong>
                <span style="margin-left: 5px;">{task.status.replace('_', ' ').title()}</span>
            </div>
        </div>
"""
        
        if task.description:
            html_content += f"""
        <div style="margin-bottom: 15px;">
            <strong style="color: #2c3e50;">📝 Description:</strong>
            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 5px; white-space: pre-line;">{task.description}</div>
        </div>
"""
        
        if task.due_date:
            html_content += f"""
        <div style="margin-bottom: 15px;">
            <strong style="color: #2c3e50;">📅 Due Date:</strong>
            <span style="margin-left: 5px; font-weight: bold;">{task.due_date.strftime('%B %d, %Y at %I:%M %p')}</span>
        </div>
"""
        
        html_content += f"""
        <div style="margin-bottom: 15px;">
            <strong style="color: #2c3e50;">🕐 Created:</strong>
            <span style="margin-left: 5px;">{task.created_at.strftime('%B %d, %Y at %I:%M %p')}</span>
        </div>
    </div>
"""
        
        if custom_message:
            html_content += f"""
    <div style="background-color: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin-bottom: 20px; border-radius: 4px;">
        <strong style="color: #1976d2;">💬 Additional Message:</strong>
        <div style="margin-top: 8px; white-space: pre-line;">{custom_message}</div>
    </div>
"""
        
        html_content += """
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; font-size: 14px; color: #6c757d;">
        This is an automated reminder from your Task Manager system.<br>
        <strong>Best regards,</strong><br>
        Task Manager API
    </div>
</body>
</html>
"""
        
        return html_content
    
    def _send_batch_summary_email(self, tasks: List[Task], recipient_email: str) -> Dict[str, Any]:
        """Send batch summary email for overdue tasks"""
        if not self.service or not tasks:
            return {'success': False, 'error': 'No service or tasks available'}
        
        try:
            msg = MIMEMultipart('alternative')
            msg['To'] = recipient_email
            msg['Subject'] = f"Task Summary: {len(tasks)} Overdue Tasks Requiring Attention"
            
            # Generate summary content
            text_content = self._generate_batch_text_summary(tasks)
            html_content = self._generate_batch_html_summary(tasks)
            
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            message = {'raw': raw_message}
            
            result = self.service.users().messages().send(userId='me', body=message).execute()
            
            return {
                'success': True,
                'message_id': result.get('id'),
                'recipient': recipient_email
            }
            
        except Exception as e:
            logger.error(f"Error sending batch summary email: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to send summary email: {str(e)}'
            }
    
    def _generate_batch_text_summary(self, tasks: List[Task]) -> str:
        """Generate text summary for batch email"""
        content = f"""
Task Summary Report

You have {len(tasks)} overdue task(s) requiring attention:

"""
        for i, task in enumerate(tasks, 1):
            days_overdue = abs(task.days_until_due()) if task.due_date else 0
            content += f"""
{i}. {task.title}
   Priority: {task.priority.title()} | Status: {task.status.replace('_', ' ').title()}
   Days overdue: {days_overdue}
   
"""
        
        content += """
Please review and update these tasks as soon as possible.

Best regards,
Task Manager API
"""
        
        return content
    
    def _generate_batch_html_summary(self, tasks: List[Task]) -> str:
        """Generate HTML summary for batch email"""
        priority_colors = {"high": "#f44336", "medium": "#ff9800", "low": "#4caf50"}
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Task Summary Report</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 700px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #ffebee; border-left: 4px solid #f44336; padding: 20px; margin-bottom: 20px; border-radius: 4px;">
        <h1 style="color: #c62828; margin-top: 0;">⚠️ Task Summary Report</h1>
        <p style="font-size: 16px; margin-bottom: 0;">You have <strong>{len(tasks)} overdue task(s)</strong> requiring attention.</p>
    </div>
    
    <div style="background-color: white; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background-color: #f8f9fa;">
                    <th style="padding: 12px; text-align: left; border-bottom: 1px solid #ddd;">#</th>
                    <th style="padding: 12px; text-align: left; border-bottom: 1px solid #ddd;">Task</th>
                    <th style="padding: 12px; text-align: left; border-bottom: 1px solid #ddd;">Priority</th>
                    <th style="padding: 12px; text-align: left; border-bottom: 1px solid #ddd;">Status</th>
                    <th style="padding: 12px; text-align: left; border-bottom: 1px solid #ddd;">Days Overdue</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for i, task in enumerate(tasks, 1):
            days_overdue = abs(task.days_until_due()) if task.due_date else 0
            priority_color = priority_colors.get(task.priority, "#ff9800")
            
            html_content += f"""
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 12px;">{i}</td>
                    <td style="padding: 12px; font-weight: bold;">{task.title}</td>
                    <td style="padding: 12px;">
                        <span style="background-color: {priority_color}; color: white; padding: 2px 6px; border-radius: 8px; font-size: 11px;">
                            {task.priority.upper()}
                        </span>
                    </td>
                    <td style="padding: 12px;">{task.status.replace('_', ' ').title()}</td>
                    <td style="padding: 12px; color: #d32f2f; font-weight: bold;">{days_overdue}</td>
                </tr>
"""
        
        html_content += """
            </tbody>
        </table>
    </div>
    
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; margin-top: 20px; font-size: 14px; color: #6c757d;">
        Please review and update these tasks as soon as possible.<br><br>
        <strong>Best regards,</strong><br>
        Task Manager API
    </div>
</body>
</html>
"""
        
        return html_content
