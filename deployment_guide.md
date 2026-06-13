# Railway Deployment Guide for Google Workspace MCP Server

This guide explains how to deploy your MCP Server to Railway so it can run securely in the cloud and be accessed remotely.

## 1. Prepare Your Repository

1.  Make sure you have committed your code to a GitHub repository.
2.  **Crucial**: Double-check that your `.gitignore` is working and you have **NOT** committed `credentials.json`, `token.json`, or your `client_secret_*.json` files. These contain sensitive access to your Google account.

## 2. Prepare Your Environment Variables

Railway runs a "headless" container, meaning it has no browser for you to log into Google. Therefore, you must pass your credentials securely via Environment Variables.

Open your local `credentials.json` and `token.json` files and copy their entire contents. You will need these raw JSON strings in the next step.

## 3. Deploy to Railway

1.  Log in to [Railway.app](https://railway.app/).
2.  Click **New Project** -> **Deploy from GitHub repo**.
3.  Select your repository.
4.  Railway will detect your `Procfile` and `requirements.txt` and begin building using Nixpacks.
5.  While it's building, go to the **Variables** tab in your new Railway service.
6.  Add the following variables:
    *   **Variable Name**: `GOOGLE_CREDENTIALS_JSON`
        *   **Value**: (Paste the entire contents of your `credentials.json` here)
    *   **Variable Name**: `GOOGLE_TOKEN_JSON`
        *   **Value**: (Paste the entire contents of your `token.json` here)
    *   **Variable Name**: `RAILWAY_ENVIRONMENT`
        *   **Value**: `true`

## 4. Test Your Deployment

Once the build finishes and the variables are injected, Railway will start the server.

1.  Go to the **Settings** tab in Railway and click **Generate Domain** (if you haven't already).
2.  Your MCP server is now running using SSE (Server-Sent Events) transport.
3.  You can verify the server is running by visiting `https://your-generated-domain.up.railway.app/health` in your browser. It should return `{"status": "ok"}`.
4.  You can configure your remote LLM client to connect to your Railway URL. The SSE endpoint is typically located at `https://your-generated-domain.up.railway.app/sse`.

## How this compares to older REST APIs
If you see other tutorials mentioning endpoints like `POST /append_to_doc` or `POST /create_email_draft`, note that this project uses a much more modern standard: **FastMCP**. Instead of exposing dozens of individual HTTP endpoints, FastMCP exposes a single, unified `/sse` connection. AI clients connect to this single endpoint and automatically discover all available tools. This means you do not need individual HTTP POST routes for your Google workspace tools!

---
*Note: We modified `main.py` to automatically detect the Railway environment and switch from local `stdio` to remote `sse` transport on the designated `PORT`. We also updated `auth.py` to seamlessly read your Google authentication keys from the environment variables.*
