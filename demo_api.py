#!/usr/bin/env python3
"""
Demo script for Task Manager API
Showcases all functionality with sample data
"""

import requests
import json
import time
from datetime import datetime, timedelta

class TaskManagerDemo:
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        
    def run_demo(self):
        """Run complete demo of Task Manager API"""
        print("🚀 Task Manager API Demo")
        print("=" * 50)
        
        # 1. Check API health
        print("\n1. 🏥 Checking API Health...")
        response = requests.get(f"{self.base_url}/health")
        print(f"   Status: {response.json()['data']['status']}")
        
        # 2. Create sample tasks
        print("\n2. 📝 Creating Sample Tasks...")
        tasks_to_create = [
            {
                "title": "Complete project proposal",
                "description": "Write and submit the Q4 project proposal",
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "priority": "high",
                "status": "pending"
            },
            {
                "title": "Review team performance",
                "description": "Conduct quarterly performance reviews",
                "due_date": (datetime.now() + timedelta(days=14)).isoformat(),
                "priority": "medium",
                "status": "pending"
            },
            {
                "title": "Update documentation",
                "description": "Update API and user documentation",
                "due_date": (datetime.now() - timedelta(days=2)).isoformat(),  # Overdue
                "priority": "low",
                "status": "pending"
            }
        ]
        
        created_tasks = []
        for i, task_data in enumerate(tasks_to_create, 1):
            response = requests.post(f"{self.base_url}/tasks", json=task_data)
            if response.status_code == 201:
                task = response.json()['data']
                created_tasks.append(task)
                print(f"   ✅ Created: {task['title']} (ID: {task['id']})")
            else:
                print(f"   ❌ Failed to create task {i}")
        
        # 3. List all tasks
        print("\n3. 📋 Listing All Tasks...")
        response = requests.get(f"{self.base_url}/tasks")
        if response.status_code == 200:
            data = response.json()['data']
            print(f"   Found {data['count']} tasks:")
            for task in data['tasks']:
                status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                print(f"   {status_emoji.get(task['status'], '📝')} {priority_emoji.get(task['priority'], '🟡')} {task['title']}")
        
        # 4. Update a task
        print("\n4. ✏️  Updating Task Status...")
        if created_tasks:
            task_id = created_tasks[0]['id']
            update_data = {"status": "in_progress"}
            response = requests.put(f"{self.base_url}/tasks/{task_id}", json=update_data)
            if response.status_code == 200:
                print(f"   ✅ Updated task {task_id} to 'in_progress'")
            else:
                print(f"   ❌ Failed to update task {task_id}")
        
        # 5. Filter tasks
        print("\n5. 🔍 Filtering Tasks...")
        filters = [
            ("status=pending", "pending tasks"),
            ("priority=high", "high priority tasks"),
            ("status=pending&priority=medium", "pending medium priority tasks")
        ]
        
        for filter_param, description in filters:
            response = requests.get(f"{self.base_url}/tasks?{filter_param}")
            if response.status_code == 200:
                count = response.json()['data']['count']
                print(f"   🔎 Found {count} {description}")
        
        # 6. Check integration status
        print("\n6. 🔗 Checking Google API Integrations...")
        response = requests.get(f"{self.base_url}/tasks/integrations")
        if response.status_code == 200:
            integrations = response.json()['data']
            for service, info in integrations.items():
                status_emoji = "✅" if info['status'] == 'connected' else "❌"
                print(f"   {status_emoji} {service.title()}: {info['status']}")
        
        # 7. Test Gmail integration (will show not configured)
        print("\n7. 📧 Testing Email Reminder...")
        if created_tasks:
            task_id = created_tasks[0]['id']
            email_data = {"recipient_email": "demo@example.com"}
            response = requests.post(f"{self.base_url}/tasks/{task_id}/email-reminder", json=email_data)
            if response.status_code == 200:
                print("   ✅ Email reminder sent successfully!")
            else:
                print("   ⚠️  Email service not configured (expected for demo)")
        
        # 8. Test Sheets export
        print("\n8. 📊 Testing Google Sheets Export...")
        export_data = {"spreadsheet_name": "Task Manager Demo Export"}
        response = requests.post(f"{self.base_url}/tasks/export-to-sheets", json=export_data)
        if response.status_code == 200:
            print("   ✅ Tasks exported to Google Sheets successfully!")
        else:
            print("   ⚠️  Sheets service not configured (expected for demo)")
        
        # 9. Test Calendar integration
        print("\n9. 📅 Testing Google Calendar Integration...")
        if created_tasks:
            task_id = created_tasks[0]['id']
            calendar_data = {
                "duration_minutes": 60,
                "reminder_minutes": 30,
                "location": "Office Conference Room"
            }
            response = requests.post(f"{self.base_url}/tasks/{task_id}/add-to-calendar", json=calendar_data)
            if response.status_code == 200:
                print("   ✅ Task added to Google Calendar successfully!")
            else:
                print("   ⚠️  Calendar service not configured (expected for demo)")
        
        # 10. View Dashboard
        print("\n10. 📊 Dashboard Statistics...")
        response = requests.get(f"{self.base_url}/dashboard")
        if response.status_code == 200:
            data = response.json()['data']
            stats = data['statistics']
            print(f"   📋 Total Tasks: {stats['total_tasks']}")
            print(f"   ✅ Completed: {stats['completed_tasks']}")
            print(f"   ⏳ Pending: {stats['pending_tasks']}")
            print(f"   ⚠️  Overdue: {stats['overdue_tasks']}")
            print(f"   📈 Completion Rate: {stats['completion_rate']}%")
        
        # 11. Batch email reminders
        print("\n11. 📬 Testing Batch Email Reminders...")
        batch_data = {"recipient_email": "demo@example.com"}
        response = requests.post(f"{self.base_url}/tasks/batch/email-reminders", json=batch_data)
        if response.status_code == 200:
            data = response.json()['data']
            print(f"   📧 Processed {data['total_tasks']} overdue tasks")
        else:
            print("   ⚠️  Email service not configured (expected for demo)")
        
        # 12. Cleanup demo data
        print("\n12. 🧹 Cleaning up demo data...")
        for task in created_tasks:
            response = requests.delete(f"{self.base_url}/tasks/{task['id']}")
            if response.status_code == 200:
                print(f"   ✅ Deleted task: {task['title']}")
        
        print("\n" + "=" * 50)
        print("✨ Demo completed successfully!")
        print("\n📚 Available Endpoints:")
        endpoints = [
            "GET    /health                     - API health check",
            "GET    /tasks                      - List all tasks",
            "POST   /tasks                      - Create new task",
            "GET    /tasks/{id}                 - Get specific task",
            "PUT    /tasks/{id}                 - Update task",
            "DELETE /tasks/{id}                 - Delete task",
            "POST   /tasks/{id}/email-reminder  - Send email reminder",
            "POST   /tasks/export-to-sheets     - Export to Google Sheets",
            "POST   /tasks/{id}/add-to-calendar - Add to Google Calendar",
            "GET    /tasks/integrations         - Integration status",
            "POST   /tasks/batch/email-reminders- Batch email reminders",
            "GET    /dashboard                  - Dashboard statistics"
        ]
        
        for endpoint in endpoints:
            print(f"  {endpoint}")
        
        print(f"\n🌐 API running at: {self.base_url}")
        print("📖 See SETUP.md for Google API configuration")
        print("📦 Import Task_Manager_API.postman_collection.json for testing")

if __name__ == "__main__":
    demo = TaskManagerDemo()
    try:
        demo.run_demo()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Please ensure the server is running:")
        print("   python app.py")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
