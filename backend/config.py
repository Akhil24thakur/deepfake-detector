import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "deepfake_detector"),
    "charset": os.environ.get("DB_CHARSET", "utf8mb4"),
}

API_URL = os.environ.get("API_URL", "http://127.0.0.1:5000")
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
