from db.db_connection import get_connection


def get_order_status(search_value):

    conn = get_connection()
    cursor = conn.cursor()

    query = """

    WITH combined AS (

        -- ORDERED
        SELECT
            order_id,
            awb_number,
            'Ordered' AS status,
            COALESCE(order_date::text, '1900-01-01') AS event_date
        FROM orders


        UNION ALL


        -- RETURNED
        SELECT
            suborder_number AS order_id,
            awb_number,
            'Returned' AS status,
            COALESCE(return_created_date::text, '1900-01-01') AS event_date
        FROM meesho_returns


        UNION ALL


        -- CLAIM SUBMITTED
        SELECT
            suborder_number AS order_id,
            NULL AS awb_number,
            'Claim Submitted' AS status,
            COALESCE(
                NULLIF(created_date::text, ''),
                '1900-01-01'
            ) AS event_date
        FROM claims


        UNION ALL


        -- CLAIM APPROVED
        SELECT
            suborder_number AS order_id,
            NULL AS awb_number,
            'Claim Approved' AS status,
            COALESCE(
                NULLIF(created_date::text, ''),
                '1900-01-01'
            ) AS event_date
        FROM claims
        WHERE ticket_status ILIKE '%%approved%%'


        UNION ALL


        -- REFUND COMPLETED
        SELECT
            suborder_number AS order_id,
            NULL AS awb_number,
            'Refund Completed' AS status,
            COALESCE(
                NULLIF(created_date::text, ''),
                '1900-01-01'
            ) AS event_date
        FROM claims
        WHERE ticket_status ILIKE '%%refund%%'

    )


    SELECT
        order_id,
        awb_number,
        status,
        event_date
    FROM combined

    WHERE
        order_id ILIKE %s
        OR COALESCE(awb_number,'') ILIKE %s

    ORDER BY event_date ASC

    """

    like = f"%{search_value}%"

    cursor.execute(query, (like, like))

    rows = cursor.fetchall()

    results = [dict(row) for row in rows]

    cursor.close()
    conn.close()

    return results
