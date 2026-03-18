import streamlit as st
import pandas as pd
from state import get_state
from shared.types import MONDASH_ENV, Env

st.set_page_config(
    page_title="View Data",
    page_icon=":material/table:"
)

# -------------------- INITIALIZE APP STATE --------------------
state = get_state()

def get_column_config() -> st.column_config:
    column_config = {
        "purchased_date": st.column_config.DateColumn(
            label="Purchase Date",
            disabled=True,
            format="DD-MM-YYYY"
        ),
        "purchased_time": st.column_config.TimeColumn(
            label="Purchase Time",
            disabled=True,
            format="HH:mm"
        ),
        "product": st.column_config.TextColumn(
            label="Product Name",
            disabled=True
        ),
        "category": st.column_config.TextColumn(
            label="Product Category",
            disabled=True
        ),
        "sub_category": st.column_config.TextColumn(
            label="Product Sub-Category",
            disabled=True
        ),
        "shop": st.column_config.TextColumn(
            label="Supermarket/Shop",
            disabled=True
        ),
        "quantity": st.column_config.NumberColumn(
            label="Quantity",
            disabled=True,
            format="plain"
        ),
        "weight": st.column_config.NumberColumn(
            label="Weight (kg)",
            disabled=True,
            format="plain"
        ),
        "price": st.column_config.NumberColumn(
            label="Total Price",
            disabled=True,
            format="euro"
        ),
        "is_essential": st.column_config.CheckboxColumn(
            label="Is Essential?",
            disabled=True
        )
    }

    return column_config

def delete_data():
    state.dataset.model_df = None
    st.toast("Data Removed. Re-upload data to view it again!", icon=":material/check:")

with st.container(horizontal_alignment="center"):
    df = state.dataset.model_df

    if df is None:
        st.info("Upload & Map a CSV file first.", icon=":material/info:")
    elif isinstance(df, pd.DataFrame) and df.empty:
        st.info("The uploaded CSV has no rows.", icon=":material/info:")
    else:
        if MONDASH_ENV == Env.PROD:
            df = df[state.dataset.schema.column_names]
            st.dataframe(data=df.set_index(pd.RangeIndex(start=1, stop=len(df)+1)), column_config=get_column_config())
        else:
            st.dataframe(data=df.set_index(pd.RangeIndex(start=1, stop=len(df)+1)))
        delete_data = st.button(label="Delete Data", icon=":material/delete:", on_click=delete_data)