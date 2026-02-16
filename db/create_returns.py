from db.db_connection import get_connection
import pandas as pd


def insert_meesho_returns(df):

    conn = get_connection()
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO meesho_returns (
            suborder_number,
            sku,
            product_name,
            courier_partner,
            awb_number,
            return_status,
            return_reason,
            detailed_return_reason,
            return_created_date,
            qty
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (suborder_number) DO NOTHING
    """

    for _, row in df.iterrows():

        cursor.execute(insert_query, (

            row.get("Suborder Number"),

            row.get("SKU"),

            row.get("Product Name"),

            row.get("Courier Partner"),

            row.get("AWB Number"),

            row.get("Status"),

            row.get("Return Reason"),

            row.get("Detailed Return Reason"),

            row.get("Return Created Date"),

            row.get("Qty")

        ))

    conn.commit()

    cursor.close()
    conn.close()
