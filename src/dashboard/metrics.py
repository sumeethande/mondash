"""This module contains dataclasses defining dashboard data and how it is stored.
"""

from dataclasses import dataclass, field

@dataclass
class OverviewKPI:
    """Represents a KPI's data of the Overview Dashboard.

    Attributes:
        current (float): Total value of the current period.
        previous (float): Total value of the previous period.
        delta (float): Difference between values of current & previous period.
    """

    current: float | None = None
    previous: float | None = None
    delta: float | None = None