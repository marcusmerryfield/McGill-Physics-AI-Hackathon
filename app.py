import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from matplotlib import pyplot as plt
import numpy as np
from plotly.tools import mpl_to_plotly

import rebound

from io import BytesIO
import base64


def fig_to_uri(in_fig, close_all=True, **save_args):
    # type: (plt.Figure) -> str
    """
    Save a figure as a URI
    """
    out_img = BytesIO()
    in_fig.savefig(out_img, format="png", **save_args)
    if close_all:
        in_fig.clf()
        plt.close("all")
    out_img.seek(0)  # rewind file
    encoded = base64.b64encode(out_img.read()).decode("ascii").replace("\n", "")
    return "data:image/png;base64,{}".format(encoded)


app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.Div(
            className="banner",
            children=[
                html.Div(
                    className="container scalable",
                    children=[
                        html.H1(
                            id="banner",
                            children=[html.A("Make Your Own Planetary System")],
                        )
                    ],
                    style={
                        "width": "100%",
                        "display": "inline-block",
                        "text-align": "center",
                    },
                ),
                # html.Div(
                #     className="logo",
                #     children=[
                #         html.A(
                #             html.Img(src=app.get_asset_url("msi_pride.png"), width=150)
                #         )
                #     ],
                #     style={'width': '49%', 'display': 'inline-block', 'margin-right': 10},
                # ),
            ],
        ),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="two columns",
                    children=[
                        html.Label("Number of Planets", style={"margin-top": "0px"}),
                        dcc.Dropdown(
                            id="n_planets",
                            options=[
                                {"label": "1", "value": 1},
                                {"label": "2", "value": 2},
                                {"label": "3", "value": 3},
                                {"label": "4", "value": 4},
                                {"label": "5", "value": 5},
                            ],
                        ),
                        html.Label("Stellar Mass", style={"margin-top": "0px"}),
                        html.Br(),
                        dcc.Input(
                            id="stellar_mass",
                            type="number",
                            placeholder="0.5 M_sun < M < 50 M_sun",
                            style={
                                "margin-top": "0px",
                                "display": "inline-block",
                                "width": "100%",
                            },
                        ),
                        html.Label("Stellar Temperature", style={"margin-top": "0px"}),
                        html.Br(),
                        dcc.Input(
                            id="stellar_temp",
                            type="number",
                            placeholder="1000 K < T < 50000 K",
                            style={
                                "margin-top": "0px",
                                "display": "inline-block",
                                "width": "100%",
                            },
                        ),
                        html.Label("Planet Masses", style={"margin-top": "0px"}),
                        html.Br(),
                        dcc.Input(
                            id="planet_mass",
                            type="text",
                            placeholder="(comma separated, 0.5 M_earth < Mass < 30 M_earth)",
                            style={
                                "margin-top": "0px",
                                "display": "inline-block",
                                "width": "100%",
                            },
                        ),
                        html.Label("Semi-Major Axes", style={"margin-top": "0px"}),
                        html.Br(),
                        dcc.Input(
                            id="semi_major_axis",
                            type="text",
                            placeholder="(comma separated, 0.01 AU < a < 100 AU)",
                            style={
                                "margin-top": "0px",
                                "display": "inline-block",
                                "width": "100%",
                            },
                        ),
                        html.Label("Orbital Eccentricity", style={"margin-top": "0px"}),
                        html.Br(),
                        dcc.Input(
                            id="eccentricity",
                            type="text",
                            placeholder="(comma separated, 0 <= e < 1)",
                            style={
                                "margin-top": "0px",
                                "display": "inline-block",
                                "width": "100%",
                            },
                        ),
                    ],
                    style={
                        "width": "50%",
                        "display": "inline-block",
                        "margin-top": "0px",
                    },
                ),
                html.Div(
                    id="plot_div",
                    className="two columns",
                    children=[html.Img(id="plot", src="")],
                    style={"width": "55%", "display": "inline-block"},
                ),
            ],
            style={"text-align": "center"},
        ),
    ]
)


@app.callback(
    Output("plot", "src"),
    [
        Input("n_planets", "value"),
        Input("stellar_mass", "value"),
        Input("stellar_temp", "value"),
        Input("planet_mass", "value"),
        Input("semi_major_axis", "value"),
        Input("eccentricity", "value"),
    ],
)
def update_figure(
    n_planets, stellar_mass, stellar_temp, planet_mass, semi_major_axis, eccentricity
):

    planet_mass = [float(i) for i in planet_mass.split(",")]
    semi_major_axis = [float(i) for i in semi_major_axis.split(",")]
    eccentricity = [float(i) for i in eccentricity.split(",")]
    assert all(
        len(i) == n_planets for i in [planet_mass, semi_major_axis, eccentricity]
    ), "The number of planet masses, semi-major axes, and eccentricities must be equal!"
    assert all(0 <= i < 1 for i in eccentricity), "Eccentricity values must 0 <= e < 1!"

    # Pretiffy with random arguments of pericenter
    omega = np.random.random(int(n_planets)) * 2 * np.pi

    # Use rebound to create a figure of orbits
    sim = rebound.Simulation()

    # Calculate semi-minor axes, perihelion and aphelion
    r_p = []
    r_a = []
    b = []
    for a, e in zip(semi_major_axis, eccentricity):
        r_p.append((1 - e) * a)
        r_a.append((1 + e) * a)
        b.append(((1 - e ** 2) * a ** 2) ** (1 / 2))

    r_a_max = np.max(r_a)
    r_p_max = np.max(r_p)
    b_max = np.max(b)
    offset_x = r_a_max * 0.1

    # Add in stellar information
    sim.add(m=stellar_mass)
    for mass, a, e, o in zip(planet_mass, semi_major_axis, eccentricity, omega):
        sim.add(primary=sim.particles[0], m=mass, a=a, e=e, omega=0)

    particles_x = []
    particles_y = []
    for particle in sim.particles:
        particles_x.append(particle.x)
        particles_y.append(particle.y)

    x_max = np.max(particles_x)
    x_min = np.min(particles_x)
    y_max = np.max(particles_y)
    y_min = np.min(particles_y)

    fig, ax = rebound.OrbitPlot(
        sim,
        color=True,
        xlim=[-(r_a_max + offset_x), r_p_max + offset_x],
        ylim=[-b_max * 1.1, b_max * 1.1],
        lw=5,
    )
    out_url = fig_to_uri(fig)
    return out_url


if __name__ == "__main__":
    app.run_server(debug=True, port=6969, host="localhost")
