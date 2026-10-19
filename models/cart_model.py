from flask import session

from models.product_model import ProductModel


class CartModel:
    @staticmethod
    def get_cart():
        cart = session.get("cart", {})
        if not isinstance(cart, dict):
            cart = {}

        normalized = {}
        for key, quantity in cart.items():
            try:
                product_id = int(key)
                qty = int(quantity)
            except (TypeError, ValueError):
                continue
            if product_id > 0 and qty > 0:
                normalized[str(product_id)] = qty

        session["cart"] = normalized
        return normalized

    @staticmethod
    def get_cart_items():
        cart = CartModel.get_cart()
        items = []

        for product_id_str, quantity in cart.items():
            product = ProductModel.get_product_by_id(int(product_id_str))
            if not product:
                continue

            available_quantity = max(int(product.get("stock_quantity", 0)), 0)
            if available_quantity <= 0:
                continue

            if quantity > available_quantity:
                cart[str(product["id"])] = available_quantity
                session["cart"] = cart
                quantity = available_quantity

            line_total = float(product["price"]) * quantity
            items.append(
                {
                    "id": product["id"],
                    "name": product["name"],
                    "slug": product["slug"],
                    "price": float(product["price"]),
                    "quantity": quantity,
                    "image": product.get("image"),
                    "category_name": product.get("category_name", "General"),
                    "line_total": line_total,
                }
            )

        return items

    @staticmethod
    def get_cart_summary(items=None):
        if items is None:
            items = CartModel.get_cart_items()

        subtotal = sum(float(item["line_total"]) for item in items)
        item_count = sum(int(item["quantity"]) for item in items)
        shipping = 0 if subtotal >= 1500 else 199.00
        total = subtotal + shipping

        return {
            "item_count": item_count,
            "subtotal": round(subtotal, 2),
            "shipping": round(shipping, 2),
            "total": round(total, 2),
        }

    @staticmethod
    def get_cart_count():
        cart = CartModel.get_cart()
        return sum(int(quantity) for quantity in cart.values())

    @staticmethod
    def add_item(product_id, quantity=1):
        product = ProductModel.get_product_by_id(product_id)
        if not product:
            raise ValueError("This product is no longer available.")

        if product.get("is_active") is False or int(product.get("is_active", 1)) == 0:
            raise ValueError("This product is currently unavailable.")

        stock_quantity = int(product.get("stock_quantity", 0))
        if stock_quantity <= 0:
            raise ValueError("This product is currently out of stock.")

        try:
            requested_quantity = int(quantity)
        except (TypeError, ValueError):
            raise ValueError("Please enter a valid quantity.") from None

        if requested_quantity <= 0:
            raise ValueError("Please enter a valid quantity.")

        cart = CartModel.get_cart()
        current_quantity = int(cart.get(str(product_id), 0))
        available_capacity = stock_quantity - current_quantity

        if requested_quantity > available_capacity:
            raise ValueError(f"Only {stock_quantity - current_quantity} units of {product['name']} are available.")

        cart[str(product_id)] = current_quantity + requested_quantity
        session["cart"] = cart
        return CartModel.get_cart_summary()

    @staticmethod
    def update_item(product_id, quantity):
        cart = CartModel.get_cart()
        product = ProductModel.get_product_by_id(product_id)

        if not product:
            raise ValueError("This product is no longer available.")

        try:
            new_quantity = int(quantity)
        except (TypeError, ValueError):
            raise ValueError("Please enter a valid quantity.") from None

        if new_quantity <= 0:
            cart.pop(str(product_id), None)
            session["cart"] = cart
            return CartModel.get_cart_summary()

        stock_quantity = int(product.get("stock_quantity", 0))
        if new_quantity > stock_quantity:
            raise ValueError(f"Only {stock_quantity} units of {product['name']} are available.")

        cart[str(product_id)] = new_quantity
        session["cart"] = cart
        return CartModel.get_cart_summary()

    @staticmethod
    def remove_item(product_id):
        cart = CartModel.get_cart()
        cart.pop(str(product_id), None)
        session["cart"] = cart
        return CartModel.get_cart_summary()

    @staticmethod
    def clear_cart():
        session["cart"] = {}
        return CartModel.get_cart_summary([])
