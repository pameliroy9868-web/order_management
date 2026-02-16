from db.db_connection import get_connection


def get_order_status(search_value):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT * FROM (

    SELECT
        order_id,
        awb_number,
        'Ordered' as status,
        order_date as event_date
    FROM orders
    WHERE order_id ILIKE %s OR awb_number ILIKE %s

    UNION ALL

    SELECT
        suborder_number as order_id,
        awb_number,
        return_status as status,
        return_created_date as event_date
    FROM meesho_returns
    WHERE suborder_number ILIKE %s OR awb_number ILIKE %s

    ) AS combined

    ORDER BY COALESCE(event_date, '1900-01-01') ASC

    """

    like = f"%{search_value}%"

    params = (like, like, like, like)

    # Print raw query with values substituted
    raw_query = cursor.mogrify(query, params).decode("utf-8")

    # print("\n===== EXECUTING RAW SQL =====")
    # print(raw_query)
    # print("=============================\n")

    cursor.execute(query, params)


    rows = cursor.fetchall()
    results = [dict(row) for row in rows]

    # Filter out header-like rows where every value equals the column name
    filtered_results = []
    for r in results:
        try:
            # skip header-like rows
            if all(str(v).strip().lower() == k.strip().lower() for k, v in r.items()):
                continue

            # FIX NULL event_date
            if r.get("event_date") is None:
                r["event_date"] = "1900-01-01"
        except Exception:
            pass
        
        filtered_results.append(r)

    cursor.close()
    conn.close()

    return filtered_results
