import streamlit as st
import pandas as pd
import plotly.express as px

# your existing imports
from scan_orders.extract_pdf import extract_orders
from db.db import save_to_db, get_all_orders, change_order_status
from db.search_orders import search_all_orders
from db.create_returns import insert_meesho_returns
from db.insert_claims import insert_claims
from utils.claims_csv import read_claims_csv
from utils.csv import read_meesho_returns_csv


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Order Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>

/* metric card container */
[data-testid="metric-container"] {
    background-color: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* metric label */
[data-testid="metric-container"] label {
    color: #555555 !important;
    font-weight: 600;
}

/* metric value */
[data-testid="metric-container"] div {
    color: #000000 !important;
    font-size: 28px !important;
    font-weight: bold;
}

/* metric delta */
[data-testid="metric-container"] span {
    color: #16a34a !important;
}

</style>
""", unsafe_allow_html=True)




# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("📦 Order Management")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "📄 Scan Orders",
        "🔍 Search Orders",
        "🔄 Change Status",
        "↩️ Upload Returns",
        "⚠️ Upload Claims",
        "📋 Claims Dashboard",
        "📈 Reports"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("OMS v1.0")


# -----------------------------
# DASHBOARD
# -----------------------------
if menu == "📊 Dashboard":

    st.title("📊 Dashboard")

    try:
        df = get_all_orders()

        total_orders = len(df)
        delivered = len(df[df["status"] == "Delivered"]) if "status" in df else 0
        returns = len(df[df["status"] == "Returned"]) if "status" in df else 0
        pending = total_orders - delivered

    except:
        total_orders = delivered = returns = pending = 0
        df = pd.DataFrame()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Orders", total_orders)
    col2.metric("Delivered", delivered)
    col3.metric("Returns", returns)
    col4.metric("Pending", pending)

    st.divider()

    if not df.empty and "status" in df:

        st.subheader("Orders by Status")

        chart = (
            df["status"]
            .value_counts()
            .reset_index()
        )

        chart.columns = ["Status", "Count"]

        fig = px.bar(
            chart,
            x="Status",
            y="Count",
            text="Count"
        )

        st.plotly_chart(fig, width='stretch')

    st.divider()

    st.subheader("Recent Orders")

    if not df.empty:
        st.dataframe(
            df.head(20),
            width='stretch',
            height=400
        )


# -----------------------------
# SCAN ORDERS
# -----------------------------
elif menu == "📄 Scan Orders":

    st.title("📄 Scan Orders")

    uploaded_file = st.file_uploader(
        "Upload Order PDF",
        type=["pdf"]
    )

    if uploaded_file:

        with st.spinner("Extracting data..."):
            df = extract_orders(uploaded_file)

        st.success("Extraction complete")

        edited_df = st.data_editor(
            df,
            width='stretch',
             num_rows="dynamic"
         )

        if st.button("💾 Save to Database"):

            save_to_db(edited_df)

            st.success("Saved successfully")


# -----------------------------
# SEARCH ORDERS
# -----------------------------
elif menu == "🔍 Search Orders":

    st.title("🔍 Search Orders")

    search = st.text_input("Enter Order ID / AWB")

    if search:

        results = search_all_orders(search)

        if len(results) > 0:

            st.success(f"{len(results)} results found")

            st.dataframe(
                results,
                width='stretch',
             height=500
         )

        else:
            st.warning("No results found")


# -----------------------------
# CHANGE STATUS
# -----------------------------
elif menu == "🔄 Change Status":

    st.title("🔄 Change Order Status")

    order_id_input = st.text_input("Order ID")

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


# -----------------------------
# RETURNS
# -----------------------------
elif menu == "↩️ Upload Returns":

    st.title("↩️ Upload Returns")

    file = st.file_uploader("Upload Returns CSV", type=["csv"])

    if file:

        df = read_meesho_returns_csv(file)

        st.dataframe(df)

        if st.button("Upload Returns"):

            insert_meesho_returns(df)

            st.success("Returns uploaded")


# -----------------------------
# CLAIMS
# -----------------------------
elif menu == "⚠️ Upload Claims":

    st.title("⚠️ Upload Claims")

    file = st.file_uploader("Upload Claims CSV", type=["csv"])

    if file:

        df = read_claims_csv(file)

        st.dataframe(df)

        if st.button("Upload Claims"):

            insert_claims(df)

            st.success("Claims uploaded")


# -----------------------------
# REPORTS
# -----------------------------
elif menu == "📈 Reports":

    st.title("📈 Reports Dashboard")

    from db.reports import (
        get_all_orders_df,
        get_returns_df,
        get_claims_df,
        get_orders_without_claims,
        get_returns_without_claims,
        get_claims_pending_refund
    )

    # load data
    orders_df = get_all_orders_df()
    returns_df = get_returns_df()
    claims_df = get_claims_df()

    no_claim_orders = get_orders_without_claims()
    no_claim_returns = get_returns_without_claims()
    refund_pending = get_claims_pending_refund()

    # -----------------------------
    # METRICS
    # -----------------------------

    total_orders = len(orders_df)
    total_returns = len(returns_df)
    total_claims = len(claims_df)
    refund_pending_count = len(refund_pending)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Orders", total_orders)
    col2.metric("Total Returns", total_returns)
    col3.metric("Total Claims", total_claims)
    col4.metric("Refund Pending", refund_pending_count)

    st.divider()

    # -----------------------------
    # TABS
    # -----------------------------

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "All Orders",
        "Returns",
        "Claims",
        "Orders Without Claims",
        "Refund Pending"
    ])

    # -----------------------------
    # ALL ORDERS
    # -----------------------------

    with tab1:
        st.subheader("All Orders")
        st.dataframe(
            orders_df,
            width='stretch',
            height=500
        )

    # -----------------------------
    # RETURNS
    # -----------------------------

    with tab2:
        st.subheader("Returns")
        st.dataframe(
            returns_df,
            width='stretch',
            height=500
        )

    # -----------------------------
    # CLAIMS
    # -----------------------------

    with tab3:
        st.subheader("Claims")
        st.dataframe(
            claims_df,
            width='stretch',
            height=500
        )

    # -----------------------------
    # ORDERS WITHOUT CLAIMS
    # -----------------------------

    with tab4:
        st.subheader("Orders Without Claims")
        st.dataframe(
            no_claim_orders,
            width='stretch',
            height=500
        )

    # -----------------------------
    # REFUND PENDING
    # -----------------------------

    with tab5:
        st.subheader("Refund Pending")
        st.dataframe(
            refund_pending,
            width='stretch',
            height=500
        )


# -----------------------------
# CLAIMS DASHBOARD
# -----------------------------
elif menu == "📋 Claims Dashboard":

    st.title("📋 Claims Dashboard")

    # get claims data
    try:
        from db.reports import get_all_claims   # or your claims fetch function
        claims_df = get_all_claims()

    except:
        st.error("Unable to load claims data")
        claims_df = pd.DataFrame()

    if claims_df.empty:
        st.warning("No claims found")
        st.stop()

    # -------------------------
    # METRICS (render only if data & columns exist)
    # -------------------------
    if not claims_df.empty:
        total_claims = len(claims_df)
        if "ticket_status" in claims_df:
            pending = len(claims_df[claims_df["ticket_status"] == "Open"])
            approved = len(claims_df[claims_df["ticket_status"] == "Approved"])
            rejected = len(claims_df[claims_df["ticket_status"] == "Rejected"])
        else:
            pending = approved = rejected = 0

        refunded = len(claims_df[claims_df["refund_status"] == "Refunded"]) if "refund_status" in claims_df else 0

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Claims", total_claims)
        col2.metric("Open", pending)
        col3.metric("Approved", approved)
        col4.metric("Rejected", rejected)
        col5.metric("Refunded", refunded)

        st.divider()

        # -------------------------
        # CLAIM STATUS CHART
        # -------------------------
        if "ticket_status" in claims_df:
            chart = claims_df["ticket_status"].value_counts().reset_index()
            chart.columns = ["Status", "Count"]
            fig = px.bar(chart, x="Status", y="Count", text="Count", color="Status")
            st.plotly_chart(fig, width='stretch')

        st.divider()

    # -------------------------
    # CLAIMS TABLE (always show)
    # -------------------------
    st.subheader("All Claims")
    st.dataframe(
        claims_df,
        width='stretch',
        height=500
    )

    # -------------------------
    # FILTER
    # -------------------------
    st.subheader("Filter Claims")
    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "Open", "Approved", "Rejected"]
    )

    if status_filter != "All":
        if "ticket_status" in claims_df:
            filtered = claims_df[claims_df["ticket_status"] == status_filter]
        else:
            filtered = pd.DataFrame()

        st.dataframe(
            filtered,
            width='stretch'
        )
