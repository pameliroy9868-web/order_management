from db.db_connection import get_connection


def get_all_orders():

    conn = get_connection()
    cursor = conn.cursor()

    query = """

    WITH combined AS (

        SELECT
            order_id,
            awb_number,
            company_name,
            courier_partner,
            sku_id,
            'Ordered' AS status,
            COALESCE(order_date, DATE '1900-01-01') AS event_date
        FROM orders

        UNION ALL

        SELECT
            suborder_number AS order_id,
            awb_number,
            '' AS company_name,
            courier_partner,
            sku AS sku_id,
            return_status AS status,
            COALESCE(return_created_date, DATE '1900-01-01') AS event_date
        FROM meesho_returns

        UNION ALL

        SELECT
        suborder_number AS order_id,
        NULL AS awb_number,
        ticket_status AS status,
        created_date AS event_date
        FROM claims

    ),

    latest AS (

        SELECT DISTINCT ON (order_id, COALESCE(awb_number,''))
            order_id,
            awb_number,
            company_name,
            courier_partner,
            sku_id,
            status,
            event_date
        FROM combined
        ORDER BY order_id, COALESCE(awb_number,''), event_date DESC

    )

    SELECT *
    FROM latest
    ORDER BY event_date DESC

    """

    cursor.execute(query)

    rows = cursor.fetchall()

    results = [dict(row) for row in rows]

    cursor.close()
    conn.close()

    return results