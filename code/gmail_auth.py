#!/usr/bin/env python3
"""
Gmail Authentication Script
Run this once to authenticate with Gmail, then use the Streamlit app.
"""

import os
import pickle

def authenticate():
    """Authenticate with Google and save token"""
    
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        print("❌ Please install: pip install google-auth google-auth-oauthlib google-api-python-client")
        return False
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/calendar.readonly'
    ]
    
    creds = None
    
    # Check for existing token
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
        print("✅ Found existing token")
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("❌ credentials.json not found!")
                print("   Please download it from Google Cloud Console")
                return False
            
            print("\n" + "="*60)
            print("📧 GMAIL AUTHENTICATION")
            print("="*60)
            print("A browser window will open for Google sign-in.")
            print("Complete the sign-in to authorize the app.")
            print("="*60 + "\n")
            
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)  # Use any available port
        
        # Save credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        print("✅ Token saved to token.pickle")
    
    # Test the connection
    try:
        gmail = build('gmail', 'v1', credentials=creds)
        profile = gmail.users().getProfile(userId='me').execute()
        print(f"\n🎉 Successfully connected to: {profile['emailAddress']}")
        print(f"   Total messages: {profile['messagesTotal']}")
        return True
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False


if __name__ == "__main__":
    print("\n📧 Gmail Authentication Script\n")
    
    success = authenticate()
    
    if success:
        print("\n" + "="*60)
        print("✅ Authentication complete!")
        print("   You can now run: streamlit run email_chat_app.py")
        print("="*60 + "\n")
    else:
        print("\n❌ Authentication failed. Please check the errors above.\n")

