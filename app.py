
import dash
import dash_auth
import dash_bootstrap_components as dbc
import logging


FA = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"
USERNAME_PASSWORD_PAIRS = [
    ['tomek','tomek'],['username','password']
]

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP, FA],
    # these meta_tags ensure content is scaled correctly on different devices
    # see: https://www.w3schools.com/css/css_rwd_viewport.asp for more
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
    suppress_callback_exceptions=True
)
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

server = app.server