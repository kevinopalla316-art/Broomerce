from pathlib import Path

from database.setup_broomerce_db import split_sql_statements
from models.product_model import ProductModel


def main():
    project_dir = Path(__file__).resolve().parents[1]
    schema_path = project_dir / "database" / "broomerce.sql"
    sql_text = schema_path.read_text(encoding="utf-8")
    product_statement = next(
        (
            statement
            for statement in split_sql_statements(sql_text)
            if statement.lstrip().upper().startswith("INSERT INTO PRODUCTS")
        ),
        None,
    )

    if product_statement is None:
        print(f"Product INSERT statement not found in {schema_path}")
        return 1

    connection = None
    cursor = None
    try:
        connection = ProductModel.get_db_connection()
        cursor = connection.cursor()
        cursor.execute(product_statement)
        print(f"Product sync complete ({cursor.rowcount} row changes).")
        return 0
    except Exception as exc:
        print(f"Product sync failed: {exc}")
        return 1
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    raise SystemExit(main())