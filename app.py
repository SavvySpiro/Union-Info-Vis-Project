import dash
from dash import html, dcc, Input, Output, State, no_update, callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
import base64
import os
import utils

# local
from livingwage_vs_stipend import livingwage_vs_stipend
# from inflation_vs_raises import compare_inflation_and_raises
from department_stipend_avgs import department_stipend_avgs
from timeline_dash import timeline

# Create figures to be displayed
fig_stipends_over_time = livingwage_vs_stipend()
# fig_inflation = compare_inflation_and_raises()
fig_dept_avg = department_stipend_avgs()
fig_timeline = timeline()
fallback_fig = px.scatter(x=[1,2,3], y=[1,2,3], title="You should not be seeing this, something went wrong")

pdf_link_mapping = {
    "hot-0-0": fig_stipends_over_time,
    "hot-0-1": fig_dept_avg, #temp
    "hot-1-0": fig_dept_avg,
    "hot-2-0": fig_timeline
    # add more mappings as needed
}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

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
# For now these are placeholder boxes. You will fill in real locations later.
# hotspot_dict[page_index] = list of hotspot coordinate dicts
hotspot_dict = {
    0: [  # page 0 hotspots
        {"top": 300, "left": 120, "width": 250, "height": 40, "id": "hot-0-0"},
        {"top": 550, "left": 150, "width": 220, "height": 35, "id": "hot-0-1"},
    ],
    1: [  # page 1 hotspots
        {"top": 200, "left": 100, "width": 300, "height": 50, "id": "hot-1-0"},
    ],
    2: [  # page 2 hotspots
        {"top": 200, "left": 100, "width": 300, "height": 50, "id": "hot-2-0"},
    ],
    # add more pages when ready
}

# FIGURE CONSISTENCY VERIFICATION
# test that all figures have a place to be and
try: 
    utils.verify_figure_mappings(pdf_link_mapping, hotspot_dict)
except ValueError as e:
    print(f"\n❌ ERROR: {e}")

# ----------------------------------------------------------------
# 3. Build layout dynamically
# ----------------------------------------------------------------
def build_page_with_overlays(img_src, page_index):
    """Create one PDF page (an image) with its overlay hotspots."""

    return html.Div(
        [
            # The PDF image
            html.Img(
                src=img_src,
                style={
                    "width": "100%",
                    "display": "block",
                },
            ),
            # Overlay hotspots for this page
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
                        "backgroundColor": "rgba(255, 255, 0, 0.3)",  # highlight
                        "border": "2px solid rgba(255,200,0,0.4)",
                    },
                )
                for hotspot in hotspot_dict.get(page_index, [])
            ],
        ],
        style={
            "position": "relative",
            "width": "70%",       # match your desired PDF width
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

        # Popup modal (same for all hotspots)
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Visualization")),
                dbc.ModalBody(
                    dcc.Graph(id="popup-figure")
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
    Output("popup-figure", "figure"),
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
        return no_update, no_update

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if triggered_id == "close-popup":
        return False, no_update

    # If a hotspot was clicked, look up the figure
    if triggered_id.startswith("hot-"):
        fig_to_show = pdf_link_mapping.get(triggered_id, fallback_fig)  # fallback figure
        return True, fig_to_show

    return no_update, no_update


# ----------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
