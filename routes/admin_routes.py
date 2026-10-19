from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.category_model import CategoryModel
from models.order_model import OrderModel
from models.product_model import ProductModel
from models.user_model import UserModel

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def login_required():
    if "user_id" not in session:
        flash("Please log in to continue.", "error")
        return redirect(url_for("auth.login"))
    return None


def staff_required():
    if "user_id" not in session:
        flash("Please log in to continue.", "error")
        return redirect(url_for("auth.login"))
    if session.get("user_role") not in {"admin", "staff"}:
        flash("You do not have permission to access the admin area.", "error")
        return redirect(url_for("main.home"))
    return None


@admin_bp.before_request
def enforce_admin_access():
    protected_paths = ["/", "/products", "/categories", "/inventory", "/inventory/movements", "/suppliers", "/purchases", "/orders", "/customers", "/reports"]
    if request.path in protected_paths:
        result = staff_required()
        if result is not None:
            return result


@admin_bp.route("")
@admin_bp.route("/")
def dashboard():
    result = staff_required()
    if result is not None:
        return result

    try:
        total_products = ProductModel.count_products()
        low_stock_products = ProductModel.count_low_stock_products()
        total_customers = UserModel.get_all_users()
        pending_orders = OrderModel.get_order_count_by_status("Pending")
        today_orders = 0
        today_sales = 0.0
        monthly_sales = 0.0
        recent_orders = OrderModel.get_all_orders(limit=5)
    except RuntimeError:
        total_products = 0
        low_stock_products = 0
        total_customers = []
        pending_orders = 0
        today_orders = 0
        today_sales = 0.0
        monthly_sales = 0.0
        recent_orders = []

    return render_template(
        "admin/dashboard.html",
        total_products=total_products,
        low_stock_products=low_stock_products,
        total_customers=len(total_customers),
        pending_orders=pending_orders,
        today_orders=today_orders,
        today_sales=today_sales,
        monthly_sales=monthly_sales,
        recent_orders=recent_orders,
        top_products=ProductModel.get_top_selling_products(limit=5),
    )


@admin_bp.route("/products")
def products():
    result = staff_required()
    if result is not None:
        return result

    items = ProductModel.get_all_products(limit=25)
    return render_template("admin/products.html", products=items)


@admin_bp.route("/categories")
def categories():
    result = staff_required()
    if result is not None:
        return result

    items = CategoryModel.get_all_categories(limit=50)
    return render_template("admin/categories.html", categories=items)


@admin_bp.route("/inventory")
def inventory():
    result = staff_required()
    if result is not None:
        return result

    items = ProductModel.get_all_products(limit=200)
    return render_template("admin/inventory.html", inventory_items=items)


@admin_bp.route("/inventory/movements")
def inventory_movements():
    result = staff_required()
    if result is not None:
        return result

    return render_template("admin/inventory_movements.html")


@admin_bp.route("/suppliers")
def suppliers():
    result = staff_required()
    if result is not None:
        return result

    return render_template("admin/suppliers.html")


@admin_bp.route("/purchases")
def purchases():
    result = staff_required()
    if result is not None:
        return result

    return render_template("admin/purchases.html")


@admin_bp.route("/orders")
def orders():
    result = staff_required()
    if result is not None:
        return result

    status = request.args.get("status", "all")
    search = request.args.get("q", "")
    items = OrderModel.get_all_orders(status=status if status != "all" else None, search=search.strip() or None)
    return render_template("admin/orders.html", orders=items, status=status, q=search)


@admin_bp.route("/orders/<order_number>")
def order_detail(order_number):
    result = staff_required()
    if result is not None:
        return result

    order_detail = OrderModel.get_order_detail(order_number, None)
    if not order_detail:
        flash("Order not found.", "error")
        return redirect(url_for("admin.orders"))

    return render_template("admin/order_detail.html", order=order_detail["order"], items=order_detail["items"], payment=order_detail["payment"])


@admin_bp.route("/customers")
def customers():
    result = staff_required()
    if result is not None:
        return result

    users = UserModel.get_all_users(limit=200)
    return render_template("admin/customers.html", users=users)


@admin_bp.route("/reports")
def reports():
    result = staff_required()
    if result is not None:
        return result

    return render_template("admin/reports.html")
