#!/usr/bin/env python3
"""
Test REAL Google Sheets Creation
Verify if actual spreadsheets are created in Google Drive
"""

import requests
import json
from datetime import datetime

def test_real_sheets_creation():
    """Test if real Google Sheets are created in your account"""
    
    base_url = "http://localhost:5000"
    
    print("🔍 Testing REAL Google Sheets Creation")
    print("=" * 60)
    
    try:
        # 1. Health Check
        print("\n1. 🏥 API Health Check")
        response = requests.get(f"{base_url}/health")
        if response.status_code != 200:
            print("   ❌ API not healthy")
            return
        print("   ✅ API is healthy")
        
        # 2. Check current tasks
        print("\n2. 📋 Checking Available Tasks")
        response = requests.get(f"{base_url}/tasks")
        if response.status_code == 200:
            tasks_data = response.json()['data']
            task_count = tasks_data['count']
            print(f"   ✅ Found {task_count} tasks to export")
            
            if task_count == 0:
                print("   📝 Creating a test task first...")
                test_task = {
                    "title": "Google Sheets Test Task",
                    "description": "This task is created to test Google Sheets integration",
                    "priority": "high",
                    "status": "pending"
                }
                
                response = requests.post(f"{base_url}/tasks", json=test_task)
                if response.status_code == 201:
                    print("   ✅ Test task created")
                else:
                    print("   ❌ Failed to create test task")
                    return
        else:
            print("   ❌ Failed to get tasks")
            return
        
        # 3. Test REAL Google Sheets Export
        print("\n3. 📊 Creating REAL Google Spreadsheet")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        export_data = {
            "spreadsheet_name": f"Task Manager REAL Test - {timestamp}"
        }
        
        print(f"   📤 Creating spreadsheet: '{export_data['spreadsheet_name']}'")
        print("   ⏳ This may take a few moments...")
        
        response = requests.post(f"{base_url}/tasks/export-to-sheets", json=export_data)
        
        print(f"\n   🔍 Response Status: {response.status_code}")
        response_data = response.json()
        print(f"   📄 Response: {json.dumps(response_data, indent=2)}")
        
        if response.status_code == 200 and response_data.get('success'):
            data = response_data.get('data', {})
            
            print(f"\n   🎉 SUCCESS! Real Google Sheet Created:")
            print(f"   📊 Name: {data.get('spreadsheet_name')}")
            print(f"   🆔 ID: {data.get('spreadsheet_id')}")
            print(f"   🔗 URL: {data.get('spreadsheet_url')}")
            print(f"   📈 Tasks Exported: {data.get('tasks_exported')}")
            
            # Provide clear instructions
            print(f"\n   ✅ VALIDATION STEPS:")
            print(f"   1. 🌐 Open this URL in your browser:")
            print(f"      {data.get('spreadsheet_url')}")
            print(f"   2. 📁 Check your Google Drive for the new spreadsheet")
            print(f"   3. 📊 Verify the data matches your tasks")
            
            return data.get('spreadsheet_url')
            
        else:
            print(f"\n   ❌ FAILED to create Google Sheet:")
            print(f"   Error: {response_data.get('error', 'Unknown error')}")
            
            if 'credentials' in str(response_data.get('error', '')).lower():
                print(f"\n   🔧 SOLUTION:")
                print(f"   The Google Sheets credentials may not be set up.")
                print(f"   The system is using the same OAuth2 setup as Gmail.")
                print(f"   Since Gmail is working, Sheets should work too.")
        
        # 4. Test another spreadsheet with different name
        print("\n4. 📊 Creating Second Spreadsheet")
        export_data2 = {
            "spreadsheet_name": f"Weekly Report - {timestamp}"
        }
        
        response2 = requests.post(f"{base_url}/tasks/export-to-sheets", json=export_data2)
        if response2.status_code == 200:
            result2 = response2.json()
            if result2.get('success'):
                data2 = result2.get('data', {})
                print(f"   ✅ Second spreadsheet created!")
                print(f"   🔗 URL: {data2.get('spreadsheet_url')}")
            else:
                print(f"   ❌ Second export failed: {result2.get('error')}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 GOOGLE SHEETS INTEGRATION TEST RESULTS")
        print("\nTo verify real spreadsheets were created:")
        print("1. 🌐 Visit: https://drive.google.com")
        print("2. 📁 Look for spreadsheets with today's timestamp")
        print("3. 📊 Open them to verify task data")
        print("4. 🔍 Check if all task fields are populated")
        
        print(f"\n📧 Account: The sheets are created in the same Google account")
        print(f"   that you used for Gmail OAuth2 setup")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Please ensure server is running")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_real_sheets_creation()
