#!/usr/bin/env python3
"""
Export credentials and token for Streamlit Cloud secrets
Run this after authenticating locally to get the TOML format for Streamlit Cloud
"""

import os
import json
import pickle

def export_secrets():
    print("\n" + "="*60)
    print("📤 EXPORT SECRETS FOR STREAMLIT CLOUD")
    print("="*60 + "\n")
    
    output = []
    output.append("# Copy everything below this line to Streamlit Cloud Secrets")
    output.append("# Go to: App Settings → Secrets → Paste this content")
    output.append("")
    
    # Export credentials.json
    cred_paths = ['credentials.json', '../credentials.json', '../../credentials.json']
    creds_data = None
    
    for path in cred_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                creds_data = json.load(f)
            break
    
    if creds_data:
        # Handle both "installed" and "web" credential types
        cred_type = "installed" if "installed" in creds_data else "web"
        cred = creds_data[cred_type]
        
        output.append("[google_oauth]")
        output.append(f'type = "{cred_type}"')
        output.append(f'client_id = "{cred.get("client_id", "")}"')
        output.append(f'project_id = "{cred.get("project_id", "")}"')
        output.append(f'auth_uri = "{cred.get("auth_uri", "")}"')
        output.append(f'token_uri = "{cred.get("token_uri", "")}"')
        output.append(f'auth_provider_x509_cert_url = "{cred.get("auth_provider_x509_cert_url", "")}"')
        output.append(f'client_secret = "{cred.get("client_secret", "")}"')
        output.append(f'redirect_uris = {json.dumps(cred.get("redirect_uris", []))}')
        output.append("")
    else:
        print("⚠️  credentials.json not found")
    
    # Export token.pickle
    token_paths = ['token.pickle', '../token.pickle', '../../token.pickle']
    token_data = None
    
    for path in token_paths:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                token_data = pickle.load(f)
            break
    
    if token_data:
        output.append("[google_token]")
        output.append(f'token = "{token_data.token}"')
        output.append(f'refresh_token = "{token_data.refresh_token}"')
        output.append(f'token_uri = "{token_data.token_uri}"')
        output.append(f'client_id = "{token_data.client_id}"')
        output.append(f'client_secret = "{token_data.client_secret}"')
        output.append("")
    else:
        print("⚠️  token.pickle not found - run gmail_auth.py first")
    
    # Add OpenAI key placeholder
    output.append("[openai]")
    output.append('api_key = "your-openai-api-key-here"')
    output.append("")
    
    # Print the output
    print("\n" + "="*60)
    print("📋 COPY THE FOLLOWING TO STREAMLIT CLOUD SECRETS:")
    print("="*60 + "\n")
    
    secrets_content = "\n".join(output)
    print(secrets_content)
    
    # Also save to file
    with open("streamlit_secrets.toml", "w") as f:
        f.write(secrets_content)
    
    print("\n" + "="*60)
    print("✅ Also saved to: streamlit_secrets.toml")
    print("="*60)
    print("\n📝 HOW TO USE:")
    print("1. Go to https://share.streamlit.io")
    print("2. Open your app → Settings → Secrets")
    print("3. Paste the content above")
    print("4. Click Save")
    print("="*60 + "\n")


if __name__ == "__main__":
    export_secrets()

