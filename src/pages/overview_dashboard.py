import streamlit as st
import pandas as pd
from state import get_state
from dashboard.compute import compute_overview_kpis

st.set_page_config(
    page_title="Overview Dashboard",
    page_icon=":material/analytics:",
    layout="wide"
)

state = get_state()

month = 0
year = 0

if state.dataset.model_df is not None:
    with st.container(horizontal=True, horizontal_alignment="left"):
        month = st.selectbox(
            label="Select Month",
            options=state.dataset.model_df["month"].unique(),
            width=150
        )

        year = st.selectbox(
            label="Select Year",
            options=state.dataset.model_df["year"].unique(),
            width=150
        )

with st.container(horizontal_alignment="distribute", horizontal=True):
    if state.dataset.model_df is None:
        st.info("Upload & Map a CSV file first.", icon=":material/info:")
    else:
        expense, essentials, basket_size, avg_weekly_ex, total_trips = compute_overview_kpis(df=state.dataset.model_df, month=month, year=year)

        st.metric(
            label="Total Expenses",
            value=f"€{expense.current}",
            delta=expense.delta,
            delta_color="inverse",
            delta_arrow="auto",
            border=True,
            width="stretch"
        )

        st.metric(
            label="% Essentials",
            value=f"{essentials.current}%",
            delta=essentials.delta,
            delta_color="normal",
            delta_arrow="auto",
            border=True,
            width="stretch"
        )

        st.metric(
            label="Avg. Basket Size",
            value=f"€{basket_size.current}",
            border=True,
            delta=basket_size.delta,
            delta_color="inverse",
            delta_arrow="auto",
            width="stretch"
        )

        st.metric(
            label="Avg. Weekly Expense",
            value=f"€{avg_weekly_ex.current}",
            border=True,
            delta=avg_weekly_ex.delta,
            delta_color="inverse",
            delta_arrow="auto",
            width="stretch"
        )

        st.metric(
            label="Total Trips",
            value=total_trips.current,
            border=True,
            delta=total_trips.delta,
            delta_color="inverse",
            delta_arrow="auto",
            width="stretch"
        )
