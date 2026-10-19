from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.user_model import UserModel

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.args.get("next") or request.form.get("next")
    if next_url and next_url.startswith("/") and not next_url.startswith("//"):
        session["redirect_after_login"] = next_url
    else:
        session.pop("redirect_after_login", None)

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please complete all required fields.", "error")
            return render_template("auth/login.html")

        try:    
            user = UserModel.verify_login(email, password)
        except RuntimeError as exc:
            flash(str(exc), "error")
            return render_template("auth/login.html")

        if user is None:
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html")

        session["user_id"] = user["id"]
        session["user_name"] = f"{user['first_name']} {user['last_name']}".strip()
        session["user_role"] = user["role"]
        flash("Login successful. Welcome back!", "success")

        target = session.pop("redirect_after_login", None)
        if user["role"] in {"admin", "staff"}:
            return redirect(target or url_for("admin.dashboard"))
        return redirect(target or url_for("main.home"))

    return render_template("auth/login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not first_name or not last_name or not email or not phone or not password or not confirm_password:
            flash("Please complete all required fields.", "error")
            return render_template("auth/signup.html")

        if "@" not in email or "." not in email:
            flash("Please enter a valid email address.", "error")
            return render_template("auth/signup.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("auth/signup.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("auth/signup.html")

        try:
            existing = UserModel.find_by_email(email)
            if existing:
                flash("An account with this email already exists.", "error")
                return render_template("auth/signup.html")

            UserModel.create_user(first_name, last_name, email, phone, password)
            flash("Account created successfully. Welcome to BROOMERCE!", "success")
            return redirect(url_for("auth.login"))
        except RuntimeError as exc:
            flash(str(exc), "error")
            return render_template("auth/signup.html")
        except Exception:
            flash("Unable to create account right now. Please try again later.", "error")
            return render_template("auth/signup.html")

    return render_template("auth/signup.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
