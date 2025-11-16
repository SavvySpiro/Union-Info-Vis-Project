import numpy as np
import textwrap
import plotly.express as px
from dash import Dash, dcc, html
import pandas as pd


def timeline():
    '''--------------------- Data Import ---------------------'''
    negotiations = pd.read_csv("data/contract_negotiations.csv")
    negotiations["Start Date"] = pd.to_datetime(negotiations["Date"])
    
    # Sort negotiations by date to ensure proper ordering
    negotiations = negotiations.sort_values(["Article", "Start Date"])
    
    def get_end_date(row):
        """
        Find the next date when the OTHER party makes a change to the same article.
        If no response from the other party, extend to the final date.
        """
        article = row["Article"]
        current_date = row["Start Date"]
        current_party = row["Party"]
        
        # Filter for same article, after current date, by different party
        future_changes = negotiations[
            (negotiations["Article"] == article) & 
            (negotiations["Start Date"] > current_date) & 
            (negotiations["Party"] != current_party)
        ]
        
        if len(future_changes) > 0:
            # Return the date of the next change by the other party
            return future_changes["Start Date"].min()
        else:
            # No response from other party, extend to "present"
            return pd.to_datetime("2025-05-30")
    
    # Apply the new end date logic
    negotiations["End Date"] = negotiations.apply(get_end_date, axis=1)
    
    # Wrap tooltip text
    def split_string(elem):
        return "<br>".join(textwrap.wrap(str(elem), width=70))
    
    negotiations["Changes from Previous Version"] = negotiations["Changes from Previous Version"].apply(split_string)
    
    ARTICLES = negotiations["Article"].unique()
    
    '''--------------------- Figure ---------------------'''
    timeline = px.timeline(
        negotiations, 
        x_start="Start Date", 
        x_end="End Date",
        y="Article",
        color="Party",
        custom_data=["Changes from Previous Version"],
        labels={"Article": ""}
    )
    
    timeline.update_traces(
        hovertemplate="<b>Topic:</b> %{y} <br>" +
                     "<b>Date: </b> %{base|%b %d, %Y} <br>" +
                     "%{customdata[0]}<extra></extra>"
    )
    
    # Get all unique dates for tick marks
    all_dates = sorted(negotiations["Start Date"].unique())
    all_dates.append(pd.to_datetime("2025-05-30"))
    
    timeline.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=all_dates,
            ticktext=[date.strftime("%b %d, %y") for date in all_dates[:-1]] + ["Present"],
            fixedrange=True,
        )
    )
    
    return timeline