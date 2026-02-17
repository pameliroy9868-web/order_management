import streamlit as st
import pandas as pd
# try:
#     import plotly.express as px
# except Exception:
    # px = None
    # Plotly unavailable; GUI will show a warning when attempting to plot
from scan_orders.extract_pdf import extract_orders
from db.db import save_to_db, get_all_orders, change_order_status
from db.search_orders import search_all_orders
from db.create_returns import insert_meesho_returns
from db.order_status import get_order_status
#from utils.status_tracker import show_status_tracker
from utils.journey_tracker import show_journey_tracker
from utils.csv import *

st.set_page_config(page_title="Order Management System", layout="wide")

# -----------------------
# Horizontal Navigation Menu
# -----------------------
menu_choice = st.radio(
    "Menu",
    ("Home", "Scan Orders", "Search Orders", "Change Status","Return Upload",  "Order Status",  "Upload Claims", "Reports"),
    horizontal=True
)

# -----------------------
# Home Page
# -----------------------
if menu_choice == "Home":
    st.title("📦 Order Management System")
    st.write("""
        Welcome to the Order Management System! This app allows you to:
        - Scan order PDFs and extract order details.
        - Edit extracted orders before saving them to PostgreSQL.
        - Search and filter orders by Company Name, Order ID, Courier, or SKU.
        - Update order status and track the full history of each order.

        Use the menu above to navigate:
        1. **Scan Orders** – Upload PDFs and edit order details.
        2. **Search Orders** – View and filter all saved orders.
        3. **Change Status** – Update the status of an order and see its full status history.
    """)

    st.info("Get started by selecting a tab from the menu above.")
    st.image("https://cdn-icons-png.flaticon.com/512/2910/2910767.png", width=150)

# -----------------------
# Scan Orders Page
# -----------------------
elif menu_choice == "Scan Orders":
    st.title("Scan Orders")

    uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

    if uploaded_file is not None:
        st.info("Extracting data from PDF...")
        extracted_data = extract_orders(uploaded_file)
        if extracted_data:
            st.success("Data extracted successfully!")

            # Convert to DataFrame
            df = pd.DataFrame(extracted_data)

            st.subheader("Edit Orders Before Saving")
            edited_df = st.data_editor(df, num_rows="dynamic")

            if st.button("Save to Database"):
                save_to_db(edited_df.to_dict(orient="records"))
                st.success("Data saved to PostgreSQL!")
        else:
            st.warning("No orders found in the PDF.")

# -----------------------
# Search Orders Page
# -----------------------
elif menu_choice == "Search Orders":

    st.title("Search Orders")

    # Use in-memory list by default; database search will be triggered
    # when the user fills the existing "Order ID" filter below.
    orders = get_all_orders()

    # import pdb; pdb.set_trace()  # Debug: check the structure of `orders` right after fetching from DB

    if orders:

        df_orders = pd.DataFrame(orders)

        # Fill missing values
        df_orders = df_orders.fillna("")

        st.subheader("All Orders")

        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            company_filter = st.text_input("Company")

        with col2:
            order_id_filter = st.text_input("Order ID")

        # If user enters an Order ID, perform a DB-backed search to include
        # orders/returns/claims that may not be present in the in-memory list.
        if order_id_filter:
            orders = search_all_orders(order_id_filter)
            # replace the dataframe source with DB search results so downstream
            # filters operate on the returned rows
            df_orders = pd.DataFrame(orders)

        with col3:
            courier_filter = st.text_input("Courier")

        col4, col5 = st.columns(2)

        with col4:
            sku_filter = st.text_input("SKU")

        with col5:
            status_filter = st.selectbox(
                "Status",
                ["", "Ordered", "Shipped", "Delivered", "Returned", "Claim Submitted", "Claim Approved", "Refund Completed"]
            )


        filtered_df = df_orders.copy()

        

        if company_filter:
            filtered_df = filtered_df[
                filtered_df['company_name'].str.contains(company_filter, case=False)
            ]

        if order_id_filter:
            filtered_df = filtered_df[
                filtered_df['order_id'].str.contains(order_id_filter, case=False)
            ]

        if courier_filter:
            filtered_df = filtered_df[
                filtered_df['courier_partner'].str.contains(courier_filter, case=False)
            ]

        if sku_filter:
            filtered_df = filtered_df[
                filtered_df['sku_id'].str.contains(sku_filter, case=False)
            ]

        if status_filter:
            filtered_df = filtered_df[
                filtered_df['status'] == status_filter
            ]

        filtered_df = filtered_df.fillna("")

        if "event_date" in filtered_df.columns:
            filtered_df = filtered_df.sort_values("event_date", ascending=False)

        # Sort newest first
        # filtered_df = filtered_df.sort_values("event_date", ascending=False)


        # Editable table
        edited_df = st.data_editor(
            filtered_df,
            width='stretch',
            num_rows="dynamic"
        )


        # Save button
        if st.button("Save Changes"):

            save_to_db(edited_df.to_dict("records"))

            st.success("Changes saved successfully!")

    else:

        st.warning("No orders found")

# -----------------------
# Change Status Page
# -----------------------
elif menu_choice == "Change Status":
    st.title("Change Order Status")

    order_id_input = st.text_input("Enter Order ID to update status")

    if order_id_input:
        # Fetch all orders for this ID
        orders = get_all_orders()
        df_orders = pd.DataFrame(orders)

        # Ensure order_id exists
        if order_id_input not in df_orders['order_id'].values:
            st.warning(f"No orders found with Order ID: {order_id_input}")
        else:
            # Get latest row (max order_sequence) for this order_id
            latest_row = df_orders[df_orders['order_id'] == order_id_input].sort_values(
                "order_sequence", ascending=False
            ).iloc[0]

            st.subheader("Latest Order Details")
            st.dataframe(latest_row.to_frame().T)  # show as table

            new_status = st.selectbox("Select New Status", ["Picked Up", "In Transit", "Delivered", "Cancelled"])

            if st.button("Update Status"):
                change_order_status(order_id_input, new_status)
                st.success(f"Status updated for Order ID {order_id_input}!")

                # Show full history after update
                updated_orders = get_all_orders()
                df_updated = pd.DataFrame(updated_orders)
                history_df = df_updated[df_updated['order_id'] == order_id_input].sort_values(
                    "order_sequence"
                )
                st.subheader("Order Status History")
                st.dataframe(history_df)

elif menu_choice == "Return Upload":
    st.header("Upload Returns CSV")
    uploaded_file = st.file_uploader("Upload Returns CSV", type=["csv"])
    if uploaded_file:
        df = read_meesho_returns_csv(uploaded_file)
        st.dataframe(df)

        if st.button("Insert into Database"):
            insert_meesho_returns(df)
            st.success("Returns inserted successfully")
elif menu_choice == "Order Status":
    st.header("Order Journey Tracker")

    search_value = st.text_input("Enter Order ID or AWB")

    if st.button("Track Order"):

        results = get_order_status(search_value)
        # Debug: show raw results in the Streamlit UI to avoid relying on terminal logs
        # st.subheader("Raw results from get_order_status")
        # st.write(results)

        if results:

            df = pd.DataFrame(results)

            # Robust parsing of `event_date`: normalize, coerce invalid values, and drop them
            if "event_date" not in df.columns:
                st.warning("Results do not contain an `event_date` column; timeline unavailable.")
                # proceed to show raw results below instead of stopping the script
                df = pd.DataFrame(results)
                has_dates = False
            else:
                has_dates = True

            df["event_date"] = df["event_date"].astype(str).str.strip()
            df.loc[df["event_date"].str.lower() == "event_date", "event_date"] = pd.NA

            df["event_date"] = pd.to_datetime(
                df["event_date"], errors="coerce", infer_datetime_format=True
            )

            df = df.dropna(subset=["event_date"])

            if df.empty:
                st.warning("No valid event dates found for this order; cannot show timeline or status history.")
                has_dates = False
            else:
                df = df.sort_values("event_date")
                latest_status = df.iloc[-1]["status"]

            # Ensure we have a latest_status to render the journey tracker even when dates are missing
            if not has_dates:
                if results and isinstance(results, list) and len(results) > 0:
                    latest_status = results[-1].get("status")
                else:
                    latest_status = None

            if latest_status:
                show_journey_tracker(latest_status)
                st.divider()

                # # SHOW STATUS BADGE
                # if latest_status == "Delivered":
                #     st.success("Delivered")

                # elif latest_status == "Returned":
                #     st.error("Returned")

            st.divider()

            # # SHOW STATUS BADGE
            # if latest_status == "Delivered":
            #     st.success("Delivered")

            # elif latest_status == "Returned":
            #     st.error("Returned")

            # elif "Claim" in latest_status:
            #     st.warning(latest_status)

            # else:
            #     st.info(latest_status)


            # st.divider()

            # # TIMELINE GRAPH
            # if px is None:
            #     st.warning("Plotly is not installed. Install with `pip install plotly` to see the timeline chart.")
            # else:
            #     fig = px.scatter(
            #         df,
            #         x="event_date",
            #         y="status",
            #         title="Order Journey Timeline",
            #         size_max=15
            #     )

            #     st.plotly_chart(fig, use_container_width=True)

            # st.divider()

            # st.subheader("Full Order History")

            # Hide None/NaN in UI and ensure AWB stays as string
            df_display = df.fillna("").astype(str)
            st.dataframe(df_display, width='stretch')

        else:

            st.warning("No order found")

elif menu_choice == "Upload Claims":

    st.title("Upload Claims CSV")

    uploaded_file = st.file_uploader(
        "Upload Claims Report",
        type=["csv"]
    )

    if uploaded_file:

        from utils.claims_csv import read_claims_csv
        from db.insert_claims import insert_claims

        records = read_claims_csv(uploaded_file)

        # Convert to DataFrame for clean table preview
        df_preview = pd.DataFrame(records).fillna("")

        # Cast to string to prevent pandas from converting long numeric-like AWB to floats/ints
        df_preview = df_preview.astype(str)

        st.subheader("Preview")

        st.dataframe(
            df_preview,
            width='stretch'
        )

        if st.button("Insert Claims"):

            insert_claims(records)

            st.success(f"{len(records)} claims inserted successfully")
elif menu_choice == "Reports":

    import pandas as pd

    from db.reports import (
        get_orders_without_claims,
        get_returned_without_claims,
        get_claims_not_approved,
        get_refund_pending
    )

    st.title("Reports Dashboard")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Orders without Claims",
        "Returned without Claims",
        "Claims Pending Approval",
        "Refund Pending"
    ])


    with tab1:

        data = get_orders_without_claims()

        df = pd.DataFrame(data).fillna("")

        st.dataframe(df, width="stretch")

        st.info(f"{len(df)} orders without claims")


    with tab2:

        data = get_returned_without_claims()

        df = pd.DataFrame(data).fillna("")

        st.dataframe(df, width="stretch")

        st.warning(f"{len(df)} returned orders without claims")


    with tab3:

        data = get_claims_not_approved()

        df = pd.DataFrame(data).fillna("")

        st.dataframe(df, width="stretch")

        st.warning(f"{len(df)} claims pending approval")


    with tab4:

        data = get_refund_pending()

        df = pd.DataFrame(data).fillna("")

        st.dataframe(df, width="stretch")

        st.warning(f"{len(df)} refunds pending")
