import pandas as pd
import plotly.express as px
from dash import html, dcc, Input, Output
import utils

def department_stipend_avgs():
    """
    Creates Dash div and callbacks for the department stipend comparison line chart
    with college filtering capability
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
    
    # Define departments and college mapping
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

    dept_to_college = {
        'computer science': 'Khoury College of Computer Sciences',
        'psychology': 'College of Social Sciences and Humanities',
        'bioengineering': 'College of Engineering',
        'english': 'College of Social Sciences and Humanities',
        'sociology and anthropology': 'College of Social Sciences and Humanities',
        'political science': 'College of Social Sciences and Humanities',
        'mechanical and industrial engineering': 'College of Engineering',
        'electrical and computer engineering': 'College of Engineering',
        'biology': 'College of Science',
        'physics': 'College of Science',
        'history': 'College of Social Sciences and Humanities'
    }
    
    # Filter for departments with data
    neu_avgs = neu_stipends[neu_stipends["Department"].isin(depts_with_data)]
    # Filter out departments with <3 years of data
    dept_counts = neu_avgs["Department"].value_counts()
    sufficient_data_depts = dept_counts[dept_counts >= 3].index
    neu_avgs = neu_avgs[neu_avgs["Department"].isin(sufficient_data_depts)]

    # Add college column (before capitalizing department names)
    neu_avgs["College"] = neu_avgs["Department"].map(dept_to_college)
    
    # Capitalize department names
    neu_avgs["Department"] = neu_avgs["Department"].str.title()

    def rounded_stipend(elem):
        return f"{round(elem, -3)}"[:2]
    neu_avgs["Pay Rounded"] = neu_avgs["Overall Pay"].apply(rounded_stipend)
    
    # Get unique colleges for filter options
    unique_colleges = sorted(neu_avgs["College"].unique())
    
    # Create layout with filter
    layout = html.Div([
        html.Div([
            html.Label("Filter by College:", style={'fontWeight': 'bold', 'marginBottom': '10px', 'display': 'block'}),
            dcc.Checklist(
                id='stipend-college-filter',
                options=[{'label': " " + college, 'value': college} for college in unique_colleges],
                value=unique_colleges,  # Start with all colleges selected
                inline=True,
                labelStyle={'marginRight': '20px', 'cursor': 'pointer'},
                style={'display': 'flex', 'flexWrap': 'wrap'}
            )
        ], style={'marginBottom': '20px', 'padding': '10px', 'backgroundColor': '#f5f5f5', 'borderRadius': '5px'}),
        
        dcc.Graph(id='stipend-time-chart'),
        
        html.Div([
            "Data Source: Living Wage Calculator (MIT) and Stipend Data Collected from ",
            html.A("phdstipends.com", href="https://www.phdstipends.com"),
        ]),
        html.Div("Data is self-reported by graduate students across various departments and universities.")
    ])
    
    # Define callback function (to be registered in main app)
    def register_callbacks(app):
        @app.callback(
            Output('stipend-time-chart', 'figure'),
            Input('stipend-college-filter', 'value')
        )
        def update_stipend_chart(selected_colleges):
            # Filter data based on selection
            if selected_colleges:  # If any colleges are selected
                filtered_data = neu_avgs[neu_avgs["College"].isin(selected_colleges)]
            else:  # If no colleges are selected, show empty chart
                filtered_data = neu_avgs[neu_avgs["College"].isin([])]
            
            # Create visualization
            neu_stipends_time = px.line(
                filtered_data,
                x="Academic Year",
                y="Overall Pay",
                color="Department",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                markers=True,
                #height=500,
                custom_data=["Department", "Pay Rounded", "College"]
            )
            
            # Format y-axis for currency
            neu_stipends_time.update_layout(
                yaxis_tickprefix='$', 
                yaxis_tickformat=',.0s',
                xaxis_title="Academic Year",
                yaxis_title="Overall Pay (Average)",
                legend_title="Department",
                hovermode='x unified'
            ).update_traces(
                hovertemplate="<b>%{customdata[0]}</b><br>" +
                            "%{customdata[2]}<br>" +
                            "Average Pay: $%{customdata[1]}k<extra></extra>"
            ).update_xaxes(
                tickmode='linear',
                dtick=1
            )

            # Background and gridlines
            neu_stipends_time.update_layout(
                plot_bgcolor="rgba(0, 4, 255, 0.02)"
            )
            neu_stipends_time.update_xaxes(
                gridcolor="rgba(0, 4, 255, 0.05)"
            )

            # Add reference lines
            neu_stipends_time.add_shape(
                type="line",
                x0=2010, x1=2025, 
                y0=63942, y1=63942,
                line=dict(color="#A2A2A2", dash="dash")
            )
            
            neu_stipends_time.add_shape(
                type="line",
                x0=2024, x1=2026,
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

            neu_stipends_time.add_hline(
                y=15650, 
                line_dash="dash", 
                annotation_text="Massachusetts Poverty Line: $15,650", 
                line=dict(color="#A2A2A2")
            )
            
            return neu_stipends_time
    
    title = "Department Stipend Averages are Erratic Across Years"
    subtitle = "Some departments' stipends have increased, some decreased over time. Overall, stipends remain well below the living wage."
    
    # Return layout and callback registration function as a list to match app.py expectations
    return layout, [register_callbacks], title, subtitle