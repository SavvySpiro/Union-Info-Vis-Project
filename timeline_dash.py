import numpy as np
import textwrap
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback
import pandas as pd
import plotly.graph_objs as go

'''--------------------- Data Processing ---------------------'''
def timeline_data():
    """
    Imports and formats data
    """
    negotiations = pd.read_csv("data/contract_negotiations.csv")
    negotiations["Start Date"] = pd.to_datetime(negotiations["Date"])
    
    # Sort negotiations by date to ensure proper ordering
    negotiations = negotiations.sort_values(["Article", "Start Date"])
    
    # Add "end" date for each timeline segment
    def next_end(df, article, start):
        """
        Find the next change to the same article. 
        If no further changes, extend to final date
        """
        temp_times = df[df["Article"] == article]["Start Date"].unique()
        later = [x for x in temp_times if x > start]
        try:
            return sorted(later, key=lambda t: t - start)[0]
        except IndexError:
            return pd.to_datetime("2025-05-30")

    negotiations["End Date"] = negotiations.apply(
        lambda x: next_end(negotiations, x["Article"], x["Start Date"]), 
        axis=1
    )
    
    # Group topics into 5-6
    topics = negotiations["Article"].unique().tolist()

    def category(article):
        """
        Quickly sorting articles into groups of 5-6
        Can/should be changed later to thematic groups
        """
        return f"Article Group {int(np.floor(topics.index(article)/6)) + 1}"
    
    negotiations["Group"] = negotiations["Article"].apply(category)
    
    # Count number of changes per article per date
    change_count = negotiations.groupby(["Article", "Start Date"])["Party"]\
        .count().reset_index().rename(columns={"Party":"Count"})
    
    change_count["Start Date"] = change_count['Start Date'].dt.strftime('%Y-%m-%d')
    change_count = change_count.set_index(['Article', 'Start Date']).to_dict()['Count']
    
    def changes(counts, article, start):
        """
        Looking up the number of changes per article per date
        """
        return counts[(article, start.strftime('%Y-%m-%d'))]
    
    negotiations["Change Count"] = negotiations.apply(lambda x: changes(change_count, x["Article"], x["Start Date"]), axis=1)
    
    # Wrap text of changes for tooltips
    # Not currently in use
    '''def split_string(elem):
        """
        Wraps the tooltip text so that it's max 70 characters wide
        """
        return "<br>".join(textwrap.wrap(elem))
    
    negotiations["Changes from Previous (formatted)"] = negotiations["Changes from Previous Version"].apply(split_string)'''
    return negotiations

'''--------------------- Timeline Figure ---------------------'''

def negotiation_timeline(negotiations, times, range_, grouping_):
    
    # Pull subset based on article group
    subset = negotiations[negotiations["Group"] == grouping_]
    
    # Consistent color dict of parties involved
    colordict = {'Union':px.colors.qualitative.Plotly[0], 
                'University':px.colors.qualitative.Plotly[1],
                'Tentative Agreement':px.colors.qualitative.Plotly[2]}
    
    # Timeline: modified Gantt plot
    timeline = px.timeline(subset, 
                x_start=subset["Start Date"], 
                x_end=subset["End Date"],
                y="Article",
                color="Party",
                color_discrete_map=colordict,
                custom_data=["Article", "Date", "Change Count"],
                labels={"Article":""})

    # Timeline hover tooltip
    timeline.update_traces(hovertemplate= 
                        "<b>Topic:</b> %{y} <br>" +
                        "<b>Date: </b> %{customdata[1]} <br>" +
                        "<b>Number of changes:</b> %{customdata[2]}<extra></extra>")
    
    # Adjusting x-axis to be consistently spaced
    present_dates=set(negotiations['Start Date']).union(set(negotiations["End Date"]))
    missing_dates = [d for d in pd.date_range(min(present_dates), \
                    max(present_dates), freq='D') if d not in present_dates]
    timeline.update_xaxes(rangebreaks = [dict(values=missing_dates)])

    # Renaming the x-axis to Mon DD, YY format, with the final "date" as "Present"
    timeline.update_layout(
        xaxis = dict(
            tickmode = "array",
            tickvals = times,
            ticktext = [time.date().strftime("%b %d, %y") for time in times[:-1]] + ["Present"],
            range = range_,
        ),
    )
    # Adding click option for linked charts
    timeline.update_layout(
        clickmode = 'event+select'
    )
    return timeline

'''--------------------- Changes Table Figure ---------------------'''

def time_changes_table(negotiations, article, date):
    # Choosing a subset of the data based on article/date
    subset = negotiations[(negotiations["Article"] == article) & (negotiations["Date"] == date)]
    
    # selecting party for color, keeping consistent with established color theme
    party = subset["Party"].unique().tolist()
    if len(party) > 1 or party[0] == 'Tentative Agreement':
        head_color = 'aquamarine',
        header_title = f"<b>Changes (Tentative Agreement)</b>"
    elif party[0] == 'Union':
        head_color = 'cornflowerblue',
        header_title = f"<b>Changes (proposed by Union)</b>"
    else:
        head_color='lightcoral',
        header_title= f"<b>Changes (proposed by University)</b>"
    
    # table
    fig = go.Figure(data=go.Table(
        header=dict(values = ["Topic", header_title], fill_color=head_color, align='left'),
        cells = dict(values=[subset["Topic"], subset["Changes from Previous Version"]], align='left')
    ),)
    
    # adding and formatting table title
    fig.update_layout(
        title = "<br>".join(textwrap.wrap(f"What changed in the {article} article on {date}", width=40))
    )
    fig.update_traces(cells_font=dict(size = 15), header_font = dict(size = 15))
    
    return fig

'''--------------------- Changes Bar Chart Figure ---------------------'''

def time_changes_bars(negotiations, article):
    # select subset of data based on article, using "mean" to get the value of the change count per date
    subset = negotiations[(negotiations["Article"] == article)][['Start Date', 'Party', 'Change Count']]\
        .groupby(['Start Date', 'Party']).mean().reset_index()

    # Consistent color dict of parties involved
    colordict = {'Union':px.colors.qualitative.Plotly[0], 
                'University':px.colors.qualitative.Plotly[1],
                'Tentative Agreement':px.colors.qualitative.Plotly[2]}
    
    # generating the bar chart
    fig = px.bar(
        subset,
        x='Start Date',
        y='Change Count',
        color = 'Party',
        color_discrete_map=colordict,
        custom_data=["Party"],
        title= "<br>".join(textwrap.wrap(f"How many changes did the {article} article go through?", width=40))
    )
    
    # Integers only on the y-axis
    fig.update_yaxes(
        tickmode='linear',
        tickformat = ',d'
    )
    
    # Updating tooltip to show relevant data
    fig.update_traces(hovertemplate= 
                        "<b>Party:</b> %{customdata[0]} <br>" +
                        "<b>Date: </b> %{x} <br>" +
                        "<b>Number of changes:</b> %{y}<extra></extra>")
    
    # Legend is labeled with total number of changes
    fig.update_legends(
        title_text = f"Total changes: {int(subset['Change Count'].sum())}",
        orientation = "h",
        yanchor = "bottom",
        y = .99
    )
    return fig
    
'''--------------------- Dash Components ---------------------'''
def timeline_negotiations():
    negotiations = timeline_data()
    
    # List of all dates
    TIMES = sorted(negotiations["Start Date"].unique())
    TIMES.append(pd.to_datetime("2025-05-30"))
    
    # Default timeline is all dates, with a selected group
    # Group has Health and Safety in it, to match the default linked charts
    timeline = negotiation_timeline(negotiations, TIMES, 
                                    [negotiations["Start Date"].min(), 
                                    negotiations["End Date"].max()], "Article Group 3")
    
    # Picked a starting table to show
    table = time_changes_table(negotiations, "Health and Safety", '8/26/2024')
    
    # matching default bar chart to the changes table
    num_changes = time_changes_bars(negotiations, "Health and Safety")
    
    # Dash layout
    layout = html.Div([
        # title
        html.Div([html.H3("Timeline of Contract Negotiations"),
        # group dropdown select
        dcc.Dropdown(
            negotiations["Group"].unique().tolist(), 
            "Article Group 1", 
            id='timeline-group')], style={'width': '49%', 'display': 'inline-block'}),
        # main timeline graph
        dcc.Graph(
            figure=timeline,
            id="negotiation-timeline",
            clickData={'points': [{'customdata': ['Article', 'Date']}]}
        ),
        # dates slider, evenly spaced
        html.Div([
            dcc.RangeSlider(
                min = 0,
                max = len(TIMES)-1,
                step=1,
                value=[0, len(TIMES)-1],
                #'''marks = dict((k, v.date().strftime("%m/%d/%y")) if k is not len(TIMES) - 1
                    #else (k, "Present") for (k,v) in enumerate(TIMES) ),'''
                marks = dict((each, {"label": str(date.date().strftime("%m/%d/%y")), "style":{"transform": "rotate(20deg)"}})
                        if each is not len(TIMES) - 1 \
                        else (each, {"label": "Present", "style":{"transform": "rotate(20deg)"}})\
                        for (each, date) in enumerate(TIMES)),
                id="timeline-slider",
                
            ),], style={'padding':'2rem 2rem', 'marginBottom': '35px'}),
        # sub-tables (linked to timeline)
        html.Div(
            [html.Div([dcc.Graph(
                figure = table,
                id='changes-table'
            )], style={'width': '49%', 'display': 'inline-block'}),
            html.Div([dcc.Graph(
                figure = num_changes,
                id='changes-bar'
            )], style={'width': '49%', 'float':'right', 'display': 'inline-block'})])
    
    ])
    
    # select date range and article group
    def tl_slidergroup_callback(app):
        @app.callback(
            Output("negotiation-timeline", "figure"),
            Input("timeline-slider", "value"), # dates
            Input('timeline-group', 'value'), # "group" of attributes
            suppress_callback_exceptions=True
        )
        def update_timeline(dates, group):
            return negotiation_timeline(negotiations, TIMES, 
                                        [TIMES[dates[0]], TIMES[dates[1]]], group)
    # update changes table
    def tl_table_callback(app):
        @app.callback(
            Output('changes-table', 'figure'),
            Input('negotiation-timeline', 'clickData'),
            prevent_initial_call=True,
            suppress_callback_exceptions=True
        )
        def update_table(clickData):
            article = clickData["points"][0]['customdata'][0]
            date = clickData["points"][0]['customdata'][1]
            return time_changes_table(negotiations, article, date)
    # update change counts bars
    def tl_bars_callback(app):
        @app.callback(
            Output('changes-bar', 'figure'),
            Input('negotiation-timeline', 'clickData'),
            prevent_initial_call=True,
            suppress_callback_exceptions=True
        )
        def update_table(clickData):
            article = clickData["points"][0]['customdata'][0]
            return time_changes_bars(negotiations, article)
    
    return layout, [tl_slidergroup_callback, tl_table_callback, tl_bars_callback]