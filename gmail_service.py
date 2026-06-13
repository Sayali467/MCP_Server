import base64
from email.message import EmailMessage
from typing import List, Dict, Any, Optional

from googleapiclient.discovery import build
from auth import get_credentials

def get_gmail_service():
    """Builds and returns the Gmail service object."""
    creds = get_credentials()
    return build("gmail", "v1", credentials=creds)

def search_emails(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search for emails using standard Gmail search queries.
    Returns a list of email metadata (id, threadId, snippet).
    """
    service = get_gmail_service()
    try:
        results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = results.get("messages", [])
        
        email_summaries = []
        for msg in messages:
            # Fetch snippet for context
            msg_detail = service.users().messages().get(userId="me", id=msg["id"], format="metadata").execute()
            
            headers = msg_detail.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"].lower() == "from"), "Unknown Sender")
            
            email_summaries.append({
                "id": msg["id"],
                "threadId": msg["threadId"],
                "subject": subject,
                "from": sender,
                "snippet": msg_detail.get("snippet", "")
            })
            
        return email_summaries
    except Exception as e:
        return [{"error": str(e)}]

def get_email_body(payload: dict) -> str:
    """Recursively extract the body text from a message payload."""
    body = ""
    if "parts" in payload:
        for part in payload["parts"]:
            body += get_email_body(part)
    elif payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data")
        if data:
            body += base64.urlsafe_b64decode(data).decode("utf-8")
    elif payload.get("mimeType") == "text/html" and not body:
        # Fallback to HTML if no plain text
        data = payload.get("body", {}).get("data")
        if data:
            body += base64.urlsafe_b64decode(data).decode("utf-8")
    else:
        # If no parts, try to get data directly
        data = payload.get("body", {}).get("data")
        if data:
            body += base64.urlsafe_b64decode(data).decode("utf-8")
            
    return body

def read_email(message_id: str) -> Dict[str, Any]:
    """Read the full content of a specific email by ID."""
    service = get_gmail_service()
    try:
        message = service.users().messages().get(userId="me", id=message_id, format="full").execute()
        
        payload = message.get("payload", {})
        headers = payload.get("headers", [])
        
        subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"].lower() == "from"), "Unknown Sender")
        to = next((h["value"] for h in headers if h["name"].lower() == "to"), "Unknown Recipient")
        date = next((h["value"] for h in headers if h["name"].lower() == "date"), "Unknown Date")
        
        body = get_email_body(payload)
        
        return {
            "id": message_id,
            "subject": subject,
            "from": sender,
            "to": to,
            "date": date,
            "body": body.strip()
        }
    except Exception as e:
        return {"error": str(e)}

def send_email(to: str, subject: str, body: str) -> Dict[str, Any]:
    """Send an email to a recipient."""
    service = get_gmail_service()
    try:
        message = EmailMessage()
        message.set_content(body)
        message["To"] = to
        message["From"] = "me"
        message["Subject"] = subject
        
        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": encoded_message}
        
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        return {
            "success": True,
            "message_id": send_message["id"],
            "thread_id": send_message["threadId"]
        }
    except Exception as e:
        return {"error": str(e)}
