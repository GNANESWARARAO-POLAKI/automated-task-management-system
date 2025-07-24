#!/usr/bin/env python3
"""
Test Automated Reminder System
Check if the reminder status and check now functionality works
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_reminder_system():
    """Test the automated reminder system functionality"""
    
    print("🔔 Testing Automated Reminder System")
    print("=" * 50)
    
    # Test 1: Check reminder status
    print("\n1. Testing reminder status check...")
    try:
        response = requests.get(f"{BASE_URL}/reminders/status")
        result = response.json()
        
        if result['success']:
            status = result['data']
            print("✅ Reminder status retrieved successfully!")
            print(f"   Running: {status['running']}")
            print(f"   Gmail Initialized: {status['gmail_initialized']}")
            print(f"   Default Email: {status.get('default_email', 'Not set')}")
            print(f"   24h Reminders Sent: {status['reminders_sent_24h']}")
            print(f"   1h Reminders Sent: {status['reminders_sent_1h']}")
            print(f"   Total Reminders: {status['total_reminders_sent']}")
        else:
            print(f"❌ Failed to get reminder status: {result['error']}")
            return
            
    except Exception as e:
        print(f"❌ Error checking reminder status: {str(e)}")
        return
    
    # Test 2: Manual reminder check (Check Now functionality)
    print("\n2. Testing manual reminder check (Check Now)...")
    try:
        response = requests.post(f"{BASE_URL}/reminders/check")
        result = response.json()
        
        if result['success']:
            status = result['data']
            print("✅ Manual reminder check completed successfully!")
            print(f"   Running: {status['running']}")
            print(f"   Gmail Initialized: {status['gmail_initialized']}")
            print(f"   24h Reminders Sent: {status['reminders_sent_24h']}")
            print(f"   1h Reminders Sent: {status['reminders_sent_1h']}")
            print(f"   Total Reminders: {status['total_reminders_sent']}")
        else:
            print(f"❌ Failed to trigger reminder check: {result['error']}")
            return
            
    except Exception as e:
        print(f"❌ Error triggering reminder check: {str(e)}")
        return
    
    # Test 3: Check if reminder system is running
    print("\n3. Testing reminder system start/stop...")
    try:
        # Try to start reminders
        response = requests.post(f"{BASE_URL}/reminders/start", json={"check_interval_minutes": 15})
        result = response.json()
        
        if result['success']:
            print("✅ Reminder system start command successful")
            print(f"   Message: {result['data']['message']}")
        else:
            print(f"⚠️  Reminder system start: {result['error']}")
        
        # Check status after start attempt
        response = requests.get(f"{BASE_URL}/reminders/status")
        result = response.json()
        
        if result['success']:
            status = result['data']
            print(f"   Status after start: Running = {status['running']}")
        
    except Exception as e:
        print(f"❌ Error testing start/stop: {str(e)}")
    
    # Test 4: Test with a task that needs reminder
    print("\n4. Testing with a sample task...")
    
    # First, register/login a user
    user_data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpass123",
        "timezone": "UTC",
        "notification_preferences": "both"
    }
    
    try:
        # Try to register (might fail if user exists)
        requests.post(f"{BASE_URL}/auth/register", json=user_data)
        
        # Login
        login_data = {"email": user_data["email"], "password": user_data["password"]}
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        result = response.json()
        
        if result['success']:
            user_id = result['data']['id']
            print(f"✅ User logged in: {user_id}")
            
            # Create a task due in 25 hours (should trigger 24h reminder)
            from datetime import datetime, timedelta
            due_date = (datetime.now() + timedelta(hours=25)).isoformat()
            
            task_data = {
                "title": "Test reminder task - due in 25 hours",
                "description": "This task should trigger a 24h reminder",
                "due_date": due_date,
                "priority": "high",
                "user_id": user_id
            }
            
            response = requests.post(f"{BASE_URL}/tasks", json=task_data)
            result = response.json()
            
            if result['success']:
                task_id = result['data']['task']['id']
                print(f"✅ Test task created: ID {task_id}")
                print(f"   Due date: {due_date}")
                
                # Now check reminders again
                print("\n   Running reminder check on test task...")
                response = requests.post(f"{BASE_URL}/reminders/check")
                result = response.json()
                
                if result['success']:
                    status = result['data']
                    print(f"   ✅ Check completed - Total reminders: {status['total_reminders_sent']}")
                else:
                    print(f"   ❌ Check failed: {result['error']}")
            else:
                print(f"❌ Failed to create test task: {result['error']}")
        else:
            print(f"❌ Failed to login test user: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error testing with sample task: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Reminder System Testing Complete!")
    print("\nTo test in browser:")
    print("1. Open http://127.0.0.1:5000")
    print("2. Go to Integrations tab")
    print("3. Click 'Check Status' under Auto Reminders")
    print("4. Click 'Check Now' to manually trigger reminder check")
    print("5. Create tasks due in 24 hours or 1 hour to test automatic reminders")

if __name__ == "__main__":
    test_reminder_system()
