import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from matplotlib import pyplot as plt
import numpy as np
from plotly.tools import mpl_to_plotly
from astropy import constants, units
import pandas as pd
from matplotlib.cm import get_cmap

import rebound

from io import BytesIO
import base64

jup_to_stellar = constants.M_jup / constants.M_sun
data = pd.read_csv("./data/planets_2019.11.01_20.07.23.csv")


def get_min_max(arr):
    return (np.nanmin(arr), np.nanmax(arr))


m_s_min, m_s_max = get_min_max(data.st_mass.values)
m_j_min, m_j_max = get_min_max(data.pl_bmassj.values)
T_s_min, T_s_max = get_min_max(data.st_teff.values)
n_p_min, n_p_max = get_min_max(data.pl_pnum.values)
a_min, a_max = get_min_max(data.pl_orbsmax.values)
e_min, e_max = get_min_max(data.pl_orbeccen.values)
cmap = get_cmap("Spectral")


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


def comma_strings_to_list(comma_lists):
    """
    Convert a list of strings which contain comma separated values
    to lists
    """
    lists = []
    for comma_list in comma_lists:
        list_thing = [float(i) for i in comma_list.split(",")]
        lists.append(list_thing)
    return lists


def scale_cmap(T):
    a = 1 / (T_s_max - T_s_min)
    b = 1 - a * T_s_max
    val = a * T + b
    return val


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
                                {"label": "6", "value": 6},
                                {"label": "7", "value": 7},
                                {"label": "8", "value": 8},
                            ],
                        ),
                        html.Label("Stellar Mass (M_sun)", style={"margin-top": "0px"}),
                        html.Br(),
                        dcc.Input(
                            id="stellar_mass",
                            type="number",
                            placeholder="Exoplanet Archive Value Range: %.2e - %.2e M_sun"
                            % (m_s_min, m_s_max),
                            style={
                                "margin-top": "0px",
                                "display": "inline-block",
                                "width": "100%",
                            },
                        ),
                        html.Label(
                            "Stellar Temperature (K)", style={"margin-top": "0px"}
                        ),
                        html.Br(),
                        dcc.Input(
                            id="stellar_temp",
                            type="number",
                            placeholder="Exoplanet Archive Value Range: %.2e - %.2e K"
                            % (T_s_min, T_s_max),
                            style={
                                "margin-top": "0px",
                                "display": "inline-block",
                                "width": "100%",
                            },
                        ),
                        html.Label(
                            "Planet Masses (M_jup)", style={"margin-top": "0px"}
                        ),
                        html.Br(),
                        dcc.Input(
                            id="planet_mass",
                            type="text",
                            placeholder="(comma separated, Exoplanet Archive Value Range: %.2e - %.2e M_jup)"
                            % (m_j_min, m_j_max),
                            style={
                                "margin-top": "0px",
                                "display": "inline-block",
                                "width": "100%",
                            },
                        ),
                        html.Label("Semi-Major Axes (AU)", style={"margin-top": "0px"}),
                        html.Br(),
                        dcc.Input(
                            id="semi_major_axis",
                            type="text",
                            placeholder="(comma separated, Exoplanet Archive Value Range: %.2e - %.2e AU)"
                            % (a_min, a_max),
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
                html.Div(
                    id="button_div",
                    className="two columns",
                    children=[
                        dcc.Input(
                            id="choose_planet",
                            type="number",
                            placeholder="Pick a planet number for which you want to find a similar system!",
                            style={
                                "margin-top": "0px",
                                "display": "inline-block",
                                "width": "50%",
                            },
                        )
                    ],
                ),
                html.Div(id="results_div", className="two columns"),
            ],
            style={"text-align": "center"},
        ),
    ]
)


@app.callback(
    Output("results_div", "children"),
    [
        Input("n_planets", "value"),
        Input("stellar_mass", "value"),
        Input("stellar_temp", "value"),
        Input("planet_mass", "value"),
        Input("semi_major_axis", "value"),
        Input("eccentricity", "value"),
        Input("choose_planet", "value"),
    ],
)
def get_results(
    n_planets,
    stellar_mass,
    stellar_temp,
    planet_mass,
    semi_major_axis,
    eccentricity,
    planet_num,
):
    try:
        planet_num = planet_num - 1
        list_to_give = [
            n_planets,
            planet_mass[planet_num],
            semi_major_axis[planet_num],
            eccentricity[planet_num],
            stellar_mass,
            stellar_temp
        ]
        #vals_retrieved = andrew_function(
        #    list_to_give
        #)
        return("Values given: {}".format(list_to_give))
    except:
        return("Waiting for all data inputs...")

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

    string_list = [planet_mass, semi_major_axis, eccentricity]
    print(string_list)
    planet_mass, semi_major_axis, eccentricity = comma_strings_to_list(string_list)
    assert all(
        len(i) == n_planets for i in [planet_mass, semi_major_axis, eccentricity]
    ), "The number of planet masses, semi-major axes, and eccentricities must equal the number of planets!"
    assert all(0 <= i < 1 for i in eccentricity), "Eccentricity values must 0 <= e < 1!"

    # Pretiffy with random arguments of pericenter (not currently using)
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
        mass = mass * jup_to_stellar
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

    # Use rebound to plot
    star_color = scale_cmap(stellar_temp)
    color_val = cmap(star_color)
    fig, ax = rebound.OrbitPlot(
        sim,
        color=True,
        xlim=[-(r_a_max + offset_x), r_p_max + offset_x],
        ylim=[-b_max * 1.1, b_max * 1.1],
        lw=3,
        star_color=color_val,
    )
    # Hack in mpl image so that dash can use it
    out_url = fig_to_uri(fig)
    return out_url


if __name__ == "__main__":
    app.run_server(debug=True, port=6969, host="localhost")
