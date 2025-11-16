import pandas as pd
import plotly.express as px

def livingwage_vs_stipend():
    stipends = pd.read_csv("data/boston_stipends.csv")

    avg_by_year = stipends[["Academic Year", "University", "Overall Pay"]
                           ].groupby(["Academic Year", "University"]
                            ).mean().reset_index()

    stipends_over_time = px.line(
        avg_by_year,
        x="Academic Year",
        y="Overall Pay",
        color="University",
        markers=True,
        title="While average stipends have gone up,<br>they are still below a living wage for the Boston area"
    
    ).update_layout(
        yaxis_tickprefix = '$', yaxis_tickformat = ',.'

    ).update_yaxes(title="Overall Pay (Average)")

    stipends_over_time.add_hline(y=63942, line_dash="dash", annotation_text="2025 Boston Living Wage: $63,942", line=dict(color="#A2A2A2"))
    stipends_over_time.add_hline(y=15650, line_dash="dash", annotation_text="Masschusetts Poverty Line: $15,650", line=dict(color="#A2A2A2"))
    stipends_over_time.add_vline(x=2025, line_dash="dot", line=dict(color="#A2A2A2"))

    return stipends_over_time #returns fig obj for display

