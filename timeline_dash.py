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
    
    # Sort negotiations by article and date to ensure proper ordering
    negotiations = negotiations.sort_values(["Article", "Start Date"])
    
    # Add "end" date for each timeline segment
    def next_end(df:pd.DataFrame, article:str, start:pd.Timestamp):
        """
        Find the next change to the same article. 
        If no further changes, extend to final date
        """
        temp_times = df[df["Article"] == article]["Start Date"].unique()
        # all the times later than current time
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
    #topics = negotiations["Article"].unique().tolist()
    topics = {
        'Labor Management Committee':"Union (General)", 
        'Union Security':"Union (General)", 
        'Union Access and Rights':"Union (General)", 
        'No Strike No Lockout':"Union (General)", 
        'Union Officers and Stewards':"Union (General)",
        'Recognition':"Union (General)",
        'Bargaining Ground Rules':"Union (Legal)", 
        'Successorship':"Union (Legal)", 
        'Comprehensive and Complete Agreement':"Union (Legal)", 
        'Severability':"Union (Legal)", 
        'Grievance and Arbitration':"Union (Legal)",
        'Employment Records':"Employment 1", 
        'Discipline and Dismissal':"Employment 1",
        'Sub-Contracting':"Employment 1", 
        'Retirement':"Employment 1", 
        'Hourly Assignments':"Employment 1",
        'Training':"Employment 3",
        'Job Postings':"Employment 2", 
        'International Worker Rights':"Employment 2", 
        'Management Rights':"Employment 2", 
        'Titles and Classifications':"Employment 2", 
        'Workspace and Materials':"Employment 2",
        'Artificial Intelligence':"Employment 3", 
        'Automation':"Employment 3", 
        'Appointments and Reappointments':"Employment 3",
        'Appointment Security':"Employment 3",
        'Housing':"Benefits", 
        'Parking and Transit':"Benefits", 
        'Relocation Assistance':"Benefits", 
        'Tax Assistance':"Benefits", 
        'Vacation and Personal Time':"Benefits", 
        'Professional Development':"Benefits", 
        'Travel':"Other",
        'Tuition and Fees':"Academic", 
        'FERPA Waiver Form':"Academic",
        'Intellectual Property':"Academic",
        'Professional and Academic Freedom':"Academic",
        'Accessibility':"Other", 
        'Prohibition Against Discrimination and Harassment':"Other", 
        'Health and Safety':"Benefits",
        'Holidays':"Other"
    }

    def category(article:str):
        """
        Quickly sorting articles into groups of 5-6
        Can/should be changed later to thematic groups
        """
        #return f"Article Group {int(np.floor(topics.index(article)/6)) + 1}"
        return topics[article]
    
    negotiations["Group"] = negotiations["Article"].apply(category)
    
    
    wrapped_articles = {article:"<br>".join(textwrap.wrap(article, width=20)) for article in negotiations["Article"].unique()}
    negotiations["Article-wrap"] = negotiations['Article'].apply(
        lambda x: wrapped_articles[x]
    )
    
    # Count number of changes per article per date
    change_count = negotiations.groupby(["Article", "Start Date"])["Party"]\
        .count().reset_index().rename(columns={"Party":"Count"})
    
    change_count["Start Date"] = change_count['Start Date'].dt.strftime('%Y-%m-%d')
    change_count = change_count.set_index(['Article', 'Start Date']).to_dict()['Count']
    
    def changes(counts:pd.DataFrame, article:str, start:pd.Timestamp):
        """
        Looking up the number of changes per article per date
        """
        return counts[(article, start.strftime('%Y-%m-%d'))]
    
    negotiations["Change Count"] = negotiations.apply(lambda x: changes(change_count, x["Article"], x["Start Date"]), axis=1)
    change_values = negotiations[["Article", "Change Count"]].groupby("Article").max().to_dict()['Change Count']
    
    negotiations["Change Value"] = negotiations.apply(
        lambda x: max(float(x["Change Count"]/change_values[x["Article"]]) - 0.15, 0.1), axis=1
    )
    
    def color_change(party, value):
        if party == "Union":
            return px.colors.sample_colorscale('Blues', value)[0]
        if party == "University":
            return px.colors.sample_colorscale('Reds', value)[0]
        else:
            return px.colors.sample_colorscale('Greens', value)[0]
    
    negotiations["Color"] = negotiations.apply(
        lambda x: color_change(x["Party"], x["Change Value"]), axis=1
    )
    
    # Wrap text of changes for tooltips
    # Not currently in use, as we could wrap within the plotly table
    # def split_string(elem):
    #     """
    #     Wraps the tooltip text so that it's max 70 characters wide
    #     """
    #     return "<br>".join(textwrap.wrap(elem))
    
    # negotiations["Changes from Previous (formatted)"] = negotiations["Changes from Previous Version"] # backslash here
    #     .apply(split_string)
    
    return negotiations

'''--------------------- Timeline Figure ---------------------'''

def negotiation_timeline(negotiations:pd.DataFrame, times:list[pd.Timestamp], 
                         range_:list[pd.Timestamp], grouping_:str = "Benefits"):
    """
    Creates the timeline figure for contract negotiations

    Args:
        negotiations (pd.DataFrame): contract change data
        times (list[pd.Timestamp]): list of all dates in contract data
        range_ (list[pd.Timestamp]): min and max dates to use
        grouping_ (str): category of articles

    Returns:
        go.Figure: modified Gantt plot
    """
    
    # Pull subset based on article group
    subset = negotiations[negotiations["Group"] == grouping_]
    
    # Consistent color dict of parties involved
    colordict = {color:color for color in negotiations["Color"].unique().tolist()}
    
    # Timeline: modified Gantt plot
    timeline = px.timeline(subset, 
                x_start=subset["Start Date"], 
                x_end=subset["End Date"],
                y="Article-wrap",
                color="Color",
                color_discrete_map=colordict,
                custom_data=["Article", "Date", "Change Count"],
                labels={"Article-wrap":"", "Color":""},
                #opacity= # needs to be [0-1], search "Change Opacity"
                )

    # Timeline hover tooltip
    timeline.update_traces(hovertemplate= 
                        "<b>Topic:</b> %{y} <br>" +
                        "<b>Date: </b> %{customdata[1]} <br>" +
                        "<b>Number of changes:</b> %{customdata[2]}<extra></extra>")
    
    timeline.update_traces(
        marker = dict(
            pattern = dict(
                path = "M0 0C3 4 4 5 8 9 4 12 3 14 0 18c4-4 7-6 12-9C7 6 4 3 0 0Z",
                size=23,
                solidity=0.7
            )
        )
    )
    
    # Adjusting x-axis to be consistently spaced
    present_dates=set(negotiations['Start Date']).union(set(negotiations["End Date"]))
    missing_dates = [d for d in pd.date_range(min(present_dates), \
                    max(present_dates), freq='D') if d not in present_dates]
    timeline.update_xaxes(rangebreaks = [dict(values=missing_dates)])

    # Renaming the x-axis to Mon DD, YY format, with the final "date" as "Present"
    # also updating margins to give it some more space
    timeline.update_layout(
        xaxis = dict(
            tickmode = "array",
            tickvals = times,
            ticktext = [time.date().strftime("%b %d, %Y") for time in times[:-1]] + ["Present"],
            range = range_,
            gridcolor = "rgba(0, 4, 255, 0.05)"
        ),
        margin={'t':75,'l':0,'b':0,'r':2},
        plot_bgcolor = "rgba(0, 4, 255, 0.02)"
    )
    
    timeline.update_legends(
        title = "Party:",
        orientation = "h",
        yanchor = "bottom",
        y = 1.02,
    )
    # Adding click option for linked charts
    timeline.update_layout(
        clickmode = 'event+select'
    )
    return timeline

'''--------------------- Changes Table Figure ---------------------'''

def time_changes_table(negotiations:pd.DataFrame, article:str, date:str):
    """
    Creates a table with the text of all the changes to the article on a given date

    Args:
        negotiations (pd.DataFrame): contract change data
        article (str): specific article
        date (str): date of change, string form instead of Timestamp for ease of use

    Returns:
        go.Figure: table chart with specific topic and the change made
    """
    # Choosing a subset of the data based on article/date
    subset = negotiations[(negotiations["Article"] == article) & (negotiations["Date"] == date)]
    
    # selecting party for color, keeping consistent with established color theme
    # but lightening it a little so that the text shows up and is readable
    party = subset["Party"].unique().tolist()
    if len(party) > 1 or party[0] == 'Tentative Agreement':
        head_color = 'aquamarine',
        header_title = f"<b>Changes (Tentative Agreement, {date})</b>"
    elif party[0] == 'Union':
        head_color = 'cornflowerblue',
        header_title = f"<b>Changes (proposed by Union, {date})</b>"
    else:
        head_color='lightcoral',
        header_title= f"<b>Changes (proposed by University, {date})</b>"
    
    # calculate max topic length for the left-hand column to be thin
    max_topic_length = subset["Topic"].str.len().max()
    max_changes_length = subset["Changes from Previous Version"].str.len().max()
    topic_proportion = max(0.2, min(0.3, max_topic_length / (max_topic_length + max_changes_length)))
    changes_proportion = 1 - topic_proportion

    # table
    fig = go.Figure(data=go.Table(
        header=dict(values=["<b>Topic</b>", header_title], fill_color=head_color, align='left'),
        cells=dict(
            values=[
                subset["Topic"], 
                subset["Changes from Previous Version"],
                
            ], 
            align='left',
        ),
        columnwidth=[topic_proportion, changes_proportion]
    ))
    
    # adding and formatting table title, adjusting margins to use full space
    fig.update_layout(
        title = "<br>".join(textwrap.wrap(f"What changed in the {article} article on {date}?", width=60)),
        height = 500,
        margin={'t':75,'l':0,'b':0,'r':0}
    )
    # increasing font size
    fig.update_traces(cells_font=dict(size = 15), header_font = dict(size = 15))
    
    return fig

def final_changes_table(negotiations:pd.DataFrame, article:str):
    """
    Creates a table with the text of all the changes to the article on a given date

    Args:
        negotiations (pd.DataFrame): contract change data
        article (str): specific article

    Returns:
        go.Figure: table chart with specific topic and the change made
    """
    # Choosing a subset of the data based on article/date
    last_date = negotiations[negotiations["Article"] == article]['Start Date'].max()
    if last_date == pd.to_datetime('2025-05-30'):
        ld_formatted = "Present"
    else:
        ld_formatted = last_date.date().strftime("%m/%d/%Y")
    final_changes:pd.DataFrame = negotiations.loc[(negotiations["Article"] == article) & (negotiations["Start Date"] == last_date)]
    # selecting party for color, keeping consistent with established color theme
    # but lightening it a little so that the text shows up and is readable
    party = final_changes["Party"].unique().tolist()
    if len(party) > 1 or party == 'Tentative Agreement':
        head_color = 'aquamarine',
        header_title = f"<b>Current Version (Tentative Agreement, {ld_formatted})</b>"
    elif party == 'Union':
        head_color = 'cornflowerblue',
        header_title = f"<b>Current Version (Union, {ld_formatted})</b>"
    else:
        head_color='lightcoral',
        header_title= f"<b>Current Version (University, {ld_formatted})</b>"
    
    # table
    fig = go.Figure(data=go.Table(
        header=dict(values=[header_title], fill_color=head_color, align='left'),
        cells=dict(
            values=[
                final_changes["Changes from Previous Version"]
            ], 
            align='left',
        )
    ))
    
    # adding and formatting table title, adjusting margins to use full space
    fig.update_layout(
        title=" ", # Most recent changes
        height = 500,
        margin={'t':75,'l':0,'b':0,'r':0}
    )
    # increasing font size
    fig.update_traces(cells_font=dict(size = 15), header_font = dict(size = 15))
    
    return fig

'''--------------------- Changes Bar Chart Figure ---------------------'''

def time_changes_bars(negotiations:pd.DataFrame, article:str):
    """
    Creates a bar chart showing the number of changes over time for a given article

    Args:
        negotiations (pd.DataFrame): contract change data
        article (str): specific article to examine

    Returns:
        go.Figure: bar chart with x-axis of dates and y-axis of count of change
    """
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
        title= "<br>".join(textwrap.wrap(f"Changes to the {article} article", width=40))
    )
    
    # Integers only on the y-axis
    fig.update_yaxes(
        tickmode='linear',
        dtick=2,
        tickformat = ',d'
    )
    
    # Updating tooltip to show relevant data
    fig.update_traces(hovertemplate= 
                        "<b>Party:</b> %{customdata[0]} <br>" +
                        "<b>Date: </b> %{x} <br>" +
                        "<b>Number of changes:</b> %{y}<extra></extra>")
    
    # setting bar width to be a fixed size
    ## apparently plotly does this in milliseconds for time data???
    fig.update_traces(
        width = [1000 * 3600 * 24 * 9 for x in range(len(subset))]
    )
    
    # Legend is labeled with total number of changes
    fig.update_legends(
        title_text = f"Total changes: {int(subset['Change Count'].sum())}<br>",
        orientation = "h",
        yanchor = "bottom",
        y = -0.5,
    )
    # updating margins for spacing
    fig.update_layout(
        margin={'t':75,'l':5,'b':0,'r':0}
    )
    return fig
    
'''--------------------- Dash Components ---------------------'''
def timeline_negotiations():
    """
    Creates Dash div and callbacks for the timeline-related charts
    This is the function that gets imported into app.py

    Returns:
        html.Div: html code for the Dash layout
        callbacks: functions for interactivity
    """
    negotiations = timeline_data()
    
    # List of all dates
    TIMES = sorted(negotiations["Start Date"].unique())
    TIMES.append(pd.to_datetime("2025-05-30"))
    
    TOPICS = sorted(negotiations["Group"].unique())
    
    # Default timeline is all dates, with a selected group
    # Group has Health and Safety in it, to match the default linked charts
    timeline = negotiation_timeline(negotiations, TIMES, 
                                    [negotiations["Start Date"].min(), 
                                    negotiations["End Date"].max()], "Benefits")
    
    # Picked a starting table to show
    table = time_changes_table(negotiations, "Health and Safety", '8/26/2024')
    
    # matching default bar chart to the changes table
    #num_changes = time_changes_bars(negotiations, "Health and Safety")
    final_changes = final_changes_table(negotiations, "Health and Safety")
    
    # Dash layout
    layout = html.Div([
        html.Div([
        # group dropdown select
        dcc.Dropdown(
            options = sorted(negotiations["Group"].unique().tolist()),
            value="Benefits", 
            id='timeline-group')], style={'width': '49%', 'display': 'inline-block'}),
        # main timeline graph
        dcc.Graph(
            figure=timeline,
            id="negotiation-timeline",
            clickData={'points': [{'customdata': ['Article', 'Date']}]}
        ),
        # dates slider, evenly spaced
        html.Div([
            html.Div([
                dcc.RangeSlider(
                    min = 0,
                    max = len(TIMES)-1,
                    step=1,
                    value=[0, len(TIMES)-1],
                    #'''marks = dict((k, v.date().strftime("%m/%d/%y")) if k is not len(TIMES) - 1
                        #else (k, "Present") for (k,v) in enumerate(TIMES) ),'''
                    marks = dict((each, {"label": str(date.date().strftime("%m/%d/%y")), 
                                        "style":{"transform": "rotate(20deg)"}})
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
                )], style={'width': '63%', 'display': 'inline-block'}),
                html.Div([dcc.Graph(
                    # figure = num_changes,
                    # id='changes-bar'
                    figure=final_changes,
                    id='final-changes'
                )], style={'width': '35%', 'float':'right', 'display': 'inline-block'})
                ])
        ])
    
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
    
    # update 
    def tl_final_callback(app):
        @app.callback(
            Output('final-changes', 'figure'),
            Input('negotiation-timeline', 'clickData'),
            prevent_initial_call=True,
            suppress_callback_exceptions=True
        )
        def update_table(clickData):
            article = clickData["points"][0]['customdata'][0]
            return final_changes_table(negotiations, article)
    
    # # update change counts bars
    # def tl_bars_callback(app):
    #     @app.callback(
    #         Output('changes-bar', 'figure'),
    #         Input('negotiation-timeline', 'clickData'),
    #         prevent_initial_call=True,
    #         suppress_callback_exceptions=True
    #     )
    #     def update_bar(clickData):
    #         article = clickData["points"][0]['customdata'][0]
    #         return time_changes_bars(negotiations, article)
        
    title = "Timeline of Contract Negotiations"
    subtitle = ""
    
    # NOTE: removed tl bars callback temporarily
    return layout, [tl_slidergroup_callback, tl_table_callback, tl_final_callback], title, subtitle
