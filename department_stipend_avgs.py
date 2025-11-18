import pandas as pd
import plotly.express as px
from dash import html, dcc
import utils


def department_stipend_avgs():
    """
    Creates Dash div and callbacks for the department stipend comparison line chart
    Analyze and visualize department stipend averages over time for Northeastern University.
    This is the function that gets imported into app.py

    Returns:
        html.Div: html code for the Dash layout
        callbacks: functions for interactivity (not currently used)
    """
    # Load data
    stipends = pd.read_csv("data/boston_stipends.csv")
    
    # Filter for Northeastern University and standardize department names
    neu_mask = stipends["University"] == "Northeastern University"
    stipends.loc[neu_mask, "Department"] = stipends[neu_mask]["Department"].apply(utils.dept_name)
    
    # Calculate department averages by academic year
    neu_stipends = (
        stipends[neu_mask][["Academic Year", "Department", "Overall Pay"]]
        .groupby(["Academic Year", "Department"])
        .mean()
        .reset_index()
    )
    
    # Define departments with sufficient data
    depts_with_data = [
        'computer science', 
        'psychology', 
        'bioengineering', 
        'english',
        'sociology and anthropology', 
        'political science',
        'mechanical and industrial engineering',
        'electrical and computer engineering', 
        'biology', 
        'physics', 
        'history'
    ]
    
    # Filter for departments with data
    neu_avgs = neu_stipends[neu_stipends["Department"].isin(depts_with_data)]
    
    def rounded_stipend(elem):
        return f"{round(elem, -3)}"[:2]
    neu_avgs["Pay Rounded"] = neu_avgs["Overall Pay"].apply(rounded_stipend)
    
    # Create visualization
    neu_stipends_time = px.line(
        neu_avgs,
        x="Academic Year",
        y="Overall Pay",
        color="Department",
        markers=True,
        height=700,
        title="Though overall stipends have increased since 2013, there is a large disparity between departments,<br>" +
                "and some departments' stipends appear to have decreased in recent years.",
        custom_data=["Department", "Pay Rounded"]
    )
    
    # Format y-axis for currency
    neu_stipends_time.update_layout(
        yaxis_tickprefix='$', 
        yaxis_tickformat=',.',
        xaxis_title="Academic Year",
        yaxis_title="Overall Pay (Average)",
        legend_title="Department",
        hovermode='x unified'
    ).update_traces(hovertemplate= 
                        "<b>%{customdata[0]}</b> <br>" +
                        "Average Pay: $%{customdata[1]}k<extra></extra>")
    
    # create layout
    layout = html.Div([
        html.H3("Northeastern University Department Stipend Averages Over Time"),
        dcc.Graph(figure=neu_stipends_time)
    ])
    
    return layout , [] # No callbacks for this component]