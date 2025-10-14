import streamlit as st
import pandas as pd
from scan_orders.extract_pdf import extract_orders
from db.db import save_to_db, get_all_orders, change_order_status

st.set_page_config(page_title="Order Management System", layout="wide")

# -----------------------
# Horizontal Navigation Menu
# -----------------------
menu_choice = st.radio(
    "Menu",
    ("Home", "Scan Orders", "Search Orders", "Change Status"),
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

    orders = get_all_orders()
    
    if orders:
        df_orders = pd.DataFrame(orders)

        # Fill missing columns and NaNs
        for col in ["company_name", "order_id", "courier_partner", "sku_id", "status"]:
            if col not in df_orders.columns:
                df_orders[col] = ""
            else:
                df_orders[col] = df_orders[col].fillna("")

        st.subheader("All Orders")

        # Filtering widgets
        company_filter = st.text_input("Filter by Company Name")
        order_id_filter = st.text_input("Filter by Order ID")
        courier_filter = st.text_input("Filter by Courier Partner")
        sku_filter = st.text_input("Filter by SKU ID")
        status_filter = st.text_input("Filter by Status")

        filtered_df = df_orders.copy()
        if company_filter:
            filtered_df = filtered_df[filtered_df['company_name'].str.contains(company_filter, case=False, na=False)]
        if order_id_filter:
            filtered_df = filtered_df[filtered_df['order_id'].str.contains(order_id_filter, case=False, na=False)]
        if courier_filter:
            filtered_df = filtered_df[filtered_df['courier_partner'].str.contains(courier_filter, case=False, na=False)]
        if sku_filter:
            filtered_df = filtered_df[filtered_df['sku_id'].str.contains(sku_filter, case=False, na=False)]
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].str.contains(status_filter, case=False, na=False)]

        # Editable table
        edited_df = st.data_editor(filtered_df, num_rows="dynamic")

        # Save changes
        if st.button("Save Changes"):
            save_to_db(edited_df.to_dict(orient="records"))
            st.success("Changes saved successfully!")

    else:
        st.warning("No orders found in the database.")

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
