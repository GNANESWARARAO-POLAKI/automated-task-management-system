#!/usr/bin/env python3
"""
Google Cloud Console Setup Helper
Provides step-by-step instructions to fix redirect_uri_mismatch error
"""

def fix_redirect_uri_mismatch():
    """Provide instructions to fix the redirect URI mismatch error"""
    
    print("🔧 Fixing OAuth2 Redirect URI Mismatch Error")
    print("=" * 60)
    
    print("\n❌ ERROR: redirect_uri_mismatch")
    print("This error occurs when the redirect URI used by the app doesn't match")
    print("the ones configured in Google Cloud Console.")
    
    print(f"\n🔍 CURRENT ISSUE:")
    print("The app is trying to use a dynamic localhost port, but Google Cloud")
    print("Console needs the exact redirect URIs to be pre-configured.")
    
    print(f"\n✅ SOLUTION: Configure Redirect URIs in Google Cloud Console")
    print("\n📋 STEP 1: Go to Google Cloud Console")
    print("   URL: https://console.cloud.google.com/apis/credentials")
    print("   Project: sylvan-dragon-454917-k5")
    
    print(f"\n📋 STEP 2: Find your OAuth 2.0 Client ID")
    print("   Client ID: 264309317138-tnen116et2iuja80pb0t7985nafefkbf.apps.googleusercontent.com")
    print("   Click on the pencil icon to edit")
    
    print(f"\n📋 STEP 3: Add ALL these Authorized Redirect URIs:")
    redirect_uris = [
        "http://localhost:8080/",
        "http://127.0.0.1:8080/",
        "http://localhost:55140/",
        "http://127.0.0.1:55140/",
        "http://localhost:53251/",
        "http://127.0.0.1:53251/",
        "http://localhost:53698/",
        "http://127.0.0.1:53698/",
        "urn:ietf:wg:oauth:2.0:oob"
    ]
    
    for i, uri in enumerate(redirect_uris, 1):
        print(f"   {i:2d}. {uri}")
    
    print(f"\n💡 WHY SO MANY URIS?")
    print("   • The Google OAuth2 library uses random ports")
    print("   • We need to cover common ports it might use")
    print("   • 'urn:ietf:wg:oauth:2.0:oob' is for manual code entry")
    
    print(f"\n📋 STEP 4: Save the Configuration")
    print("   • Click 'Save' in Google Cloud Console")
    print("   • Wait 5-10 minutes for changes to propagate")
    
    print(f"\n📋 STEP 5: Restart the Application")
    print("   • Stop the current app (Ctrl+C)")
    print("   • Run: python app.py")
    print("   • The OAuth2 flow should work now")
    
    print("\n" + "=" * 60)
    print("🚀 ALTERNATIVE: Use Manual OAuth2 Flow")
    print("If you continue having issues, we can use a manual approach:")
    print("1. Get authorization code manually from browser")
    print("2. Paste it into the application")
    print("3. No redirect URI needed")

def create_manual_auth_script():
    """Create a script for manual OAuth2 authorization"""
    
    print(f"\n🛠️  Creating Manual Authorization Helper...")
    
    manual_auth_code = '''#!/usr/bin/env python3
"""
Manual Google OAuth2 Authorization
Use this if you're having redirect URI issues
"""

import json
from google_auth_oauthlib.flow import InstalledAppFlow

def manual_authorize(service_name):
    """Manually authorize a Google service"""
    
    credentials_file = f"credentials/{service_name}_credentials.json"
    
    # Define scopes for each service
    scopes = {
        'gmail': ['https://www.googleapis.com/auth/gmail.send'],
        'sheets': ['https://www.googleapis.com/auth/spreadsheets'],
        'calendar': ['https://www.googleapis.com/auth/calendar.events']
    }
    
    if service_name not in scopes:
        print(f"❌ Unknown service: {service_name}")
        return
    
    try:
        # Create flow
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file, 
            scopes[service_name]
        )
        
        # Get authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        print(f"\\n🔐 Manual Authorization for {service_name.title()}")
        print("=" * 50)
        print("1. Open this URL in your browser:")
        print(f"   {auth_url}")
        print("\\n2. Complete the authorization")
        print("3. Copy the authorization code from the browser")
        print("4. Paste it below:")
        
        # Get authorization code from user
        auth_code = input("\\nEnter authorization code: ").strip()
        
        # Exchange code for credentials
        flow.fetch_token(code=auth_code)
        
        # Save credentials
        with open(f"credentials/{service_name}_token.json", 'w') as f:
            f.write(flow.credentials.to_json())
        
        print(f"✅ {service_name.title()} authorization complete!")
        print(f"   Token saved to: credentials/{service_name}_token.json")
        
    except Exception as e:
        print(f"❌ Authorization failed: {e}")

if __name__ == "__main__":
    print("🔐 Manual Google API Authorization")
    print("Choose service to authorize:")
    print("1. Gmail")
    print("2. Google Sheets") 
    print("3. Google Calendar")
    print("4. All Services")
    
    choice = input("\\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        manual_authorize("gmail")
    elif choice == "2":
        manual_authorize("sheets")
    elif choice == "3":
        manual_authorize("calendar")
    elif choice == "4":
        for service in ["gmail", "sheets", "calendar"]:
            print(f"\\n--- Authorizing {service.title()} ---")
            manual_authorize(service)
    else:
        print("❌ Invalid choice")
'''
    
    with open("manual_oauth.py", "w") as f:
        f.write(manual_auth_code)
    
    print("   ✅ Created: manual_oauth.py")
    print("   Usage: python manual_oauth.py")

if __name__ == "__main__":
    fix_redirect_uri_mismatch()
    create_manual_auth_script()
