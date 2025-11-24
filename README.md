# Telegram to Google Drive Bot

A Telegram bot that uploads received files (up to 2GB) directly to your Google Drive.

## Features
- Handles documents, photos, videos, audio, voice messages, and animations
- Replies with a Google Drive download link
- Easy deployment on Railway, Render, or any cloud/VPS

## Setup

### 1. Authorize Google Drive
- Get `credentials.json` from [Google Cloud Console](https://console.developers.google.com/).
- Run the script locally to generate `token.json`. This is your Google API access token.

### 2. Deploy

#### Railway
- Upload your files to a private repo.
- On Railway dashboard:
  - Add `BOT_TOKEN` as an environment variable.
  - Upload `credentials.json` and `token.json` (generated from local run).
- Set the start command to `python3 telegram_to_drive_bot.py` (default).

### 3. Usage
- Start your Telegram bot and send any supported file.
- Bot will reply with a Google Drive link after upload.

## Notes
- Only files up to 2GB supported due to Telegram bot API limit.
- Keep your credentials and tokens safe. Do **not** push them to public repositories.
