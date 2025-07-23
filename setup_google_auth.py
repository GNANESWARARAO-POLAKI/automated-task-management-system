#!/usr/bin/env python3
"""
Simple Google API Authorization Setup
This script helps you manually complete the OAuth2 authorization
"""

import json
import os

def generate_auth_instructions():
    """Generate step-by-step authorization instructions"""
    
    print("🔧 Google API Setup Instructions")
    print("=" * 60)
    
    # Read the credentials to get client ID
    creds_file = "credentials/gmail_credentials.json"
    if not os.path.exists(creds_file):
        print("❌ Credentials file not found!")
        return
    
    with open(creds_file, 'r') as f:
        creds = json.load(f)
    
    client_id = creds['web']['client_id']
    project_id = creds['web']['project_id']
    
    print(f"📋 Project ID: {project_id}")
    print(f"🔑 Client ID: {client_id}")
    
    print(f"\n🚀 STEP 1: Enable APIs in Google Cloud Console")
    print("   Go to: https://console.cloud.google.com/apis/dashboard")
    print("   Select your project: " + project_id)
    print("   Enable these APIs:")
    print("   ✅ Gmail API")
    print("   ✅ Google Sheets API")
    print("   ✅ Google Calendar API")
    
    print(f"\n🔧 STEP 2: Configure OAuth2 Consent Screen")
    print("   Go to: https://console.cloud.google.com/apis/credentials/consent")
    print("   Configure the OAuth consent screen:")
    print("   - App name: Task Manager API")
    print("   - User support email: your email")
    print("   - Developer contact: your email")
    print("   - Scopes: Add the following scopes:")
    print("     • https://www.googleapis.com/auth/gmail.send")
    print("     • https://www.googleapis.com/auth/spreadsheets")
    print("     • https://www.googleapis.com/auth/calendar.events")
    
    print(f"\n⚙️  STEP 3: Update OAuth2 Redirect URIs")
    print("   Go to: https://console.cloud.google.com/apis/credentials")
    print("   Click on your OAuth 2.0 Client ID")
    print("   Add these Authorized redirect URIs:")
    print("   • http://localhost:8080/")
    print("   • http://localhost:8080/oauth2callback")
    print("   • http://127.0.0.1:8080/")
    print("   • urn:ietf:wg:oauth:2.0:oob")
    
    print(f"\n🔐 STEP 4: Manual Authorization URLs")
    print("   Use these URLs to manually authorize each service:\n")
    
    # Gmail authorization URL
    gmail_scopes = "https://www.googleapis.com/auth/gmail.send%20https://www.googleapis.com/auth/gmail.readonly"
    gmail_url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={client_id}&redirect_uri=http://localhost:8080/&scope={gmail_scopes}&access_type=offline&prompt=consent"
    print("📧 Gmail API Authorization:")
    print(f"   {gmail_url}\n")
    
    # Sheets authorization URL  
    sheets_scopes = "https://www.googleapis.com/auth/spreadsheets%20https://www.googleapis.com/auth/drive.file"
    sheets_url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={client_id}&redirect_uri=http://localhost:8080/&scope={sheets_scopes}&access_type=offline&prompt=consent"
    print("📊 Google Sheets API Authorization:")
    print(f"   {sheets_url}\n")
    
    # Calendar authorization URL
    calendar_scopes = "https://www.googleapis.com/auth/calendar%20https://www.googleapis.com/auth/calendar.events"
    calendar_url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={client_id}&redirect_uri=http://localhost:8080/&scope={calendar_scopes}&access_type=offline&prompt=consent"
    print("📅 Google Calendar API Authorization:")
    print(f"   {calendar_url}\n")
    
    print("=" * 60)
    print("💡 IMPORTANT NOTES:")
    print("   • Complete STEPS 1-3 in Google Cloud Console first")
    print("   • Then use the authorization URLs above")
    print("   • After setup, run: python app.py")
    print("   • The API will guide you through the OAuth flow")

def check_setup_status():
    """Check if the basic setup is complete"""
    print("\n🔍 Checking Setup Status...")
    
    # Check credentials
    required_files = [
        "credentials/gmail_credentials.json",
        "credentials/sheets_credentials.json", 
        "credentials/calendar_credentials.json"
    ]
    
    all_present = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            all_present = False
    
    if all_present:
        print("   ✅ All credential files present")
    else:
        print("   ⚠️  Some credential files missing")
    
    # Check tokens directory
    if os.path.exists("tokens"):
        print("   ✅ Tokens directory exists")
        token_files = [f for f in os.listdir("tokens") if f.endswith(".pickle")]
        if token_files:
            print(f"   ✅ Found {len(token_files)} token files")
            for token_file in token_files:
                print(f"      • {token_file}")
        else:
            print("   ⚠️  No token files found (run authorization first)")
    else:
        print("   ⚠️  Tokens directory doesn't exist")

if __name__ == "__main__":
    generate_auth_instructions()
    check_setup_status()
    
    print(f"\n🎯 Quick Start After Setup:")
    print("   1. Complete Google Cloud Console setup (Steps 1-3)")
    print("   2. Run: python app.py")
    print("   3. API will handle OAuth2 flow automatically")
    print("   4. Run: python demo_api.py (to test all features)")
