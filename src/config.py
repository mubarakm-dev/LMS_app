import os

from dotenv import load_dotenv

load_dotenv()  # reads the .env file into environment variables

# Database. The second argument is a harmless fallback used only if .env lacks the key.
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))  # env values are strings, so convert
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "lms_db")

# Email (no fallbacks for secrets)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Generated files (CSV exports, temp audio)
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
