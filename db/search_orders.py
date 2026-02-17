from db.db_connection import get_connection


def search_all_orders(search_value):

    conn = get_connection()
    cursor = conn.cursor()

    query = """

    SELECT
        'ORDER' as source,
        order_id,
        sku_id as sku,
        awb_number,
        courier_partner,
        order_date,
        invoice_date,
        NULL as return_status,
        NULL as return_reason
    FROM orders
    WHERE
        order_id ILIKE %s
        OR awb_number ILIKE %s
        OR sku_id ILIKE %s


    UNION ALL


    SELECT
        'RETURN' as source,
        suborder_number as order_id,
        sku,
        awb_number,
        courier_partner,
        NULL as order_date,
        NULL as invoice_date,
        return_status,
        return_reason
    FROM meesho_returns
    WHERE
        suborder_number ILIKE %s
        OR awb_number ILIKE %s
        OR sku ILIKE %s


    UNION ALL

    SELECT
        'CLAIM' as source,
        order_number as order_id,
        sku,
        NULL as awb_number,
        NULL as courier_partner,
        created_date as order_date,
        NULL as invoice_date,
        ticket_status as return_status,
        issue as return_reason
    FROM claims
    WHERE
        order_number ILIKE %s
        OR suborder_number ILIKE %s
        OR sku ILIKE %s

    ORDER BY order_id

    """

    like_value = f"%{search_value}%"

    cursor.execute(query, (

        like_value, like_value, like_value,
        like_value, like_value, like_value,
        like_value, like_value, like_value

    ))

    # columns = [col[0] for col in cursor.description]

    rows = cursor.fetchall()
    # results = [
    #     dict(zip(columns, row))
    #     for row in cursor.fetchall()
    # ]
    results = [dict(row) for row in rows]

    print(f"Search for '{search_value}' returned {len(results)} results.")

    cursor.close()
    conn.close()

    return results
