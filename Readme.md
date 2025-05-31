# DRM Uploader Bot v2

A Telegram bot for downloading and uploading DRM-protected content from Utkarsh Classes, Appx, and ClassPlus platforms.

## Deployment on Render

1. **Create a new Web Service** on Render
2. Connect your GitHub repository
3. Set the following environment variables:
   - `API_ID`: Your Telegram API ID
   - `API_HASH`: Your Telegram API hash
   - `BOT_TOKEN`: Your Telegram bot token
   - `MONGODB_URI`: Your MongoDB connection string
   - `ADMIN_IDS`: Comma-separated list of admin user IDs
4. Set the build command: `pip install -r requirements.txt`
5. Set the start command: `python main.py`
6. Deploy!

## Features

- Supports multiple education platforms
- DRM protection for downloaded content
- User authorization system
- Activity logging
- Telegram file upload

## Admin Commands

- `/adduser <user_id>` - Authorize a new user
- `/removeuser <user_id>` - Remove user authorization
- `/logs` - View activity logs
