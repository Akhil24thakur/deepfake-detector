import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "")

if DATABASE_URL and DATABASE_URL.startswith("postgres"):
    DB_TYPE = "postgresql"
elif DATABASE_URL and DATABASE_URL.startswith("sqlite"):
    DB_TYPE = "sqlite"
else:
    DB_TYPE = "sqlite"

SQLITE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "deepfake.db")

API_URL = os.environ.get("API_URL", "")
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
