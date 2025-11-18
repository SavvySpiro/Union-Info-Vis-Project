import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, Input, Output
import numpy as np
import utils

def benefits():
    # Read the CSV
    benefits_df = pd.read_csv("data/health_insurance_comparison.csv")
    
    # Get unique universities and benefits
    universities = benefits_df['University'].unique()
    
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
            # Left side - benefits unit chart
            html.Div([
                dcc.Graph(
                    id='benefits-unit-chart',
                    figure=benefits_fig_main,
                    config={'displayModeBar': False},
                    clickData={'points': [{'customdata': ['Deductible']}]}  # Default selection
                )
            ], style={'width': '68%', 'display': 'inline-block', 'verticalAlign': 'top', 'overflow': 'visible', 'zIndex': 1000}),
            
            # Right side - benefit details
            html.Div([
                dcc.Graph(
                    id='benefits-details-chart',
                    figure=benefits_details_fig,
                    config={'displayModeBar': False}
                )
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

    # Create callback function (following the same pattern as timeline)
    def benefits_details_callback(app):
        @app.callback(
            Output('benefits-details-chart', 'figure'),
            Input('benefits-unit-chart', 'clickData'),
            prevent_initial_call=True,
            suppress_callback_exceptions=True
        )
        def update_details(clickData):
            # Extract benefit name from the clicked point
            # The hovertemplate has the benefit name in it
            point_data = clickData["points"][0]
            
            # Get the benefit name from customdata
            # We need to modify benefits_fig to include benefit name in customdata
            benefit_name = point_data['customdata'][0]
            
            return benefit_details(universities, benefits_df_filtered, benefit_name)
    
    title = 'University Health Insurance Benefits Comparison'
    subtitle = 'Click on benefit icons to see detailed comparisons'
    
    # Return layout and callback list just like timeline does
    return div, [benefits_details_callback], title, subtitle

def benefits_fig(universities, benefits_df_filtered):
    # Create the figure
    fig = go.Figure()
    
    # Calculate max benefits on positive and negative sides separately
    max_positive = 0
    max_negative = 0

    # Calculate spacing parameters
    for uni in universities:
        uni_data = benefits_df_filtered[benefits_df_filtered['University'] == uni]
        positive_count = len(uni_data[uni_data['Coverage (Yes/No)'] == 'Yes'])
        negative_count = len(uni_data[uni_data['Coverage (Yes/No)'] == 'No'])
        max_positive = max(max_positive, positive_count)
        max_negative = max(max_negative, negative_count)

    # Icon size in pixels (marker size 40 + some padding)
    icon_total_height_px = 45 # 40px marker + 20px padding
    
    # Calculate height based on the larger side
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
    color_yes = '#2ecc71'
    color_no = '#e74c3c'
    
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
                customdata=[[benefit, utils.wrap_text(details, width=40)]],  # Wrap the details text
                hovertemplate=(
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
    # Lower section (red background)
    fig.add_shape(
        type="rect",
        xref="paper", yref="y",
        x0=0, y0=y_min,
        x1=1, y1=0,
        fillcolor="rgba(255, 200, 200, 0.3)",  # Light red with transparency
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
        font=dict(size=16, color="#2ecc71", family="Arial, sans-serif"),
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
        font=dict(size=16, color="#e74c3c", family="Arial, sans-serif"),
        xshift=10  # Shift slightly to the right
    )

    # Upper section (green background)
    fig.add_shape(
        type="rect",
        xref="paper", yref="y",
        x0=0, y0=0,
        x1=1, y1=y_max,
        fillcolor="rgba(200, 255, 200, 0.3)",  # Light green with transparency
        line=dict(width=0),
        layer="below"
    )
    
    # Update layout
    fig.update_layout(
        xaxis=dict(
            ticktext=list(universities),
            tickvals=list(range(len(universities))),
            tickmode='array',
            title='',
            tickfont=dict(size=14),
            range=[-0.5, len(universities) - 0.5]
        ),
        yaxis=dict(
            title='Benefit Inclusion in Graduate Student Health Insurance',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#666',
            gridcolor='rgba(224, 224, 224, 0.5)',  # More subtle grid
            tickvals=[],
            range=[y_min, y_max],
            fixedrange=True  # Prevent zooming which can mess up spacing
        ),
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

    fig.add_hline(y=0, line_dash="solid", line_color="#666", line_width=2)

    return fig

def benefit_details(universities, benefits_df_filtered, selected_benefit='Deductible'):
    """
    Creates a bar chart for any benefit with automatic value extraction.
    """
    fig = go.Figure()
    
    # Get data for the selected benefit
    benefit_data = []
    value_type = None
    
    for uni in universities:
        uni_data = benefits_df_filtered[
            (benefits_df_filtered['University'] == uni) & 
            (benefits_df_filtered['Benefit'] == selected_benefit)
        ]
        
        if not uni_data.empty:
            has_coverage = uni_data.iloc[0]['Coverage (Yes/No)'] == 'Yes'
            details = uni_data.iloc[0]['Details'] if has_coverage else 'Not covered'
            
            if has_coverage:
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
    
    # Check if we have numerical values to compare
    has_numerical = any(df['HasValue'])

    numerical_df = df[df['HasValue']].copy()
    no_value_df = df[~df['HasValue']].copy()
    
    if has_numerical:
        
        # Create numerical comparison chart
        # Calculate the mean of numerical values
        mean_value = numerical_df['Value'].mean()
        
        # Set a small minimum value for visualization
        min_bar_height = min(mean_value * 0.01, 1) if mean_value > 0 else 0.1
        
        # Determine if this is a cost benefit (lower is better)
        cost_benefits = ['Deductible', 'Out-of-Pocket Maximum', 'Primary Care Visit', 
                        'Emergency Room', 'Urgent Care', 'Specialist Visit', 
                        'Prescription Drugs', 'Imaging', 'Diagnostic Tests']
        is_cost_benefit = any(cost_word in selected_benefit for cost_word in cost_benefits)
        
        # Determine colors for numerical values
        if is_cost_benefit:
            # For costs: below mean is good (green), above is bad (red)
            bar_colors = ['#2ecc71' if v < mean_value else '#e74c3c' for v in numerical_df['Value']]
        else:
            # For coverage amounts: above mean is good (green), below is bad (red)
            bar_colors = ['#2ecc71' if v > mean_value else '#e74c3c' for v in numerical_df['Value']]
        
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
            # Color for no coverage: green for cost benefits, red for coverage benefits
            no_coverage_color = '#2ecc71' if is_cost_benefit else '#e74c3c'
            
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
            title=f'{selected_benefit} Comparison',
            xaxis_title='University',
            yaxis_title=y_title,
            height=400,
            width=360,
            showlegend=False,
            bargap=0.2
        )
    else:
        # Coverage status chart (no numerical values found)
        colors = ['#2ecc71' if v == 1 else '#e74c3c' for v in df['Value']]
        
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
            title=f'{selected_benefit} Coverage by University',
            xaxis_title='University',
            yaxis=dict(visible=False),
            height=400,
            width=360,
            showlegend=False
        )
    
    return fig

def extract_numerical_values(details_text):
    """
    Automatically extract numerical values from benefit details text.
    Returns a list of found values with their context.
    """
    import re
    
    if pd.isna(details_text) or details_text == 'Not covered' or details_text == 'No':
        return []
    
    values = []
    
    # First, find all dollar amounts with their full context
    # This pattern captures more context before and after the dollar amount
    dollar_pattern = r'(?:([^$]{0,30})\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)([^$]{0,30}))'
    
    for match in re.finditer(dollar_pattern, details_text):
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
    
    # Find percentages (but exclude if followed by time units)
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
    
    # Find visit/day limits (but be more specific)
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
    Get the best numerical value for comparison based on the benefit type.
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
    # we might want the highest value instead of the first
    if is_coverage and len(values) > 1:
        # For coverage benefits, higher values are usually better
        # Sort by value descending
        values_sorted = sorted(values, key=lambda x: x['value'], reverse=True)
        best_value = values_sorted[0]
    else:
        # For cost benefits or unknown types, use priority system
        best_value = values[0]  # Already sorted by priority
    
    return best_value['value'], best_value['type']

if __name__ == "__main__":
    div, callbacks = benefits()
