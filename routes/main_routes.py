from flask import Blueprint, redirect, render_template, session, url_for

from models.category_model import CategoryModel
from models.product_model import ProductModel

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    try:
        categories = CategoryModel.get_active_categories(limit=5)
        featured_products = ProductModel.get_featured_products(limit=4)
    except RuntimeError:
        categories = []
        featured_products = []
    return render_template(
        "customer/home.html",
        categories=categories,
        featured_products=featured_products,
    )


@main_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("customer/home.html")
