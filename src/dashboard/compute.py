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
        avg_weekly_ex.current = round(df[(expense_condition)].groupby("week")["price"].sum().mean(),2)

        # 5. Compute Total no. of trips
        no_of_trips.current = len(df[expense_condition]["basket_id"].unique())

        # Data from December of previous year exists then,
        if previous_exists:

            # 1. Compute PREVIOUS and DELTA Total Spendings
            expense.previous = round(df[(df["year"] == year - 1) & (df["month"] == 12)]["price"].sum(), 2)
            expense.delta = round(expense.current - expense.previous, 2)

            # 2. Compute PREVIOUS and CURRENT % Essentials vs Non-Essentials
            essentials.previous = round(df[(df["year"] == year - 1)&(df["month"] == 12)&(df["is_essential"]==True)]["is_essential"].count() / ( (df[(df["year"] == year - 1)&(df["month"] == 12)&(df["is_essential"]==True)]["is_essential"].count() + df[(df["year"] == year - 1)&(df["month"] == 12)&(df["is_essential"]==False)]["is_essential"].count()) ) * 100 ,2)
            essentials.delta = round(essentials.current - essentials.previous, 2)

            # 3. Compute PREVIOUS Avg. Basket Size
            basket_size.previous = round(df[(df["year"] == year - 1) & (df["month"] == 12)].groupby("basket_id")["price"].sum().mean(),2)
            basket_size.delta = round(basket_size.current - basket_size.previous,2)

            # 4. Computer PREVIOUS Avg. Weekly Spendings
            avg_weekly_ex.previous = round(df[(df["year"] == year - 1) & (df["month"] == 12)].groupby("week")["price"].sum().mean(),2)
            avg_weekly_ex.delta = round(avg_weekly_ex.current - avg_weekly_ex.previous, 2)

            # 5. Compute PREVIOUS Total no. of trips
            no_of_trips.previous = len(df[(df["year"] == year - 1) & (df["month"] == 12)]["basket_id"].unique())
            no_of_trips.delta = no_of_trips.current - no_of_trips.previous

    # CASE: User selects months other than January from the filter
    else:
        expense_condition = (df["month"] == month) & (df["year"] == year)
        essentials_true = (df["month"] == month) & (df["year"] == year) & (df["is_essential"] == True)
        essentials_false = (df["month"] == month) & (df["year"] == year) & (df["is_essential"] == False)

        previous_exists = (df["month"] == month - 1).any()

        # Compute CURRENT
        # 1. Compute Total Spendings
        expense.current = round(df[expense_condition]["price"].sum(), 2)

        # 2. Compute % Essentials vs Non-Essentials
        essentials_current_true_count = df[essentials_true]["is_essential"].count()
        essentials_current_false_count = df[essentials_false]["is_essential"].count()
        essentials.current = round((essentials_current_true_count / (essentials_current_true_count + essentials_current_false_count) ) * 100, 2)

        # 3. Compute Avg. Basket Size
        basket_size.current = round(df[expense_condition].groupby("basket_id")["price"].sum().mean(), 2)

        # 4. Compute Avg. Weekly spendings
        avg_weekly_ex.current = round(df[(expense_condition)].groupby("week")["price"].sum().mean(),2)

        # 5. Compute Total no. of trips
        no_of_trips.current = len(df[expense_condition]["basket_id"].unique())

        # Data from previous month exists then,
        if previous_exists:

            # 1. Compute Total Spendings
            expense.previous = round(df[(df["month"] == month - 1) & (df["year"] == year)]["price"].sum(), 2)
            expense.delta = round(expense.current - expense.previous, 2)

            # 2. Compute % Essentials vs Non-Essentials
            essentials.previous = round(df[(df["year"] == year)&(df["month"] == month - 1)&(df["is_essential"]==True)]["is_essential"].count() / ( (df[(df["year"] == year)&(df["month"] == month - 1)&(df["is_essential"]==True)]["is_essential"].count() + df[(df["year"] == year)&(df["month"] == month - 1)&(df["is_essential"]==False)]["is_essential"].count()) ) * 100 ,2)
            essentials.delta = round(essentials.current - essentials.previous, 2)
    
            # 3. Compute Avg. Basket Size
            basket_size.previous = round(df[(df["year"] == year) & (df["month"] == month - 1)].groupby("basket_id")["price"].sum().mean(),2)
            basket_size.delta = round(basket_size.current - basket_size.previous,2)

            # 4. Computer PREVIOUS Avg. Weekly Spendings
            avg_weekly_ex.previous = round(df[(df["year"] == year) & (df["month"] == month - 1)].groupby("week")["price"].sum().mean(),2)
            avg_weekly_ex.delta = round(avg_weekly_ex.current - avg_weekly_ex.previous, 2)

            # 5. Compute PREVIOUS Total no. of trips
            no_of_trips.previous = len(df[(df["year"] == year) & (df["month"] == month - 1)]["basket_id"].unique())
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

def compute_category_bar(df: pd.DataFrame, month: int, year: int) -> pd.DataFrame:
    """Computes data required for plotting the category comparison bar graph.

    Args:
        df (pd.Dataframe): Input dataframe
        month (int): Month filter for which calculations are made.
        year (int): Year filter for which calculations are made.

    Returns:
        pd.Dataframe: A Dataframe containing data to plot the bar graph.    
    """

    filtered_df = df[(df["month"] == month) & (df["year"] == year)]

    return filtered_df.groupby("sub_category", as_index=False)["price"].sum()