# Google Workspace MCP Server

This project is an MCP (Model Context Protocol) server that provides tools to interact with Gmail and Google Docs.

## Prerequisites

1.  **Python 3.10+**
2.  **Google Cloud Project**: You need to create a project in the Google Cloud Console and enable the Gmail and Google Docs APIs.

### Setting up Google Cloud Credentials

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project.
3.  Go to **APIs & Services > Library**.
4.  Search for and enable **Gmail API** and **Google Docs API**.
5.  Go to **APIs & Services > OAuth consent screen**.
    *   Choose **External** (or Internal if you have a Google Workspace org).
    *   Fill in the required app information.
    *   Add the following scopes:
        *   `https://www.googleapis.com/auth/gmail.modify`
        *   `https://www.googleapis.com/auth/documents`
    *   Add your Google email address as a **Test user**.
6.  Go to **APIs & Services > Credentials**.
7.  Click **Create Credentials > OAuth client ID**.
8.  Choose **Desktop app** as the application type.
9.  Click **Create** and then **Download JSON**.
10. Rename the downloaded file to `credentials.json` and place it in the root directory of this project.

## Installation

It is recommended to use a virtual environment.

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## Running the Server

To start the MCP server, use the `mcp` CLI tool (installed via dependencies):

```bash
mcp dev main.py
```

The first time you run this, a browser window will open asking you to log in with your Google account and grant permissions to the app. After granting permissions, a `token.json` file will be created locally to store your access and refresh tokens.

## Available Tools

The following tools will be exposed to your LLM:

*   `search_emails(query, max_results)`: Search for emails matching a Gmail query.
*   `read_email(message_id)`: Read the content of a specific email.
*   `send_email(to, subject, body)`: Send an email.
*   `read_document(document_id)`: Read the text content of a Google Doc.
*   `create_document(title, content)`: Create a new Google Doc with optional initial content.
