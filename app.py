import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1("Make Your Own Solar System!", id="title"),
    
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True, port=6969, host="localhost")
