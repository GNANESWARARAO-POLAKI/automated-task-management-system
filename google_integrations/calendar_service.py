"""
Google Calendar Service Integration for Task Manager API
Handles creating calendar events from tasks
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
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

class CalendarService:
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Calendar service with authentication"""
        if not GOOGLE_AVAILABLE:
            logger.warning("Google API libraries not available. Install with: pip install google-auth google-auth-oauthlib google-api-python-client")
            return
        
        try:
            # Load credentials
            if os.path.exists('credentials/calendar_token.json'):
                self.credentials = Credentials.from_authorized_user_file('credentials/calendar_token.json', self.SCOPES)
            
            # If there are no (valid) credentials available, let the user log in
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    try:
                        self.credentials.refresh(Request())
                    except RefreshError:
                        logger.error("Failed to refresh Calendar credentials")
                        return
                else:
                    if os.path.exists('credentials/calendar_credentials.json'):
                        flow = InstalledAppFlow.from_client_secrets_file('credentials/calendar_credentials.json', self.SCOPES)
                        # Use fixed port for OAuth redirect
                        self.credentials = flow.run_local_server(port=8080)
                    else:
                        logger.warning("Calendar credentials file not found at credentials/calendar_credentials.json")
                        return
                
                # Save the credentials for the next run
                os.makedirs('credentials', exist_ok=True)
                with open('credentials/calendar_token.json', 'w') as token:
                    token.write(self.credentials.to_json())
            
            self.service = build('calendar', 'v3', credentials=self.credentials)
            logger.info("Google Calendar service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {str(e)}")
            self.service = None
    
    def check_connection(self) -> Dict[str, Any]:
        """Check Google Calendar API connection status"""
        if not GOOGLE_AVAILABLE:
            return {
                'success': False,
                'error': 'Google API libraries not installed. Run: pip install google-auth google-auth-oauthlib google-api-python-client'
            }
        
        if not self.service:
            return {
                'success': False,
                'error': 'Google Calendar service not initialized. Check credentials setup.'
            }
        
        try:
            # Test the connection by getting calendar list
            calendar_list = self.service.calendarList().list(maxResults=1).execute()
            return {
                'success': True,
                'details': f'Connected to Google Calendar (found {len(calendar_list.get("items", []))} calendar(s))'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Google Calendar connection failed: {str(e)}'
            }
    
    def create_event_from_task(self, task: Task, event_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a calendar event from a task"""
        if not self.service:
            return {
                'success': False,
                'error': 'Google Calendar service not available. Please check credentials setup.'
            }
        
        if not task.due_date:
            return {
                'success': False,
                'error': 'Task must have a due date to create calendar event'
            }
        
        try:
            # Parse event options
            options = event_options or {}
            duration_minutes = options.get('duration_minutes', 60)
            reminder_minutes = options.get('reminder_minutes', 30)
            location = options.get('location', '')
            calendar_id = options.get('calendar_id', 'primary')
            
            # Create event
            event = self._build_calendar_event(task, duration_minutes, reminder_minutes, location)
            
            # Insert event
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            
            event_url = created_event.get('htmlLink')
            event_id = created_event.get('id')
            
            logger.info(f"Calendar event created for task {task.id}: {event_url}")
            
            return {
                'success': True,
                'event_id': event_id,
                'event_url': event_url,
                'task_id': task.id
            }
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            return {
                'success': False,
                'error': f'Google Calendar API error: {error}'
            }
        except Exception as e:
            logger.error(f"Error creating calendar event: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to create calendar event: {str(e)}'
            }
    
    def update_event_from_task(self, task: Task, event_id: str, event_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update an existing calendar event from task"""
        if not self.service:
            return {
                'success': False,
                'error': 'Google Calendar service not available'
            }
        
        try:
            options = event_options or {}
            calendar_id = options.get('calendar_id', 'primary')
            
            # Get existing event
            existing_event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Update event with task data
            duration_minutes = options.get('duration_minutes', 60)
            reminder_minutes = options.get('reminder_minutes', 30)
            location = options.get('location', existing_event.get('location', ''))
            
            updated_event = self._build_calendar_event(task, duration_minutes, reminder_minutes, location)
            
            # Preserve original event ID and creation time
            updated_event['id'] = event_id
            if 'created' in existing_event:
                updated_event['created'] = existing_event['created']
            
            # Update the event
            result = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=updated_event
            ).execute()
            
            return {
                'success': True,
                'event_id': result.get('id'),
                'event_url': result.get('htmlLink'),
                'task_id': task.id
            }
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            return {
                'success': False,
                'error': f'Google Calendar API error: {error}'
            }
        except Exception as e:
            logger.error(f"Error updating calendar event: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to update calendar event: {str(e)}'
            }
    
    def delete_event(self, event_id: str, calendar_id: str = 'primary') -> Dict[str, Any]:
        """Delete a calendar event"""
        if not self.service:
            return {
                'success': False,
                'error': 'Google Calendar service not available'
            }
        
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            return {
                'success': True,
                'message': 'Calendar event deleted successfully'
            }
            
        except HttpError as error:
            if error.resp.status == 404:
                return {
                    'success': True,
                    'message': 'Calendar event not found (may have been already deleted)'
                }
            logger.error(f"Google Calendar API error: {error}")
            return {
                'success': False,
                'error': f'Google Calendar API error: {error}'
            }
        except Exception as e:
            logger.error(f"Error deleting calendar event: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to delete calendar event: {str(e)}'
            }
    
    def sync_task_status(self, task: Task, event_id: str, calendar_id: str = 'primary') -> Dict[str, Any]:
        """Sync task status with calendar event"""
        if not self.service:
            return {
                'success': False,
                'error': 'Google Calendar service not available'
            }
        
        try:
            # Get the event
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Update event based on task status
            if task.status == 'completed':
                # Mark event as completed (change color to green)
                event['colorId'] = '10'  # Green
                event['summary'] = f"✅ {task.title} (Completed)"
            elif task.status == 'in_progress':
                # Mark as in progress (change color to yellow)
                event['colorId'] = '5'   # Yellow
                event['summary'] = f"🔄 {task.title} (In Progress)"
            else:
                # Pending or other status (default color)
                event['colorId'] = '1'   # Blue
                event['summary'] = f"📋 {task.title}"
            
            # Update description with current task details
            event['description'] = self._generate_event_description(task)
            
            # Update the event
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            return {
                'success': True,
                'event_id': updated_event.get('id'),
                'event_url': updated_event.get('htmlLink'),
                'message': f'Event synced with task status: {task.status}'
            }
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            return {
                'success': False,
                'error': f'Google Calendar API error: {error}'
            }
        except Exception as e:
            logger.error(f"Error syncing task status: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to sync task status: {str(e)}'
            }
    
    def create_batch_events(self, tasks: List[Task], event_options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Create calendar events for multiple tasks"""
        results = []
        
        for task in tasks:
            if task.due_date:  # Only create events for tasks with due dates
                result = self.create_event_from_task(task, event_options)
                result['task_id'] = task.id
                result['task_title'] = task.title
                results.append(result)
            else:
                results.append({
                    'success': False,
                    'task_id': task.id,
                    'task_title': task.title,
                    'error': 'Task has no due date'
                })
        
        return results
    
    def _build_calendar_event(self, task: Task, duration_minutes: int, reminder_minutes: int, location: str) -> Dict[str, Any]:
        """Build calendar event structure from task"""
        # Calculate event times
        start_time = task.due_date
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Determine event title based on task status
        if task.status == 'completed':
            title = f"✅ {task.title} (Completed)"
            color_id = '10'  # Green
        elif task.status == 'in_progress':
            title = f"🔄 {task.title} (In Progress)"
            color_id = '5'   # Yellow
        else:
            title = f"📋 {task.title}"
            color_id = '1'   # Blue
        
        # Build event
        event = {
            'summary': title,
            'description': self._generate_event_description(task),
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC'
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC'
            },
            'colorId': color_id,
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': reminder_minutes},
                    {'method': 'popup', 'minutes': 10}
                ]
            }
        }
        
        # Add location if provided
        if location:
            event['location'] = location
        
        return event
    
    def _generate_event_description(self, task: Task) -> str:
        """Generate calendar event description from task"""
        description = []
        
        description.append(f"📋 Task: {task.title}")
        description.append(f"🔸 Priority: {task.priority.title()}")
        description.append(f"📊 Status: {task.status.replace('_', ' ').title()}")
        
        if task.description:
            description.append(f"\n📝 Description:\n{task.description}")
        
        description.append(f"\n🕐 Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        if task.updated_at:
            description.append(f"📝 Last Updated: {task.updated_at.strftime('%Y-%m-%d %H:%M')}")
        
        description.append("\n" + "="*50)
        description.append("Generated by Task Manager API")
        
        return "\n".join(description)
    
    def get_calendar_list(self) -> Dict[str, Any]:
        """Get list of available calendars"""
        if not self.service:
            return {
                'success': False,
                'error': 'Google Calendar service not available'
            }
        
        try:
            calendar_list = self.service.calendarList().list().execute()
            calendars = []
            
            for calendar in calendar_list.get('items', []):
                calendars.append({
                    'id': calendar['id'],
                    'summary': calendar['summary'],
                    'primary': calendar.get('primary', False),
                    'access_role': calendar.get('accessRole', 'reader')
                })
            
            return {
                'success': True,
                'calendars': calendars
            }
            
        except Exception as e:
            logger.error(f"Error getting calendar list: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to get calendar list: {str(e)}'
            }
    
    def create_task_manager_calendar(self) -> Dict[str, Any]:
        """Create a dedicated Task Manager calendar"""
        if not self.service:
            return {
                'success': False,
                'error': 'Google Calendar service not available'
            }
        
        try:
            calendar = {
                'summary': 'Task Manager',
                'description': 'Calendar for Task Manager API events',
                'timeZone': 'UTC'
            }
            
            created_calendar = self.service.calendars().insert(body=calendar).execute()
            
            return {
                'success': True,
                'calendar_id': created_calendar['id'],
                'calendar_url': created_calendar.get('htmlLink', ''),
                'message': 'Task Manager calendar created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating Task Manager calendar: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to create Task Manager calendar: {str(e)}'
            }
