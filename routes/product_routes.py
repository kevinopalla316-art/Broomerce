from flask import Blueprint, flash, redirect, render_template, request, url_for

from models.category_model import CategoryModel
from models.product_model import ProductModel

product_bp = Blueprint("products", __name__)


@product_bp.route("/products")
@product_bp.route("/products/")
def products():
    search_term = request.args.get("q", "").strip()
    category_id = request.args.get("category", type=int)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    sort = request.args.get("sort", "featured")
    page = max(request.args.get("page", 1, type=int), 1)

    try:
        categories = CategoryModel.get_active_categories()
    except RuntimeError:
        categories = []
        flash("The product catalog is currently unavailable.", "error")

    try:
        total_products = ProductModel.count_products(
            search_term=search_term,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
        )
        page_size = 12
        offset = (page - 1) * page_size
        products_list = ProductModel.search_products(
            search_term=search_term,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            sort=sort,
            limit=page_size,
            offset=offset,
        )
        total_pages = max((total_products + page_size - 1) // page_size, 1)
    except RuntimeError:
        products_list = []
        total_products = 0
        total_pages = 1
        flash("The product catalog is currently unavailable.", "error")

    return render_template(
        "customer/products.html",
        products=products_list,
        categories=categories,
        active_category_id=category_id,
        search_term=search_term,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        page=page,
        total_pages=total_pages,
        total_products=total_products,
    )


@product_bp.route("/category/<int:category_id>")
def category_products(category_id):
    category = CategoryModel.get_category_by_id(category_id)
    if not category:
        return redirect(url_for("products.products"))

    return redirect(url_for("products.products", category=category_id))


@product_bp.route("/products/<slug>")
def product_details(slug):
    try:
        product = ProductModel.get_product_by_slug(slug)
    except RuntimeError:
        flash("The product catalog is currently unavailable.", "error")
        return render_template("errors/404.html"), 404

    if not product:
        return render_template("errors/404.html"), 404

    try:
        related_products = ProductModel.get_products_by_category(product["category_id"], limit=3)
    except RuntimeError:
        related_products = []

    return render_template(
        "customer/product_details.html",
        product=product,
        related_products=related_products,
    )
