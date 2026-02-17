import pandas as pd
from psycopg2.extras import execute_values, RealDictCursor
from db.db_connection import get_connection

# -----------------------
# Save orders to DB
# -----------------------
def save_to_db(data):
    conn = get_connection()
    cursor = conn.cursor()

    columns = [
        "courier_partner", "company_name", "tax_invoice_no", "invoice_date", "order_date",
        "awb_number", "order_id", "sku_id", "qty", "hsn", "gross_amount", "discount",
        "taxable_amount", "total_other_charges", "order_sequence", "status"
    ]

    values = []
    for order in data:
        row = []
        for col in columns:
            val = order.get(col, None)

            # Convert empty strings or invalid values to None
            if val in ["", None, "NaT"]:
                val = None

            # Convert date fields
            if col in ["order_date", "invoice_date"] and val is not None:
                val = pd.to_datetime(val, errors='coerce')
                if pd.isna(val):
                    val = None
                else:
                    val = val.date()

            # Convert numeric fields
            if col in ["qty", "gross_amount", "discount", "taxable_amount", "total_other_charges"]:
                try:
                    val = float(val) if val is not None else None
                except:
                    val = None

            row.append(val)
        values.append(tuple(row))

    query = f"""
        INSERT INTO orders ({', '.join(columns)})
        VALUES %s
    """
    execute_values(cursor, query, values)
    conn.commit()
    cursor.close()
    conn.close()


# -----------------------
# Fetch all orders
# -----------------------
def get_all_orders():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM orders ORDER BY order_id, order_sequence")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    return df  # list of dictionaries


# -----------------------
# Change order status (duplicates row with incremented sequence)
# -----------------------
def change_order_status(order_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE order_id=%s ORDER BY order_sequence DESC LIMIT 1", (order_id,))
    latest_row = cursor.fetchone()

    if latest_row is None:
        seq = 1
        # Insert a default row if order_id is new
        cursor.execute("""
        INSERT INTO orders (order_id, order_sequence, status)
        VALUES (%s, %s, %s)
    """, (order_id, seq, new_status))

    else:
        # Existing order, get latest sequence safely
        latest_seq = latest_row['order_sequence'] if latest_row['order_sequence'] is not None else 0
        seq = latest_seq + 1

        # Duplicate row with incremented sequence and new status
        cursor.execute("""
            INSERT INTO orders (
                courier_partner, company_name, tax_invoice_no, invoice_date, order_date,
                awb_number, order_id, sku_id, qty, hsn, gross_amount, discount, taxable_amount,
                total_other_charges, order_sequence, status
            )
            SELECT
                courier_partner, company_name, tax_invoice_no, invoice_date, order_date,
                awb_number, order_id, sku_id, qty, hsn, gross_amount, discount, taxable_amount,
                total_other_charges, %s, %s
            FROM orders
            WHERE order_id=%s
            ORDER BY order_sequence DESC
            LIMIT 1
        """, (seq, new_status, order_id))

    conn.commit()
    cursor.close()
    conn.close()