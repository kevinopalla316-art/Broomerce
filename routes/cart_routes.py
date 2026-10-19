from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.cart_model import CartModel
from models.product_model import ProductModel

cart_bp = Blueprint("cart", __name__)


def _safe_redirect_to_login(next_url=None):
    login_target = url_for("auth.login")
    if next_url and next_url.startswith("/") and not next_url.startswith("//"):
        login_target = url_for("auth.login", next=next_url)
    return redirect(login_target)


def _parse_quantity(raw_quantity, default=1):
    try:
        quantity = int(raw_quantity)
    except (TypeError, ValueError):
        raise ValueError("Please enter a valid quantity.") from None

    if quantity <= 0:
        raise ValueError("Please enter a valid quantity.")

    return quantity


@cart_bp.route("/cart")
def cart():
    items = CartModel.get_cart_items()
    summary = CartModel.get_cart_summary(items)
    return render_template(
        "customer/cart.html",
        items=items,
        item_count=summary["item_count"],
        subtotal=summary["subtotal"],
        shipping=summary["shipping"],
        total=summary["total"],
    )


@cart_bp.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = ProductModel.get_product_by_id(product_id)
    if not product:
        flash("This product is no longer available.", "error")
        return redirect(url_for("products.products"))

    if int(product.get("is_active", 1)) == 0:
        flash("This product is currently unavailable.", "error")
        return redirect(url_for("products.product_details", slug=product["slug"]))

    try:
        quantity = _parse_quantity(request.form.get("quantity", 1))
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("products.product_details", slug=product["slug"]))

    if int(product.get("stock_quantity", 0)) <= 0:
        flash("This product is currently out of stock.", "error")
        return redirect(url_for("products.product_details", slug=product["slug"]))

    if quantity > int(product["stock_quantity"]):
        flash(f"Only {product['stock_quantity']} units of {product['name']} are available.", "error")
        return redirect(url_for("products.product_details", slug=product["slug"]))

    try:
        CartModel.add_item(product_id, quantity)
        flash(f"{product['name']} added to cart.", "success")
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("products.product_details", slug=product["slug"]))

    next_url = request.form.get("next") or request.args.get("next")
    if next_url and next_url.startswith("/") and not next_url.startswith("//"):
        return redirect(next_url)

    return redirect(url_for("cart.cart"))


@cart_bp.route("/buy-now/<int:product_id>", methods=["POST"])
@cart_bp.route("/cart/buy-now/<int:product_id>", methods=["POST"])
def buy_now(product_id):
    if "user_id" not in session:
        flash("Please log in to continue to checkout.", "error")
        return _safe_redirect_to_login(url_for("cart.checkout"))

    product = ProductModel.get_product_by_id(product_id)
    if not product:
        flash("This product is no longer available.", "error")
        return redirect(url_for("products.products"))

    if int(product.get("is_active", 1)) == 0:
        flash("This product is currently unavailable.", "error")
        return redirect(url_for("products.product_details", slug=product["slug"]))

    try:
        quantity = _parse_quantity(request.form.get("quantity", 1))
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("products.product_details", slug=product["slug"]))

    if int(product.get("stock_quantity", 0)) <= 0:
        flash("This product is currently out of stock.", "error")
        return redirect(url_for("products.product_details", slug=product["slug"]))

    if quantity > int(product["stock_quantity"]):
        flash(f"Only {product['stock_quantity']} units of {product['name']} are available.", "error")
        return redirect(url_for("products.product_details", slug=product["slug"]))

    try:
        CartModel.add_item(product_id, quantity)
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("products.product_details", slug=product["slug"]))

    flash(f"{product['name']} added to cart for checkout.", "success")
    return redirect(url_for("cart.checkout"))


@cart_bp.route("/cart/update/<int:product_id>", methods=["POST"])
def update_cart_item(product_id):
    try:
        quantity = _parse_quantity(request.form.get("quantity", 1))
        CartModel.update_item(product_id, quantity)
        flash("Your cart has been updated.", "success")
    except ValueError as exc:
        flash(str(exc), "error")
    return redirect(url_for("cart.cart"))


@cart_bp.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_cart_item(product_id):
    CartModel.remove_item(product_id)
    flash("Item removed from your cart.", "success")
    return redirect(url_for("cart.cart"))


@cart_bp.route("/cart/clear", methods=["POST"])
def clear_cart():
    CartModel.clear_cart()
    flash("Your cart has been cleared.", "success")
    return redirect(url_for("cart.cart"))


@cart_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "user_id" not in session:
        flash("Please log in to continue to checkout.", "error")
        return _safe_redirect_to_login(url_for("cart.checkout"))

    items = CartModel.get_cart_items()
    if not items:
        flash("Your cart is empty. Add a broom before checking out.", "error")
        return redirect(url_for("cart.cart"))

    summary = CartModel.get_cart_summary(items)
    checkout_data = session.get("checkout_data", {})

    if request.method == "POST":
        form_data = {
            "first_name": request.form.get("first_name", "").strip(),
            "last_name": request.form.get("last_name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "address": request.form.get("address", "").strip(),
            "city": request.form.get("city", "").strip(),
            "province": request.form.get("province", "").strip(),
            "postal_code": request.form.get("postal_code", "").strip(),
            "payment_method": request.form.get("payment_method", "").strip(),
            "delivery_method": request.form.get("delivery_method", "standard").strip(),
            "shipping_instructions": request.form.get("shipping_instructions", "").strip(),
        }

        required_fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "city",
            "province",
            "postal_code",
            "payment_method",
            "delivery_method",
        ]

        if any(not form_data[field] for field in required_fields):
            flash("Please complete all shipping and payment details.", "error")
            return render_template(
                "customer/checkout.html",
                items=items,
                checkout_data=form_data,
                item_count=summary["item_count"],
                subtotal=summary["subtotal"],
                shipping=summary["shipping"],
                total=summary["total"],
                order_placed=False,
            )

        session["checkout_data"] = form_data
        return redirect(url_for("orders.place_order"))

    return render_template(
        "customer/checkout.html",
        items=items,
        checkout_data=checkout_data,
        item_count=summary["item_count"],
        subtotal=summary["subtotal"],
        shipping=summary["shipping"],
        total=summary["total"],
        order_placed=False,
    )
