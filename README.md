# BROOMERCE

BROOMERCE: A Web-Based E-Commerce and Inventory Management System for Broom Products.

## Project Purpose

BROOMERCE is a web-based e-commerce platform for a broom products business. The project is being developed in five phases to keep the architecture organized and easy to deploy.

## Current Completed Phases

PHASE 1:

- Foundation and application structure
- Flask configuration
- MySQL integration
- User authentication and sessions
- Login/signup screens
- Base customer layout

PHASE 2:

- Product catalog
- Categories
- Product details
- Search
- Filtering
- Sorting
- Responsive product UI

PHASE 3:

- Cart and cart summary logic
- Add to cart from product listing and detail pages
- Quantity updates and removal actions
- Checkout form and order summary
- Ready-to-place order handoff for future order processing

Future phases:

- PHASE 4: Orders + Order Tracking
- PHASE 5: Admin + Inventory + Reports + Final Deployment

## Technology Stack

- Python
- Flask
- MySQL
- Jinja2
- HTML5
- CSS3
- JavaScript
- mysql-connector-python
- python-dotenv

## Folder Structure

```text
Broomerce/
├── app.py
├── config.py
├── wsgi.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── database/
│   └── broomerce.sql
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py
│   ├── main_routes.py
│   └── product_routes.py
├── models/
│   ├── __init__.py
│   ├── user_model.py
│   ├── category_model.py
│   └── product_model.py
├── templates/
│   ├── base.html
│   ├── components/
│   │   ├── navbar.html
│   │   ├── footer.html
│   │   └── flash_messages.html
│   ├── auth/
│   │   ├── login.html
│   │   └── signup.html
│   ├── customer/
│   │   ├── home.html
│   │   ├── products.html
│   │   └── product_details.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
├── static/
│   ├── css/
│   │   ├── style.css
│   │   ├── auth.css
│   │   └── responsive.css
│   ├── js/
│   │   ├── main.js
│   │   └── auth.js
│   └── images/
│       ├── logo/
│       ├── products/
│       └── banners/
├── uploads/
│   └── products/
└── venv/
```

## Local Setup

### 1) Create a virtual environment

```bash
python -m venv venv
```

Activate it:

- Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

- Windows Command Prompt:

```cmd
venv\Scripts\activate.bat
```

- macOS/Linux:

```bash
source venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure environment variables

Copy the example file to `.env` and update values as needed:

```bash
copy .env.example .env
```

Example:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=change_this_secret_key
APP_HOST=0.0.0.0
APP_PORT=5000

DB_HOST=localhost
DB_PORT=3306
DB_NAME=broomerce
DB_USER=broomerce_user
DB_PASSWORD=your_local_mysql_password
```

## MySQL Setup

Create the database and import the schema file as a MySQL administrator. The app itself must keep reading `DB_USER` and `DB_PASSWORD` from `.env`.

```sql
CREATE DATABASE IF NOT EXISTS broomerce
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'broomerce_user'@'localhost' IDENTIFIED BY 'your_local_mysql_password';
GRANT ALL PRIVILEGES ON broomerce.* TO 'broomerce_user'@'localhost';
FLUSH PRIVILEGES;
```

Then import:

```bash
mysql -u root -p broomerce < database/broomerce.sql
```

If you use a GUI tool, import the file `database/broomerce.sql` manually.

### Update seeded products

After editing the product values in `database/broomerce.sql`, run this from the project folder in PowerShell to apply the product upsert to the database configured in `.env`:

```powershell
.\.venv\Scripts\python.exe -m database.update_products
```

Refresh the browser after the command completes.

For local development, `database/seed.sql` creates this admin account:

```text
Email: admin@broomerce.local
Password: Admin@123
```

Do not use these demo credentials in production.

> The actual password should never be committed to Git. Keep it in your local `.env` only.

## Run the Application

Local development:

```bash
python app.py
```

Production WSGI entry point:

```bash
gunicorn wsgi:app
```

Default local URL:

```text
http://127.0.0.1:5000/
```

## Current Routes

- `/` — customer home page
- `/login` — login page
- `/signup` — sign-up page
- `/logout` — logout action
- `/products` — product listing page
- `/products/<slug>` — product details page
- `/category/<category_id>` — category redirect
- `/cart` — shopping cart summary and item controls
- `/cart/add/<product_id>` — add product to cart
- `/checkout` — shipping details and order summary

## Deployment Readiness Notes

- The application uses environment variables for MySQL config and does not hardcode `root` or a local password in Python files.
- The database is organized for local development via `.env` and for production via platform environment variables.
- The schema includes the tables the current Flask app expects: `users`, `categories`, `products`, `inventory_movements`, `orders`, `order_items`, `payments`, `suppliers`, `purchases`, and `purchase_items`.
- MySQL imports should be run by an administrator; the runtime app uses `DB_USER`/`DB_PASSWORD` from `.env` and should not be changed to `root`.

This project has been structured to be deployment-friendly:

- no hardcoded credentials
- no Windows-specific paths in app logic
- static files use Flask URL generation
- configuration is stored in environment variables
- WSGI compatibility is prepared via `wsgi.py`

## Notes

This project uses environment variables to keep sensitive configuration out of source code and to keep the app ready for deployment later.
