from mcp.server.fastmcp import FastMCP
from pydantic import Field
from starlette.requests import Request
from starlette.responses import JSONResponse

import gmail_service
import docs_service
import os

# Initialize FastMCP Server
port = int(os.environ.get("PORT", 8000))
mcp = FastMCP("Google Workspace MCP Server", host="0.0.0.0", port=port)

# --- Gmail Tools ---

@mcp.tool()
def search_emails(query: str, max_results: int = 10) -> list:
    """
    Search for emails in your Gmail account.
    
    Args:
        query: Standard Gmail search query (e.g., "from:user@example.com is:unread").
        max_results: Maximum number of emails to return (default: 10).
    """
    return gmail_service.search_emails(query, max_results)

@mcp.tool()
def read_email(message_id: str) -> dict:
    """
    Read the full content and metadata of a specific email.
    
    Args:
        message_id: The ID of the Gmail message to read.
    """
    return gmail_service.read_email(message_id)

@mcp.tool()
def send_email(to: str, subject: str, body: str) -> dict:
    """
    Send an email from your Gmail account.
    
    Args:
        to: Email address of the recipient.
        subject: Subject of the email.
        body: Plain text content of the email.
    """
    return gmail_service.send_email(to, subject, body)

# --- Google Docs Tools ---

@mcp.tool()
def read_document(document_id: str) -> dict:
    """
    Read the text content of a Google Document.
    
    Args:
        document_id: The ID of the Google Document (found in the URL).
    """
    return docs_service.read_document(document_id)

@mcp.tool()
def create_document(title: str, initial_content: str = "") -> dict:
    """
    Create a new Google Document, optionally with some initial text content.
    
    Args:
        title: The title of the new document.
        initial_content: Optional text to insert into the new document.
    """
    # FastMCP uses Pydantic under the hood for type hints. We provide a default string.
    content = initial_content if initial_content else None
    return docs_service.create_document(title, content)

# --- Health Check ---

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse({"status": "ok"})

if __name__ == "__main__":
    if "RAILWAY_ENVIRONMENT" in os.environ or os.environ.get("TRANSPORT") == "sse":
        print(f"Starting server with SSE transport on port {port}")
        mcp.run(transport="sse")
    else:
        # The default execution when run normally. 
        # Usually you'd run `mcp dev main.py` or use the standard startup method if integrating differently.
        mcp.run()
