"""
Task Model for Task Manager API
Represents a task with all its properties and methods
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import json

@dataclass
class Task:
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str = 'medium'  # low, medium, high
    status: str = 'pending'   # pending, in_progress, completed
    created_at: datetime = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None
    calendar_event_id: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create Task from dictionary"""
        task_data = data.copy()
        
        # Handle date parsing - ensure timezone-naive datetimes for SQLite
        if 'due_date' in task_data and task_data['due_date']:
            if isinstance(task_data['due_date'], str):
                try:
                    # Parse ISO format and convert to naive datetime
                    dt = datetime.fromisoformat(task_data['due_date'].replace('Z', '+00:00'))
                    # Convert to naive datetime (remove timezone info)
                    task_data['due_date'] = dt.replace(tzinfo=None) if dt.tzinfo else dt
                except ValueError:
                    # Try parsing different date formats
                    for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                        try:
                            task_data['due_date'] = datetime.strptime(task_data['due_date'], fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        task_data['due_date'] = None
        
        if 'created_at' in task_data and task_data['created_at']:
            if isinstance(task_data['created_at'], str):
                dt = datetime.fromisoformat(task_data['created_at'].replace('Z', '+00:00'))
                task_data['created_at'] = dt.replace(tzinfo=None) if dt.tzinfo else dt
        
        if 'updated_at' in task_data and task_data['updated_at']:
            if isinstance(task_data['updated_at'], str):
                task_data['updated_at'] = datetime.fromisoformat(task_data['updated_at'].replace('Z', '+00:00'))
        
        return cls(**task_data)
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'Task':
        """Create Task from database row"""
        task_data = row.copy()
        
        # Parse datetime strings from database
        if task_data.get('due_date'):
            task_data['due_date'] = datetime.fromisoformat(task_data['due_date'])
        
        if task_data.get('created_at'):
            task_data['created_at'] = datetime.fromisoformat(task_data['created_at'])
        
        if task_data.get('updated_at'):
            task_data['updated_at'] = datetime.fromisoformat(task_data['updated_at'])
        
        return cls(**task_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Task to dictionary"""
        result = asdict(self)
        
        # Convert datetime objects to ISO strings
        if result['due_date']:
            result['due_date'] = result['due_date'].isoformat()
        
        if result['created_at']:
            result['created_at'] = result['created_at'].isoformat()
        
        if result['updated_at']:
            result['updated_at'] = result['updated_at'].isoformat()
        
        return result
    
    def to_json(self) -> str:
        """Convert Task to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if not self.due_date or self.status == 'completed':
            return False
        return self.due_date < datetime.now()
    
    def days_until_due(self) -> Optional[int]:
        """Get number of days until due date"""
        if not self.due_date:
            return None
        
        delta = self.due_date - datetime.now()
        return delta.days
    
    def get_priority_value(self) -> int:
        """Get numeric priority value for sorting"""
        priority_map = {
            'low': 1,
            'medium': 2,
            'high': 3
        }
        return priority_map.get(self.priority, 2)
    
    def validate(self) -> Dict[str, Any]:
        """Validate task data"""
        errors = []
        
        if not self.title or len(self.title.strip()) == 0:
            errors.append("Title is required")
        
        if len(self.title) > 200:
            errors.append("Title must be less than 200 characters")
        
        if self.description and len(self.description) > 1000:
            errors.append("Description must be less than 1000 characters")
        
        if self.priority not in ['low', 'medium', 'high']:
            errors.append("Priority must be one of: low, medium, high")
        
        if self.status not in ['pending', 'in_progress', 'completed']:
            errors.append("Status must be one of: pending, in_progress, completed")
        
        if self.due_date and self.due_date < datetime.now() - timedelta(days=365):
            errors.append("Due date cannot be more than a year in the past")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def __str__(self) -> str:
        return f"Task(id={self.id}, title='{self.title}', status='{self.status}', priority='{self.priority}')"
    
    def __repr__(self) -> str:
        return self.__str__()
