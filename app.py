import dash
from dash import html, dcc, Input, Output, State, no_update, callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
import base64
import os
import utils

# local
from livingwage_vs_stipend import livingwage_vs_stipend
from department_stipend_avgs import department_stipend_avgs
from timeline_dash import timeline_negotiations
from benefits_summary import benefits

# Create HTML content and get callbacks
html_stipends_over_time, callbacks_stipends = livingwage_vs_stipend()
html_dept_avg, callbacks_dept = department_stipend_avgs()
html_timeline, callbacks_timeline = timeline_negotiations()
html_benefits, callbacks_benefits, title_benefits, subtitle_benefits = benefits()

fallback_html = html.Div("You should not be seeing this, something went wrong")

# Map hotspots to their content and callbacks
content_mapping = {
    "hot-0-0": {"html": html_stipends_over_time, "callbacks": callbacks_stipends},
    "hot-0-1": {"html": html_dept_avg, "callbacks": callbacks_dept},
    "hot-1-0": {"html": html_dept_avg, "callbacks": callbacks_dept},
    "hot-2-0": {"html": html_timeline, "callbacks": callbacks_timeline},
    "hot-3-0": {"html": html_benefits, "callbacks": callbacks_benefits, "title": title_benefits, "subtitle":subtitle_benefits}
}

app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)
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
hotspot_dict = {
    0: [
        {"top": 300, "left": 120, "width": 250, "height": 40, "id": "hot-0-0"},
        {"top": 550, "left": 150, "width": 220, "height": 35, "id": "hot-0-1"},
    ],
    1: [
        {"top": 200, "left": 100, "width": 300, "height": 50, "id": "hot-1-0"},
    ],
    2: [
        {"top": 200, "left": 100, "width": 300, "height": 50, "id": "hot-2-0"},
    ],
    3: [
        {"top": 200, "left": 100, "width": 300, "height": 50, "id": "hot-3-0"},
    ],
}

# FIGURE CONSISTENCY VERIFICATION
try: 
    utils.verify_figure_mappings(content_mapping, hotspot_dict)
except ValueError as e:
    print(f"\n❌ ERROR: {e}")

# ----------------------------------------------------------------
# 3. Build layout dynamically
# ----------------------------------------------------------------
def build_page_with_overlays(img_src, page_index):
    """Create one PDF page (an image) with its overlay hotspots."""
    return html.Div(
        [
            html.Img(
                src=img_src,
                style={
                    "width": "100%",
                    "display": "block",
                },
            ),
            *[
                html.Div(
                    id=hotspot["id"],
                    n_clicks=0,
                    style={
                        "position": "absolute",
                        "top": f"{hotspot['top']}px",
                        "left": f"{hotspot['left']}px",
                        "width": f"{hotspot['width']}px",
                        "height": f"{hotspot['height']}px",
                        "cursor": "pointer",
                        "backgroundColor": "rgba(255, 255, 0, 0.3)",
                        "border": "2px solid rgba(255,200,0,0.4)",
                    },
                )
                for hotspot in hotspot_dict.get(page_index, [])
            ],
        ],
        style={
            "position": "relative",
            "width": "70%",
            "margin": "20px auto",
        },
    )

app.layout = html.Div(
    [
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

        # Popup modal - now contains a Div instead of a Graph
        dbc.Modal(
            [
                dbc.ModalHeader([
                    dbc.ModalTitle("Main Title", id="popup-title"),
                    html.P(className="text-muted small mb-0", id="popup-subtitle")
                ]),     
                dbc.ModalBody(
                    html.Div(id="popup-content"),  # Changed from dcc.Graph
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-popup", n_clicks=0)
                ),
            ],
            id="popup-modal",
            is_open=False,
            size="xl",
            scrollable=True,
        ),
    ],
    style={"height": "100vh", "overflow": "hidden"},
)

# ----------------------------------------------------------------
# 4. Callback: any hotspot opens the popup
# ----------------------------------------------------------------
@app.callback(
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
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update, no_update
    
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if triggered_id == "close-popup":
        return False, no_update, no_update
    
    # If a hotspot was clicked, look up the HTML content
    if triggered_id.startswith("hot-"):
        content = content_mapping.get(triggered_id, {
            "html": fallback_html,
            "title": "Default Title",
            "subtitle": ""
        })
        
        # Create the title component with subtitle if provided
        if content.get("subtitle"):
            title_component = html.Div([
                html.Div(content.get("title", "Main Title"), 
                        style={"fontSize": "1.25rem", "marginBottom": "2px"}),
                html.Div(content.get("subtitle", ""), 
                        style={"fontSize": "0.9rem", "color": "#6c757d", "fontWeight": "normal"})
            ])
        else:
            title_component = content.get("title", "Main Title")
        
        return True, content["html"], title_component
    
    return no_update, no_update, no_update

# ----------------------------------------------------------------
# 5. Register all callbacks from the visualization functions
# ----------------------------------------------------------------
def register_callbacks():
    """Register all callbacks from the visualization modules."""
    for hotspot_id, content in content_mapping.items():
        if content["callbacks"]:
            for callback_func in content["callbacks"]:
                callback_func(app)

# Register all callbacks after app layout is defined
register_callbacks()

# ----------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)