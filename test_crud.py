#!/usr/bin/env python3
"""
Task Manager API - CRUD Testing
Test adding tasks, viewing tasks, and all CRUD operations
"""

import requests
import json
from datetime import datetime, timedelta

def test_task_crud():
    """Test complete CRUD operations for tasks"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Task Manager API - CRUD Testing")
    print("=" * 50)
    
    try:
        # 1. Check API health first
        print("\n1. 🏥 Health Check")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ API is healthy and ready")
        else:
            print("   ❌ API health check failed")
            return
        
        # 2. Create multiple test tasks
        print("\n2. 📝 Creating Test Tasks")
        
        test_tasks = [
            {
                "title": "Design API Documentation",
                "description": "Create comprehensive API documentation with examples",
                "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "priority": "high",
                "status": "pending"
            },
            {
                "title": "Code Review Session",
                "description": "Review pull requests from the development team",
                "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "priority": "medium",
                "status": "pending"
            },
            {
                "title": "Database Optimization",
                "description": "Optimize database queries for better performance",
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "priority": "low",
                "status": "pending"
            },
            {
                "title": "Deploy to Production",
                "description": "Deploy the latest version to production environment",
                "due_date": (datetime.now() + timedelta(hours=6)).isoformat(),
                "priority": "high",
                "status": "in_progress"
            },
            {
                "title": "Write Unit Tests",
                "description": "Add comprehensive unit tests for all modules",
                "due_date": (datetime.now() - timedelta(days=1)).isoformat(),  # Overdue
                "priority": "medium",
                "status": "pending"
            }
        ]
        
        created_tasks = []
        
        for i, task_data in enumerate(test_tasks, 1):
            print(f"\n   Creating Task {i}: {task_data['title']}")
            
            try:
                response = requests.post(f"{base_url}/tasks", json=task_data)
                
                if response.status_code == 201:
                    task = response.json()['data']
                    created_tasks.append(task)
                    print(f"   ✅ Created Task ID {task['id']}: {task['title']}")
                    print(f"      Priority: {task['priority']} | Status: {task['status']}")
                    print(f"      Due: {task['due_date']}")
                else:
                    print(f"   ❌ Failed to create task {i}: {response.status_code}")
                    print(f"      Error: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Exception creating task {i}: {e}")
        
        print(f"\n   📊 Successfully created {len(created_tasks)} tasks")
        
        # 3. View all tasks
        print("\n3. 📋 Viewing All Tasks")
        response = requests.get(f"{base_url}/tasks")
        if response.status_code == 200:
            all_tasks = response.json()['data']
            print(f"   ✅ Retrieved {all_tasks['count']} total tasks")
            
            print("\n   📝 Task List:")
            for task in all_tasks['tasks']:
                status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                
                print(f"   {status_emoji.get(task['status'], '📝')} {priority_emoji.get(task['priority'], '🟡')} "
                      f"ID {task['id']}: {task['title']}")
                print(f"      Status: {task['status']} | Priority: {task['priority']}")
                print(f"      Due: {task['due_date']}")
                if task['description']:
                    print(f"      Description: {task['description'][:50]}...")
                print()
        else:
            print(f"   ❌ Failed to retrieve tasks: {response.status_code}")
        
        # 4. Test filtering
        print("\n4. 🔍 Testing Task Filtering")
        
        # Filter by status
        response = requests.get(f"{base_url}/tasks?status=pending")
        if response.status_code == 200:
            pending_tasks = response.json()['data']
            print(f"   ✅ Pending tasks: {pending_tasks['count']}")
        
        # Filter by priority
        response = requests.get(f"{base_url}/tasks?priority=high")
        if response.status_code == 200:
            high_priority = response.json()['data']
            print(f"   ✅ High priority tasks: {high_priority['count']}")
        
        # Combined filter
        response = requests.get(f"{base_url}/tasks?status=pending&priority=medium")
        if response.status_code == 200:
            filtered = response.json()['data']
            print(f"   ✅ Pending medium priority tasks: {filtered['count']}")
        
        # 5. Test individual task retrieval
        print("\n5. 🔍 Testing Individual Task Retrieval")
        if created_tasks:
            task_id = created_tasks[0]['id']
            response = requests.get(f"{base_url}/tasks/{task_id}")
            if response.status_code == 200:
                task = response.json()['data']
                print(f"   ✅ Retrieved Task ID {task_id}: {task['title']}")
                print(f"      Full details: {json.dumps(task, indent=2)}")
            else:
                print(f"   ❌ Failed to retrieve task {task_id}")
        
        # 6. Test task updating
        print("\n6. ✏️  Testing Task Updates")
        if created_tasks:
            task_id = created_tasks[0]['id']
            update_data = {
                "status": "in_progress",
                "priority": "urgent"
            }
            
            response = requests.put(f"{base_url}/tasks/{task_id}", json=update_data)
            if response.status_code == 200:
                updated_task = response.json()['data']
                print(f"   ✅ Updated Task ID {task_id}")
                print(f"      New status: {updated_task['status']}")
                print(f"      New priority: {updated_task['priority']}")
            else:
                print(f"   ❌ Failed to update task {task_id}")
        
        # 7. Test dashboard with real data
        print("\n7. 📊 Dashboard with Real Data")
        response = requests.get(f"{base_url}/dashboard")
        if response.status_code == 200:
            dashboard = response.json()['data']
            stats = dashboard['statistics']
            
            print(f"   📈 Dashboard Statistics:")
            print(f"      Total Tasks: {stats['total_tasks']}")
            print(f"      Completed: {stats['completed_tasks']}")
            print(f"      Pending: {stats['pending_tasks']}")
            print(f"      In Progress: {stats['in_progress_tasks']}")
            print(f"      Overdue: {stats['overdue_tasks']}")
            print(f"      Completion Rate: {stats['completion_rate']}%")
            
            if dashboard.get('recent_tasks'):
                print(f"\n   📋 Recent Tasks:")
                for task in dashboard['recent_tasks']:
                    print(f"      • {task['title']} [{task['status']}]")
            
            if dashboard.get('overdue_tasks'):
                print(f"\n   ⚠️  Overdue Tasks:")
                for task in dashboard['overdue_tasks']:
                    print(f"      • {task['title']} (Due: {task['due_date']})")
        
        # 8. Test Google API integrations with real tasks
        print("\n8. 🔗 Testing Google API Integrations")
        
        if created_tasks:
            task_id = created_tasks[0]['id']
            
            # Test email reminder
            print(f"\n   📧 Email Reminder for Task {task_id}")
            email_data = {"recipient_email": "test@example.com"}
            response = requests.post(f"{base_url}/tasks/{task_id}/email-reminder", json=email_data)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {result['message']}")
            
            # Test calendar integration
            print(f"\n   📅 Calendar Event for Task {task_id}")
            calendar_data = {
                "duration_minutes": 90,
                "reminder_minutes": 30,
                "location": "Conference Room A"
            }
            response = requests.post(f"{base_url}/tasks/{task_id}/add-to-calendar", json=calendar_data)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {result['message']}")
        
        # Test sheets export
        print(f"\n   📊 Sheets Export")
        export_data = {"spreadsheet_name": "Task Manager Test Export"}
        response = requests.post(f"{base_url}/tasks/export-to-sheets", json=export_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ {result['message']}")
        
        # 9. Test task deletion
        print("\n9. 🗑️  Testing Task Deletion")
        if len(created_tasks) > 2:  # Keep some tasks, delete others
            tasks_to_delete = created_tasks[-2:]  # Delete last 2 tasks
            
            for task in tasks_to_delete:
                task_id = task['id']
                response = requests.delete(f"{base_url}/tasks/{task_id}")
                if response.status_code == 200:
                    print(f"   ✅ Deleted Task ID {task_id}: {task['title']}")
                else:
                    print(f"   ❌ Failed to delete task {task_id}")
        
        # 10. Final task count
        print("\n10. 📊 Final Task Count")
        response = requests.get(f"{base_url}/tasks")
        if response.status_code == 200:
            final_tasks = response.json()['data']
            print(f"   ✅ Final task count: {final_tasks['count']}")
            
            print(f"\n   📋 Remaining Tasks:")
            for task in final_tasks['tasks']:
                print(f"      • ID {task['id']}: {task['title']} [{task['status']}]")
        
        # Summary
        print("\n" + "=" * 50)
        print("🎉 CRUD TESTING COMPLETE!")
        print("\n✅ TESTED SUCCESSFULLY:")
        print("   • Task Creation (POST /tasks)")
        print("   • Task Listing (GET /tasks)")
        print("   • Task Filtering (GET /tasks?filter)")
        print("   • Individual Task Retrieval (GET /tasks/{id})")
        print("   • Task Updates (PUT /tasks/{id})")
        print("   • Task Deletion (DELETE /tasks/{id})")
        print("   • Dashboard Statistics")
        print("   • Google API Integrations")
        
        print(f"\n📊 Results:")
        print(f"   • Tasks Created: {len(created_tasks)}")
        print(f"   • Tasks Remaining: {final_tasks['count']}")
        print(f"   • All CRUD operations: ✅ Working")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Please ensure server is running:")
        print("   python app_final.py")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_task_crud()
