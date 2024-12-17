import os
from dotenv import load_dotenv

load_dotenv()

IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASS = os.getenv("IMAP_PASS")
IMAP_FOLDER = os.getenv("IMAP_FOLDER", "INBOX")

LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'app.log')
OUTPUT_CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'output.csv')
