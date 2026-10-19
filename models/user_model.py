import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config


class UserModel:
    @staticmethod
    def get_db_connection():
        if not Config.DB_USER or not Config.DB_NAME:
            raise RuntimeError(
                "Database is not configured. Set DB_USER, DB_PASSWORD, DB_NAME, and DB_HOST in your .env file before signing up."
            )

        try:
            connection = mysql.connector.connect(**Config.DB_CONFIG)
            return connection
        except Error as exc:
            raise RuntimeError(
                f"Database connection failed: {exc}. Check your MySQL credentials in .env and confirm the database server is running."
            ) from exc

    @staticmethod
    def create_user(first_name, last_name, email, phone, password):
        conn = UserModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            password_hash = generate_password_hash(password)
            query = """
                INSERT INTO users (first_name, last_name, email, phone, password_hash, role, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            cursor.execute(
                query,
                (first_name, last_name, email, phone, password_hash, "customer", 1),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def find_by_email(email):
        conn = UserModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = "SELECT * FROM users WHERE email = %s LIMIT 1"
            cursor.execute(query, (email,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def verify_login(email, password):
        user = UserModel.find_by_email(email)
        if not user:
            return None

        if not check_password_hash(user["password_hash"], password):
            return None

        return user

    @staticmethod
    def get_user_by_id(user_id):
        conn = UserModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = "SELECT * FROM users WHERE id = %s LIMIT 1"
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_all_users(limit=None, offset=0):
        conn = UserModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = "SELECT * FROM users ORDER BY created_at DESC"
            if limit is not None:
                query += " LIMIT %s OFFSET %s"
                cursor.execute(query, (limit, offset))
            else:
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def update_user_status(user_id, is_active):
        conn = UserModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                "UPDATE users SET is_active = %s, updated_at = NOW() WHERE id = %s",
                (1 if is_active else 0, user_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
