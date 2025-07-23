#!/usr/bin/env python3
"""
Google API OAuth2 Authorization Helper
Run this to complete the OAuth2 flow for Gmail, Sheets, and Calendar APIs
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

class GoogleAPIAuthHelper:
    
    def __init__(self):
        self.credentials_dir = "credentials"
        self.tokens_dir = "tokens"
        
        # Create tokens directory if it doesn't exist
        if not os.path.exists(self.tokens_dir):
            os.makedirs(self.tokens_dir)
    
    def authorize_service(self, service_name, scopes):
        """Authorize a Google service and save tokens"""
        print(f"\n🔐 Authorizing {service_name.title()} API...")
        
        credentials_file = f"{self.credentials_dir}/{service_name}_credentials.json"
        token_file = f"{self.tokens_dir}/{service_name}_token.pickle"
        
        if not os.path.exists(credentials_file):
            print(f"❌ Credentials file not found: {credentials_file}")
            return False
        
        creds = None
        # Load existing token
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Refreshing expired token...")
                creds.refresh(Request())
            else:
                print(f"🌐 Starting OAuth2 flow for {service_name}...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, scopes)
                # Use a specific port for consistency
                creds = flow.run_local_server(port=8080, open_browser=False)
                print(f"📋 Please visit this URL to authorize the application:")
                print(f"   {flow.authorization_url()[0]}")
                print("🔐 After authorization, the token will be saved automatically.")
            
            # Save the credentials for the next run
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        print(f"✅ {service_name.title()} API authorized successfully!")
        return True
    
    def authorize_all_services(self):
        """Authorize all Google services"""
        print("🚀 Google API Authorization Helper")
        print("=" * 50)
        
        services = {
            'gmail': [
                'https://www.googleapis.com/auth/gmail.send',
                'https://www.googleapis.com/auth/gmail.readonly'
            ],
            'sheets': [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.file'
            ],
            'calendar': [
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/calendar.events'
            ]
        }
        
        success_count = 0
        for service_name, scopes in services.items():
            try:
                if self.authorize_service(service_name, scopes):
                    success_count += 1
                else:
                    print(f"❌ Failed to authorize {service_name}")
            except Exception as e:
                print(f"❌ Error authorizing {service_name}: {e}")
        
        print("\n" + "=" * 50)
        print(f"✨ Authorization Complete!")
        print(f"✅ Successfully authorized {success_count}/3 services")
        
        if success_count == 3:
            print("\n🎉 All Google APIs are now ready to use!")
            print("🚀 You can now run the Task Manager API with full functionality:")
            print("   python app.py")
            print("   python demo_api.py")
        else:
            print("\n⚠️  Some services failed to authorize.")
            print("💡 Make sure you have enabled the APIs in Google Cloud Console:")
            print("   - Gmail API")
            print("   - Google Sheets API") 
            print("   - Google Calendar API")

if __name__ == "__main__":
    auth_helper = GoogleAPIAuthHelper()
    auth_helper.authorize_all_services()
