import numpy as np
import textwrap
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

'''--------------------- Data Processing ---------------------'''
def timeline_data():
    """
    Imports and formats data
    """
    negotiations = pd.read_csv("data/contract_negotiations.csv")
    negotiations["Start Date"] = pd.to_datetime(negotiations["Date"])
    
    # Sort negotiations by article and date to ensure proper ordering
    negotiations = negotiations.sort_values(["Article", "Start Date"], ascending=True)
    
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
        'Union Officers and Stewards':"Union (General)",
        'Recognition':"Union (General)",
        'Bargaining Ground Rules':"Union (Legal)",
        
        'No Strike No Lockout':"Union (Legal)", 
        'Successorship':"Union (Legal)", 
        'Comprehensive and Complete Agreement':"Union (Legal)", 
        'Severability':"Union (Legal)", 
        'Grievance and Arbitration':"Union (Legal)",
        
        
        'Hourly Assignments':"Employment (Requirements)",
        'Titles and Classifications':"Employment (Requirements)",
        'Employment Records':"Employment (Requirements)",
        'Appointments and Reappointments':"Employment (Requirements)",
        'Management Rights':"Employment (Requirements)",
        'Training':"Employment (Requirements)",
        
        
        'Appointment Security':"Employment (Protections)",
        'Job Postings':"Employment (Rights)",
        'International Worker Rights':"Employment (Rights)",
        'Workspace and Materials':"Employment (Rights)",
        'Holidays':"Employment (Rights)",
        'Travel':"Employment (Rights)",
        
        
        'Artificial Intelligence':"Employment (Protections)", 
        'Automation':"Employment (Protections)",
        'Sub-Contracting':"Employment (Protections)",
        'Prohibition Against Discrimination and Harassment':"Employment (Protections)",
        'Health and Safety':"Employment (Protections)",
        'Accessibility':"Employment (Protections)",
        'Discipline and Dismissal':"Employment (Rights)",
        
        
        'Housing':"Benefits", 
        'Parking and Transit':"Benefits", 
        'Relocation Assistance':"Benefits", 
        'Tax Assistance':"Benefits", 
        'Vacation and Personal Time':"Benefits", 
        'Professional Development':"Benefits",
        'Retirement':"Benefits",
        
        
        'Tuition and Fees':"Academic", 
        'FERPA Waiver Form':"Academic",
        'Intellectual Property':"Academic",
        'Professional and Academic Freedom':"Academic"
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
            return px.colors.sample_colorscale('Reds', value)[0]
        if party == "University":
            return px.colors.sample_colorscale('Teal', value)[0]
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
                         range_:list[pd.Timestamp], grouping_:str = "Employment (Requirements)"):
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
    subset['Duration'] = (subset['End Date'] - subset['Start Date']).dt.days
    
    # Consistent color dict of parties involved
    colordict = {color:color for color in negotiations["Color"].unique().tolist()}
    
    # Timeline: modified Gantt plot
    timeline = px.timeline(subset, 
                x_start=subset["Start Date"], 
                x_end=subset["End Date"],
                y="Article-wrap",
                color="Color",
                color_discrete_map=colordict,
                custom_data=["Article", "Date", "Change Count", "Duration"],
                labels={"Article-wrap":""},
                #opacity= # needs to be [0-1], search "Change Opacity"
                )

    # Timeline hover tooltip
    timeline.update_traces(hovertemplate= 
                        "<b>Topic:</b> %{y} <br>" +
                        "<b>Date: </b> %{customdata[1]} <br>" +
                        "<b>Duration until next change:</b> %{customdata[3]} days<br>" +  
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
        plot_bgcolor = "rgba(0, 4, 255, 0.02)",
        showlegend=False
    )
    
    # timeline.update_legends(
    #     title = "Party:",
    #     orientation = "h",
    #     yanchor = "bottom",
    #     y = 1.02,
    # )
    
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
        head_color = 'mediumaquamarine',
        header_title = f"<b>Changes (Tentative Agreement, {date})</b>"
    elif party[0] == 'Union':
        head_color = 'lightcoral',
        header_title = f"<b>Changes (proposed by Union, {date})</b>"
    else:
        head_color='lightsteelblue',
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
        title = "<br>".join(textwrap.wrap(f"What changed in the {article} article on {date}?", width=60)) \
            + "<br><sup>To see all of the changes, scroll down.</sup>",
        height = 500,
        margin={'t':90,'l':0,'b':0,'r':0},
        
    )
    # increasing font size
    fig.update_traces(cells_font=dict(size = 15), header_font = dict(size = 15))
    
    return fig

def final_changes_table(negotiations:pd.DataFrame, article:str):
    """
    Creates a table with the most recent summaries for all topics within an article

    Args:
        negotiations (pd.DataFrame): contract change data (for compatibility)
        article (str): specific article

    Returns:
        go.Figure: table chart with most recent summaries for all topics in the article
    """
    # Load the recent summaries CSV
    summaries = pd.read_csv("data/contract_recent_summaries.csv")
    
    # Filter to get all topics for this article
    article_summaries = summaries[summaries["Article"] == article]
    
    if article_summaries.empty:
        # If no summaries found, return empty figure
        return go.Figure()
    
    # Parse party and date from the first summary to determine color
    # (assuming all topics in an article have the same party/date for the most recent change)
    first_summary = article_summaries["Summary"].values[0]
    
    if first_summary.startswith("Tentative Agreement:"):
        head_color = 'aquamarine'
        header_title = "<b>Most Recent Language</b>"
    elif first_summary.startswith("Union ("):
        head_color = 'cornflowerblue'
        import re
        date_match = re.search(r'\((\d{2}-\d{2}-\d{2})', first_summary)
        date_str = f", {date_match.group(1)}" if date_match else ""
        header_title = f"<b>Most Recent Language (Union{date_str})</b>"
    elif first_summary.startswith("University ("):
        head_color = 'lightcoral'
        import re
        date_match = re.search(r'\((\d{2}-\d{2}-\d{2})', first_summary)
        date_str = f", {date_match.group(1)}" if date_match else ""
        header_title = f"<b>Most Recent Language (University{date_str})</b>"
    else:
        ld_formatted = last_date.date().strftime("%m/%d/%Y")
    final_changes:pd.DataFrame = negotiations.loc[(negotiations["Article"] == article) & (negotiations["Start Date"] == last_date)]
    # selecting party for color, keeping consistent with established color theme
    # but lightening it a little so that the text shows up and is readable
    party = final_changes["Party"].unique().tolist()
    if len(party) > 1 or party[0] == 'Tentative Agreement':
        head_color = 'mediumaquamarine',
        header_title = f"<b>Most Recent (Tentative Agreement, {ld_formatted})</b>"
    elif party[0] == 'Union':
        head_color = 'lightcoral',
        header_title = f"<b>Most Recent (Union, {ld_formatted})</b>"
    else:
        head_color='lightsteelblue',
        header_title= f"<b>Most Recent (University, {ld_formatted})</b>"
    
    # table
        # Default if format doesn't match
        head_color = 'lightgray'
        header_title = "<b>Most Recent Language</b>"
    
    # Clean the summary text (remove the party/date prefix) for all summaries
    clean_summaries = []
    for summary in article_summaries["Summary"]:
        clean_summary = re.sub(r'^(Tentative Agreement|Union \([^)]+\)|University \([^)]+\)):\s*', '', summary)
        clean_summaries.append(clean_summary)
    
    # Create table with two columns: Topic and Summary

    fig = go.Figure(data=go.Table(
        header=dict(
            values=["<b>Topic</b>", header_title], 
            fill_color=head_color, 
            align='left'
        ),
        cells=dict(
            values=[
                article_summaries["Topic"].tolist(),  # Topics column
                clean_summaries  # Cleaned summaries column
            ], 
            align='left',
        ),
        columnwidth=[0.25, 0.75]  # Adjust column widths: 25% for topics, 75% for summaries
    ))
    
    # Adding and formatting table title, adjusting margins to use full space
    fig.update_layout(
        title=" ",  # Most recent changes
        height = 500,
        margin={'t':90,'l':0,'b':0,'r':0}
    )
    # Increasing font size
    fig.update_traces(cells_font=dict(size = 15), header_font = dict(size = 15))
    
    return fig

def create_instruction_prompt():
    """
    Creates an instruction prompt to display instead of empty tables
    """
    return html.Div([
        html.Div([
            html.I(className="fas fa-hand-pointer fa-3x", style={'color': '#007bff', 'marginBottom': '20px'}),
            html.H4("Select a Proposal to Explore", style={'color': '#333', 'marginBottom': '15px'}),
            html.P("Click on any bar in the timeline above to view:", style={'fontSize': '16px', 'color': '#666'}),
            html.Ul([
                html.Li("Detailed changes made on that date", style={'marginBottom': '8px'}),
                html.Li("The party who proposed the changes", style={'marginBottom': '8px'}),
                html.Li("Topic-by-topic breakdown of modifications", style={'marginBottom': '8px'})
            ], style={'textAlign': 'left', 'display': 'inline-block', 'fontSize': '15px', 'color': '#666'}),
            html.Hr(style={'margin': '25px 0', 'opacity': '0.3'}),
            html.P([
                html.I(className="fas fa-info-circle", style={'marginRight': '8px'}),
                "Tip: Use the dropdown above to filter by different topic groups"
            ], style={'fontSize': '14px', 'color': '#888', 'fontStyle': 'italic'})
        ], style={
            'textAlign': 'center',
            'padding': '60px 40px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '10px',
            'border': '2px dashed #dee2e6',
            'height': '400px',
            'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'center',
            'alignItems': 'center'
        })
    ], style={'height': '100%'})

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
    
    # Topic group descriptions
    TOPIC_DESCRIPTIONS = {
        'Union (General)': 'The organization of the union and recognition by the university',
        'Union (Legal)': 'How the contract legally binds both parties',
        'Employment (Requirements)': 'What is a graduate student worker required to do as an employee of the university',
        'Employment (Rights)': 'What does a graduate student worker get as part of their work',
        'Employment (Protections)': "How are graduate student workers' rights protected",
        "Academic": 'Tuition and intellectual property/academic freedom',
        "Benefits": 'What are the benefits for being a graduate student worker'
    }
    
    def summarize_topic(topic):
        return TOPIC_DESCRIPTIONS.get(topic, "")
    
    # Default timeline is all dates, with a selected group
    timeline = negotiation_timeline(negotiations, TIMES, 
                                    [negotiations["Start Date"].min(), 
                                    negotiations["End Date"].max()], "Employment (Requirements)")
    
    # Create instruction prompt instead of default tables
    instruction_prompt = create_instruction_prompt()
    
    # Dash layout with improved dropdown section
    layout = html.Div([
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("Select Topic Group:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        options=sorted(negotiations["Group"].unique().tolist()),
                        value="Employment (Requirements)", 
                        id='timeline-group'
                    )
                ], width=5),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-info-circle", 
                               style={'color': '#007bff', 'marginRight': '8px', 'fontSize': '16px'}),
                        html.Span(
                            summarize_topic("Employment (Requirements)"),
                            id='topic-description',
                            style={
                                'fontSize': '14px', 
                                'color': '#495057',
                                'fontStyle': 'italic'
                            }
                        )
                    ], style={
                        'padding': '10px 15px',
                        'backgroundColor': '#f8f9fa',
                        'borderRadius': '5px',
                        'border': '1px solid #dee2e6',
                        'marginTop': '28px'
                    })
                ], width=7)
            ])
        ], style={'marginBottom': '20px'}),
        
        # main timeline graph
        dcc.Graph(
            figure=timeline,
            id="negotiation-timeline"
        ),
        
        # dates slider, evenly spaced
        html.Div([
            html.Div([
                dcc.RangeSlider(
                    min=0,
                    max=len(TIMES)-1,
                    step=1,
                    value=[0, len(TIMES)-1],
                    marks=dict((each, {"label": str(date.date().strftime("%m/%d/%y")), 
                                      "style":{"transform": "rotate(20deg)"}})
                            if each is not len(TIMES) - 1 
                            else (each, {"label": "Present", "style":{"transform": "rotate(20deg)"}})
                            for (each, date) in enumerate(TIMES)),
                    id="timeline-slider",
                ),
            ], style={'padding':'2rem 2rem', 'marginBottom': '35px'}),
            
            # sub-tables (linked to timeline)
            html.Div([
                html.Div(id='left-content-container', 
                    children=instruction_prompt,
                    style={
                        'width': '49%', 
                        'display': 'inline-block',
                        "overflowY": "auto",
                        'overflowX': 'hidden',
                        'minHeight': '500px'
                    }),
                html.Div(id='right-content-container',
                    children=html.Div(),
                    style={
                        'width': '49%', 
                        'float':'right', 
                        'display': 'inline-block', 
                        "overflowY": "auto",
                        'minHeight': '500px'
                    })
            ])
        ])
    ])
    
    # UPDATED CALLBACK: Now also updates the description
    def tl_slidergroup_callback(app):
        @app.callback(
            Output("negotiation-timeline", "figure"),
            Output("topic-description", "children"),
            Input("timeline-slider", "value"),
            Input('timeline-group', 'value'),
            suppress_callback_exceptions=True
        )
        def update_timeline(dates, group):
            return (
                negotiation_timeline(negotiations, TIMES, 
                                   [TIMES[dates[0]], TIMES[dates[1]]], group), 
                summarize_topic(group)
            )
    
    # update content containers
    def tl_content_callback(app):
        @app.callback(
            Output('left-content-container', 'children'),
            Output('right-content-container', 'children'),
            Input('negotiation-timeline', 'clickData'),
            prevent_initial_call=True,
            suppress_callback_exceptions=True
        )
        def update_content(clickData):
            if clickData is None or 'points' not in clickData:
                return create_instruction_prompt(), html.Div()
            
            try:
                article = clickData["points"][0]['customdata'][0]
                date = clickData["points"][0]['customdata'][1]
                
                table_fig = time_changes_table(negotiations, article, date)
                final_fig = final_changes_table(negotiations, article)
                
                left_content = dcc.Graph(figure=table_fig, id='changes-table')
                right_content = dcc.Graph(figure=final_fig, id='final-changes')
                
                return left_content, right_content
                
            except (KeyError, IndexError):
                return create_instruction_prompt(), html.Div()
        
    title = "How have contract negotiations progressed over time?"
    subtitle = "Use the dropdown to filter by topic group. Click on a bar in the timeline to see the specific changes made to that article on that date."
    
    return layout, [tl_slidergroup_callback, tl_content_callback], title, subtitle