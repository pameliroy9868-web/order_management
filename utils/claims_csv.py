import pandas as pd


def read_claims_csv(uploaded_file):

    # Read important ID-like columns as strings to preserve formatting (prevent scientific notation)
    df = pd.read_csv(
        uploaded_file,
        engine="python",
        dtype={
            "Order Number": str,
            "Suborder Number": str,
            "Ticket ID": str,
            "Meesho PID": str,
            "SKU": str,
        },
    )
    

    df = df.rename(columns={
        "Suborder Number": "suborder_number",
        "Order Number": "order_number",
        "Ticket ID": "ticket_id",
        "Ticket Status": "ticket_status",
        "Created Date": "created_date",
        "Issue": "issue",
        "Product Name": "product_name",
        "SKU": "sku",
        "Variation": "variation",
        "Qty": "qty",
        "Meesho PID": "meesho_pid",
        "Last Update": "last_update",
        "Reopen Validity": "reopen_validity",
        "CPP Flag": "cpp_flag"
    })

    # Ensure ID-like columns are strings and stripped of whitespace
    if "ticket_id" in df.columns:
        df["ticket_id"] = df["ticket_id"].fillna("").astype(str).str.strip()
    if "order_number" in df.columns:
        df["order_number"] = df["order_number"].fillna("").astype(str).str.strip()
    if "suborder_number" in df.columns:
        df["suborder_number"] = df["suborder_number"].fillna("").astype(str).str.strip()

    # Normalize meesho_pid: fill missing, strip whitespace, and convert 'nan'/'none' to empty
    if "meesho_pid" in df.columns:
        df["meesho_pid"] = df["meesho_pid"].fillna("").astype(str).str.strip()
        df.loc[df["meesho_pid"].str.lower().isin(["nan", "none", "none."]), "meesho_pid"] = ""

    # Fix qty column
    if "qty" in df.columns:
        df["qty"] = pd.to_numeric(df["qty"], errors="coerce")

    # Replace NaN with None (important for PostgreSQL)
    df = df.where(pd.notnull(df), None)

    return df.to_dict("records")
