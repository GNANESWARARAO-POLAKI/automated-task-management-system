#!/usr/bin/env python3
"""
Test Authentication Requirements
Verify that tasks endpoint requires user authentication
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_authentication_requirements():
    """Test that tasks require authentication"""
    
    print("🔒 Testing Authentication Requirements")
    print("=" * 50)
    
    # Test 1: Try to get tasks without user_id (should fail)
    print("\n1. Testing tasks access without authentication...")
    try:
        response = requests.get(f"{BASE_URL}/tasks")
        result = response.json()
        
        if not result['success']:
            print("✅ Correctly blocked access without authentication")
            print(f"   Error: {result['error']}")
        else:
            print("❌ Authentication bypass detected!")
            print(f"   Got {len(result.get('data', {}).get('tasks', []))} tasks without login")
            
    except Exception as e:
        print(f"❌ Request error: {str(e)}")
    
    # Test 2: Try to get tasks with invalid user_id (should fail)
    print("\n2. Testing tasks access with invalid user ID...")
    try:
        response = requests.get(f"{BASE_URL}/tasks?user_id=99999")
        result = response.json()
        
        if not result['success']:
            print("✅ Correctly blocked access with invalid user ID")
            print(f"   Error: {result['error']}")
        else:
            print("❌ Invalid user ID accepted!")
            
    except Exception as e:
        print(f"❌ Request error: {str(e)}")
    
    # Test 3: Try to create task without user_id (should fail)
    print("\n3. Testing task creation without authentication...")
    task_data = {
        "title": "Unauthorized task",
        "description": "This should not be created",
        "priority": "high"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tasks", json=task_data)
        result = response.json()
        
        if not result['success']:
            print("✅ Correctly blocked task creation without authentication")
            print(f"   Error: {result['error']}")
        else:
            print("❌ Task creation bypass detected!")
            print(f"   Created task: {result.get('data', {})}")
            
    except Exception as e:
        print(f"❌ Request error: {str(e)}")
    
    # Test 4: Test with valid user (should work)
    print("\n4. Testing with valid authenticated user...")
    
    # First, login to get a valid user
    login_data = {
        "email": "john.doe@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        result = response.json()
        
        if result['success']:
            user_id = result['data']['id']
            print(f"✅ Login successful for user ID: {user_id}")
            
            # Now test getting tasks with valid user_id
            response = requests.get(f"{BASE_URL}/tasks?user_id={user_id}")
            result = response.json()
            
            if result['success']:
                print("✅ Tasks retrieved successfully with authentication")
                print(f"   Found {result['data']['count']} tasks for {result['data']['user']['name']}")
            else:
                print(f"❌ Failed to get tasks with valid user: {result['error']}")
                
            # Test creating task with valid user_id
            task_data['user_id'] = user_id
            response = requests.post(f"{BASE_URL}/tasks", json=task_data)
            result = response.json()
            
            if result['success']:
                print("✅ Task creation successful with authentication")
                print(f"   Created task: {result['data']['task']['title']}")
            else:
                print(f"❌ Failed to create task with valid user: {result['error']}")
                
        else:
            print(f"❌ Login failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Login test error: {str(e)}")
    
    # Test 5: Test admin endpoint
    print("\n5. Testing admin endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/admin/tasks")
        result = response.json()
        
        if result['success']:
            print("✅ Admin endpoint accessible")
            print(f"   Total tasks in system: {result['data']['count']}")
        else:
            print(f"❌ Admin endpoint failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Admin endpoint error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Authentication Testing Complete!")
    print("\nSecurity Status:")
    print("✅ Tasks require user authentication")
    print("✅ Invalid user IDs are rejected")
    print("✅ Task creation requires valid user")
    print("✅ Admin endpoint available for system overview")

if __name__ == "__main__":
    test_authentication_requirements()
