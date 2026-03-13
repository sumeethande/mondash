"""A core module defining the schema of the data used throughout the app.
"""

from dataclasses import dataclass, field
from shared.types import ValidationError
from typing import Type, Callable
import pandas as pd

@dataclass(frozen=True)
class MondashColumn:
    """Represents a column in a MondashSchema.

    Attributes:
        name (str): Name of the Mondash Column.
        types (tuple[Type, ...]): A tuple of acceptable Data-types for the Mondash Column.
        null_okay (bool): Whether null values are acceptable in the Mondash Column.
        coerce (callable): A callback function to fix errors for the Mondash Column. 
    """
    name: str
    types: tuple[Type, ...]
    null_okay: bool = False
    coerce: Callable[[pd.Series], pd.Series] | None = None

@dataclass(frozen=True)
class MondashSchema:
    """Represents a schema of the CSV which is used throughout the Mondash web-app.

    Attributes:
        columns (tuple[MondashColumn, ...]): A tuple of Mondash Columns of type MondashColumn.
    """
    columns: tuple[MondashColumn, ...]

    _by_name: dict[str, MondashColumn] = field(init=False, repr=False)

    def __post_init__(self):
        object.__setattr__(
            self,
            "_by_name",
            {c.name: c for c in self.columns}
        )
    
    def get(self, name:str) -> MondashColumn:
        """Gives the MondashColumn from the MondashSchema.

        Args:
            name (str): Name of the Mondash Column.

        Returns:
            MondashColumn: An object of type MondashColumn.
        """
        return self._by_name[name]
    
    @property
    def column_names(self) -> list[str]:
        """list[str]: A list of column names in the MondashSchema"""
        return list(self._by_name.keys())

@dataclass(frozen=True)
class ColumnMapping:
    """Represents a one-to-one mapping of User CSV's columns to MondashColumns

    Args:
        model_to_user (dict[str, str]): A mapping of column names from MondashColumn to the User CSV's column. For example, {"date":"purchased_date"}
    """
    # model_column (key) -> user_column (value)
    model_to_user: dict[str, str]

    def get_user_col(self, model_column: str) -> str:
        """Returns name of the column as it appears in the User's CSV.

        Args:
            model_column (str): Name of the Mondash Column.

        Returns:
            str: Name of Column in User's CSV.
        """
        return self.model_to_user[model_column]

@dataclass(frozen=True)
class ValidationIssue:
    """Represents an error in the User's CSV.

    Attributes:
        model_col (str): Name of the Mondash column which has error or None.
        user_col (str): Name of the User CSV's column which has error or None.
        error (ValidationError): Error enum of type ValidationError.
        error_details (str): Description of Error.
    """
    model_col: str | None
    user_col: str | None
    error: ValidationError
    error_details: str | None = None

    @property
    def error_message(self) -> str:
        """str: Description of the Error."""
        return self.error.err_text

@dataclass()
class ValidationReport:
    """Represents an object holding all errors of type ValidationIssue.

    Attributes:
        issues (list[ValidationIssue]): List of all ValidationIssue objects.
    """
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_successful(self) -> bool:
        """Checks if Validation has been a success or not.

        Returns:
            bool: True if Validation is successful and False if Validation has failed.
        """
        return len(self.issues) == 0
    
    def add(self, *issues: ValidationIssue) -> None:
        """Adds a ValidationIssue to the ValidationReport.

        Args:
            issues: One or more instances of ValidationIssue.
        """
        self.issues.extend(issues)

@dataclass()
class Dataset:
    """Represents complete dataset used by the Mondash Web-app.

    Attributes:
        original_df (pd.DataFrame): Dataframe representing user uploaded CSV.
        model_df (pd.DataFrame): Dataframe representing user CSV after validation. Contains mondash column names instead of User's CSV column names.
        mapping (ColumnMapping): A Mapping object containing a dictionary of colummn mappings between User's CSV and Mondash Columns.
        schema (MondashSchema): A Schema representing Mondash CSV used by the web-app.
        report (ValidationReport): A report object containing all issues/errors during validation of User's CSV.
    """
    original_df: pd.DataFrame | None = None
    model_df: pd.DataFrame | None = None
    mapping: ColumnMapping | None = None
    schema: MondashSchema | None = None
    report: ValidationReport | None = None