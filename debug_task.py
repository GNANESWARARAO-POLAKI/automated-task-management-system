#!/usr/bin/env python3
"""
Simple Task Creation Test - Debug the 500 error
"""

import requests
import json

def simple_task_test():
    """Simple test to debug task creation"""
    
    base_url = "http://localhost:5000"
    
    print("🔍 Simple Task Creation Test")
    print("=" * 40)
    
    # Test 1: Very basic task
    print("\n1. Testing Basic Task Creation")
    basic_task = {
        "title": "Simple Test Task"
    }
    
    print(f"   Sending: {json.dumps(basic_task, indent=2)}")
    
    try:
        response = requests.post(f"{base_url}/tasks", json=basic_task)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Task with more fields
    print("\n2. Testing Task with All Fields")
    full_task = {
        "title": "Full Test Task",
        "description": "Test description",
        "due_date": "2025-07-25T10:00:00",
        "priority": "medium",
        "status": "pending"
    }
    
    print(f"   Sending: {json.dumps(full_task, indent=2)}")
    
    try:
        response = requests.post(f"{base_url}/tasks", json=full_task)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Check if tasks endpoint is working at all
    print("\n3. Testing GET /tasks")
    try:
        response = requests.get(f"{base_url}/tasks")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Current task count: {data['data']['count']}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    simple_task_test()
