import pandas as pd
import zipfile
from db.db_connection import get_connection


# ============================================================
# EXTRACT PAYMENTS
# ============================================================

def extract_payments_df(zip_file):

    with zipfile.ZipFile(zip_file, 'r') as z:

        file_name = z.namelist()[0]

        with z.open(file_name) as excel_file:

            df_raw = pd.read_excel(
                excel_file,
                sheet_name="Order Payments",
                header=None,
                engine="openpyxl"
            )

    # Combine row 0 and row 1 to create headers
    header = (
        df_raw.iloc[0].fillna('').astype(str)
        + " "
        + df_raw.iloc[1].fillna('').astype(str)
    ).str.strip()

    df = df_raw[2:].copy()
    df.columns = header

    # Use correct columns from your file
    order_col = "Order Related Details Sub Order No"
    status_col = "Live Order Status"
    payment_date_col = "Payment Details Payment Date"
    amount_col = "Final Settlement Amount"

    clean_df = pd.DataFrame()

    clean_df["order_id"] = df[order_col]

    clean_df["raw_status"] = df[status_col] if status_col in df.columns else None

    clean_df["payment_date"] = (
        pd.to_datetime(df[payment_date_col], errors="coerce")
        if payment_date_col in df.columns
        else None
    )

    clean_df["amount"] = (
        pd.to_numeric(df[amount_col], errors="coerce")
        if amount_col in df.columns
        else None
    )

    clean_df = clean_df.dropna(subset=["order_id"])

    return clean_df


# ============================================================
# INSERT INTO DATABASE
# ============================================================

def insert_payments_from_zip(zip_file):

    df = extract_payments_df(zip_file)

    conn = get_connection()
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO payments_upload
        (
            order_id,
            payment_reference,
            amount,
            payment_date,
            raw_status,
            settlement_status
        )
        VALUES (%s, %s, %s, %s, %s, 'PENDING')
    """

    for _, row in df.iterrows():

        order_id = str(row["order_id"]).strip()

        if order_id.lower() == "nan":
            continue

        amount = (
            float(row["amount"])
            if pd.notna(row["amount"])
            else None
        )

        payment_date = (
            row["payment_date"]
            if pd.notna(row["payment_date"])
            else None
        )

        raw_status = (
            str(row["raw_status"])
            if pd.notna(row["raw_status"])
            else None
        )

        cursor.execute(
            insert_query,
            (
                order_id,
                None,
                amount,
                payment_date,
                raw_status
            )
        )

    conn.commit()

    update_settlement_status(cursor)

    conn.commit()

    cursor.close()
    conn.close()


# ============================================================
# UPDATE SETTLEMENT STATUS
# ============================================================

def update_settlement_status(cursor):

    cursor.execute("""

        UPDATE payments_upload p

        SET
            settlement_status = 'SETTLED',
            settlement_date =
                CAST(NULLIF(TRIM(c.last_update),'') AS TIMESTAMP)

        FROM claims c

        WHERE p.order_id::text = c.suborder_number::text

        AND LOWER(c.ticket_status) = 'approved'

        AND c.last_update IS NOT NULL

        AND TRIM(c.last_update) <> ''

    """)
