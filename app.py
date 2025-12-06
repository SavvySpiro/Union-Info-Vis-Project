import dash
from dash import html, dcc, Input, Output, State, no_update, callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
import dash.dependencies
import base64
import os
import utils

# local imports for visualizations
from livingwage_vs_stipend import livingwage_vs_stipend
from department_stipend_avgs import department_stipend_avgs
from timeline_dash import timeline_negotiations
from benefits_summary import benefits

# Create HTML content and get callbacks, titles, subtitles for modal
html_stipends_over_time, callbacks_stipends, title_stipends, subtitle_stipends = livingwage_vs_stipend()
html_dept_avg, callbacks_dept, title_dept, subtitle_dept = department_stipend_avgs()
html_timeline, callbacks_timeline, title_timeline, subtitle_timeline = timeline_negotiations()
html_benefits, callbacks_benefits, title_benefits, subtitle_benefits = benefits()

fallback_html = html.Div("You should not be seeing this, something went wrong")

# Map hotspots to their content and callbacks
content_mapping = {
    "hot-0-0": {"html": html_timeline, "callbacks": callbacks_timeline, "title": title_timeline, "subtitle": subtitle_timeline},
    "hot-2-0": {"html": html_stipends_over_time, "callbacks": callbacks_stipends, "title": title_stipends, "subtitle": subtitle_stipends},
    "hot-3-0": {"html": html_dept_avg, "callbacks": callbacks_dept, "title": title_dept, "subtitle": subtitle_dept},
    "hot-5-0": {"html": html_benefits, "callbacks": callbacks_benefits, "title": title_benefits, "subtitle":subtitle_benefits}
}

# define dash app
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP], #bootstrap is for modals
                suppress_callback_exceptions=True) #dynamic callbacks like to whine

# ----------------------------------------------------------------
# 1. Load PDF page images
# ----------------------------------------------------------------
PDF_IMAGE_FOLDER = "assets/"
pdf_images = [
    os.path.join(PDF_IMAGE_FOLDER, filename)
    for filename in sorted(os.listdir(PDF_IMAGE_FOLDER))
    if filename.lower().endswith((".png", ".jpg", ".jpeg"))
]

def serve_image(path):
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{encoded}"

# ----------------------------------------------------------------
# 2. Define hotspots (clickable regions)
# ----------------------------------------------------------------
# print img height and width for reference
from PIL import Image
img = Image.open(pdf_images[0])
print(img.size)  # Output: (width, height)

IMAGE_WIDTH = 1700  # Replace with your actual width
IMAGE_HEIGHT = 2200  # Replace with your actual height

hotspot_dict = {
    0: [
        {
            "top": (610 / IMAGE_HEIGHT) * 100,     # Convert to %
            "left": (170 / IMAGE_WIDTH) * 100,     # Convert to %
            "width": (1400 / IMAGE_WIDTH) * 100,   # Convert to %
            "height": (240 / IMAGE_HEIGHT) * 100,  # Convert to %
            "id": "hot-0-0"
        },
        # add hotspoty on articles 5 and 6
    ],
    2: [
        {
            "top": (600 / IMAGE_HEIGHT) * 100,
            "left": (170 / IMAGE_WIDTH) * 100,
            "width": (1400 / IMAGE_WIDTH) * 100,
            "height": (250 / IMAGE_HEIGHT) * 100,
            "id": "hot-2-0"
        },
    ],
    3: [
        {
            "top": (550 / IMAGE_HEIGHT) * 100,
            "left": (170 / IMAGE_WIDTH) * 100,
            "width": (1300 / IMAGE_WIDTH) * 100,
            "height": (180 / IMAGE_HEIGHT) * 100,
            "id": "hot-3-0"
        },
    ],
    5: [
        {
            "top": (730 / IMAGE_HEIGHT) * 100,
            "left": (170 / IMAGE_WIDTH) * 100,
            "width": (1300 / IMAGE_WIDTH) * 100,
            "height": (460 / IMAGE_HEIGHT) * 100,
            "id": "hot-5-0"
        },
    ]
}

# Verify consistency between the hotspot dict and the content mapping
try: 
    utils.verify_figure_mappings(content_mapping, hotspot_dict)
except ValueError as e:
    print(f"\n❌ ERROR: {e}")

# ----------------------------------------------------------------
# 3. Build app layout 
# ----------------------------------------------------------------
def build_page_with_overlays(img_src, page_index):
    """
    Create one PDF page (an image) with its overlay hotspots and title text boxes
    """
    # Calculate how far left the container is from the screen edge
    # Container has: margin 20px auto, padding 0 15px, maxWidth 1200px
    # So the offset is: (100vw - 1200px) / 2 when centered, plus the 15px padding
    
    return html.Div(
        [
            # pdf page image
            html.Img(
                src=img_src,
                style={
                    "width": "100%",
                    "height": "auto",
                    "display": "block",
                },
            ),
            *[
                html.Div([
                    # Text box on the left
                    html.Div(
                        content_mapping.get(hotspot["id"], {}).get("title", ""),
                        style={
                            "position": "absolute",
                            "top": f"{hotspot['top']}%",
                            "right": f"{100 - hotspot['left']}%",  # Right edge at hotspot
                            "width": f"calc(20px + max(0px, (100vw - 1230px) / 2) + {hotspot['left']}%)",  # From screen edge to hotspot
                            "height": f"{hotspot['height']}%",
                            "marginLeft": f"calc(-20px - max(0px, (100vw - 1230px) / 2))",  # Pull left to screen edge
                            "marginRight": "5px",  # Pull it left
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "padding": "10px",
                            "fontSize": "1.2rem",
                            "fontFamily": "Source Sans Pro, sans-serif",
                            "fontWeight": "bold",
                            "color": "#990000",
                            "textAlign": "center",
                            "wordWrap": "break-word",
                            "overflowWrap": "break-word",
                            # "backgroundColor": "rgba(255, 0, 0, 0.2)", #for debugging
                            "boxSizing": "border-box",
                        }
                    ),
                    # Hotspot (clickable area)
                    html.Div(
                        id=hotspot["id"],
                        n_clicks=0,
                        style={
                            "position": "absolute",
                            "top": f"{hotspot['top']}%",      
                            "left": f"{hotspot['left']}%",    
                            "width": f"{hotspot['width']}%",  
                            "height": f"{hotspot['height']}%", 
                            "cursor": "pointer",
                            "backgroundColor": "rgba(255, 255, 0, 0.3)",
                            "border": "2px solid rgba(255,200,0,0.4)",
                            "zIndex": "10",
                        },
                    ),
                ])
                for hotspot in hotspot_dict.get(page_index, [])
            ],
        ],
        style={
            "position": "relative",
            "maxWidth": "1200px",
            "margin": "20px auto",
            "width": "100%",       
            "padding": "0 15px",
            "boxSizing": "border-box",
            "overflow": "visible",
        },
    )

# Jump modal layout
jump_modal_layout = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Jump to Visualization")),
        dbc.ModalBody(
            html.Div([
                html.Div([
                    html.Div([
                        html.H5(content_mapping[hotspot_id]["title"], 
                               style={"marginBottom": "10px", "color": "#990000"}),
                        html.P(content_mapping[hotspot_id].get("subtitle", ""),
                              style={"fontSize": "0.9rem", "color": "#666"}),
                        html.A(
                            f"Go to Page {page_idx + 1}",
                            id={"type": "jump-to", "index": hotspot_id},
                            href=f"#{hotspot_id}",
                            style={
                                "padding": "8px 15px",
                                "backgroundColor": "#990000",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "5px",
                                "cursor": "pointer",
                                "fontSize": "0.9rem",
                                "textDecoration": "none",
                                "display": "inline-block"
                            }
                        )
                    ], style={"flex": "1", "paddingRight": "20px"}),
                ], style={
                    "display": "flex", 
                    "alignItems": "center",
                    "padding": "15px",
                    "borderBottom": "1px solid #ddd",
                    "marginBottom": "10px"
                })
                for page_idx, hotspots in hotspot_dict.items()
                for hotspot in hotspots
                for hotspot_id in [hotspot["id"]]
            ])
        ),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-jump-modal", n_clicks=0)
        ),
    ],
    id="jump-modal",
    is_open=False,
    size="lg",
    scrollable=True,
)


title = "See What's at Stake: Northeastern/GENU-UAW Contract Proposal Visualized"
subtitle = "Unlike traditional contract negotiations which are article-by-article, Northeastern released a complete 'Final' contract proposal all at once. This dashboard visualizes key provisions to help union members understand what's being offered." 
instructions = "Click on the highlighted sections of the proposal pages below to explore interactive visualizations that break down important aspects of the contract like stipend trends, departmental averages, negotiation timelines, and insurance benefits summaries."

app.layout = html.Div(
    [
    # header and explanation
        html.Div(
            [html.Header(title,
                style={
                "fontFamily": "Source Sans Pro, sans-serif", #matches genu font
                "fontSize": "3rem",
                "fontWeight": "bold",
                "marginBottom": "10px",
                "textAlign": "center",
                "textDecoration": "underline",
                "textDecorationThickness": "4px",
            }),
            html.Div(
                subtitle,
                style={
                    "fontFamily": "Source Sans Pro, sans-serif", #matches genu font
                    "fontSize": "2rem",
                    "color": "#666",
                    "marginBottom": "15px",
                    "marginLeft": "20px",
                    "marginRight": "20px",
                }
            ),
            html.Div(
                instructions,
                style={
                    "fontFamily": "Source Sans Pro, sans-serif", #matches genu font
                    "fontSize": "2rem",
                    "marginBottom": "20px",
                    "marginLeft": "20px",
                    "marginRight": "20px",
                    "whiteSpace": "pre-line",
                    "color": "#990000"
                }
            ),
            # button for jumping around
            html.Button("Jump to Visualization", id="jump-button", n_clicks=0, 
                        style={"marginBottom": "20px",
                               "marginLeft": "20px",
                            "padding": "10px 15px", 
                            "fontSize": "1rem",
                            "backgroundColor": "#990000",
                            "color": "white",
                            "border": "none",
                            "borderRadius": "5px",
                            "cursor": "pointer",
                            "hover": {
                                "backgroundColor": "#770000"
                            }
                        }),
            ]),
        # horizontal line
        html.Hr(),
        html.Div(
            
            [
                build_page_with_overlays(serve_image(img), i)
                for i, img in enumerate(pdf_images)
            ],
            style={
                "display": "flex",
                "flexDirection": "column",
                "overflowY": "scroll",
                "height": "100vh",
                "padding": "20px",
            },
        ),

        # Popup modal
        dbc.Modal(
            [
                dbc.ModalHeader([
                    # custom title and subtitle come from figure functions
                    dbc.ModalTitle("Main Title", id="popup-title"),
                    html.P(className="text-muted small mb-0", id="popup-subtitle")
                ]),     
                # holds a html div returned from the figure functions
                dbc.ModalBody(
                    html.Div(id="popup-content"),
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-popup", n_clicks=0)
                ),
            ],
            id="popup-modal",
            is_open=False,
            size="xl",
            scrollable=True,
            style={"width": "95%", 'maxWidth': 'none'}, #TODO: this doesnt make the modal wider, not sure how to
        ),
        jump_modal_layout,
        dcc.Location(id='url', refresh=False),
    ],
    style={"height": "100vh", "overflow": "hidden"},
)

# ----------------------------------------------------------------
# 4. Callback: any hotspot opens the corresponding popup
# ----------------------------------------------------------------
@app.callback(
    # defines which html id and what content to change in it
    Output("popup-modal", "is_open"),
    Output("popup-content", "children"),
    Output("popup-title", "children"),
    [
        Input(hotspot["id"], "n_clicks")
        for page in hotspot_dict.values()
        for hotspot in page
    ] + [Input("close-popup", "n_clicks")],
    State("popup-modal", "is_open")
)

def open_popup(*args):
    # Determine which input triggered the callback
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update, no_update
    
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # if the trigger was the close button
    if triggered_id == "close-popup":
        return False, no_update, no_update
    
    # If a hotspot was clicked, look up the HTML content
    if triggered_id.startswith("hot-"):

        content = content_mapping.get(triggered_id, {
            "html": fallback_html, #default
            "title": "Default Title",
            "subtitle": ""
        })
        
        # Create the title component with subtitle if provided
        if content.get("subtitle"):
            title_component = html.Div([
                html.Div(content.get("title", "Main Title"), 
                        style={"fontSize": "3rem", "marginBottom": "2px"}),
                html.Div(content.get("subtitle", ""), 
                        style={"fontSize": "2rem", "color": "#6c757d", "fontWeight": "normal"})
            ])
        else:
            title_component = content.get("title", "Main Title")
        
        return True, content["html"], title_component
    
    return no_update, no_update, no_update

# ----------------------------------------------------------------
# 5. Register all callbacks from the visualization functions
# ----------------------------------------------------------------
def register_callbacks():
    """
    Register all callbacks from the visualization modules
    """
    
    for hotspot_id, content in content_mapping.items():
        if content["callbacks"]:
            for callback_func in content["callbacks"]:
                callback_func(app)

# Register all callbacks after app layout is defined
register_callbacks()


# ----------------------------------------------------------------
# 6. Additional Callbacks and buttons
# ----------------------------------------------------------------
# Jump modal layout  
jump_modal_layout = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Jump to Visualization")),
        dbc.ModalBody(
            html.Div([
                html.Div([
                    html.Div([
                        html.H5(content_mapping[hotspot_id]["title"], 
                               style={"marginBottom": "10px", "color": "#990000"}),
                        html.P(content_mapping[hotspot_id].get("subtitle", ""),
                              style={"fontSize": "0.9rem", "color": "#666"}),
                        html.Button(
                            f"Go to Page {page_idx + 1}",
                            id={"type": "jump-to", "index": hotspot_id},
                            n_clicks=0,
                            **{"data-hotspot": hotspot_id},  # Store hotspot ID as data attribute
                            style={
                                "padding": "8px 15px",
                                "backgroundColor": "#990000",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "5px",
                                "cursor": "pointer",
                                "fontSize": "0.9rem"
                            }
                        )
                    ], style={"flex": "1", "paddingRight": "20px"}),
                ], style={
                    "display": "flex", 
                    "alignItems": "center",
                    "padding": "15px",
                    "borderBottom": "1px solid #ddd",
                    "marginBottom": "10px"
                })
                for page_idx, hotspots in hotspot_dict.items()
                for hotspot in hotspots
                for hotspot_id in [hotspot["id"]]
            ])
        ),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-jump-modal", n_clicks=0)
        ),
    ],
    id="jump-modal",
    is_open=False,
    size="lg",
    scrollable=True,
)

@app.callback(
    Output("jump-modal", "is_open"),
    [Input("jump-button", "n_clicks"),
     Input("close-jump-modal", "n_clicks"),
     Input({"type": "jump-to", "index": dash.dependencies.ALL}, "n_clicks")],
    State("jump-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_jump_modal(jump_clicks, close_clicks, jump_to_clicks, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return is_open
    
    triggered_id = ctx.triggered[0]["prop_id"]
    
    if "jump-button" in triggered_id:
        return not is_open
    elif "close-jump-modal" in triggered_id:
        return False
    elif "jump-to" in triggered_id:
        return False
    
    return is_open


# ----------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)