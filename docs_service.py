from typing import Dict, Any, Optional

from googleapiclient.discovery import build
from auth import get_credentials

def get_docs_service():
    """Builds and returns the Google Docs service object."""
    creds = get_credentials()
    return build("docs", "v1", credentials=creds)

def read_document_text(elements: list) -> str:
    """Recursively extract text from document elements."""
    text = ""
    for value in elements:
        if "paragraph" in value:
            elements = value.get("paragraph", {}).get("elements", [])
            for elem in elements:
                text_run = elem.get("textRun")
                if text_run:
                    text += text_run.get("content", "")
        elif "table" in value:
            # The text in table cells are in table cells' content.
            table = value.get("table", {})
            for row in table.get("tableRows", []):
                for cell in row.get("tableCells", []):
                    text += read_document_text(cell.get("content", []))
        elif "tableOfContents" in value:
            # The text in the TOC is also in a content field.
            toc = value.get("tableOfContents", {})
            text += read_document_text(toc.get("content", []))
    return text

def read_document(document_id: str) -> Dict[str, Any]:
    """Read the text content of a Google Doc by ID."""
    service = get_docs_service()
    try:
        document = service.documents().get(documentId=document_id).execute()
        
        title = document.get("title", "Untitled Document")
        content = document.get("body", {}).get("content", [])
        
        text_content = read_document_text(content)
        
        return {
            "document_id": document_id,
            "title": title,
            "content": text_content.strip()
        }
    except Exception as e:
        return {"error": str(e)}

def create_document(title: str, initial_content: Optional[str] = None) -> Dict[str, Any]:
    """Create a new Google Doc, optionally with initial content."""
    service = get_docs_service()
    try:
        # Create a blank document
        body = {"title": title}
        doc = service.documents().create(body=body).execute()
        document_id = doc.get("documentId")
        
        if initial_content:
            # Insert the initial content
            requests = [
                {
                    "insertText": {
                        "location": {
                            "index": 1,
                        },
                        "text": initial_content
                    }
                }
            ]
            service.documents().batchUpdate(
                documentId=document_id, body={"requests": requests}
            ).execute()
            
        return {
            "success": True,
            "document_id": document_id,
            "title": title
        }
    except Exception as e:
        return {"error": str(e)}
