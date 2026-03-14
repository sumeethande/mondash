import streamlit as st
import pandas as pd
from state import get_state

st.set_page_config(
    page_title="View Data",
    page_icon=":material/table:"
)

# -------------------- INITIALIZE APP STATE --------------------
state = get_state()

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
        selective_df = df[state.dataset.schema.column_names]
        st.dataframe(data=selective_df.set_index(pd.RangeIndex(start=1, stop=len(df)+1)))
        delete_data = st.button(label="Delete Data", icon=":material/delete:", on_click=delete_data)