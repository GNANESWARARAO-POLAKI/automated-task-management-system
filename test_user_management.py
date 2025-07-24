#!/usr/bin/env python3
"""
Test User Management System
Quick demo of user registration, login, and task creation
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_user_management():
    """Test the complete user management flow"""
    
    print("🧪 Testing User Management System")
    print("=" * 50)
    
    # Test 1: User Registration
    print("\n1. Testing User Registration...")
    user_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "testpassword123",
        "timezone": "America/New_York",
        "notification_preferences": "both"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        result = response.json()
        
        if result['success']:
            print("✅ User registered successfully!")
            print(f"   User ID: {result['data']['id']}")
            print(f"   Email: {result['data']['email']}")
            user_id = result['data']['id']
        else:
            print(f"❌ Registration failed: {result['error']}")
            return
            
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return
    
    # Test 2: User Login
    print("\n2. Testing User Login...")
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        result = response.json()
        
        if result['success']:
            print("✅ Login successful!")
            print(f"   Welcome: {result['data']['name']}")
            print(f"   Session Token: {result['data'].get('session_token', 'N/A')[:50]}...")
        else:
            print(f"❌ Login failed: {result['error']}")
            return
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return
    
    # Test 3: Create User-Specific Task
    print("\n3. Testing User-Specific Task Creation...")
    task_data = {
        "title": "Complete user management testing",
        "description": "Test the new user management features thoroughly",
        "due_date": "2025-07-24T16:00:00",
        "priority": "high",
        "user_id": user_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tasks", json=task_data)
        result = response.json()
        
        if result['success']:
            print("✅ User task created successfully!")
            print(f"   Task ID: {result['data']['task']['id']}")
            print(f"   Title: {result['data']['task']['title']}")
            print(f"   User Email: {result['data']['task']['user_email']}")
            task_id = result['data']['task']['id']
        else:
            print(f"❌ Task creation failed: {result['error']}")
            return
            
    except Exception as e:
        print(f"❌ Task creation error: {str(e)}")
        return
    
    # Test 4: Get User-Specific Tasks
    print("\n4. Testing User-Specific Task Retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/tasks?user_id={user_id}")
        result = response.json()
        
        if result['success']:
            print("✅ User tasks retrieved successfully!")
            print(f"   Found {result['data']['count']} tasks for user")
            for task in result['data']['tasks']:
                print(f"   - {task['title']} (ID: {task['id']}, Email: {task.get('user_email', 'N/A')})")
        else:
            print(f"❌ Task retrieval failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Task retrieval error: {str(e)}")
    
    # Test 5: Get User Profile
    print("\n5. Testing User Profile Retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/auth/profile?user_id={user_id}")
        result = response.json()
        
        if result['success']:
            print("✅ User profile retrieved successfully!")
            print(f"   Name: {result['data']['name']}")
            print(f"   Email: {result['data']['email']}")
            print(f"   Timezone: {result['data']['timezone']}")
            print(f"   Notifications: {result['data']['notification_preferences']}")
        else:
            print(f"❌ Profile retrieval failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Profile retrieval error: {str(e)}")
    
    # Test 6: Get All Users (Admin View)
    print("\n6. Testing All Users Retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/users")
        result = response.json()
        
        if result['success']:
            print("✅ All users retrieved successfully!")
            print(f"   Total users: {len(result['data'])}")
            for user in result['data']:
                print(f"   - {user['name']} ({user['email']}) - ID: {user['id']}")
        else:
            print(f"❌ Users retrieval failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Users retrieval error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 User Management Testing Complete!")
    print("\nNext steps:")
    print("1. Open http://127.0.0.1:5000 in your browser")
    print("2. Go to the 'User' tab")
    print("3. Try registering and logging in")
    print("4. Create tasks and see they're associated with your user")
    print("5. Test automated reminders with your email!")

if __name__ == "__main__":
    test_user_management()
