import pandas as pd
import plotly.graph_objects as go
from dash import State, dcc, html, Input, Output
import numpy as np
import dash_bootstrap_components as dbc
import utils
import re

def benefits():
    # Read the CSV
    benefits_df = pd.read_csv("data/health_insurance_comparison.csv")
    
    # Get unique universities and benefits
    universities = benefits_df['University'].unique()
    
    print(universities)

    networks = {
        'MIT': 'Blue Cross Blue Shield',
        'Harvard': 'Blue Cross Blue Shield',
        'Northeastern': 'Blue Cross Blue Shield',
        'Boston University': 'Aetna',
        'Tufts': 'United Healthcare',
        'UMass Boston': 'Blue Cross Blue Shield'
    }

    benefits_df['Network'] = benefits_df['University'].map(networks)
    
    # Define key benefits to display
    key_benefits = [
        'Deductible',
        'Out-of-Pocket Maximum',
        'Primary Care Visit',
        'Emergency Room',
        'Prescription Drugs (Generic)',
        'Mental Health Outpatient',
        'Dental (Adult)',
        'Vision Exam (Adult)',
        'Eyeglasses (Adult)',
        'Birth Control',
        'Diagnostic Tests (X-ray/Blood)',
        'Imaging (CT/MRI/PET)'
    ]
    
    # Filter for only key benefits
    benefits_df_filtered = benefits_df[benefits_df['Benefit'].isin(key_benefits)]

    # Create the unit chart figure
    benefits_fig_main = benefits_fig(universities, benefits_df_filtered)
    
    # Create initial details figure (default to Deductible)
    benefits_details_fig = benefit_details(universities, benefits_df_filtered, 'Deductible')
    
    # Create the Dash layout with side-by-side graphs
    div = html.Div([
        html.Div([
            html.Label("Filter by Network:", style={'fontWeight': 'bold', 'marginRight': '15px'}),
            dcc.RadioItems(
                id='benefits-network-filter',
                options=[{'label': 'All', 'value': 'All'}] + [{'label': net, 'value': net} for net in sorted(set(networks.values()))],
                value='All',
                inline=True,
                labelStyle={'marginRight': '20px', 'cursor': 'pointer'}
            )
        ], style={'marginBottom': '20px', 'padding': '10px', 'backgroundColor': '#f5f5f5', 'borderRadius': '5px'}),
        
        html.Div([
            # Left side - benefits unit chart
            html.Div([
                dcc.Graph(
                    id='benefits-unit-chart',
                    figure=benefits_fig_main,
                    config={'displayModeBar': False},
                    clickData={'points': [{'customdata': ['Deductible']}]}
                )
            ], style={'width': '68%', 'display': 'inline-block', 'verticalAlign': 'top', 'overflow': 'visible', 'zIndex': 1000}),
            
            # Right side - benefit details
            html.Div([
                dcc.Graph(
                    id='benefits-details-chart',
                    figure=benefits_details_fig,
                    config={'displayModeBar': False}
                ),
                html.Div(id='benefits-legend-container')  # Make legend dynamic too
            ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding':'none'})
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
            'margin': '0 auto',
            'overflow': 'visible'
        })
    ])

    # NEW CALLBACK: Filter by network
    def network_filter_callback(app):
        @app.callback(
            [Output('benefits-unit-chart', 'figure'),
             Output('benefits-details-chart', 'figure'),
             Output('benefits-legend-container', 'children')],
            [Input('benefits-network-filter', 'value')],
            [State('benefits-unit-chart', 'clickData')],
            suppress_callback_exceptions=True
        )
        def update_by_network(selected_network, clickData):
            # Filter universities by network
            if selected_network == 'All':
                filtered_unis = universities
            else:
                filtered_unis = [uni for uni, net in networks.items() if net == selected_network]
            
            # Filter benefits dataframe
            filtered_df = benefits_df_filtered[benefits_df_filtered['University'].isin(filtered_unis)]
            
            # Get selected benefit from clickData
            benefit_name = 'Deductible'  # default
            if clickData and 'points' in clickData:
                benefit_name = clickData['points'][0]['customdata'][0]
            
            # Update all three components
            new_unit_chart = benefits_fig(filtered_unis, filtered_df)
            new_details = benefit_details(filtered_unis, filtered_df, benefit_name)
            new_legend = benefits_legend(filtered_unis, filtered_df)
            
            return new_unit_chart, new_details, new_legend

    # EXISTING CALLBACK: Update details when clicking
    def benefits_details_callback(app):
        @app.callback(
            Output('benefits-details-chart', 'figure', allow_duplicate=True),
            Input('benefits-unit-chart', 'clickData'),
            State('benefits-network-filter', 'value'),
            prevent_initial_call=True,
            suppress_callback_exceptions=True
        )
        def update_details(clickData, selected_network):
            # Filter universities by network
            if selected_network == 'All':
                filtered_unis = universities
            else:
                filtered_unis = [uni for uni, net in networks.items() if net == selected_network]
            
            filtered_df = benefits_df_filtered[benefits_df_filtered['University'].isin(filtered_unis)]
            
            benefit_name = clickData["points"][0]['customdata'][0]
            return benefit_details(filtered_unis, filtered_df, benefit_name)
    
    title = 'Compare Northeastern with Other Universities on Health Insurance Benefits'
    subtitle = 'To see details for each benefit, hover over the icons. To see comparisons, click on an icon.'
    
    # Return BOTH callbacks
    return div, [network_filter_callback, benefits_details_callback], title, subtitle

# main figure, unit chart with the benefits
def benefits_fig(universities, benefits_df_filtered):
    # Create the figure
    fig = go.Figure()
    
    # Calculate max benefits on positive and negative sides separately
    max_positive = 0
    max_negative = 0

    # Calculate spacing parameters (top and bottom might be different)
    for uni in universities:
        uni_data = benefits_df_filtered[benefits_df_filtered['University'] == uni]
        positive_count = len(uni_data[uni_data['Coverage (Yes/No)'] == 'Yes'])
        negative_count = len(uni_data[uni_data['Coverage (Yes/No)'] == 'No'])
        max_positive = max(max_positive, positive_count) #num positive benefits
        max_negative = max(max_negative, negative_count) #num negative benefits

    # Icon size in pixels (marker size + some padding)
    icon_total_height_px = 45 
    
    # Calculate height of the chart
    margin_top_bottom = 20
    chart_area_height = (max_positive + max_negative) * icon_total_height_px
    dynamic_height = margin_top_bottom + chart_area_height
    
    # Calculate different spacing for positive and negative sides
    # We'll use different y-ranges for each side
    if max_positive > 0:
        positive_range = max_positive 
        positive_spacing = positive_range / max_positive
    else:
        positive_range = 1
        positive_spacing = 1
        
    if max_negative > 0:
        negative_range = max_negative 
        negative_spacing = negative_range / max_negative
    else:
        negative_range = 1
        negative_spacing = 1
    
    # Colors for yes/no
    color_yes = "#1c7cfa"
    color_no = "#f7af3b"
    
    # Calculate positions for each university
    uni_positions = {uni: i for i, uni in enumerate(universities)}
    
    # Add scatter points for each benefit
    for uni in universities:
        uni_data = benefits_df_filtered[benefits_df_filtered['University'] == uni]
        
        # Track y position for stacking
        y_pos_positive = positive_spacing / 2
        y_pos_negative = -negative_spacing / 2
        
        for _, row in uni_data.iterrows():
            benefit = row['Benefit']
            has_benefit = row['Coverage (Yes/No)'] == 'Yes'
            details = row['Details'] if pd.notna(row['Details']) else 'No details available'
            
            # Get icon
            icon = utils.benefit_icons.get(benefit, '❓')
            
            # Set position and color based on coverage   
            if has_benefit:
                y = y_pos_positive
                y_pos_positive += positive_spacing
                color = color_yes
            else:
                y = y_pos_negative
                y_pos_negative -= negative_spacing
                color = color_no
            
            # Add the point
            fig.add_trace(go.Scatter(
                x=[uni_positions[uni]],
                y=[y],
                mode='markers+text',
                marker=dict(
                    size=30,
                    color=color,
                    line=dict(color='white', width=2)
                ),
                text=[icon],
                textposition="middle center",
                textfont=dict(size=20),
                customdata=[[benefit, utils.wrap_text(details, width=40)]],  # Wrap the details text because its going off the screen
                hovertemplate=( # custom tooltips
                    f"<b>{uni}</b><br>"
                    f"<b>{benefit}</b><br>"
                    f"Coverage: {'Yes' if has_benefit else 'No'}<br>"
                    f"<i>%{{customdata[1]}}</i>"  # Use the wrapped text from customdata
                    "<extra></extra>"
                ),
                showlegend=False
            ))
    
    # Set y-axis range based on actual usage
    y_buffer = 1
    y_min = -(negative_range + y_buffer) if max_negative > 0 else -2
    y_max = positive_range + y_buffer if max_positive > 0 else 2
    
    # Add background shapes for upper and lower sections
    # Lower section ( warm yellow ) background)
    fig.add_shape(
        type="rect",
        xref="paper", yref="y",
        x0=0, y0=y_min,
        x1=1, y1=0,
        fillcolor="rgba(255, 200, 100, 0.3)",  # Light warm yellow with transparency
        line=dict(width=0),
        layer="below"
    )

    # Upper section (blue background)
    fig.add_shape(
        type="rect",
        xref="paper", yref="y",
        x0=0, y0=0,
        x1=1, y1=y_max,
        fillcolor="rgba(100, 150, 255, 0.3)",  # Light blue with transparency
        line=dict(width=0),
        layer="below"
    )
    
    # Add text annotations for "Included" and "Excluded"
    fig.add_annotation(
        x=len(universities) - 0.5,  # Position at the right edge
        y=y_max / 2,  # Middle of the positive section
        text="Included",
        showarrow=False,
        xref="x",
        yref="y",
        xanchor="left",
        yanchor="middle",
        font=dict(size=16, color=color_yes, family="Arial, sans-serif"),
        xshift=10  # Shift slightly to the right
    )
    
    fig.add_annotation(
        x=len(universities) - 0.5,  # Position at the right edge
        y=y_min / 2,  # Middle of the negative section
        text="Excluded",
        showarrow=False,
        xref="x",
        yref="y",
        xanchor="left",
        yanchor="middle",
        font=dict(size=16, color=color_no, family="Arial, sans-serif"),
        xshift=10  # Shift slightly to the right
    )

    # Update layout
    fig.update_layout(
        # assign x ticks to university
        xaxis=dict(
            ticktext=list(universities),
            tickvals=list(range(len(universities))),
            tickmode='array',
            title='',
            tickfont=dict(size=14),
            range=[-0.5, len(universities) - 0.5],
            showgrid=False  # Add this
        ),
        # assign y ticks to calculated height of the scatter
        yaxis=dict(
            title='Benefit Inclusion in Graduate Student Health Insurance',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#666',
            gridcolor='rgba(224, 224, 224, 0.5)',
            tickvals=[],
            range=[y_min, y_max],
            fixedrange=True,
            showgrid=False  # Add this
        ),
        # label and hovering details
        plot_bgcolor='white',
        paper_bgcolor='#f5f5f5',
        height=dynamic_height,
        margin=dict(l=80, r=90, t=20, b=60),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )

    # remove gridlines (keep these but add showgrid above too)
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False)

    # center 0 line
    fig.add_hline(y=0, line_dash="solid", line_color="#666", line_width=2)

    return fig

def benefit_details(universities, benefits_df_filtered, selected_benefit='Deductible'):
    """
    Creates a bar chart for any benefit with automatic value extraction
    """
    fig = go.Figure()
    
    # Get data for the selected benefit
    benefit_data = []
    value_type = None
    
    for uni in universities:
        # get uni data
        uni_data = benefits_df_filtered[
            (benefits_df_filtered['University'] == uni) & 
            (benefits_df_filtered['Benefit'] == selected_benefit)
        ]
        
        if not uni_data.empty:
            # get coverage status and details
            has_coverage = uni_data.iloc[0]['Coverage (Yes/No)'] == 'Yes'
            details = uni_data.iloc[0]['Details'] if has_coverage else 'Not covered'
            
            if has_coverage:
                # get the values to put in the bar chart
                value, vtype = get_best_comparison_value(details, selected_benefit)

                if value is not None:
                    benefit_data.append({
                        'University': uni, 
                        'Value': value,
                        'ValueType': vtype,
                        'Details': details,
                        'HasValue': True
                    })
                    if value_type is None:
                        value_type = vtype
                else:
                    # No numerical value found but has coverage
                    benefit_data.append({
                        'University': uni, 
                        'Value': 1,
                        'ValueType': 'coverage',
                        'Details': details,
                        'HasValue': False
                    })
            else:
                benefit_data.append({
                    'University': uni, 
                    'Value': 0,
                    'ValueType': 'coverage',
                    'Details': 'Not covered',
                    'HasValue': False
                })
    
    if not benefit_data:
        return fig
    
    df = pd.DataFrame(benefit_data)

#    Sort universities alphabetically
    df = df.sort_values(by='University')

    # Get the sorted university order to enforce consistency
    university_order = sorted(universities)  # Use the input universities list

    # Check if we have numerical values to compare
    has_numerical = any(df['HasValue'])

    numerical_df = df[df['HasValue']].copy()
    no_value_df = df[~df['HasValue']].copy()

    
    if has_numerical:
        
        # Create numerical comparison chart
        # Calculate the mean of numerical values
        mean_value = numerical_df['Value'].mean()
        
        # Set a small minimum value for visualization (so 0s dont show as just nothing)
        min_bar_height = min(mean_value * 0.01, 1) if mean_value > 0 else 0.1
        
        # Determine if this is a cost benefit (lower is better) manually
        cost_benefits = ['Deductible', 'Out-of-Pocket Maximum', 'Primary Care Visit', 
                        'Emergency Room', 'Urgent Care', 'Specialist Visit', 
                        'Prescription Drugs', 'Imaging', 'Diagnostic Tests']
        is_cost_benefit = any(cost_word in selected_benefit for cost_word in cost_benefits)

        selected_icon = utils.benefit_icons.get(selected_benefit, '❓')
        
        # Determine colors for numerical values
        if is_cost_benefit:
            # For costs: below mean is good (blue), above is bad (yellow)
            bar_colors = ['#1c7cfa' if v <= mean_value else '#f7af3b' for v in numerical_df['Value']]
        else:
            # For coverage amounts: above mean is good (blue), below is bad (yellow)
            bar_colors = ['#1c7cfa' if v >= mean_value else '#f7af3b' for v in numerical_df['Value']]
        
        # Format text based on value type
        if value_type == 'dollar':
            text_values = ['${:,.0f}'.format(v) for v in numerical_df['Value']]
            y_title = 'Cost ($)'
            mean_text = f'Mean: ${mean_value:,.0f}'
        elif value_type == 'percent':
            text_values = ['{:.0f}%'.format(v) for v in numerical_df['Value']]
            y_title = 'Percentage'
            mean_text = f'Mean: {mean_value:.0f}%'
        else:
            text_values = ['{:.0f}'.format(v) for v in numerical_df['Value']]
            y_title = 'Count'
            mean_text = f'Mean: {mean_value:.0f}'
        
        # Add bars for universities with values
        fig.add_trace(go.Bar(
            x=numerical_df['University'],
            y=numerical_df['Value'],
            marker_color=bar_colors,
            text=text_values,
            textposition='auto',
            customdata=[utils.wrap_text(d, width=50) for d in numerical_df['Details']],
            hovertemplate='<b>%{x}</b><br>%{text}<br>%{customdata}<extra></extra>',
            name='With values'
        ))
        
        # Add bars for universities without values (if any)
        if not no_value_df.empty:
            # Color for no coverage: blue for cost benefits, yellow for coverage benefits
            no_coverage_color = '#1c7cfa' if is_cost_benefit else '#f7af3b'
            
            fig.add_trace(go.Bar(
                x=no_value_df['University'],
                y=[min_bar_height] * len(no_value_df),  # Small height to make visible
                marker_color=no_coverage_color,
                text=['$0' if value_type == 'dollar' else '0'] * len(no_value_df),
                textposition='outside',
                customdata=[utils.wrap_text(d, width=50) for d in no_value_df['Details']],
                hovertemplate='<b>%{x}</b><br>%{text}<br>%{customdata}<extra></extra>',
                name='No data'
            ))
        
        # Add horizontal mean line
        fig.add_hline(
            y=mean_value,
            line_dash="dash",
            line_color="#666",
            line_width=2,
            annotation_text=mean_text,
            annotation_position="top right"
        )
        
        fig.update_layout(
            title=utils.wrap_text(f'{selected_icon} {selected_benefit} Comparison', width = 30),
            xaxis_title='University',
            yaxis_title=y_title,
            height=400,
            width=360,
            showlegend=False,
            bargap=0.2,
            margin = {'t':75,'l':5,'b':0,'r':0},
            xaxis=dict(
                categoryorder='array',
                categoryarray=university_order  # Force this order
            )
        )
        # remove gridlines
        fig.update_yaxes(showgrid=False)
        fig.update_xaxes(categoryorder='array', categoryarray=university_order)
    else:
        # Coverage status chart (no numerical values found)
        if not no_value_df.empty:
            fig.add_trace(go.Bar(
                x=no_value_df['University'],
                y=[0] * len(no_value_df),
                marker_color='#95a5a6',
                text=['No data' if row['Value'] == 1 else 'Not covered' 
                    for _, row in no_value_df.iterrows()],
                textposition='inside',
                customdata=[utils.wrap_text(d, width=50) for d in no_value_df['Details']],
                hovertemplate='<b>%{x}</b><br>%{text}<br>%{customdata}<extra></extra>',
                name='No data'
            ))

        fig.update_layout(
            title=utils.wrap_text(f'{selected_benefit} Coverage by University', width = 30),
            xaxis_title='University',
            yaxis=dict(visible=False),
            height=400,
            width=360,
            showlegend=False,
            margin = {'t':75,'l':15,'b':0,'r':0}
        )

        fig.update_xaxes(categoryorder='array', categoryarray=university_order)
    
    return fig


def benefits_legend(universities, benefits_df_filtered):
    """
    Creates a legend for the benefits unit chart with styled tooltips
    """
    all_icons = utils.benefit_icons
    
    benefit_descriptions = {
        'Deductible': 'The amount you pay out-of-pocket before insurance starts covering costs',
        'Out-of-Pocket Maximum': 'The most you will pay in a year; after this, insurance covers 100%',
        'Primary Care Visit': 'Cost to see your regular doctor for routine checkups and non-emergency care',
        'Emergency Room': 'Cost for emergency medical care at a hospital emergency department',
        'Diagnostic Tests (X-ray/Blood)': 'Cost for medical tests like X-rays and blood work ordered by your doctor',
        'Imaging (CT/MRI/PET)': 'Cost for advanced imaging scans like CT, MRI, or PET scans',
        'Mental Health Outpatient': 'Cost for therapy or counseling sessions with mental health professionals',
        'Prescription Drugs (Generic)': 'Cost for generic (non-brand name) prescription medications',
        'Birth Control': 'Coverage for contraceptive medications and devices',
        'Vision Exam (Adult)': 'Cost for routine eye exams to check vision and eye health',
        'Eyeglasses (Adult)': 'Coverage or discount for prescription eyeglasses or frames',
        'Dental (Adult)': 'Coverage for dental care including cleanings, fillings, and procedures'
    }
    
    legend_items = []
    tooltips = []
    
    for idx, (benefit, icon) in enumerate(all_icons.items()):
        if benefit in benefits_df_filtered['Benefit'].values:
            item_id = f"benefit-legend-{idx}"
            
            legend_items.append(
                html.Div([
                    html.Span(icon, style={'fontSize': '12px', 'marginRight': '5px'}),
                    html.Span(benefit, style={'fontSize': '10px'})
                ], 
                id=item_id,
                style={
                    'display': 'flex', 
                    'alignItems': 'center', 
                    'marginBottom': '8px',
                    'cursor': 'help'
                })
            )
            
            tooltips.append(
                dbc.Tooltip(
                    benefit_descriptions.get(benefit, ''),
                    target=item_id,
                    placement="top"
                )
            )
    
    return html.Div([
        html.Div(
            legend_items, 
            style={
                'marginTop': '20px',
                'marginLeft': '20%',
                'display': 'grid',
                'gridTemplateColumns': '1fr 1fr',
                'gap': '10px'
            }
        ),
        *tooltips  # Add all tooltips
    ])

def extract_numerical_values(details_text):
    """
    Automatically extract numerical values from benefit details text.
    Returns a list of found values with their context.
    """
    
    if pd.isna(details_text) or details_text == 'Not covered' or details_text == 'No':
        return []
    
    values = []
    
    # First, find all dollar amounts with their full context
    dollar_pattern = r'(?:([^$]{0,30})\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)([^$]{0,30}))'
    
    for match in re.finditer(dollar_pattern, details_text):
        # splits into 3 sections and checks for context
        before_context = match.group(1).lower()
        value = float(match.group(2).replace(',', ''))
        after_context = match.group(3).lower()
        
        # Skip if this is part of a date/time context (like "30 days")
        if any(time_word in after_context.split()[:3] for time_word in ['days', 'day', 'months', 'month', 'years', 'year', 'hours', 'hour']):
            continue
            
        # Determine priority based on context
        priority = 5  # Default low priority
        
        # Highest priority for individual/member costs
        if any(word in before_context + after_context for word in ['individual', 'member', 'person']):
            priority = 1
        # High priority for in-network
        elif 'in-network' in before_context or 'in network' in before_context:
            priority = 2
        # Good priority for generic/tier 1/retail
        elif any(word in before_context + after_context for word in ['generic', 'tier 1', 'retail', 'copay', 'visit']):
            priority = 3
        # Lower priority for family/out-of-network
        elif any(word in before_context + after_context for word in ['family', 'out-of-network', 'out of network']):
            priority = 6
        
        values.append({
            'value': value,
            'type': 'dollar',
            'context': before_context.strip() + " $" + str(value) + " " + after_context.strip(),
            'priority': priority,
            'full_match': match.group(0)
        })
    
    # Find percentages
    percent_pattern = r'(\d+)%(?!\s*(?:days?|months?|years?))'
    for match in re.finditer(percent_pattern, details_text):
        value = float(match.group(1))
        values.append({
            'value': value,
            'type': 'percent',
            'context': 'percentage',
            'priority': 7,
            'full_match': match.group(0)
        })
    
    # Find visit/day limits
    visit_pattern = r'(\d+)\s+(?:visits?|sessions?)\s+(?:per|/)'
    for match in re.finditer(visit_pattern, details_text, re.IGNORECASE):
        value = float(match.group(1))
        values.append({
            'value': value,
            'type': 'count',
            'context': 'visit limit',
            'priority': 8,
            'full_match': match.group(0)
        })
    
    # Sort by priority and return
    return sorted(values, key=lambda x: (x['priority'], x['value']))

def get_best_comparison_value(details_text, benefit_name):
    """
    Get the best numerical value for comparison on the bar chart based on the benefit type
    """
    values = extract_numerical_values(details_text)
    
    if not values:
        return None, None
    
    # For prescription drugs, we want the lowest cost (generic/tier 1)
    if 'Prescription' in benefit_name:
        # Filter to only dollar values
        dollar_values = [v for v in values if v['type'] == 'dollar']
        if dollar_values:
            # For prescriptions, lower is better, so take the minimum
            # But prioritize based on context first
            best_value = min(dollar_values, key=lambda x: (x['priority'], x['value']))
            return best_value['value'], best_value['type']
    
    # For benefits that are coverage amounts (higher is better)
    coverage_benefits = ['Vision', 'Dental', 'Hearing Aids', 'Eyeglasses']
    
    # Check if this is a cost-based or coverage-based benefit
    is_coverage = any(coverage_word in benefit_name for coverage_word in coverage_benefits)
    
    # If it's a coverage benefit and we have multiple values, 
    # we want the highest value instead of the first
    if is_coverage and len(values) > 1:
        # For coverage benefits, higher values are usually better
        # Sort by value descending
        values_sorted = sorted(values, key=lambda x: x['value'], reverse=True)
        best_value = values_sorted[0]
    else:
        # For cost benefits or unknown types, use priority system
        best_value = values[0] 
    
    return best_value['value'], best_value['type']

if __name__ == "__main__":
    div, callbacks = benefits()
