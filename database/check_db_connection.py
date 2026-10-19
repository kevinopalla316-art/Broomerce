import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import mysql.connector

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

from config import Config


def main():
    print("Database configuration:")
    print(f"Host: {Config.DB_HOST}")
    print(f"Port: {Config.DB_PORT}")
    print(f"Database: {Config.DB_NAME}")
    print(f"User: {Config.DB_USER}")
    print("Password configured: %s" % ("YES" if Config.DB_PASSWORD else "NO"))

    try:
        connection = mysql.connector.connect(**Config.DB_CONFIG)
        connection.close()
        print("Database connection: SUCCESS")
        return 0
    except Exception as exc:  # pragma: no cover - intentionally reports runtime connection state
        print("Database connection: FAILED")
        print(f"Error: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
