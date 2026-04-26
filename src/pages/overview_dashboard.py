import streamlit as st
import pandas as pd
from state import get_state
from dashboard.compute import compute_overview_kpis, compute_spend_trend, compute_category_bar

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

if state.dataset.model_df is None:
    st.info("Upload & Map a CSV file first.", icon=":material/info:")
else:

    with st.container(horizontal_alignment="distribute", horizontal=True):
        expense, essentials, basket_size, avg_weekly_ex, total_trips = compute_overview_kpis(df=state.dataset.model_df, month=month, year=year)

        st.metric(
            label="Total Expenses",
            value=f"€{expense.current}",
            delta=expense.delta,
            delta_color="inverse",
            delta_arrow="auto",
            border=True,
            width="stretch",
            help='''
            This indicates the total money spent in the current selected period.
            The number below it indicates the difference in the total money spent between the current selected and the previous
            period. A :red[red] shows an "excess" compared to last period and a :green[green] shows a "saving" compared to the last period.
            '''
        )

        st.metric(
            label="% Essentials",
            value=f"{essentials.current}%",
            delta=essentials.delta,
            delta_color="normal",
            delta_arrow="auto",
            border=True,
            width="stretch",
            help="This indicates 'What percent of the total money were spent on essential products'."
        )

        st.metric(
            label="Avg. Basket Size",
            value=f"€{basket_size.current}",
            border=True,
            delta=basket_size.delta,
            delta_color="inverse",
            delta_arrow="auto",
            width="stretch",
            help="This indicates the average money spent on each shopping trip."
        )

        st.metric(
            label="Avg. Weekly Expense",
            value=f"€{avg_weekly_ex.current}",
            border=True,
            delta=avg_weekly_ex.delta,
            delta_color="inverse",
            delta_arrow="auto",
            width="stretch",
            help="Indicates the weekly average spending."
        )

        st.metric(
            label="Total Trips",
            value=total_trips.current,
            border=True,
            delta=total_trips.delta,
            delta_color="inverse",
            delta_arrow="auto",
            width="stretch",
            help="The total number of shopping trips made in the current selected period."
        )


    with st.container(horizontal=True, horizontal_alignment="distribute"):
                
        graph_data = compute_spend_trend(state.dataset.model_df, month=month, year=year)

        left_col, right_col = st.columns(2, gap="xsmall", vertical_alignment="top", border=True)

        with left_col:
            st.text(f"Spend Trend for month {month}", width="stretch", text_alignment="center")
            st.line_chart(
                data=graph_data,
                x="day",
                x_label="Date",
                y="price",
                y_label="Money Spend (€)"
            )
        
        bar_graph_data = compute_category_bar(state.dataset.model_df, month=month, year=year)

        with right_col:
            st.text(f"Sub-Category breakdown for month {month}", width="stretch", text_alignment="center")
            st.bar_chart(
                data=bar_graph_data,
                x="sub_category",
                x_label="Sub-Category",
                y="price",
                y_label="Money Spend (€)"
            )