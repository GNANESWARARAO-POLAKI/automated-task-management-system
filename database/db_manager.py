"""
Database Manager for Task Manager API
Handles SQLite database operations for tasks and users
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from models.task import Task
import logging

if TYPE_CHECKING:
    from models.user import User

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
        """Initialize database with users and tasks tables"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    password_hash TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    timezone TEXT DEFAULT 'UTC',
                    notification_preferences TEXT DEFAULT 'both'
                )
            ''')
            
            # Create tasks table with user association
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
                    calendar_event_id TEXT,
                    user_id INTEGER,
                    user_email TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Check if user_id column exists in tasks table (for migration)
            cursor.execute("PRAGMA table_info(tasks)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'user_id' not in columns:
                cursor.execute('ALTER TABLE tasks ADD COLUMN user_id INTEGER')
                cursor.execute('ALTER TABLE tasks ADD COLUMN user_email TEXT')
                logger.info("Added user columns to existing tasks table")
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)')
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully with users support")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def create_task(self, task: Task) -> Task:
        """Create a new task"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tasks (title, description, due_date, priority, status, created_at, user_id, user_email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.title,
                task.description,
                task.due_date.isoformat() if task.due_date else None,
                task.priority,
                task.status,
                task.created_at.isoformat(),
                task.user_id,
                task.user_email
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
    
    # User Management Methods
    
    def create_user(self, user) -> 'User':
        """Create a new user"""
        try:
            from models.user import User
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (email, name, password_hash, created_at, is_active, timezone, notification_preferences)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.email,
                user.name,
                user.password_hash,
                user.created_at.isoformat(),
                user.is_active,
                user.timezone,
                user.notification_preferences
            ))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            user.id = user_id
            logger.info(f"Created user: {user.email}")
            return user
            
        except sqlite3.IntegrityError as e:
            logger.error(f"User creation failed - email already exists: {user.email}")
            raise ValueError(f"User with email {user.email} already exists")
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional['User']:
        """Get user by email"""
        try:
            from models.user import User
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE email = ? AND is_active = TRUE', (email,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User.from_db_row(dict(row))
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise
    
    def get_user_by_id(self, user_id: int) -> Optional['User']:
        """Get user by ID"""
        try:
            from models.user import User
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE id = ? AND is_active = TRUE', (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User.from_db_row(dict(row))
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            raise
    
    def update_user(self, user) -> 'User':
        """Update user information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            user.updated_at = datetime.now()
            
            cursor.execute('''
                UPDATE users 
                SET name = ?, password_hash = ?, updated_at = ?, timezone = ?, notification_preferences = ?
                WHERE id = ?
            ''', (
                user.name,
                user.password_hash,
                user.updated_at.isoformat(),
                user.timezone,
                user.notification_preferences,
                user.id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated user: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise
    
    def get_all_users(self) -> List['User']:
        """Get all active users"""
        try:
            from models.user import User
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE is_active = TRUE ORDER BY email')
            rows = cursor.fetchall()
            conn.close()
            
            return [User.from_db_row(dict(row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            raise
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user (soft delete)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users 
                SET is_active = FALSE, updated_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), user_id))
            
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Deactivated user ID: {user_id}")
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Error deactivating user: {str(e)}")
            raise
    
    # Updated Task Methods with User Support
    
    def get_tasks_by_user(self, user_id: int, status: Optional[str] = None) -> List[Task]:
        """Get all tasks for a specific user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if status:
                cursor.execute('''
                    SELECT * FROM tasks 
                    WHERE user_id = ? AND status = ?
                    ORDER BY created_at DESC
                ''', (user_id, status))
            else:
                cursor.execute('''
                    SELECT * FROM tasks 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [Task.from_db_row(dict(row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting tasks for user {user_id}: {str(e)}")
            raise
    
    def get_user_tasks_due_soon(self, user_id: int, hours_ahead: int = 24) -> List[Task]:
        """Get tasks due within specified hours for a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            current_time = datetime.now()
            future_time = current_time + timedelta(hours=hours_ahead)
            
            cursor.execute('''
                SELECT * FROM tasks 
                WHERE user_id = ? 
                AND due_date IS NOT NULL 
                AND due_date BETWEEN ? AND ?
                AND status != 'completed'
                ORDER BY due_date ASC
            ''', (user_id, current_time.isoformat(), future_time.isoformat()))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [Task.from_db_row(dict(row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting due soon tasks for user {user_id}: {str(e)}")
            raise
