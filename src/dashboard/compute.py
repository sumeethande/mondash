"""This module computes all required data neeeded for the dashboards.
"""

import pandas as pd
from .metrics import *

def compute_overview_kpis(df: pd.DataFrame, month: int, year: int) -> tuple[OverviewKPI, ...]:
    """Computes the following KPI's needed for Overview Dashboard:

    1. Total Spendings (OverviewKPI)
    2. % Spendings on Essentials vs Non-Essentials
    3. Basket Size
    4. Avg. weekly spendings

    Args:
        df (pd.Dataframe): Input dataframe
        month (str): Month filter for which calculations are made. 3 Letter format (JAN, FEB, MAR)
        year (int): Year filter for which calculations are made.

    Returns:
        tuple: A tuple of of 4 special type objects each corresponding to the KPI mentioned.
    """
    expense = OverviewKPI()
    essentials = OverviewKPI()
    basket_size = OverviewKPI()
    avg_weekly_ex = OverviewKPI()
    no_of_trips = OverviewKPI()
    
    # CASE: User selects January from filter
    if month == 1:
        expense_condition = (df["month"] == 1) & (df["year"] == year)
        essentials_true = (df["month"] == 1) & (df["year"] == year) & (df["is_essential"] == True)
        essentials_false = (df["month"] == 1) & (df["year"] == year) & (df["is_essential"] == False)
        previous_exists = ((df["year"] == year - 1) & (df["month"] == 12)).any()
        previous_exists_condition = (df["year"] == year - 1) & (df["month"] == 12)
    # CASE: User selects any other month
    else:
        expense_condition = (df["month"] == month) & (df["year"] == year)
        essentials_true = (df["month"] == month) & (df["year"] == year) & (df["is_essential"] == True)
        essentials_false = (df["month"] == month) & (df["year"] == year) & (df["is_essential"] == False)
        previous_exists = ((df["month"] == month - 1) & (df["year"] == year)).any()
        previous_exists_condition = (df["year"] == year - 1) & (df["month"] == 12)

    # Compute CURRENT
    # 1. Compute Total Spendings
    expense.current = round(df[expense_condition]["price"].sum(), 2)

    # 2. Compute % Essentials vs Non-Essentials
    essentials_current_true_count = df[essentials_true]["is_essential"].count()
    essentials_current_false_count = df[essentials_false]["is_essential"].count()
    essentials.current = round(( essentials_current_true_count / (essentials_current_true_count + essentials_current_false_count) ) * 100, 2)

    # 3. Compute Avg. Basket Size
    basket_size.current = round(df[expense_condition].groupby("basket_id")["price"].sum().mean(), 2)

    # 4. Compute Avg. Weekly spendings
    avg_weekly_ex.current = round(df[expense_condition].groupby("week")["price"].sum().mean(),2)

    # 5. Compute Total no. of trips
    no_of_trips.current = len(df[expense_condition]["basket_id"].unique())

    # Data from December of previous year exists then,
    if previous_exists:

        # 1. Compute PREVIOUS and DELTA Total Spendings
        expense.previous = round(df[previous_exists_condition]["price"].sum(), 2)
        expense.delta = round(expense.current - expense.previous, 2)

        # 2. Compute PREVIOUS and CURRENT % Essentials vs Non-Essentials
        essentials.previous = round(df[previous_exists_condition & essentials_true]["is_essential"].count() / ( (df[(df["year"] == year - 1)&(df["month"] == 12)&(df["is_essential"]==True)]["is_essential"].count() + df[(df["year"] == year - 1)&(df["month"] == 12)&(df["is_essential"]==False)]["is_essential"].count()) ) * 100 ,2)
        essentials.delta = round(essentials.current - essentials.previous, 2)

        # 3. Compute PREVIOUS Avg. Basket Size
        basket_size.previous = round(df[previous_exists_condition].groupby("basket_id")["price"].sum().mean(),2)
        basket_size.delta = round(basket_size.current - basket_size.previous,2)

        # 4. Computer PREVIOUS Avg. Weekly Spendings
        avg_weekly_ex.previous = round(df[previous_exists_condition].groupby("week")["price"].sum().mean(),2)
        avg_weekly_ex.delta = round(avg_weekly_ex.current - avg_weekly_ex.previous, 2)

        # 5. Compute PREVIOUS Total no. of trips
        no_of_trips.previous = len(df[previous_exists_condition]["basket_id"].unique())
        no_of_trips.delta = no_of_trips.current - no_of_trips.previous

    return (expense, essentials, basket_size, avg_weekly_ex, no_of_trips)

def compute_spend_trend(df: pd.DataFrame, month: int, year: int) -> pd.DataFrame:
    """Computes data required for plotting expense trend over a period.

    Args:
        df (pd.Dataframe): Input dataframe
        month (int): Month filter for which calculations are made.
        year (int): Year filter for which calculations are made.

    Returns:
        pd.Dataframe: A Dataframe containing data to plot the line graph.
    """

    filtered_df = df[(df["month"] == month) & (df["year"] == year)]

    return filtered_df.groupby("day", as_index=False)["price"].sum()

def compute_day_spending_bar(df: pd.DataFrame, month: int, year: int) -> pd.DataFrame:
    """Computes data required for plotting the spending by day of the week bar graph.

    Args:
        df (pd.Dataframe): Input dataframe
        month (int): Month filter for which calculations are made.
        year (int): Year filter for which calculations are made.

    Returns:
        pd.Dataframe: A Dataframe containing data to plot the bar graph.    
    """

    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    filtered_df = df[(df["month"] == month) & (df["year"] == year)]

    filtered_df["day_name"] = pd.Categorical(filtered_df["day_name"], categories=weekday_order, ordered=True)

    return filtered_df.groupby("day_name", as_index=False)["price"].sum().sort_values("day_name")

def compute_heatmap(df: pd.DataFrame, month: int, year: int) -> pd.DataFrame:
    """Computes data required for plotting the heatmap for day of the week and top 6 sub-categories spending.

    Args:
        df (pd.Dataframe): Input dataframe
        month (int): Month filter for which calculations are made.
        year (int): Year filter for which calculations are made.

    Returns:
        pd.Dataframe: A Dataframe containing data to plot the heat map.    
    """

    filtered_df = df[(df["month"] == month) & (df["year"] == year)]

    DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Get top 6 sub-categories by total spend
    top_6 = (filtered_df.groupby("sub_category")["price"].sum().nlargest(6).index)

    # Filter dataframe to only top 6
    df_top6 = filtered_df[filtered_df["sub_category"].isin(top_6)]

    return df_top6.groupby(["sub_category", "day_name"])["price"].sum().unstack(fill_value=0).reindex(columns=DAY_ORDER)