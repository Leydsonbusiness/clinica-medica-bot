# arquivo para configs

import os 
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
Chat_id_medico = os.getenv("Chat_id_medico")
GOOGLE_CREDENTIALS_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
CALENDAR_ID = os.getenv("CALENDAR_ID")