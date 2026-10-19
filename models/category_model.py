import mysql.connector
from mysql.connector import Error

from config import Config


class CategoryModel:
    @staticmethod
    def get_db_connection():
        try:
            return mysql.connector.connect(**Config.DB_CONFIG)
        except Error as exc:
            raise RuntimeError(f"Database connection failed: {exc}") from exc

    @staticmethod
    def get_active_categories(limit=None):
        conn = CategoryModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT c.*, COUNT(p.id) AS product_count
                FROM categories c
                LEFT JOIN products p ON p.category_id = c.id AND p.is_active = 1
                WHERE c.is_active = 1
                GROUP BY c.id
                ORDER BY c.name ASC
            """
            if limit:
                query += " LIMIT %s"
                cursor.execute(query, (limit,))
            else:
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_category_by_id(category_id):
        conn = CategoryModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = "SELECT * FROM categories WHERE id = %s AND is_active = 1 LIMIT 1"
            cursor.execute(query, (category_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def count_products_by_category(category_id):
        conn = CategoryModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = "SELECT COUNT(*) AS total FROM products WHERE category_id = %s AND is_active = 1"
            cursor.execute(query, (category_id,))
            result = cursor.fetchone()
            return int(result["total"]) if result else 0
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_all_categories(limit=None, offset=0):
        conn = CategoryModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = "SELECT * FROM categories ORDER BY name ASC"
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
    def create_category(name, description=None, image=None, is_active=1):
        conn = CategoryModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                INSERT INTO categories (name, description, image, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """
            cursor.execute(query, (name.strip(), description.strip() if description else None, image.strip() if image else None, 1 if is_active else 0))
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def update_category(category_id, name, description=None, image=None, is_active=1):
        conn = CategoryModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                UPDATE categories
                SET name = %s,
                    description = %s,
                    image = %s,
                    is_active = %s,
                    updated_at = NOW()
                WHERE id = %s
            """
            cursor.execute(query, (name.strip(), description.strip() if description else None, image.strip() if image else None, 1 if is_active else 0, category_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_category_by_name(name):
        conn = CategoryModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = "SELECT * FROM categories WHERE name = %s LIMIT 1"
            cursor.execute(query, (name.strip(),))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
