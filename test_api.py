"""
Test Script for Task Manager API
Comprehensive testing of all endpoints and Google API integrations
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

class TaskManagerAPITester:
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.created_task_ids = []
        
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Task Manager API Test Suite")
        print("=" * 50)
        
        # Test basic API health
        if not self.test_health_check():
            print("❌ API is not responding. Please start the server first.")
            return
            
        # Core CRUD tests
        print("\n📋 Testing Core CRUD Operations...")
        self.test_create_task()
        self.test_get_all_tasks()
        self.test_get_single_task()
        self.test_update_task()
        self.test_filter_tasks()
        
        # Google API integration tests
        print("\n🔗 Testing Google API Integrations...")
        self.test_integration_status()
        self.test_gmail_integration()
        self.test_sheets_integration()
        self.test_calendar_integration()
        
        # Bonus feature tests
        print("\n✨ Testing Bonus Features...")
        self.test_dashboard()
        self.test_batch_operations()
        
        # Error handling tests
        print("\n⚠️ Testing Error Handling...")
        self.test_error_handling()
        
        # Cleanup
        print("\n🧹 Cleaning up test data...")
        self.cleanup_test_data()
        
        print("\n✅ Test Suite Complete!")
        
    def test_health_check(self) -> bool:
        """Test API health check"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_create_task(self):
        """Test task creation"""
        test_tasks = [
            {
                "title": "Test Task 1 - High Priority",
                "description": "This is a test task with high priority",
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "priority": "high",
                "status": "pending"
            },
            {
                "title": "Test Task 2 - Overdue",
                "description": "This task is intentionally overdue for testing",
                "due_date": (datetime.now() - timedelta(days=2)).isoformat(),
                "priority": "medium",
                "status": "pending"
            },
            {
                "title": "Test Task 3 - No Due Date",
                "description": "This task has no due date",
                "priority": "low",
                "status": "in_progress"
            }
        ]
        
        for i, task_data in enumerate(test_tasks, 1):
            try:
                response = self.session.post(
                    f"{self.base_url}/tasks",
                    json=task_data
                )
                
                if response.status_code == 201:
                    data = response.json()
                    task_id = data['data']['id']
                    self.created_task_ids.append(task_id)
                    print(f"✅ Created test task {i}: ID {task_id}")
                else:
                    print(f"❌ Failed to create test task {i}: {response.status_code}")
                    print(response.text)
                    
            except Exception as e:
                print(f"❌ Error creating test task {i}: {e}")
    
    def test_get_all_tasks(self):
        """Test getting all tasks"""
        try:
            response = self.session.get(f"{self.base_url}/tasks")
            
            if response.status_code == 200:
                data = response.json()
                task_count = data['data']['count']
                print(f"✅ Retrieved all tasks: {task_count} tasks found")
            else:
                print(f"❌ Failed to get all tasks: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error getting all tasks: {e}")
    
    def test_get_single_task(self):
        """Test getting a single task"""
        if not self.created_task_ids:
            print("⚠️ No tasks to test single task retrieval")
            return
            
        task_id = self.created_task_ids[0]
        try:
            response = self.session.get(f"{self.base_url}/tasks/{task_id}")
            
            if response.status_code == 200:
                print(f"✅ Retrieved single task: ID {task_id}")
            else:
                print(f"❌ Failed to get single task {task_id}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error getting single task: {e}")
    
    def test_update_task(self):
        """Test updating a task"""
        if not self.created_task_ids:
            print("⚠️ No tasks to update")
            return
            
        task_id = self.created_task_ids[0]
        update_data = {
            "status": "completed",
            "description": "Updated description during testing"
        }
        
        try:
            response = self.session.put(
                f"{self.base_url}/tasks/{task_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                print(f"✅ Updated task: ID {task_id}")
            else:
                print(f"❌ Failed to update task {task_id}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error updating task: {e}")
    
    def test_filter_tasks(self):
        """Test task filtering"""
        filters = [
            {"status": "pending"},
            {"priority": "high"},
            {"status": "completed", "priority": "high"}
        ]
        
        for filter_params in filters:
            try:
                response = self.session.get(f"{self.base_url}/tasks", params=filter_params)
                
                if response.status_code == 200:
                    data = response.json()
                    count = data['data']['count']
                    filter_str = "&".join([f"{k}={v}" for k, v in filter_params.items()])
                    print(f"✅ Filter test ({filter_str}): {count} tasks")
                else:
                    print(f"❌ Filter test failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error in filter test: {e}")
    
    def test_integration_status(self):
        """Test integration status endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/tasks/integrations")
            
            if response.status_code == 200:
                data = response.json()
                gmail_status = data['data']['gmail']['status']
                sheets_status = data['data']['sheets']['status']
                calendar_status = data['data']['calendar']['status']
                
                print(f"✅ Integration Status - Gmail: {gmail_status}, Sheets: {sheets_status}, Calendar: {calendar_status}")
            else:
                print(f"❌ Failed to get integration status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error getting integration status: {e}")
    
    def test_gmail_integration(self):
        """Test Gmail API integration"""
        if not self.created_task_ids:
            print("⚠️ No tasks to test Gmail integration")
            return
            
        task_id = self.created_task_ids[0]
        email_data = {
            "recipient_email": "test@example.com"  # Use a valid email for real testing
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/tasks/{task_id}/email-reminder",
                json=email_data
            )
            
            if response.status_code == 200:
                print("✅ Gmail integration test passed")
            elif response.status_code == 500:
                data = response.json()
                if "Gmail service not available" in data.get('error', ''):
                    print("⚠️ Gmail integration not configured (this is expected in testing)")
                else:
                    print(f"❌ Gmail integration error: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ Gmail integration failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing Gmail integration: {e}")
    
    def test_sheets_integration(self):
        """Test Google Sheets API integration"""
        export_data = {
            "spreadsheet_name": "Test Export"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/tasks/export-to-sheets",
                json=export_data
            )
            
            if response.status_code == 200:
                print("✅ Google Sheets integration test passed")
            elif response.status_code == 500:
                data = response.json()
                if "Sheets service not available" in data.get('error', ''):
                    print("⚠️ Sheets integration not configured (this is expected in testing)")
                else:
                    print(f"❌ Sheets integration error: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ Sheets integration failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing Sheets integration: {e}")
    
    def test_calendar_integration(self):
        """Test Google Calendar API integration"""
        if not self.created_task_ids:
            print("⚠️ No tasks to test Calendar integration")
            return
            
        # Find a task with a due date
        task_id = None
        for tid in self.created_task_ids:
            try:
                response = self.session.get(f"{self.base_url}/tasks/{tid}")
                if response.status_code == 200:
                    task_data = response.json()
                    if task_data['data']['due_date']:
                        task_id = tid
                        break
            except:
                continue
                
        if not task_id:
            print("⚠️ No tasks with due dates found for Calendar integration test")
            return
            
        calendar_data = {
            "duration_minutes": 60,
            "reminder_minutes": 15,
            "location": "Test Location"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/tasks/{task_id}/add-to-calendar",
                json=calendar_data
            )
            
            if response.status_code == 200:
                print("✅ Google Calendar integration test passed")
            elif response.status_code == 500:
                data = response.json()
                if "Calendar service not available" in data.get('error', ''):
                    print("⚠️ Calendar integration not configured (this is expected in testing)")
                else:
                    print(f"❌ Calendar integration error: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ Calendar integration failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing Calendar integration: {e}")
    
    def test_dashboard(self):
        """Test dashboard endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                stats = data['data']['statistics']
                print(f"✅ Dashboard test passed - Total tasks: {stats['total_tasks']}, Completed: {stats['completed_tasks']}")
            else:
                print(f"❌ Dashboard test failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing dashboard: {e}")
    
    def test_batch_operations(self):
        """Test batch operations"""
        batch_data = {
            "recipient_email": "test@example.com"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/tasks/batch/email-reminders",
                json=batch_data
            )
            
            if response.status_code == 200:
                data = response.json()
                total_tasks = data['data']['total_tasks']
                print(f"✅ Batch operations test passed - Processed {total_tasks} overdue tasks")
            elif response.status_code == 500:
                print("⚠️ Batch operations failed (likely due to Gmail service not configured)")
            else:
                print(f"❌ Batch operations failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing batch operations: {e}")
    
    def test_error_handling(self):
        """Test various error scenarios"""
        error_tests = [
            # Invalid task creation
            {
                "method": "POST",
                "url": "/tasks",
                "data": {"title": ""},  # Empty title
                "expected_code": 400,
                "name": "Empty title validation"
            },
            # Non-existent task
            {
                "method": "GET",
                "url": "/tasks/99999",
                "expected_code": 404,
                "name": "Non-existent task"
            },
            # Invalid task update
            {
                "method": "PUT",
                "url": f"/tasks/{self.created_task_ids[0] if self.created_task_ids else 1}",
                "data": {"priority": "invalid"},
                "expected_code": 400,
                "name": "Invalid priority validation"
            },
            # Invalid endpoint
            {
                "method": "GET",
                "url": "/invalid-endpoint",
                "expected_code": 404,
                "name": "Invalid endpoint"
            }
        ]
        
        for test in error_tests:
            try:
                if test["method"] == "GET":
                    response = self.session.get(f"{self.base_url}{test['url']}")
                elif test["method"] == "POST":
                    response = self.session.post(f"{self.base_url}{test['url']}", json=test.get("data"))
                elif test["method"] == "PUT":
                    response = self.session.put(f"{self.base_url}{test['url']}", json=test.get("data"))
                
                if response.status_code == test["expected_code"]:
                    print(f"✅ Error handling test passed: {test['name']}")
                else:
                    print(f"❌ Error handling test failed: {test['name']} (expected {test['expected_code']}, got {response.status_code})")
                    
            except Exception as e:
                print(f"❌ Error in error handling test {test['name']}: {e}")
    
    def cleanup_test_data(self):
        """Clean up test data"""
        for task_id in self.created_task_ids:
            try:
                response = self.session.delete(f"{self.base_url}/tasks/{task_id}")
                if response.status_code == 200:
                    print(f"✅ Deleted test task: ID {task_id}")
                else:
                    print(f"⚠️ Could not delete test task {task_id}: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Error deleting test task {task_id}: {e}")

def main():
    """Run the test suite"""
    import sys
    
    base_url = "http://localhost:5000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    tester = TaskManagerAPITester(base_url)
    tester.run_all_tests()

if __name__ == "__main__":
    main()
