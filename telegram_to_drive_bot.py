import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    creds = None
    # If running on Railway, token.json should have been generated locally and added to the project.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        # If token.json isn't present, try to run OAuth flow (will fail on Railway web, so run locally once).
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

drive_service = get_drive_service()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Send me any file (document, photo, video, audio, etc., up to 2GB) and I will upload it to Google Drive.'
    )

async def handle_attachment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = None
    file_name = None

    # Document
    if update.message.document:
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name
    # Photo (pick largest)
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_name = f"photo_{update.message.message_id}.jpg"
    # Video
    elif update.message.video:
        file_id = update.message.video.file_id
        file_name = update.message.video.file_name or f"video_{update.message.message_id}.mp4"
    # Audio
    elif update.message.audio:
        file_id = update.message.audio.file_id
        file_name = update.message.audio.file_name or f"audio_{update.message.message_id}.mp3"
    # Voice
    elif update.message.voice:
        file_id = update.message.voice.file_id
        file_name = f"voice_{update.message.message_id}.ogg"
    # Animation
    elif update.message.animation:
        file_id = update.message.animation.file_id
        file_name = update.message.animation.file_name or f"animation_{update.message.message_id}.gif"
    else:
        await update.message.reply_text("Unsupported file type. Please send document, photo, video, audio, voice, or animation.")
        return

    try:
        telegram_file = await context.bot.get_file(file_id)
        await telegram_file.download_to_drive(custom_path=file_name)
    except Exception as e:
        await update.message.reply_text(f"Error downloading file from Telegram: {str(e)}")
        return

    try:
        file_metadata = {'name': file_name}
        media = MediaFileUpload(file_name, resumable=True)
        drive_file = drive_service.files().create(
            body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        drive_url = drive_file.get("webViewLink")
    except Exception as e:
        await update.message.reply_text(f"Error uploading file to Google Drive: {str(e)}")
        os.remove(file_name)
        return

    try:
        os.remove(file_name)
    except Exception as e:
        logger.warning(f"Could not remove temp file: {str(e)}")

    await update.message.reply_text(
        f'File uploaded!\nDownload from Google Drive: {drive_url}'
    )

def main():
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    if not BOT_TOKEN:
        raise Exception("BOT_TOKEN environment variable not set!")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(
        filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO |
        filters.VOICE | filters.ANIMATION, handle_attachment)
    )
    app.run_polling()

if __name__ == '__main__':
    main()