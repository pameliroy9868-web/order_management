import streamlit as st
from utils.order_flow import ORDER_FLOW


def show_status_tracker(current_status):

    st.subheader("Order Progress")

    cols = st.columns(len(ORDER_FLOW))

    for i, status in enumerate(ORDER_FLOW):

        if status == current_status:
            cols[i].success(status)

        elif ORDER_FLOW.index(status) < ORDER_FLOW.index(current_status):
            cols[i].info(status)

        else:
            cols[i].write(status)
