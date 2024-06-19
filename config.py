import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
ADMINS = [int(admin_id) for admin_id in os.getenv('ADMINS', '').split(',')]
# تنظیمات لاگینگ
LOGGING_ENABLED = True  # این را به False تغییر دهید تا لاگینگ غیرفعال شود
LOGGING_LEVEL = 'DEBUG'  # سطوح لاگینگ: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = 'bot.log'