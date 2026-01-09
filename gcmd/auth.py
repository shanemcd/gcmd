"""
Authentication module for Google Drive OAuth flow.
"""

import os
import json
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes required for Drive and Tasks operations
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/tasks.readonly",
]


def get_config_dir() -> Path:
    """Get the configuration directory for gcmd."""
    config_home = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    config_dir = Path(config_home) / "gcmd"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_token_path() -> Path:
    """Get the path to the stored token file."""
    return get_config_dir() / "token.json"


def get_credentials_path() -> Path:
    """Get the path to the OAuth client credentials file."""
    return get_config_dir() / "credentials.json"


def save_credentials(creds: Credentials) -> None:
    """Save credentials to token file."""
    token_path = get_token_path()
    with open(token_path, "w") as token_file:
        token_file.write(creds.to_json())


def load_credentials() -> Optional[Credentials]:
    """Load credentials from token file if it exists."""
    token_path = get_token_path()
    if not token_path.exists():
        return None
    
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    return creds


def get_authenticated_credentials() -> Credentials:
    """
    Get authenticated credentials, refreshing or initiating OAuth flow as needed.
    
    Returns:
        Credentials: Valid Google OAuth credentials
        
    Raises:
        FileNotFoundError: If credentials.json is not found
        Exception: If authentication fails
    """
    creds = load_credentials()
    
    # If we have valid credentials, return them
    if creds and creds.valid:
        return creds
    
    # If credentials exist but are expired, refresh them
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            save_credentials(creds)
            return creds
        except Exception as e:
            print(f"Failed to refresh token: {e}")
            print("Re-authenticating...")
    
    # Otherwise, initiate OAuth flow
    credentials_path = get_credentials_path()
    if not credentials_path.exists():
        raise FileNotFoundError(
            f"\n{'='*70}\n"
            f"FIRST-TIME SETUP REQUIRED\n"
            f"{'='*70}\n\n"
            f"OAuth credentials file not found at:\n"
            f"  {credentials_path}\n\n"
            f"To use gcmd, you need to create OAuth credentials:\n\n"
            f"1. Go to: https://console.cloud.google.com/apis/credentials\n"
            f"   - Create a new project (or select existing)\n"
            f"   - Click '+ CREATE CREDENTIALS' → 'OAuth client ID'\n"
            f"   - Application type: 'Desktop app'\n"
            f"   - Name it anything (e.g., 'gcmd')\n\n"
            f"2. Enable required APIs:\n"
            f"   - Google Drive API: https://console.cloud.google.com/apis/library/drive.googleapis.com\n"
            f"   - Google Docs API: https://console.cloud.google.com/apis/library/docs.googleapis.com\n"
            f"   - Google Tasks API: https://console.cloud.google.com/apis/library/tasks.googleapis.com\n\n"
            f"3. Download the credentials:\n"
            f"   - Click the download icon (⬇) next to your OAuth client\n"
            f"   - Save the JSON file as: {credentials_path}\n\n"
            f"4. Run the command again - your browser will open for authentication!\n"
            f"{'='*70}\n"
        )
    
    flow = InstalledAppFlow.from_client_secrets_file(
        str(credentials_path),
        SCOPES
    )
    
    print("\n" + "="*70)
    print("AUTHENTICATION REQUIRED")
    print("="*70)
    print("\nAttempting to open your browser for Google authentication...")
    print("If the browser doesn't open, copy and paste this URL:\n")
    
    # Run local server to handle OAuth callback
    # The library will print the URL automatically
    try:
        creds = flow.run_local_server(
            port=0,
            authorization_prompt_message="",  # We already printed our own message
            success_message="✓ Authentication successful! You may close this window.",
            open_browser=True
        )
    except Exception as e:
        # If browser fails, provide manual flow
        print(f"\nBrowser authentication failed: {e}")
        print("\nFalling back to manual authentication...")
        print("Please visit this URL to authorize:\n")
        
        # Get the authorization URL
        flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        auth_url, _ = flow.authorization_url(prompt="consent")
        print(f"  {auth_url}\n")
        print("After authorizing, paste the authorization code here:")
        
        code = input("Code: ").strip()
        flow.fetch_token(code=code)
        creds = flow.credentials
    
    print("\n✓ Authentication successful! Credentials saved.")
    print("="*70 + "\n")
    
    # Save credentials for future use
    save_credentials(creds)
    
    return creds


def revoke_credentials() -> None:
    """Revoke and delete stored credentials."""
    token_path = get_token_path()
    if token_path.exists():
        token_path.unlink()
        print(f"Removed credentials from {token_path}")
    else:
        print("No credentials found to revoke")

