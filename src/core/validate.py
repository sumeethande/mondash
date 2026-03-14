"""A core module containing validation tools for validating and cleaning user uploaded CSV
"""

import re
import pandas as pd
from core.schema import MondashSchema, MondashColumn, ColumnMapping, ValidationIssue, ValidationReport, ValidationError
from pandas.api.types import (
    is_string_dtype,
    is_integer_dtype,
    is_float_dtype,
    is_bool_dtype,
    is_datetime64_any_dtype
)
from datetime import date, datetime, time

def coerce_date(column: pd.Series) -> pd.Series:
    """Fixes problems with the date column.

    Use this function as a callback while instantiating the MondashSchema for the appropriate column.

    Args:
        column (pd.Series): A Column from a pandas Dataframe which need to be corrected. This should be a column containing values of type date, datetime or str.
    """
    return pd.to_datetime(column, errors="coerce", dayfirst=True)

def coerce_time(column: pd.Series) -> pd.Series:
    """Fixes problems with the time column.

    Use this function as a callback while instantiating the MondashSchema for the appropriate column.

    Args:
        column (pd.Series): A Column from a pandas Dataframe which need to be corrected. This should be a column containing values of type date, datetime or str.
    """
    return pd.to_datetime(column, format="%H:%M", errors="coerce")
    
def coerce_float(column: pd.Series) -> pd.Series:
    """Fixes problems with the price mondash column or the weight mondash column.

    Use this function as a callback while instantiating the MondashSchema for the appropriate column.

    Args:
        column (pd.Series): A Column from a pandas Dataframe which need to be corrected. This should be a column containing values of str or float.
    """

    # Function handles cases like "1,23", "€1.23", "1 234,56"
    def clean(x):
        if pd.isna(x):
            return x
        x = str(x).strip()
        # remove currency symbols/spaces
        x = re.sub(r"[^\d,.\-]", "", x)
        # If comma is decimal separator (common in EU) and dot is thousands sep
        if x.count(",") == 1 and x.count(".") >= 1:
            x = x.replace(".", "").replace(",", ".")
        elif x.count(",") == 1 and x.count(".") == 0:
            x = x.replace(",", ".")
        return x
    
    cleaned = column.map(clean)
    return pd.to_numeric(cleaned, errors="coerce")

def coerce_int(column: pd.Series) -> pd.Series:
    """Fixes problems with the quantity mondash column.

    Use this function as a callback while instantiating the MondashSchema for the appropriate column.

    Args:
        column (pd.Series): A Column from a pandas Dataframe which need to be corrected. This should be a column containing values of type int.
    """
    f = pd.to_numeric(column, errors="coerce")
    # Keep as pandas nullable integer
    return f.round().astype("Int64")

def coerce_bool(column: pd.Series) -> pd.Series:
    """Fixes problems with the is_essential mondash column.

    Use this function as a callback while instantiating the MondashSchema for the appropriate column.

    Args:
        column (pd.Series): A Column from a pandas Dataframe which need to be corrected. This should be a column containing values of type boolean or str.
    """
    mapping = {"yes": True, "no": False, "true": True, "false": False, "1": True, "0": False}
    return column.str.strip().str.lower().map(mapping).astype("boolean")

class Validator:
    """This class is used for CSV validation.

    Attributes:
        schema (MondashSchema): Model schema which is used throughout the app
        mapping (ColumnMapping): Mapping of the columns between the user's CSV and model CSV.
    """

    def __init__(self, schema: MondashSchema, mapping: ColumnMapping) -> None:
        self.schema = schema
        self.mapping = mapping
    
    def _check_mapping(self, report: ValidationReport) -> None:
        """Internal method to be used inside validate method.

        Checks if the mapping submitted by the user is valid or invalid.

        Args:
            report (ValidationReport): An object of type ValidationReport.
        """
        mapped_model_cols = list(self.mapping.model_to_user.keys())

        # Check for unmapped Mondash Columns
        for col_name in self.schema.column_names:
            if col_name not in mapped_model_cols:
                report.add(ValidationIssue(
                    model_col=col_name,
                    user_col=None,
                    error=ValidationError.COLUMN_UNMAPPED,
                    error_details=f"'{col_name}' has not been mapped to any column in the uploaded CSV."
                ))

        # Check for duplicate mappings (one mondash column mapped more than once)
        seen = set()
        for model_col in mapped_model_cols:
            if model_col in seen:
                report.add(ValidationIssue(
                    model_col=model_col,
                    user_col=self.mapping.get_user_col(model_col),
                    error=ValidationError.COLUMN_MULTIMAPPED,
                    error_details=f"'{col_name}' mapped more than once."
                ))
            
            seen.add(model_col)
        
    def _check_nulls(self, user_col: pd.Series, mondash_col: MondashColumn, user_col_name: str, report: ValidationReport) -> None:
        """Internal method to be used inside validate method.

        Checks if a user column contains nulls and is allowed to contain nulls by checking the respective mapped mondash column.

        Args:
            user_col (pd.Series): The column from User's dataframe to be checked for nulls.
            mondash_col (MondashColumn): MondashColumn mapped to the user_col.
            user_col_name (str): Name of the user_col.
            report (ValidationReport): An object representing the Validation Report.
        """
        if not mondash_col.null_okay and user_col.isna().any():
            report.add(ValidationIssue(
                model_col=mondash_col.name,
                user_col=user_col_name,
                error=ValidationError.NULL_OKAY_FAILED,
                error_details=f"'{user_col_name}' contains empty/NULL values but '{mondash_col.name}' does not allow them."
            ))

    def _check_type(self, user_col: pd.Series, mondash_col: MondashColumn, user_col_name: str, report: ValidationReport) -> None:
        """Internal method to be used inside validate method.

        Checks the type of the user csv column and if it matches the required type of the mapped Mondash Column.

        Args:
            user_col (pd.Series): The column from User's dataframe to be checked for nulls.
            mondash_col (MondashColumn): MondashColumn mapped to the user_col.
            user_col_name (str): Name of the user_col.
            report (ValidationReport): An object representing the Validation Report.        
        """
        cleaned = user_col.dropna()
        type_matched = any(self._matches_type(cleaned, t) for t in mondash_col.types)

        if not type_matched:
            accepted = ", ".join(t.__name__ for t in mondash_col.types)
            report.add(ValidationIssue(
                model_col=mondash_col.name,
                user_col=user_col_name,
                error=ValidationError.DATA_TYPE_MISMATCH,
                error_details=f"{user_col_name} does not match accepted type(s) [{accepted}] for '{mondash_col.name}'."
            ))
        
    def _matches_type(self, column: pd.Series, type_to_check: type) -> bool:
        if type_to_check == str:
            return is_string_dtype(column)
        if type_to_check == float:
            return is_float_dtype(column)
        if type_to_check == int:
            return is_integer_dtype(column)
        if type_to_check in (datetime, date, time):
            if is_datetime64_any_dtype(column):
                return True
            cleaned = column.dropna()
            return cleaned.apply(lambda x: isinstance(x, (date, datetime, time))).all()
        if type_to_check == bool:
            return is_bool_dtype(column)
        return False

    def validate(self, csv_df: pd.DataFrame) -> tuple[ValidationReport, pd.DataFrame]:
        """This method validates a given CSV.

        It follows the MondashSchema while performing validation. The given CSV must follow the
        MondashSchema for a successful validation.

        Args:
            csv_df (pd.Dataframe): A dataframe which needs validation.

        Returns:
            tuple (tuple[ValidationReport, pd.Dataframe]): A tuple containing an object of type ValidationReport and the clean dataframe of type pandas.Dataframe
        """

        report = ValidationReport()
        coerced_df = csv_df.copy()

        # Steps
        # 1. Check the mapping of columns provided by user.
        self._check_mapping(report)

        # Stop the checks here itself if the mapping is invalid
        if not report.is_successful:
            return report, coerced_df
        
        for mondash_col_name in self.schema.column_names:
            # Get the mondash column from the name
            mondash_col = self.schema.get(mondash_col_name)
            user_col_name = self.mapping.get_user_col(mondash_col_name)

            # 2. Coerce the column
            if mondash_col.coerce is not None:
                coerced_df[user_col_name] = mondash_col.coerce(coerced_df[user_col_name])
            
            # 3. Check for NULL values in the coerced column
            self._check_nulls(coerced_df[user_col_name], mondash_col, user_col_name, report)

            # 4. Type check in the coerced column
            self._check_type(coerced_df[user_col_name], mondash_col, user_col_name, report)
        
        return report, coerced_df

    def post_validation(self, validated_df: pd.DataFrame) -> pd.DataFrame:
        """Perform additional post-validation steps.

        This method renames column names of the User's CSV (validated) to mondash schema's column names.
        It also adds helper columns like day, month, year and hour.

        Args:
            validated_df (pd.Dataframe): A validated df (output of Validator.validate). 
        
        Returns:
            pd.Dataframe: A dataframe with added helper columns and renamed column names.
        """
        # Drop unmapped columns
        cols_to_drop = []
        for column_name in validated_df.columns:
            mondash_col_name = self.mapping.get_model_col(column_name)
            # If a mapping is not found, it means the User column is unmapped and therefore
            # that column can be dropped
            if not mondash_col_name:
                cols_to_drop.append(column_name)
        validated_df.drop(cols_to_drop, axis="columns", inplace=True)

        # Rename columns to mondash column names
        rename_map = {
            self.mapping.get_user_col(mondash_col): mondash_col
            for mondash_col in self.schema.column_names
        }
        validated_df.rename(columns=rename_map, inplace=True)

        # Add helper columns
        validated_df["day"] = validated_df["purchased_date"].dt.day
        validated_df["month"] = validated_df["purchased_date"].dt.month
        validated_df["year"] = validated_df["purchased_date"].dt.year
        validated_df["hour"] = validated_df["purchased_time"].dt.hour

        return validated_df