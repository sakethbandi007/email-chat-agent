#!/usr/bin/env python3
"""
Switch Gmail Account Script
Use this to authenticate with a different Google account
"""

import os
import sys

def switch_account():
    """Delete existing token and re-authenticate"""
    
    token_files = [
        'token.pickle',
        '../token.pickle',
        '../../token.pickle'
    ]
    
    print("\n" + "="*60)
    print("🔄 SWITCH GMAIL ACCOUNT")
    print("="*60)
    
    # Find and delete existing tokens
    deleted = False
    for token_file in token_files:
        if os.path.exists(token_file):
            os.remove(token_file)
            print(f"✅ Deleted: {token_file}")
            deleted = True
    
    if not deleted:
        print("ℹ️  No existing token found")
    
    print("\n" + "="*60)
    print("📧 NEW AUTHENTICATION")
    print("="*60)
    print("A browser window will open.")
    print("⚠️  IMPORTANT: Sign in with the DIFFERENT Google account!")
    print("="*60 + "\n")
    
    # Import and run authentication
    try:
        from gmail_auth import authenticate
        success = authenticate()
        
        if success:
            print("\n" + "="*60)
            print("✅ Account switched successfully!")
            print("   You can now run: streamlit run email_chat_app.py")
            print("="*60 + "\n")
        else:
            print("\n❌ Authentication failed.\n")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    switch_account()

