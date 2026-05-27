import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
DONATE_TEXT = os.getenv("DONATE_TEXT")
DONATE_IMAGE_FILE_ID = os.getenv("DONATE_IMAGE_FILE_ID")
DONATE_URL = os.getenv("DONATE_URL")

if not all([BOT_TOKEN, ADMIN_ID, DONATE_TEXT, DONATE_IMAGE_FILE_ID, DONATE_URL]):
    raise ValueError("Ошибка: Не все переменные окружения заданы в .env!")

try:
    ADMIN_ID = int(ADMIN_ID)
except ValueError:
    raise ValueError("Ошибка: ADMIN_ID должен быть целым числом!")
