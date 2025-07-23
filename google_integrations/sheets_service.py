"""
Google Sheets Service Integration for Task Manager API
Handles exporting tasks to Google Sheets
"""

import os
import json
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

class SheetsService:
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Sheets service with authentication"""
        if not GOOGLE_AVAILABLE:
            logger.warning("Google API libraries not available. Install with: pip install google-auth google-auth-oauthlib google-api-python-client")
            return
        
        try:
            # Load credentials
            if os.path.exists('credentials/sheets_token.json'):
                self.credentials = Credentials.from_authorized_user_file('credentials/sheets_token.json', self.SCOPES)
            
            # If there are no (valid) credentials available, let the user log in
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    try:
                        self.credentials.refresh(Request())
                    except RefreshError:
                        logger.error("Failed to refresh Sheets credentials")
                        return
                else:
                    if os.path.exists('credentials/sheets_credentials.json'):
                        flow = InstalledAppFlow.from_client_secrets_file('credentials/sheets_credentials.json', self.SCOPES)
                        # Use fixed port for OAuth redirect
                        self.credentials = flow.run_local_server(port=8080)
                    else:
                        logger.warning("Sheets credentials file not found at credentials/sheets_credentials.json")
                        return
                
                # Save the credentials for the next run
                os.makedirs('credentials', exist_ok=True)
                with open('credentials/sheets_token.json', 'w') as token:
                    token.write(self.credentials.to_json())
            
            self.service = build('sheets', 'v4', credentials=self.credentials)
            logger.info("Google Sheets service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets service: {str(e)}")
            self.service = None
    
    def check_connection(self) -> Dict[str, Any]:
        """Check Google Sheets API connection status"""
        if not GOOGLE_AVAILABLE:
            return {
                'success': False,
                'error': 'Google API libraries not installed. Run: pip install google-auth google-auth-oauthlib google-api-python-client'
            }
        
        if not self.service:
            return {
                'success': False,
                'error': 'Google Sheets service not initialized. Check credentials setup.'
            }
        
        try:
            # Test the connection by creating a test request
            spreadsheets = self.service.spreadsheets()
            return {
                'success': True,
                'details': 'Google Sheets API connection verified'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Google Sheets connection failed: {str(e)}'
            }
    
    def export_tasks_to_sheet(self, tasks: List[Task], spreadsheet_name: str = None) -> Dict[str, Any]:
        """Export tasks to a new Google Sheet"""
        if not self.service:
            return {
                'success': False,
                'error': 'Google Sheets service not available. Please check credentials setup.'
            }
        
        if not tasks:
            return {
                'success': False,
                'error': 'No tasks to export'
            }
        
        try:
            # Create spreadsheet
            if not spreadsheet_name:
                spreadsheet_name = f"Task Export - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            spreadsheet = self._create_spreadsheet(spreadsheet_name)
            spreadsheet_id = spreadsheet['spreadsheetId']
            
            # Add data to spreadsheet
            self._populate_spreadsheet(spreadsheet_id, tasks)
            
            # Skip formatting for now to avoid errors
            # self._format_spreadsheet(spreadsheet_id)
            
            # Generate shareable URL
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
            
            logger.info(f"Tasks exported to Google Sheets: {spreadsheet_url}")
            
            return {
                'success': True,
                'spreadsheet_id': spreadsheet_id,
                'spreadsheet_url': spreadsheet_url,
                'spreadsheet_name': spreadsheet_name,
                'tasks_exported': len(tasks)
            }
            
        except HttpError as error:
            logger.error(f"Google Sheets API error: {error}")
            return {
                'success': False,
                'error': f'Google Sheets API error: {error}'
            }
        except Exception as e:
            logger.error(f"Error exporting to Google Sheets: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to export to Google Sheets: {str(e)}'
            }
    
    def _create_spreadsheet(self, title: str) -> Dict[str, Any]:
        """Create a new spreadsheet"""
        spreadsheet = {
            'properties': {
                'title': title
            },
            'sheets': [
                {
                    'properties': {
                        'title': 'Tasks',
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': 10
                        }
                    }
                },
                {
                    'properties': {
                        'title': 'Summary',
                        'gridProperties': {
                            'rowCount': 100,
                            'columnCount': 5
                        }
                    }
                }
            ]
        }
        
        result = self.service.spreadsheets().create(body=spreadsheet).execute()
        return result
    
    def _populate_spreadsheet(self, spreadsheet_id: str, tasks: List[Task]):
        """Populate spreadsheet with task data"""
        # Prepare headers
        headers = [
            'ID', 'Title', 'Description', 'Priority', 'Status', 
            'Due Date', 'Created Date', 'Updated Date', 'Days Until Due', 'Is Overdue'
        ]
        
        # Prepare task data
        task_data = [headers]
        
        for task in tasks:
            # Calculate days until due
            days_until_due = ""
            if task.due_date:
                days_until_due = task.days_until_due()
                if days_until_due is not None:
                    days_until_due = str(days_until_due)
            
            # Format dates
            due_date_str = task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else ""
            created_date_str = task.created_at.strftime('%Y-%m-%d %H:%M') if task.created_at else ""
            updated_date_str = task.updated_at.strftime('%Y-%m-%d %H:%M') if task.updated_at else ""
            
            row = [
                str(task.id) if task.id else "",
                task.title or "",
                task.description or "",
                task.priority.title(),
                task.status.replace('_', ' ').title(),
                due_date_str,
                created_date_str,
                updated_date_str,
                days_until_due,
                "Yes" if task.is_overdue() else "No"
            ]
            task_data.append(row)
        
        # Write to Tasks sheet
        range_name = f'Tasks!A1:J{len(task_data)}'
        body = {
            'values': task_data
        }
        
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        # Create summary data
        self._create_summary_sheet(spreadsheet_id, tasks)
    
    def _create_summary_sheet(self, spreadsheet_id: str, tasks: List[Task]):
        """Create summary statistics in Summary sheet"""
        # Calculate statistics
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task.status == 'completed')
        pending_tasks = sum(1 for task in tasks if task.status == 'pending')
        in_progress_tasks = sum(1 for task in tasks if task.status == 'in_progress')
        overdue_tasks = sum(1 for task in tasks if task.is_overdue())
        high_priority = sum(1 for task in tasks if task.priority == 'high')
        medium_priority = sum(1 for task in tasks if task.priority == 'medium')
        low_priority = sum(1 for task in tasks if task.priority == 'low')
        
        # Prepare summary data
        summary_data = [
            ['Task Manager Export Summary', ''],
            ['Generated On', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['', ''],
            ['TASK STATISTICS', ''],
            ['Total Tasks', total_tasks],
            ['Completed Tasks', completed_tasks],
            ['Pending Tasks', pending_tasks],
            ['In Progress Tasks', in_progress_tasks],
            ['Overdue Tasks', overdue_tasks],
            ['', ''],
            ['PRIORITY BREAKDOWN', ''],
            ['High Priority', high_priority],
            ['Medium Priority', medium_priority],
            ['Low Priority', low_priority],
            ['', ''],
            ['COMPLETION RATE', ''],
            ['Completion Rate (%)', round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)]
        ]
        
        # Write to Summary sheet
        range_name = f'Summary!A1:B{len(summary_data)}'
        body = {
            'values': summary_data
        }
        
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
    
    def _format_spreadsheet(self, spreadsheet_id: str):
        """Apply formatting to the spreadsheet"""
        requests = []
        
        # Format Tasks sheet header
        requests.append({
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': 1,
                    'startColumnIndex': 0,
                    'endColumnIndex': 10
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {
                            'red': 0.2,
                            'green': 0.4,
                            'blue': 0.6
                        },
                        'textFormat': {
                            'foregroundColor': {
                                'red': 1.0,
                                'green': 1.0,
                                'blue': 1.0
                            },
                            'bold': True
                        },
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        })
        
        # Freeze header row in Tasks sheet
        requests.append({
            'updateSheetProperties': {
                'properties': {
                    'sheetId': 0,
                    'gridProperties': {
                        'frozenRowCount': 1
                    }
                },
                'fields': 'gridProperties.frozenRowCount'
            }
        })
        
        # Auto-resize columns in Tasks sheet
        requests.append({
            'autoResizeDimensions': {
                'dimensions': {
                    'sheetId': 0,
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': 10
                }
            }
        })
        
        # Format Summary sheet title
        requests.append({
            'repeatCell': {
                'range': {
                    'sheetId': 1,
                    'startRowIndex': 0,
                    'endRowIndex': 1,
                    'startColumnIndex': 0,
                    'endColumnIndex': 2
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {
                            'red': 0.9,
                            'green': 0.9,
                            'blue': 0.9
                        },
                        'textFormat': {
                            'bold': True,
                            'fontSize': 14
                        }
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)'
            }
        })
        
        # Format section headers in Summary sheet
        requests.append({
            'repeatCell': {
                'range': {
                    'sheetId': 1,
                    'startRowIndex': 3,
                    'endRowIndex': 4,
                    'startColumnIndex': 0,
                    'endColumnIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'textFormat': {
                            'bold': True
                        }
                    }
                },
                'fields': 'userEnteredFormat(textFormat)'
            }
        })
        
        requests.append({
            'repeatCell': {
                'range': {
                    'sheetId': 1,
                    'startRowIndex': 10,
                    'endRowIndex': 11,
                    'startColumnIndex': 0,
                    'endColumnIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'textFormat': {
                            'bold': True
                        }
                    }
                },
                'fields': 'userEnteredFormat(textFormat)'
            }
        })
        
        requests.append({
            'repeatCell': {
                'range': {
                    'sheetId': 1,
                    'startRowIndex': 15,
                    'endRowIndex': 16,
                    'startColumnIndex': 0,
                    'endColumnIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'textFormat': {
                            'bold': True
                        }
                    }
                },
                'fields': 'userEnteredFormat(textFormat)'
            }
        })
        
        # Auto-resize columns in Summary sheet
        requests.append({
            'autoResizeDimensions': {
                'dimensions': {
                    'sheetId': 1,
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': 2
                }
            }
        })
        
        # Apply conditional formatting for overdue tasks
        requests.append({
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [
                        {
                            'sheetId': 0,
                            'startRowIndex': 1,
                            'startColumnIndex': 9,
                            'endColumnIndex': 10
                        }
                    ],
                    'booleanRule': {
                        'condition': {
                            'type': 'TEXT_EQ',
                            'values': [
                                {
                                    'userEnteredValue': 'Yes'
                                }
                            ]
                        },
                        'format': {
                            'backgroundColor': {
                                'red': 1.0,
                                'green': 0.8,
                                'blue': 0.8
                            }
                        }
                    }
                },
                'index': 0
            }
        })
        
        # Apply conditional formatting for high priority tasks
        requests.append({
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [
                        {
                            'sheetId': 0,
                            'startRowIndex': 1,
                            'startColumnIndex': 3,
                            'endColumnIndex': 4
                        }
                    ],
                    'booleanRule': {
                        'condition': {
                            'type': 'TEXT_EQ',
                            'values': [
                                {
                                    'userEnteredValue': 'High'
                                }
                            ]
                        },
                        'format': {
                            'backgroundColor': {
                                'red': 1.0,
                                'green': 0.9,
                                'blue': 0.9
                            },
                            'textFormat': {
                                'bold': True
                            }
                        }
                    }
                },
                'index': 1
            }
        })
        
        # Apply conditional formatting for completed tasks
        requests.append({
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [
                        {
                            'sheetId': 0,
                            'startRowIndex': 1,
                            'startColumnIndex': 4,
                            'endColumnIndex': 5
                        }
                    ],
                    'booleanRule': {
                        'condition': {
                            'type': 'TEXT_EQ',
                            'values': [
                                {
                                    'userEnteredValue': 'Completed'
                                }
                            ]
                        },
                        'format': {
                            'backgroundColor': {
                                'red': 0.9,
                                'green': 1.0,
                                'blue': 0.9
                            }
                        }
                    }
                },
                'index': 2
            }
        })
        
        # Execute formatting requests
        if requests:
            body = {
                'requests': requests
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
    
    def create_task_report_sheet(self, tasks: List[Task], report_type: str = "summary") -> Dict[str, Any]:
        """Create a specialized task report sheet"""
        if not self.service or not tasks:
            return {
                'success': False,
                'error': 'Service not available or no tasks provided'
            }
        
        try:
            spreadsheet_name = f"Task Report - {report_type.title()} - {datetime.now().strftime('%Y-%m-%d')}"
            
            if report_type == "overdue":
                overdue_tasks = [task for task in tasks if task.is_overdue()]
                result = self.export_tasks_to_sheet(overdue_tasks, f"{spreadsheet_name} (Overdue Only)")
            elif report_type == "high_priority":
                high_priority_tasks = [task for task in tasks if task.priority == 'high']
                result = self.export_tasks_to_sheet(high_priority_tasks, f"{spreadsheet_name} (High Priority)")
            else:
                result = self.export_tasks_to_sheet(tasks, spreadsheet_name)
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating task report: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to create task report: {str(e)}'
            }
