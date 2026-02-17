from db.db_connection import get_connection


def get_orders_without_claims():

    conn = get_connection()
    cursor = conn.cursor()

    query = """

    SELECT
        o.order_id,
        o.awb_number,
        o.company_name,
        o.courier_partner,
        o.sku_id,
        o.order_date,
        'No Claim' AS report_type

    FROM orders o

    LEFT JOIN claims c
        ON c.suborder_number = o.order_id

    WHERE c.suborder_number IS NULL

    ORDER BY o.order_date DESC NULLS LAST

    """

    cursor.execute(query)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [dict(row) for row in rows]



def get_returned_without_claims():

    conn = get_connection()
    cursor = conn.cursor()

    query = """

    SELECT
        r.suborder_number AS order_id,
        r.awb_number,
        r.courier_partner,
        r.return_created_date,
        'Returned but No Claim' AS report_type

    FROM meesho_returns r

    LEFT JOIN claims c
        ON c.suborder_number = r.suborder_number

    WHERE c.suborder_number IS NULL

    ORDER BY r.return_created_date DESC NULLS LAST

    """

    cursor.execute(query)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [dict(row) for row in rows]



def get_claims_not_approved():

    conn = get_connection()
    cursor = conn.cursor()

    query = """

    SELECT
        suborder_number AS order_id,
        ticket_id,
        ticket_status,
        created_date,
        'Claim Pending Approval' AS report_type

    FROM claims

    WHERE ticket_status NOT ILIKE '%approved%'
      AND ticket_status NOT ILIKE '%refund%'

    ORDER BY created_date DESC NULLS LAST

    """

    cursor.execute(query)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [dict(row) for row in rows]



def get_refund_pending():

    conn = get_connection()
    cursor = conn.cursor()

    query = """

    SELECT
        suborder_number AS order_id,
        ticket_id,
        ticket_status,
        created_date,
        'Refund Pending' AS report_type

    FROM claims

    WHERE ticket_status ILIKE '%approved%'
      AND ticket_status NOT ILIKE '%refund%'

    ORDER BY created_date DESC NULLS LAST

    """

    cursor.execute(query)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [dict(row) for row in rows]
