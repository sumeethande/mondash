import streamlit as st

overview_dashboard = st.Page(page="./pages/overview_dashboard.py", title="Overview")
upload_page = st.Page(page="./pages/upload_page.py", title="Upload Data", default=True)
view_data = st.Page(page="./pages/view_data.py", title="View Data")

navigator = st.navigation(pages=[upload_page, view_data, overview_dashboard], position="sidebar", expanded=True)

navigator.run()