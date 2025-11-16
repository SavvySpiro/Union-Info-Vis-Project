import pandas as pd
import numpy as np
import textwrap
import plotly.express as px
from dash import Dash, dcc, html

'''--------------------- Data Import ---------------------'''
negotiations = pd.read_csv("data/contract_negotiations.csv")

negotiations["Start Date"] = pd.to_datetime(negotiations["Date"])
times = sorted(negotiations["Start Date"].unique())
times.append(pd.to_datetime("2025-05-30")) # the "final time"

def end_date(elem):
    # creates an end date based on the next changed contract date
    time = times.index(elem)
    return times[time + 1]

negotiations["End Date"] = negotiations["Start Date"].apply(end_date)

def split_string(elem):
    # wraps the tooltip text so that it's max 70 characters wide
    return "<br>".join(textwrap.wrap(elem))

negotiations["Changes from Previous Version"] = negotiations["Changes from Previous Version"].apply(split_string)

ARTICLES = negotiations["Article"].unique()

'''--------------------- Figure ---------------------'''

timeline = px.timeline(negotiations, 
            x_start=negotiations["Start Date"], 
            x_end=negotiations["End Date"],
            y="Article",
            color="Party",
            custom_data="Changes from Previous Version",
            labels = {
                "Article":""
            })

timeline.update_traces(hovertemplate= 
                       "<b>Topic:</b> %{y} <br>" +
                       "<b>Date: </b> %{x} <br>" +
                       "%{customdata}<extra></extra>")

timeline.update_layout(
    xaxis = dict(
        tickmode = "array",
        tickvals = times,
        ticktext = [time.date().strftime("%b %d, %y") for time in times[:-1]] + ["Present"],
        fixedrange=True,
    )
)


'''--------------------- Dash App ---------------------'''

app = Dash()
app.layout = html.Div([
    dcc.Graph(figure=timeline)
])

app.run(debug=True)  # Turn off reloader if inside Jupyter