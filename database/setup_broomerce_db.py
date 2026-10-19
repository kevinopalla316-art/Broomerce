import os
from pathlib import Path

from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error


def split_sql_statements(sql_text):
    statements = []
    current = []
    in_single = False
    in_double = False

    for ch in sql_text:
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double

        current.append(ch)

        if ch == ";" and not in_single and not in_double:
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []

    tail = "".join(current).strip()
    if tail:
        statements.append(tail)

    return statements


def main():
    base_dir = Path(__file__).resolve().parents[1]
    load_dotenv(dotenv_path=base_dir / ".env")

    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "3306"))
    db_name = os.getenv("DB_NAME", "broomerce")
    app_user = os.getenv("DB_USER", "broomerce_user")
    app_password = os.getenv("DB_PASSWORD", "")
    root_password = os.getenv("DB_ROOT_PASSWORD", app_password)

    print("Database setup:")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Database: {db_name}")
    print(f"User: {app_user}")
    print("Password configured: %s" % ("YES" if app_password else "NO"))

    if not app_password:
        print("DB_PASSWORD is empty—set the local MySQL password in .env before continuing.")
        return 1

    try:
        admin_conn = mysql.connector.connect(
            host=host,
            port=port,
            user="root",
            password=root_password,
            autocommit=True,
            charset="utf8mb4",
            use_pure=True,
        )
    except Error as exc:
        print("Admin database connection: FAILED")
        print(f"Error: {type(exc).__name__}: {exc}")
        return 1

    cursor = admin_conn.cursor(dictionary=True)
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    admin_conn.database = db_name

    cursor.execute("SELECT 1 FROM mysql.user WHERE User = %s AND Host = 'localhost' LIMIT 1", (app_user,))
    if cursor.fetchone() is None:
        cursor.execute("CREATE USER %s@'localhost' IDENTIFIED BY %s", (app_user, app_password))
        print("Application user created: YES")
    else:
        cursor.execute("ALTER USER %s@'localhost' IDENTIFIED BY %s", (app_user, app_password))
        print("Application user updated: YES")

    cursor.execute(f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO %s@'localhost'", (app_user,))
    cursor.execute("FLUSH PRIVILEGES")

    schema_path = base_dir / "database" / "broomerce.sql"
    if not schema_path.exists():
        print(f"Schema file not found: {schema_path}")
        admin_conn.close()
        return 1

    sql_text = schema_path.read_text(encoding="utf-8")
    for statement in split_sql_statements(sql_text):
        if not statement.strip() or statement.strip().startswith("--"):
            continue
        if statement.strip().upper().startswith("CREATE DATABASE") or statement.strip().upper().startswith("USE "):
            continue
        cursor.execute(statement)

    seed_path = base_dir / "database" / "seed.sql"
    if seed_path.exists():
        seed_text = seed_path.read_text(encoding="utf-8")
        for statement in split_sql_statements(seed_text):
            if not statement.strip() or statement.strip().startswith("--"):
                continue
            if statement.strip().upper().startswith("USE "):
                continue
            cursor.execute(statement)

    admin_conn.close()
    print("Database repair: COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
