import streamlit as st
from core import Dataset, MondashSchema, MondashColumn, coerce_time, coerce_int, coerce_date, coerce_float, coerce_bool
from dataclasses import dataclass, field
from typing import cast
from datetime import date, time

@dataclass
class AppState:
    """Typed streamlit session state. 
    
    Instead of directly using session state as `st.session_state["key"]` 
    to get `value`, the AppState will define the streamlit's session state which will be "typed" providiing
    intellisense and autocompletion.

    Attributes:
        dataset (Dataset): A Dataset object of type `Dataset`.
    """
    dataset: Dataset = field(default_factory=Dataset)

def _build_schema() -> MondashSchema:
    """Internal function which intializes/builds required schema.

    Returns:
        MondashSchema: An object of type MondashSchema
    """
    return MondashSchema(columns=(
        MondashColumn("purchased_date", (date, str), False, coerce_date),
        MondashColumn("purchased_time", (time, str), False, coerce_time),
        MondashColumn("product", (str,), False),
        MondashColumn("category", (str,), False),
        MondashColumn("sub_category", (str,), False),
        MondashColumn("shop", (str,), False),
        MondashColumn("quantity", (int, float), True, coerce_int),
        MondashColumn("weight", (int, float), True, coerce_float),
        MondashColumn("price", (float,), False, coerce_float),
        MondashColumn("is_essential", (bool,), False, coerce_bool)
    ))

def get_state() -> AppState:
    """Get the current AppState.

    Returns:
        AppState: An object of type AppState with schema intialized.
    """

    if "state" not in st.session_state:
        state = AppState()
        state.dataset.schema = _build_schema()
        st.session_state.state = state
    return cast(AppState, st.session_state.state)

