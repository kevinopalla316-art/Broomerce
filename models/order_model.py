from datetime import datetime

import mysql.connector
from mysql.connector import Error

from config import Config


class OrderModel:
    VALID_DELIVERY_METHODS = {
        "standard": {"label": "Standard Delivery", "fee": 60.00},
        "express": {"label": "Express Delivery", "fee": 120.00},
    }
    VALID_PAYMENT_METHODS = {
        "cod": "Cash on Delivery",
        "gcash": "GCash",
        "bank_transfer": "Bank Transfer",
    }
    STATUS_SEQUENCE = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]

    @staticmethod
    def get_db_connection():
        try:
            connection = mysql.connector.connect(**Config.DB_CONFIG)
            return connection
        except Error as exc:
            raise RuntimeError(f"Database connection failed: {exc}") from exc

    @staticmethod
    def format_delivery_method(value):
        method = (value or "standard").strip().lower()
        return OrderModel.VALID_DELIVERY_METHODS.get(method, {"label": "Standard Delivery", "fee": 60.00})["label"]

    @staticmethod
    def format_payment_method(value):
        method = (value or "cod").strip().lower()
        label = OrderModel.VALID_PAYMENT_METHODS.get(method, "Cash on Delivery")
        return label

    @staticmethod
    def format_order_status(value):
        return (value or "Pending").strip()

    @staticmethod
    def generate_order_number(cursor):
        today = datetime.now().strftime("%Y%m%d")
        cursor.execute(
            "SELECT COUNT(*) AS total FROM orders WHERE DATE(created_at) = CURDATE()"
        )
        result = cursor.fetchone()
        sequence = int(result["total"]) + 1 if result else 1
        return f"BRM-{today}-{sequence:04d}"

    @staticmethod
    def build_status_timeline(status):
        status = (status or "Pending").strip()
        timeline = [
            {"name": "Order Placed", "active": status in {"Pending", "Processing", "Shipped", "Delivered", "Cancelled"}},
            {"name": "Processing", "active": status in {"Processing", "Shipped", "Delivered"}},
            {"name": "Shipped", "active": status in {"Shipped", "Delivered"}},
            {"name": "Delivered", "active": status == "Delivered"},
        ]
        if status == "Cancelled":
            timeline = [
                {"name": "Order Placed", "active": True},
                {"name": "Cancelled", "active": True},
            ]
        return timeline

    @staticmethod
    def create_order_from_cart(user_id, shipping_data, delivery_method, payment_method):
        if not user_id:
            raise ValueError("Please log in to place an order.")

        cart = {str(k): int(v) for k, v in (shipping_data.get("cart") or {}).items()}
        if not cart:
            raise ValueError("Your cart is empty.")

        delivery_key = (delivery_method or "standard").strip().lower()
        if delivery_key not in OrderModel.VALID_DELIVERY_METHODS:
            raise ValueError("Invalid delivery method selected.")

        payment_key = (payment_method or "cod").strip().lower()
        if payment_key not in OrderModel.VALID_PAYMENT_METHODS:
            raise ValueError("Invalid payment method selected.")

        required_fields = [
            "first_name",
            "last_name",
            "phone",
            "address",
            "city",
            "province",
            "postal_code",
        ]
        for field in required_fields:
            value = (shipping_data.get(field) or "").strip()
            if not value:
                raise ValueError("Please complete all shipping details before placing your order.")

        shipping_data = {
            "first_name": shipping_data.get("first_name", "").strip(),
            "last_name": shipping_data.get("last_name", "").strip(),
            "phone": shipping_data.get("phone", "").strip(),
            "address": shipping_data.get("address", "").strip(),
            "city": shipping_data.get("city", "").strip(),
            "province": shipping_data.get("province", "").strip(),
            "postal_code": shipping_data.get("postal_code", "").strip(),
            "instructions": (shipping_data.get("shipping_instructions") or "").strip(),
        }

        conn = OrderModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            conn.autocommit = False
            conn.start_transaction()

            product_ids = [int(product_id) for product_id in cart.keys()]
            placeholder_sql = ", ".join(["%s"] * len(product_ids))
            query = f"""
                SELECT p.id, p.name, p.sku, p.price, p.stock_quantity, p.is_active
                FROM products p
                WHERE p.id IN ({placeholder_sql})
                AND p.is_active = 1
                FOR UPDATE
            """
            cursor.execute(query, tuple(product_ids))
            available_products = cursor.fetchall()

            if len(available_products) != len(product_ids):
                raise ValueError("One or more products in your cart are no longer available.")

            product_map = {int(product["id"]): product for product in available_products}
            subtotal = 0.0
            order_items = []

            for product_id_string, quantity in cart.items():
                product_id = int(product_id_string)
                product = product_map.get(product_id)
                if product is None:
                    raise ValueError("One of the products in your cart is no longer available.")

                requested_quantity = int(quantity)
                if requested_quantity <= 0:
                    raise ValueError(f"Invalid quantity for {product['name']}.")

                available_stock = int(product["stock_quantity"])
                if requested_quantity > available_stock:
                    raise ValueError(
                        f"Insufficient stock for {product['name']}. Available quantity: {available_stock}. Requested quantity: {requested_quantity}."
                    )

                unit_price = float(product["price"])
                line_total = unit_price * requested_quantity
                subtotal += line_total
                order_items.append(
                    {
                        "product_id": product_id,
                        "product_name": product["name"],
                        "sku": product["sku"],
                        "unit_price": unit_price,
                        "quantity": requested_quantity,
                        "subtotal": line_total,
                    }
                )

            shipping_fee = float(OrderModel.VALID_DELIVERY_METHODS[delivery_key]["fee"])
            total_amount = round(subtotal + shipping_fee, 2)
            order_number = OrderModel.generate_order_number(cursor)

            cursor.execute(
                """
                INSERT INTO orders (
                    order_number,
                    user_id,
                    status,
                    payment_method,
                    payment_status,
                    delivery_method,
                    shipping_fee,
                    subtotal,
                    total_amount,
                    shipping_first_name,
                    shipping_last_name,
                    shipping_phone,
                    shipping_address,
                    shipping_city,
                    shipping_province,
                    shipping_postal_code,
                    shipping_instructions,
                    created_at,
                    updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """,
                (
                    order_number,
                    user_id,
                    "Pending",
                    payment_key,
                    "Pending",
                    delivery_key,
                    shipping_fee,
                    round(subtotal, 2),
                    total_amount,
                    shipping_data["first_name"],
                    shipping_data["last_name"],
                    shipping_data["phone"],
                    shipping_data["address"],
                    shipping_data["city"],
                    shipping_data["province"],
                    shipping_data["postal_code"],
                    shipping_data["instructions"],
                ),
            )
            order_id = cursor.lastrowid

            for item in order_items:
                cursor.execute(
                    """
                    INSERT INTO order_items (
                        order_id,
                        product_id,
                        product_name,
                        sku,
                        unit_price,
                        quantity,
                        subtotal,
                        created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    """,
                    (
                        order_id,
                        item["product_id"],
                        item["product_name"],
                        item["sku"],
                        item["unit_price"],
                        item["quantity"],
                        item["subtotal"],
                    ),
                )

            reference_number = f"PAY-{order_number}"
            cursor.execute(
                """
                INSERT INTO payments (
                    order_id,
                    payment_method,
                    payment_status,
                    amount,
                    reference_number,
                    created_at,
                    updated_at
                ) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                """,
                (order_id, payment_key, "Pending", total_amount, reference_number),
            )

            for product_id, item in [(int(item["product_id"]), item) for item in order_items]:
                cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - %s WHERE id = %s AND stock_quantity >= %s",
                    (item["quantity"], product_id, item["quantity"]),
                )
                if cursor.rowcount != 1:
                    raise ValueError(f"Unable to update stock for {item['product_name']}.")

                previous_stock_query = "SELECT stock_quantity FROM products WHERE id = %s LIMIT 1"
                cursor.execute(previous_stock_query, (product_id,))
                previous_stock_row = cursor.fetchone()
                previous_stock = int(previous_stock_row["stock_quantity"]) if previous_stock_row else 0
                new_stock = previous_stock - int(item["quantity"])

                cursor.execute(
                    """
                    INSERT INTO inventory_movements (
                        product_id,
                        movement_type,
                        quantity,
                        previous_stock,
                        new_stock,
                        reference,
                        user_id,
                        notes,
                        created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """,
                    (
                        product_id,
                        "SALE",
                        -int(item["quantity"]),
                        previous_stock,
                        new_stock,
                        order_number,
                        user_id,
                        f"Order {order_number} sale",
                    ),
                )

            conn.commit()
            return {
                "order_id": order_id,
                "order_number": order_number,
                "subtotal": round(subtotal, 2),
                "shipping_fee": round(shipping_fee, 2),
                "total_amount": round(total_amount, 2),
                "status": "Pending",
                "payment_method": payment_key,
            }
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_orders_for_user(user_id, status=None):
        conn = OrderModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM orders WHERE user_id = %s"
            params = [user_id]
            if status and status != "all":
                query += " AND status = %s"
                params.append(status)
            query += " ORDER BY created_at DESC"
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_all_orders(status=None, search=None, limit=None, offset=0):
        conn = OrderModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT o.*, u.first_name, u.last_name, u.email
                FROM orders o
                INNER JOIN users u ON u.id = o.user_id
                WHERE 1=1
            """
            params = []

            if status and status != "all":
                query += " AND o.status = %s"
                params.append(status)

            if search:
                query += " AND (o.order_number LIKE %s OR u.first_name LIKE %s OR u.last_name LIKE %s OR u.email LIKE %s)"
                pattern = f"%{search}%"
                params.extend([pattern, pattern, pattern, pattern])

            query += " ORDER BY o.created_at DESC"
            if limit is not None:
                query += " LIMIT %s OFFSET %s"
                params.extend([limit, offset])

            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_order_count_by_status(status):
        conn = OrderModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = "SELECT COUNT(*) AS total FROM orders WHERE status = %s"
            cursor.execute(query, (status,))
            result = cursor.fetchone()
            return int(result["total"]) if result else 0
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def update_order_status(order_number, new_status, user_id=None):
        valid = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
        if new_status not in valid:
            raise ValueError("Invalid order status selected.")

        conn = OrderModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                "UPDATE orders SET status = %s, updated_at = NOW() WHERE order_number = %s",
                (new_status, order_number),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_order_detail(order_number, user_id=None):
        conn = OrderModel.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            if user_id is None:
                cursor.execute(
                    "SELECT * FROM orders WHERE order_number = %s LIMIT 1",
                    (order_number,),
                )
            else:
                cursor.execute(
                    "SELECT * FROM orders WHERE order_number = %s AND user_id = %s LIMIT 1",
                    (order_number, user_id),
                )
            order = cursor.fetchone()
            if not order:
                return None

            cursor.execute(
                "SELECT * FROM order_items WHERE order_id = %s ORDER BY id ASC",
                (order["id"],),
            )
            items = cursor.fetchall()

            cursor.execute(
                "SELECT * FROM payments WHERE order_id = %s LIMIT 1",
                (order["id"],),
            )
            payment = cursor.fetchone()

            return {"order": order, "items": items, "payment": payment}
        finally:
            cursor.close()
            conn.close()
