import pandas as pd
import plotly.express as px
from dash import html, dcc

def livingwage_vs_stipend():
    """
    Creates Dash div and callbacks for the living wage comparison line chart
    Compares 6 Boston-area universities between 2013 and 2025
    This is the function that gets imported into app.py

    Returns:
        html.Div: html code for the Dash layout
        callbacks: functions for interactivity (not currently used)
    """

    stipends = pd.read_csv("data/boston_stipends.csv")
    
    def uni_shorthand(elem):
        # Adding shorthand for tooltips
        unis = {"Boston University": "BU", "Harvard University":"Harvard",
                "MIT":"MIT", "Northeastern University":"Northeastern",
                "Tufts University":"Tufts", "UMass Boston":"UMass Boston"}
        return unis[elem]
    stipends["Univ. Shorthand"] = stipends["University"].apply(uni_shorthand)

    avg_by_year = stipends[["Academic Year", "University", "Univ. Shorthand", "Overall Pay"]
                           ].groupby(["Academic Year", "University", "Univ. Shorthand"]
                            ).mean().reset_index()
    
    def rounded_stipend(elem):
        return f"{round(elem, -3)}"[:2]
    
    avg_by_year["Pay Rounded"] = avg_by_year["Overall Pay"].apply(rounded_stipend)

    stipends_over_time = px.line(
        avg_by_year,
        x="Academic Year",
        y="Overall Pay",
        color="University",
        markers=True,
        custom_data=["Univ. Shorthand", "Pay Rounded"]
    ).update_layout(
        yaxis_tickprefix = '$', yaxis_tickformat = ',.'

    ).update_yaxes(title="Overall Pay (Average)"
    ).update_layout(
        hovermode = 'x unified'
    ).update_traces(hovertemplate= 
                        "<b>%{customdata[0]}</b> <br>" +
                        "Average Pay: $%{customdata[1]}k<extra></extra>")

    stipends_over_time.add_hline(y=63942, line_dash="dash", annotation_text="2025 Boston Living Wage: $63,942", line=dict(color="#A2A2A2"))
    stipends_over_time.add_hline(y=15650, line_dash="dash", annotation_text="Masschusetts Poverty Line: $15,650", line=dict(color="#A2A2A2"))
    stipends_over_time.add_vline(x=2025, line_dash="dot", line=dict(color="#A2A2A2"))

    # create layout
    layout = html.Div([
        dcc.Graph(figure=stipends_over_time)
    ])

    title = "Stipends Over Time vs Living Wage"
    subtitle = "While average stipends have gone up across Boston area colleges,<br> they are still below a living wage for the area."

    return layout , [], title, subtitle
