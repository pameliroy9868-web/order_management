from db.db_connection import get_connection


def insert_claims(records):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO claims (

        suborder_number,
        order_number,
        ticket_id,
        ticket_status,
        created_date,
        issue,
        product_name,
        sku,
        variation,
        qty,
        meesho_pid,
        last_update,
        reopen_validity,
        cpp_flag

    )
    VALUES (

        %(suborder_number)s,
        %(order_number)s,
        %(ticket_id)s,
        %(ticket_status)s,
        %(created_date)s,
        %(issue)s,
        %(product_name)s,
        %(sku)s,
        %(variation)s,
        %(qty)s,
        %(meesho_pid)s,
        %(last_update)s,
        %(reopen_validity)s,
        %(cpp_flag)s

    )
    ON CONFLICT (ticket_id) DO NOTHING
    """

    # Sanitize and coerce numeric fields to avoid integer overflow errors
    sanitized = []
    INT32_MAX = 2_147_483_647
    for r in records:
        rec = dict(r)  # copy
        # Normalize qty: allow None/empty -> NULL, coerce to int, cap to INT32 range
        qty = rec.get("qty")
        if qty is None or (isinstance(qty, str) and qty.strip() == ""):
            rec["qty"] = None
        else:
            try:
                q = int(float(qty))
                if q > INT32_MAX:
                    q = INT32_MAX
                if q < -INT32_MAX - 1:
                    q = -INT32_MAX - 1
                rec["qty"] = q
            except Exception:
                rec["qty"] = None

        sanitized.append(rec)

    cursor.executemany(query, sanitized)

    conn.commit()

    cursor.close()
    conn.close()
