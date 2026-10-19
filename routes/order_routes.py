from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.order_model import OrderModel

order_bp = Blueprint("orders", __name__)


@order_bp.route("/checkout/place-order", methods=["GET", "POST"])
def place_order():
    if "user_id" not in session:
        flash("Please log in to place an order.", "error")
        return redirect(url_for("auth.login"))

    cart = session.get("cart", {})
    if not cart:
        flash("Your cart is empty.", "error")
        return redirect(url_for("cart.cart"))

    checkout_data = session.get("checkout_data", {})
    if not checkout_data:
        flash("Please complete your checkout details before placing the order.", "error")
        return redirect(url_for("cart.checkout"))

    delivery_method = (request.form.get("delivery_method") or checkout_data.get("delivery_method") or "standard").strip().lower()
    payment_method = (request.form.get("payment_method") or checkout_data.get("payment_method") or "cod").strip().lower()

    shipping_data = {
        "first_name": (request.form.get("first_name") or checkout_data.get("first_name") or "").strip(),
        "last_name": (request.form.get("last_name") or checkout_data.get("last_name") or "").strip(),
        "phone": (request.form.get("phone") or checkout_data.get("phone") or "").strip(),
        "address": (request.form.get("address") or checkout_data.get("address") or "").strip(),
        "city": (request.form.get("city") or checkout_data.get("city") or "").strip(),
        "province": (request.form.get("province") or checkout_data.get("province") or "").strip(),
        "postal_code": (request.form.get("postal_code") or checkout_data.get("postal_code") or "").strip(),
        "shipping_instructions": (request.form.get("shipping_instructions") or checkout_data.get("shipping_instructions") or "").strip(),
        "cart": cart,
    }

    try:
        result = OrderModel.create_order_from_cart(session["user_id"], shipping_data, delivery_method, payment_method)
        session.pop("checkout_data", None)
        session["cart"] = {}
        return redirect(url_for("orders.order_confirmation", order_number=result["order_number"]))
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("cart.checkout"))
    except RuntimeError as exc:
        flash(str(exc), "error")
        return redirect(url_for("cart.checkout"))
    except Exception:
        flash("We couldn't complete your order right now. Please try again later.", "error")
        return redirect(url_for("cart.checkout"))


@order_bp.route("/order-confirmation/<order_number>")
def order_confirmation(order_number):
    if "user_id" not in session:
        flash("Please log in to view your order.", "error")
        return redirect(url_for("auth.login"))

    order_detail = OrderModel.get_order_detail(order_number, session["user_id"])
    if not order_detail:
        flash("Order not found.", "error")
        return redirect(url_for("orders.orders"))

    order = order_detail["order"]
    payment = order_detail["payment"]
    items = order_detail["items"]
    return render_template(
        "customer/order_confirmation.html",
        order=order,
        items=items,
        payment=payment,
        status_timeline=OrderModel.build_status_timeline(order["status"]),
    )


@order_bp.route("/orders")
def orders():
    if "user_id" not in session:
        flash("Please log in to view your orders.", "error")
        return redirect(url_for("auth.login"))

    status_filter = request.args.get("status", "all").strip().lower()
    valid_statuses = ["all", "pending", "processing", "shipped", "delivered", "cancelled"]
    if status_filter not in valid_statuses:
        status_filter = "all"

    raw_status = None if status_filter == "all" else status_filter.title()
    items = OrderModel.get_orders_for_user(session["user_id"], raw_status)

    return render_template(
        "customer/orders.html",
        orders=items,
        filter=status_filter,
        valid_statuses=valid_statuses,
    )


@order_bp.route("/orders/<order_number>")
def order_detail(order_number):
    if "user_id" not in session:
        flash("Please log in to view your order.", "error")
        return redirect(url_for("auth.login"))

    order_detail = OrderModel.get_order_detail(order_number, session["user_id"])
    if not order_detail:
        return render_template("errors/404.html"), 404

    order = order_detail["order"]
    payment = order_detail["payment"]
    items = order_detail["items"]
    return render_template(
        "customer/order_detail.html",
        order=order,
        items=items,
        payment=payment,
        status_timeline=OrderModel.build_status_timeline(order["status"]),
    )
