import time
import streamlit as st
import pandas as pd
from state.state_handler import get_state
from core.schema import ColumnMapping
from core.validate import Validator

st.set_page_config(
    page_title="Upload Data",
    page_icon=":material/upload:"
)

# -------------------- INITIALIZE APP STATE --------------------
state = get_state()

def column_map_card(col_name: str) -> None:
    with st.container(border=False, horizontal=True):

        col1, col2, col3, col4 = st.columns([0.15, 0.35, 0.2, 0.3], gap=None, vertical_alignment="center")

        with col1:
            st.write(":red[CSV Column]")
        with col2:
            st.write(col_name)
        with col3:
            st.write(":blue[Mondash Column]")
        with col4:
            st.selectbox(
                label="Map column", 
                label_visibility="collapsed",
                options=state.dataset.schema.column_names,
                index=None,
                placeholder="Map column to...",
                key=col_name
            )

def get_column_mapping() -> ColumnMapping:
    """Gets the mapped column names from the Selectbox widgets and returns a ColumnMapping object.

    Returns:
        ColumnMapping: An object of type ColumnMapping.
    """
    mapping_dict = {}
    for key, value in st.session_state.items():
        if isinstance(value, str) and value in state.dataset.schema.column_names:
            mapping_dict[value] = key
    
    return ColumnMapping(mapping_dict)

def save_callback() -> None:

    # Using Streamlit's Status container
    with st.status(
        label="Validating...",
        state="running",
        expanded=False
    ) as status:
        # User CSV as a dataframe
        csv_df = state.dataset.original_df

        # Get the user given mapping
        column_mapping = get_column_mapping()
        state.dataset.mapping = column_mapping

        # Set the validator
        validator = Validator(state.dataset.schema, state.dataset.mapping)

        # Validate the columns
        report, cleaned_df = validator.validate(state.dataset.original_df)

        time.sleep(0.7)
        
        # Validation has failed
        if not report.is_successful:
            status.update(label="Validation Failed", expanded=True, state="error")
            for issue in report.issues:
                st.error(f":red[{issue.error.err_text}]: {issue.error_details}", icon=":material/error:")
            
        else:
            status.update(label="Validation Successful", expanded=True, state="complete")
            state.dataset.model_df = cleaned_df
            st.success("Validation is complete! You can now view dashboards", icon=":material/check:")
        

@st.dialog(title="About Mondash columns", width="medium", icon=":material/help:")
def help_dialog() -> None:
    st.write(
        f'''
        Please map your CSV columns with the required columns Mondash will need for creating dashboards. 
        Unmapped columns will not be considered for dashboards.
        Mapping :red[must be] one-on-one. It is not allowed to map one CSV column to more than one Mondash column.
        Mondash has :blue[{len(state.dataset.schema.column_names)}] columns which it considers :red[required] for it's dashboards. 
        It is important to map all the mondash columns with the columns from your CSV file. If your CSV has more columns,
        those will be ignored. This is the information about columns used by Mondash:
        '''
        )
    
    # Loop over SCHEMA COLUMNS DETAILS dictionary to create data for a dataframe
    column_data = []
    for mondash_col in state.dataset.schema.columns:
        row_data = []
        row_data.append(f":blue[{mondash_col.name}]")
        row_data.append(f"{mondash_col.types[0].__name__} OR {mondash_col.types[1].__name__}" if len(mondash_col.types) == 2 else f"{mondash_col.types[0].__name__}")
        row_data.append(":green[YES]" if mondash_col.null_okay else ":red[NO]")

        column_data.append(row_data)
    
    column_df = pd.DataFrame(
        column_data, 
        index=[i for i in range(1, len(state.dataset.schema.column_names) + 1)],
        columns=["Column name", "Accepted Types", "Is NULL okay?"]
    )

    st.table(column_df, border=True)

def column_mapper() -> None:
    
    data_columns = state.dataset.original_df.columns

    with st.container(border=True, key="upload_page_sub_container"):
        with st.container(border=False, horizontal=True, horizontal_alignment="distribute", vertical_alignment="center"):
            st.write(f"Columns identified in CSV file:  :red[{len(data_columns)}]")
            st.button(
                label="",
                icon=":material/help:",
                on_click=help_dialog
            )
        
        for col_name in data_columns:
            column_map_card(col_name)
    
    with st.container(border=False, horizontal=True, horizontal_alignment="center"):
        save_button_clicked = st.button(
            label="Validate & Save",
            key="save_button",
            icon=":material/save:",
        )

    if save_button_clicked:
        save_callback()

def sync_data() -> None:
    # Ensure widget is not None
    if st.session_state["csv_upload_widget"] is not None:
        state.dataset.original_df = pd.read_csv(st.session_state["csv_upload_widget"])
    
with st.container(border=False, key="upload_page_main_container"):

    st.space(size="small")

    st.title("💲Mondash💲", text_alignment="center", anchor=False)
    st.text(
        '''
        Welcome to Mondash!
        Mondash stands for 'Money Dashboard'. You can use this service to get detailed
        dashboards and analyse how your money gets spent. You can start by uploading a CSV of
        your data to continue. 
        ''', 
        text_alignment="center",
        width="stretch"
    )

    data = st.file_uploader(
                label="Upload your data",
                type="csv",
                accept_multiple_files=False,
                max_upload_size=200,
                key="csv_upload_widget",
                help="Only CSV files with less than 200 MB in size will be accepted as input.",
                on_change=sync_data
            )
    
    if data:
        column_mapper()

