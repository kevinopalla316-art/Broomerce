import mysql.connector
from mysql.connector import Error

from config import Config


class ProductModel:
    @staticmethod
    def get_db_connection():
        try:
            return mysql.connector.connect(**Config.DB_CONFIG)
        except Error as exc:
            raise RuntimeError(f"Database connection failed: {exc}") from exc

    @staticmethod
    def get_active_products(limit=None, offset=0):
        conn = ProductModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT p.*, c.name AS category_name
                FROM products p
                INNER JOIN categories c ON c.id = p.category_id
                WHERE p.is_active = 1
                ORDER BY p.created_at DESC
            """
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
    def get_product_by_id(product_id):
        conn = ProductModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT p.*, c.name AS category_name
                FROM products p
                INNER JOIN categories c ON c.id = p.category_id
                WHERE p.id = %s AND p.is_active = 1
                LIMIT 1
            """
            cursor.execute(query, (product_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_product_by_slug(slug):
        conn = ProductModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT p.*, c.name AS category_name
                FROM products p
                INNER JOIN categories c ON c.id = p.category_id
                WHERE p.slug = %s AND p.is_active = 1
                LIMIT 1
            """
            cursor.execute(query, (slug,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_products_by_category(category_id, limit=None, offset=0):
        conn = ProductModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT p.*, c.name AS category_name
                FROM products p
                INNER JOIN categories c ON c.id = p.category_id
                WHERE p.category_id = %s AND p.is_active = 1
                ORDER BY p.created_at DESC
            """
            if limit is not None:
                query += " LIMIT %s OFFSET %s"
                cursor.execute(query, (category_id, limit, offset))
            else:
                cursor.execute(query, (category_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def search_products(search_term=None, category_id=None, min_price=None, max_price=None, sort="featured", limit=12, offset=0):
        conn = ProductModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT p.*, c.name AS category_name
                FROM products p
                INNER JOIN categories c ON c.id = p.category_id
                WHERE p.is_active = 1
            """
            params = []

            if search_term:
                query += " AND (p.name LIKE %s OR p.description LIKE %s OR p.sku LIKE %s) "
                pattern = f"%{search_term}%"
                params.extend([pattern, pattern, pattern])

            if category_id:
                query += " AND p.category_id = %s"
                params.append(category_id)

            if min_price is not None:
                query += " AND p.price >= %s"
                params.append(float(min_price))

            if max_price is not None:
                query += " AND p.price <= %s"
                params.append(float(max_price))

            if sort == "price_asc":
                query += " ORDER BY p.price ASC, p.created_at DESC"
            elif sort == "price_desc":
                query += " ORDER BY p.price DESC, p.created_at DESC"
            elif sort == "name_asc":
                query += " ORDER BY p.name ASC"
            elif sort == "newest":
                query += " ORDER BY p.created_at DESC"
            else:
                query += " ORDER BY p.created_at DESC"

            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def count_products(search_term=None, category_id=None, min_price=None, max_price=None):
        conn = ProductModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT COUNT(*) AS total
                FROM products p
                WHERE p.is_active = 1
            """
            params = []

            if search_term:
                query += " AND (p.name LIKE %s OR p.description LIKE %s OR p.sku LIKE %s) "
                pattern = f"%{search_term}%"
                params.extend([pattern, pattern, pattern])

            if category_id:
                query += " AND p.category_id = %s"
                params.append(category_id)

            if min_price is not None:
                query += " AND p.price >= %s"
                params.append(float(min_price))

            if max_price is not None:
                query += " AND p.price <= %s"
                params.append(float(max_price))

            cursor.execute(query, tuple(params))
            result = cursor.fetchone()
            return int(result["total"]) if result else 0
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_featured_products(limit=4):
        conn = ProductModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT p.*, c.name AS category_name
                FROM products p
                INNER JOIN categories c ON c.id = p.category_id
                WHERE p.is_active = 1
                ORDER BY p.created_at DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_all_products(limit=None, offset=0):
        conn = ProductModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT p.*, c.name AS category_name
                FROM products p
                INNER JOIN categories c ON c.id = p.category_id
                ORDER BY p.created_at DESC
            """
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
    def count_low_stock_products():
        conn = ProductModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT COUNT(*) AS total
                FROM products
                WHERE is_active = 1 AND stock_quantity <= low_stock_threshold
            """
            cursor.execute(query)
            result = cursor.fetchone()
            return int(result["total"]) if result else 0
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_low_stock_products(limit=10):
        conn = ProductModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT p.*, c.name AS category_name
                FROM products p
                INNER JOIN categories c ON c.id = p.category_id
                WHERE p.is_active = 1 AND p.stock_quantity <= p.low_stock_threshold
                ORDER BY p.stock_quantity ASC, p.name ASC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def create_product(data):
        conn = ProductModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                INSERT INTO products (
                    category_id, name, slug, description, price, stock_quantity,
                    low_stock_threshold, sku, image, is_active, is_featured,
                    created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            cursor.execute(
                query,
                (
                    int(data["category_id"]),
                    data["name"].strip(),
                    data["slug"].strip(),
                    data["description"].strip(),
                    float(data["price"]),
                    int(data["stock_quantity"]),
                    int(data.get("low_stock_threshold", 5)),
                    data["sku"].strip(),
                    data.get("image") or None,
                    1 if data.get("is_active") else 0,
                    1 if data.get("is_featured") else 0,
                ),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def update_product(product_id, data):
        conn = ProductModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                UPDATE products
                SET category_id = %s,
                    name = %s,
                    slug = %s,
                    description = %s,
                    price = %s,
                    stock_quantity = %s,
                    low_stock_threshold = %s,
                    sku = %s,
                    image = %s,
                    is_active = %s,
                    is_featured = %s,
                    updated_at = NOW()
                WHERE id = %s
            """
            cursor.execute(
                query,
                (
                    int(data["category_id"]),
                    data["name"].strip(),
                    data["slug"].strip(),
                    data["description"].strip(),
                    float(data["price"]),
                    int(data["stock_quantity"]),
                    int(data.get("low_stock_threshold", 5)),
                    data["sku"].strip(),
                    data.get("image") or None,
                    1 if data.get("is_active") else 0,
                    1 if data.get("is_featured") else 0,
                    int(product_id),
                ),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_top_selling_products(limit=5):
        conn = ProductModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT p.id, p.name, p.sku,
                       SUM(oi.quantity) AS units_sold,
                       SUM(oi.subtotal) AS revenue
                FROM order_items oi
                INNER JOIN products p ON p.id = oi.product_id
                INNER JOIN orders o ON o.id = oi.order_id
                WHERE o.status IN ('Processing', 'Shipped', 'Delivered')
                GROUP BY p.id, p.name, p.sku
                ORDER BY units_sold DESC, revenue DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
