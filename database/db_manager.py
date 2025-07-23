"""
Database Manager for Task Manager API
Handles SQLite database operations for tasks
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from models.task import Task
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "task_manager.db"):
        self.db_path = db_path
        
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def init_db(self):
        """Initialize database with tasks table"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    calendar_event_id TEXT
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)')
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def create_task(self, task: Task) -> Task:
        """Create a new task"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tasks (title, description, due_date, priority, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                task.title,
                task.description,
                task.due_date.isoformat() if task.due_date else None,
                task.priority,
                task.status,
                task.created_at.isoformat()
            ))
            
            task_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Set the task ID and return the task
            task.id = task_id
            return task
            
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            raise
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return Task.from_db_row(dict(row))
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {str(e)}")
            raise
    
    def get_all_tasks(self, status: Optional[str] = None, priority: Optional[str] = None, limit: Optional[int] = None) -> List[Task]:
        """Get all tasks with optional filtering"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = 'SELECT * FROM tasks WHERE 1=1'
            params = []
            
            if status:
                query += ' AND status = ?'
                params.append(status)
                
            if priority:
                query += ' AND priority = ?'
                params.append(priority)
            
            query += ' ORDER BY created_at DESC'
            
            if limit:
                query += ' LIMIT ?'
                params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [Task.from_db_row(dict(row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting all tasks: {str(e)}")
            raise
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Alias for get_task"""
        return self.get_task(task_id)
    
    def update_task(self, task_id: int, updates: Dict[str, Any]) -> bool:
        """Update a task"""
        try:
            if not updates:
                return True
                
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build dynamic update query
            set_clauses = []
            params = []
            
            for key, value in updates.items():
                if key in ['title', 'description', 'priority', 'status', 'calendar_event_id']:
                    set_clauses.append(f'{key} = ?')
                    params.append(value)
                elif key == 'due_date' and value:
                    set_clauses.append('due_date = ?')
                    # Handle both string and datetime objects
                    if isinstance(value, str):
                        params.append(value)
                    else:
                        params.append(value.isoformat())
            
            if set_clauses:
                set_clauses.append('updated_at = ?')
                # Use system local time for all timestamps (synchronized with user's system)
                params.append(datetime.now().isoformat())
                params.append(task_id)
                
                query = f'UPDATE tasks SET {", ".join(set_clauses)} WHERE id = ?'
                cursor.execute(query, params)
                
                success = cursor.rowcount > 0
                conn.commit()
                conn.close()
                
                return success
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            raise
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            success = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            raise
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            current_date = datetime.now().isoformat()
            
            cursor.execute('''
                SELECT * FROM tasks 
                WHERE due_date IS NOT NULL 
                AND due_date < ? 
                AND status != 'completed'
                ORDER BY due_date ASC
            ''', (current_date,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [Task.from_db_row(dict(row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting overdue tasks: {str(e)}")
            raise
    
    def get_tasks_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Task]:
        """Get tasks within a date range"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM tasks 
                WHERE due_date IS NOT NULL 
                AND due_date BETWEEN ? AND ?
                ORDER BY due_date ASC
            ''', (start_date.isoformat(), end_date.isoformat()))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [Task.from_db_row(dict(row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting tasks by date range: {str(e)}")
            raise
