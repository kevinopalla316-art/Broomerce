import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.getenv("SECRET_KEY", "change_this_secret_key")
    SESSION_SECRET = os.getenv("SESSION_SECRET", SECRET_KEY)
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", "5000"))
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(BASE_DIR, "uploads"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024)))

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_NAME = os.getenv("DB_NAME", "broomerce")
    DB_USER = os.getenv("DB_USER", "broomerce_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    DB_CONFIG = {
        "host": DB_HOST,
        "port": DB_PORT,
        "database": DB_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "autocommit": True,
        "charset": "utf8mb4",
        "use_pure": True,
    }
