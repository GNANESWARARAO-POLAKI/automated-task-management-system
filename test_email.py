#!/usr/bin/env python3
"""
Test Email Reminder Functionality
Send email reminder to chandu0polaki@gmail.com
"""

import requests
import json
from datetime import datetime, timedelta

def test_email_reminder():
    """Test sending email reminder to your Gmail"""
    
    base_url = "http://localhost:5000"
    
    print("📧 Testing Email Reminder to chandu0polaki@gmail.com")
    print("=" * 60)
    
    try:
        # 1. Check if API is running
        print("\n1. 🏥 Checking API Health")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ API is healthy and ready")
        else:
            print("   ❌ API health check failed")
            return
        
        # 2. Get existing tasks first
        print("\n2. 📋 Getting Existing Tasks")
        response = requests.get(f"{base_url}/tasks")
        if response.status_code == 200:
            tasks_data = response.json()['data']
            tasks = tasks_data['tasks']
            print(f"   ✅ Found {tasks_data['count']} existing tasks")
            
            if tasks:
                # Use first existing task
                task = tasks[0]
                task_id = task['id']
                print(f"   📝 Using Task ID {task_id}: {task['title']}")
            else:
                print("   📝 No existing tasks, creating a new one...")
                # Create a test task if none exist
                task_data = {
                    "title": "Email Test Task",
                    "description": "This is a test task for email reminder functionality",
                    "due_date": (datetime.now() + timedelta(hours=2)).isoformat(),
                    "priority": "high",
                    "status": "pending"
                }
                
                response = requests.post(f"{base_url}/tasks", json=task_data)
                if response.status_code == 201:
                    task = response.json()['data']
                    task_id = task['id']
                    print(f"   ✅ Created Task ID {task_id}: {task['title']}")
                else:
                    print(f"   ❌ Failed to create task: {response.text}")
                    return
        else:
            print(f"   ❌ Failed to get tasks: {response.text}")
            return
        
        # 3. Test email reminder with default recipient (your email)
        print(f"\n3. 📧 Sending Email Reminder for Task ID {task_id}")
        print(f"   📝 Task: {task['title']}")
        print(f"   📧 Recipient: chandu0polaki@gmail.com (default)")
        
        # Send email with custom message
        email_data = {
            "custom_message": "This is a test email from your Task Manager API! The email functionality is working perfectly."
        }
        
        print(f"   📤 Sending email...")
        response = requests.post(f"{base_url}/tasks/{task_id}/email-reminder", json=email_data)
        
        print(f"   🔍 Response Status: {response.status_code}")
        print(f"   📄 Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ Email sent successfully!")
                print(f"   📧 Recipient: {result.get('data', {}).get('recipient', 'chandu0polaki@gmail.com')}")
                print(f"   📋 Task ID: {result.get('data', {}).get('task_id', task_id)}")
                print(f"   📝 Message: {result.get('message', 'Email reminder sent successfully')}")
            else:
                print(f"   ❌ Email sending failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ API request failed with status {response.status_code}")
        
        # 4. Test with explicit recipient email
        print(f"\n4. 📧 Testing with Explicit Recipient Email")
        email_data_explicit = {
            "recipient_email": "chandu0polaki@gmail.com",
            "custom_message": "This email was sent with explicit recipient address!"
        }
        
        response = requests.post(f"{base_url}/tasks/{task_id}/email-reminder", json=email_data_explicit)
        
        print(f"   🔍 Response Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ Explicit email sent successfully!")
                print(f"   📧 Confirmed Recipient: {result.get('data', {}).get('recipient', 'Unknown')}")
            else:
                print(f"   ❌ Explicit email failed: {result.get('error', 'Unknown error')}")
        
        # 5. Show task details that were emailed
        print(f"\n5. 📋 Task Details That Were Emailed")
        print(f"   📝 Title: {task['title']}")
        print(f"   📄 Description: {task.get('description', 'No description')}")
        print(f"   🎯 Priority: {task['priority']}")
        print(f"   📊 Status: {task['status']}")
        print(f"   ⏰ Due Date: {task.get('due_date', 'No due date')}")
        print(f"   🕒 Created: {task['created_at']}")
        
        # Summary
        print("\n" + "=" * 60)
        print("🎉 EMAIL REMINDER TEST COMPLETE!")
        print("\n📧 Email Details:")
        print("   • Recipient: chandu0polaki@gmail.com")
        print("   • Subject: Task Reminder: [Task Title]")
        print("   • Format: HTML + Plain Text")
        print("   • Content: Task details + Custom message")
        
        print("\n📋 What to expect in your email:")
        print("   ✅ Professional HTML formatted email")
        print("   ✅ Task title, description, priority, status")
        print("   ✅ Due date and creation time")
        print("   ✅ Custom message included")
        print("   ✅ Responsive design for mobile/desktop")
        
        print(f"\n🔍 Check your email at chandu0polaki@gmail.com!")
        print("   (Note: Email will only be sent if Gmail OAuth2 is configured)")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Please ensure server is running:")
        print("   python app_final.py")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_email_reminder()
