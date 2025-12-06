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
    # filter out departments with <3 years of data
    dept_counts = neu_avgs["Department"].value_counts()
    sufficient_data_depts = dept_counts[dept_counts >= 3].index
    neu_avgs = neu_avgs[neu_avgs["Department"].isin(sufficient_data_depts)]

    # Capitalize department names
    neu_avgs["Department"] = neu_avgs["Department"].str.title()

    def rounded_stipend(elem):
        return f"{round(elem, -3)}"[:2]
    neu_avgs["Pay Rounded"] = neu_avgs["Overall Pay"].apply(rounded_stipend)
    
    # Create visualization
    neu_stipends_time = px.line(
        neu_avgs,
        x="Academic Year",
        y="Overall Pay",
        color="Department",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        markers=True,
        height=700,
        custom_data=["Department", "Pay Rounded"]
    )
    
    # Format y-axis for currency
    neu_stipends_time.update_layout(
        yaxis_tickprefix='$', 
        yaxis_tickformat=',.0s',
        xaxis_title="Academic Year",
        yaxis_title="Overall Pay (Average)",
        legend_title="Department",
        hovermode='x unified'
    ).update_traces(hovertemplate= 
                        "<b>%{customdata[0]}</b> <br>" +
                        "Average Pay: $%{customdata[1]}k<extra></extra>"
    ).update_xaxes(
        tickmode='linear',
        dtick=1
    )

    # background and gridlines
    neu_stipends_time.update_layout(
        plot_bgcolor = "rgba(0, 4, 255, 0.02)"
    )
    neu_stipends_time.update_xaxes(
        gridcolor = "rgba(0, 4, 255, 0.05)"
    )

        # add dotted lines for lower and upper boundaries
    neu_stipends_time.add_shape(
        type="line",
        x0=2010, x1=2025, 
        y0=63942, y1=63942,
        line=dict(color="#A2A2A2", dash="dash")
    )
    
    neu_stipends_time.add_shape(
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

    neu_stipends_time.add_hline(y=15650, line_dash="dash", annotation_text="Masschusetts Poverty Line: $15,650", line=dict(color="#A2A2A2"))



    # create layout
    layout = html.Div([
        dcc.Graph(figure=neu_stipends_time),
        html.Div(
            ["Data Source: Living Wage Calculator (MIT) and Stipend Data Collected from ",
            html.A("phdstipends.com", href="https://www.phdstipends.com"),
            ]
        ),
        html.Div("Data is self-reported by graduate students across various departments and universities.")
    ])
    
    title = "Department Stipend Averages are Erratic Across Years"
    subtitle ="Some departments' stipends have increased, some decreased over time. Overall, stipends remain well below the living wage."
    
    return layout , [], title, subtitle