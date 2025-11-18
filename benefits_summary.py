import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
import numpy as np
import utils

def benefits():
    # Read the CSV
    benefits_df = pd.read_csv("data/health_insurance_comparison.csv")
    
    # Get unique universities and benefits
    universities = benefits_df['University'].unique()
    
    # Define key benefits to display (you can modify this list)
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
    
    # Create the figure
    fig = go.Figure()
    
    # Calculate max benefits on positive and negative sides separately
    max_positive = 0
    max_negative = 0
    
    # First pass to count benefits per side for each university
    for uni in universities:
        uni_data = benefits_df_filtered[benefits_df_filtered['University'] == uni]
        positive_count = len(uni_data[uni_data['Coverage (Yes/No)'] == 'Yes'])
        negative_count = len(uni_data[uni_data['Coverage (Yes/No)'] == 'No'])
        max_positive = max(max_positive, positive_count)
        max_negative = max(max_negative, negative_count)
    
    # Calculate spacing parameters
    # Icon size in pixels (marker size 40 + some padding)
    icon_total_height_px = 40 # 40px marker + 20px padding
    
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
                hovertemplate=(
                    f"<b>{uni}</b><br>"
                    f"<b>{benefit}</b><br>"
                    f"Coverage: {'Yes' if has_benefit else 'No'}<br>"
                    f"<i>{details}</i>"
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
        margin=dict(l=80, r=90, t=20, b=80),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    
    # Add horizontal line at y=0
    fig.add_hline(y=0, line_dash="solid", line_color="#666", line_width=2)
    
    # Create the Dash component
    div = html.Div([
        html.Div([
            dcc.Graph(
                id='benefits-unit-chart',
                figure=fig,
                config={'displayModeBar': False}
            )
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
            'maxWidth': '1400px',
            'margin': '0 auto'
        })
    ])

    title = 'University Health Insurance Benefits Comparison'
    subtitle = 'Select icons to compare benefit details'
    # Return the div and empty callbacks list (add callbacks here if needed)
    return div, [], title, subtitle

if __name__ == "__main__":
    div, callbacks = benefits()
