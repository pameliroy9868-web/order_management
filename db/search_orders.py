from db.connection import get_connection


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

    ORDER BY order_id

    """

    like_value = f"%{search_value}%"

    cursor.execute(query, (

        like_value, like_value, like_value,
        like_value, like_value, like_value

    ))

    columns = [col[0] for col in cursor.description]

    results = [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return results
