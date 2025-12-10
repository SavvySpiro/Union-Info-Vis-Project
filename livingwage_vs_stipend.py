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

    # read data
    stipends = pd.read_csv("data/boston_stipends.csv")
    
    # Adding shorthand for tooltips
    def uni_shorthand(elem):
        unis = {"Boston University": "BU", "Harvard University":"Harvard",
                "MIT":"MIT", "Northeastern University":"Northeastern",
                "Tufts University":"Tufts", "UMass Boston":"UMass Boston"}
        return unis[elem]
    
    # apply shorthand
    stipends["Univ. Shorthand"] = stipends["University"].apply(uni_shorthand)

    # get avg each year
    avg_by_year = stipends[["Academic Year", "University", "Univ. Shorthand", "Overall Pay"]
                           ].groupby(["Academic Year", "University", "Univ. Shorthand"]
                            ).mean().reset_index()
    
    # Colors: neu is red, all others are varying shades of desaturated colors
    colors = {
        "Northeastern University":'#C8102E',
        "Boston University":  '#A3C9E2',
        "Harvard University": '#D9C5A1',
        "MIT":  '#A8D8AE',
        "Tufts University":  '#C9B8DC',
        "UMass Boston": '#E5B8B8'
    }

    def rounded_stipend(elem):
        return f"{round(elem, -3)}"[:2]
    
    # round to k
    avg_by_year["Pay Rounded"] = avg_by_year["Overall Pay"].apply(rounded_stipend)

    # make the line plot
    stipends_over_time = px.line(
        avg_by_year,
        x="Academic Year",
        y="Overall Pay",
        color="University",
        color_discrete_map=colors,
        markers=True,
        custom_data=["Univ. Shorthand", "Pay Rounded"]
    ).update_layout(
        yaxis_tickprefix = '$', 
        yaxis_tickformat = ',.0s',
        hovermode = 'x unified',  # Changed from 'x unified'
        xaxis_title="Academic Year"
    ).update_yaxes(
        title="Overall Pay (Average)"
    ).update_xaxes(
        tickmode='linear',
        dtick=1
    ).update_traces(
        hovertemplate= 
        "<b>%{customdata[0]}</b><br>" +
        "Average Pay: $%{customdata[1]}k<extra></extra>"
    )

    # add dotted lines for lower and upper boundaries
    stipends_over_time.add_shape(
        type="line",
        x0=2010, x1=2025, 
        y0=63942, y1=63942,
        line=dict(color="#A2A2A2", dash="dash")
    )
    
    stipends_over_time.add_shape(
        type="line",
        x0=2024, x1=2026,  # Only from 2024 to 2025
        y0=63942, y1=63942,
        line=dict(color="#248f24", dash="dash")
    ).add_annotation(
        x=2020.5,
        y=63942,
        text="2025 Boston Living Wage: $63,942",
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
        font=dict(color="#248f24")
    )

    stipends_over_time.add_hline(y=15650, line_dash="dash", annotation_text="Federal Poverty Line: $15,650", line=dict(color="#A2A2A2"))

    stipends_over_time.update_layout(
        plot_bgcolor = "rgba(0, 4, 255, 0.02)"
    )
    stipends_over_time.update_xaxes(
        gridcolor = "rgba(0, 4, 255, 0.05)"
    )

    for trace in stipends_over_time.data:
        if 'Northeastern' in trace.name:
            stipends_over_time.data = tuple([t for t in stipends_over_time.data if t != trace] + [trace])
            break

    # create layout
    layout = html.Div([
        dcc.Graph(figure=stipends_over_time),
        html.Div(
            ["Data Source: Living Wage Calculator (MIT) and Stipend Data Collected from ",
            html.A("phdstipends.com", href="https://www.phdstipends.com"),
            ]
        ),
        html.Div("Data is self-reported by graduate students across various departments and universities.")


    ])


    title = "Average Graduate Student Stipends have Increased but Remain Far Below a Living Wage"
    subtitle = "Comparison of Average Stipends at Six Boston-Area Universities to the 2025 Living Wage and Poverty Line in Boston"

    return layout , [], title, subtitle
