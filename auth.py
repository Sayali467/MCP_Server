import os.path
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/documents"
]

def get_credentials() -> Credentials:
    """
    Gets valid user credentials from storage, environment variables, or initiates the OAuth2 flow.
    """
    creds = None
    
    # 1. Try to load token from environment variable first (for Railway)
    token_json_str = os.environ.get("GOOGLE_TOKEN_JSON")
    if token_json_str:
        try:
            token_info = json.loads(token_json_str)
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        except Exception as e:
            print(f"Error loading token from environment: {e}")

    # 2. Try to load from file (for local dev)
    if not creds and os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_secret_str = os.environ.get("GOOGLE_CREDENTIALS_JSON")
            if client_secret_str:
                client_config = json.loads(client_secret_str)
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            elif os.path.exists("credentials.json"):
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
            else:
                raise FileNotFoundError(
                    "Google credentials not found. Please set GOOGLE_CREDENTIALS_JSON env var or provide credentials.json."
                )
            
            # This will fail in a headless environment like Railway, so it should only run locally
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run (only works if we have filesystem write access)
        try:
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"Could not save token.json: {e}")
            
    return creds

if __name__ == "__main__":
    print("Starting authentication flow...")
    get_credentials()
    print("Authentication successful! token.json has been created.")
