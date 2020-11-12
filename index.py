
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from functions.functions import *
from app import app
from pages import renko_macd






navbar = dbc.NavbarSimple(
    children=[
        dbc.Nav(
        [
        dbc.NavItem(dbc.NavLink("ALL", href="/page-1",id='page-1-link')),
        dbc.NavItem(dbc.NavLink("EUR/PLN", href="/page-2",id='page-2-link')),
        dbc.NavItem(dbc.NavLink("EUR/CHF", href="/page-3",id='page-3-link')),
        dbc.NavItem(dbc.NavLink("EUR/USD", href="/page-4",id='page-4-link')),
        ],
    pills=True,
    # vertical='lg'
        )
    ],
    brand="Forex Market Cup !",
    brand_href="/",
    color="dark",
    dark=True,
    id='nav'
    
)

#content = html.Div(id="page-content")

app.layout = html.Div([dcc.Location(id="url"), navbar, dbc.Container(id='page-content')])

@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 5)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f"/page-{i}" for i in range(1, 5)]

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1"]:
        return renko_macd.create_layout(app)
    elif pathname == "/page-2":
        return html.P("Dominik, tutaj jeszcze nic nie ma...")
    elif pathname == "/page-3":
        return html.P("Dominik, tutaj jeszcze nic nie ma....")
    elif pathname == "/page-4":
        return html.P("Dominik, tutaj jeszcze nic nie ma.....")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )




if __name__ == "__main__":
    app.run_server(debug=False)
