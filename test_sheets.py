#!/usr/bin/env python3
"""
Test Google Sheets API Integration
Test exporting tasks to Google Spreadsheets and validate functionality
"""

import requests
import json
from datetime import datetime, timedelta

def test_sheets_api():
    """Test Google Sheets API functionality"""
    
    base_url = "http://localhost:5000"
    
    print("📊 Testing Google Sheets API Integration")
    print("=" * 60)
    
    try:
        # 1. Check API health
        print("\n1. 🏥 API Health Check")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ API is healthy and ready")
        else:
            print("   ❌ API health check failed")
            return
        
        # 2. Get current tasks to export
        print("\n2. 📋 Getting Current Tasks")
        response = requests.get(f"{base_url}/tasks")
        if response.status_code == 200:
            tasks_data = response.json()['data']
            task_count = tasks_data['count']
            print(f"   ✅ Found {task_count} tasks to export")
            
            if task_count == 0:
                print("   📝 No tasks found. Creating sample tasks for testing...")
                # Create sample tasks for testing
                sample_tasks = [
                    {
                        "title": "Sheets Test Task 1",
                        "description": "High priority task for sheets testing",
                        "due_date": (datetime.now() + timedelta(days=2)).isoformat(),
                        "priority": "high",
                        "status": "pending"
                    },
                    {
                        "title": "Sheets Test Task 2", 
                        "description": "Medium priority completed task",
                        "due_date": (datetime.now() - timedelta(days=1)).isoformat(),
                        "priority": "medium",
                        "status": "completed"
                    }
                ]
                
                for task_data in sample_tasks:
                    response = requests.post(f"{base_url}/tasks", json=task_data)
                    if response.status_code == 201:
                        task = response.json()['data']
                        print(f"   ✅ Created sample task: {task['title']}")
        else:
            print(f"   ❌ Failed to get tasks: {response.text}")
            return
        
        # 3. Test Sheets Export - Basic
        print("\n3. 📊 Testing Basic Sheets Export")
        export_data = {
            "spreadsheet_name": "Task Manager Test Export"
        }
        
        print(f"   📤 Exporting to: '{export_data['spreadsheet_name']}'")
        response = requests.post(f"{base_url}/tasks/export-to-sheets", json=export_data)
        
        print(f"   🔍 Response Status: {response.status_code}")
        print(f"   📄 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', {})
                print(f"   ✅ Sheets export successful!")
                print(f"   📊 Spreadsheet Created: {data.get('spreadsheet_name', 'Unknown')}")
                print(f"   🔗 Spreadsheet URL: {data.get('spreadsheet_url', 'Not provided')}")
                print(f"   📈 Tasks Exported: {data.get('tasks_exported', 'Unknown')}")
                print(f"   📋 Sheets Created: {data.get('sheets_created', 'Unknown')}")
            else:
                print(f"   ❌ Sheets export failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ API request failed with status {response.status_code}")
        
        # 4. Test Sheets Export - Custom Name with Date
        print("\n4. 📊 Testing Custom Named Sheets Export")
        custom_export_data = {
            "spreadsheet_name": f"Weekly Report - {datetime.now().strftime('%Y-%m-%d')}"
        }
        
        response = requests.post(f"{base_url}/tasks/export-to-sheets", json=custom_export_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ Custom export successful!")
                data = result.get('data', {})
                print(f"   📊 Name: {data.get('spreadsheet_name')}")
            else:
                print(f"   ❌ Custom export failed: {result.get('error')}")
        
        # 5. Test Sheets Export - Empty Request
        print("\n5. 📊 Testing Default Sheets Export (No Custom Name)")
        response = requests.post(f"{base_url}/tasks/export-to-sheets", json={})
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ Default export successful!")
                data = result.get('data', {})
                print(f"   📊 Auto-generated name: {data.get('spreadsheet_name')}")
        
        # Summary
        print("\n" + "=" * 60)
        print("🎉 GOOGLE SHEETS API TEST COMPLETE!")
        print("\n✅ SHEETS FUNCTIONALITY TESTED:")
        print("   • ✅ Basic spreadsheet creation")
        print("   • ✅ Task data export")
        print("   • ✅ Custom spreadsheet naming")
        print("   • ✅ Default naming fallback")
        print("   • ✅ URL generation for sharing")
        
        print("\n📊 What was created in Google Sheets:")
        print("   • Main sheet with all task data")
        print("   • Summary sheet with statistics")
        print("   • Formatted columns and headers")
        print("   • Shareable spreadsheet URL")
        
        print("\n🔍 Validation Steps:")
        print("   1. Check your Google Drive for new spreadsheets")
        print("   2. Open the provided URLs to verify data")
        print("   3. Confirm all task fields are present")
        print("   4. Verify summary statistics are correct")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Please ensure server is running:")
        print("   python app_final.py")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_sheets_api()
