import streamlit as st

st.set_page_config(
    page_title="Overview Dashboard",
    page_icon=":material/analytics:"
)

with st.container(horizontal_alignment="center"):
    df = st.session_state.get("data_df", None)

    if df is None:
        st.info("Upload & Map a CSV file first.", icon=":material/info:")
    else:
        st.write("Dashboard under construction", icon=":material/construction:")