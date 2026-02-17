import pandas as pd
from db.db_connection import get_connection


def run_query_df(query):

    conn = get_connection()

    cursor = conn.cursor()

    try:
        cursor.execute(query)

        rows = cursor.fetchall()

        # get column names
        columns = [desc[0] for desc in cursor.description]

        # convert to DataFrame
        df = pd.DataFrame(rows, columns=columns)

    finally:
        cursor.close()
        conn.close()

    return df


def get_all_orders_df():
    query = """
    SELECT *
    FROM orders
    ORDER BY order_date DESC
    """
    return run_query_df(query)


def get_returns_df():
    query = """
    SELECT *
    FROM meesho_returns
    ORDER BY created_at DESC
    """
    return run_query_df(query)


def get_claims_df():
    query = """
    SELECT *
    FROM claims
    ORDER BY created_at DESC
    """
    return run_query_df(query)


def get_orders_without_claims():
    query = """
    SELECT o.*
    FROM orders o
    LEFT JOIN claims c
    ON o.order_id::text = c.order_number::text
    WHERE c.order_number IS NULL
    """
    return run_query_df(query)


def get_returns_without_claims():
    query = """
    SELECT r.*
    FROM meesho_returns r
    LEFT JOIN claims c
    ON r.suborder_number::text = c.suborder_number::text
    WHERE c.suborder_number IS NULL
    """
    return run_query_df(query)


def get_claims_pending_refund():
    query = """
    SELECT *
    FROM claims
    WHERE COALESCE(ticket_status,'') != 'Refunded'
    """
    return run_query_df(query)


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

def get_all_claims():

    conn = get_connection()
    cursor = conn.cursor()
    query = """
    SELECT *
    FROM claims
    ORDER BY created_at DESC
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # convert fetched rows to list-of-dicts then DataFrame for proper columns
    try:
        df = pd.DataFrame([dict(r) for r in rows])
    except Exception:
        df = pd.DataFrame()
    return df