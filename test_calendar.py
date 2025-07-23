#!/usr/bin/env python3
"""
Test script for Calendar API integration
Tests creating real Google Calendar events from tasks
"""

import requests
import json
from datetime import datetime, timedelta

# API Configuration
BASE_URL = "http://127.0.0.1:5000"

def test_calendar_integration():
    """Test the complete Calendar API integration"""
    print("🗓️  Testing Calendar API Integration")
    print("=" * 50)
    
    # Test 1: Create a task first
    print("\n1. Creating a test task...")
    task_data = {
        "title": "Calendar Test Task - " + datetime.now().strftime("%H:%M:%S"),
        "description": "Testing Google Calendar integration with real calendar events",
        "priority": "high",
        "status": "pending",
        "due_date": (datetime.now() + timedelta(days=2)).isoformat()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tasks", json=task_data)
        if response.status_code == 201:
            result = response.json()
            if 'data' in result:
                task = result['data']
            else:
                task = result
            task_id = task['id']
            print(f"✅ Task created successfully with ID: {task_id}")
            print(f"   Title: {task['title']}")
            print(f"   Due Date: {task['due_date']}")
        else:
            print(f"❌ Failed to create task: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating task: {str(e)}")
        print(f"   Full response: {response.text if 'response' in locals() else 'No response'}")
        return False
    
    # Test 2: Check Calendar service via health endpoint
    print(f"\n2. Testing Calendar service connection via health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API Health: {health}")
            if 'data' in health and 'calendar' in health['data']:
                print(f"   Calendar service: {health['data']['calendar']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error checking health: {str(e)}")
    
    # Test 3: Create calendar event for the task
    print(f"\n3. Creating Google Calendar event for task {task_id}...")
    try:
        # Prepare calendar event data
        calendar_data = {
            "event_title": f"Calendar Event: {task['title']}",
            "duration_minutes": 60,
            "reminder_minutes": 15,
            "location": "Test Location",
            "description": "Calendar integration test event"
        }
        
        response = requests.post(
            f"{BASE_URL}/tasks/{task_id}/add-to-calendar",
            json=calendar_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Calendar event created successfully!")
            if 'data' in result:
                data = result['data']
                print(f"   Event ID: {data.get('event_id', 'N/A')}")
                print(f"   Event URL: {data.get('event_url', 'N/A')}")
                print(f"   Event Title: {data.get('event_title', 'N/A')}")
                print(f"   Start Time: {data.get('start_time', 'N/A')}")
                print(f"   Duration: {data.get('duration_minutes', 'N/A')} minutes")
                print(f"   Message: {data.get('message', 'N/A')}")
            else:
                print(f"   Response: {result}")
            return True
        else:
            print(f"❌ Failed to create calendar event: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating calendar event: {str(e)}")
        return False

def check_api_server():
    """Check if the API server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🗓️  Calendar API Integration Test")
    print("================================")
    
    # Check if API server is running
    if not check_api_server():
        print("❌ API server is not running!")
        print("   Please start the server with: python app_final.py")
        exit(1)
    
    print("✅ API server is running")
    
    # Run calendar tests
    success = test_calendar_integration()
    
    if success:
        print(f"\n🎉 Calendar API testing completed successfully!")
        print(f"💡 Check your Google Calendar to see the events!")
        print(f"   Events should appear in your primary calendar")
    else:
        print(f"\n⚠️  Calendar API testing encountered issues")
        print(f"   Check the error messages above for troubleshooting")
