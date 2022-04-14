import webbrowser
import plotly.express as px
from dash import Dash, html, dcc
from threading import Timer

# Provides access to Plotly express functionality such as creating returnable graph figures
# Currently instantiated with a specific data frame to reduce the number of times we pass df around,
# we MAY want to change this to be more like a generic library/SpotifyHelper in the future
class PlotlyHelper(object):
    def __init__(self, df):
        self.df = df
    
    # Creates a histogram using the values in self.df from the specified category
    def create_histogram(self, category: str):
        return px.histogram(self.df, x=category)

# Creates and runs a Dash app with certain Plotly graphs from the specified df
# We WILL need to change this to be more generic in the future OR aggregate all data into one df
def run_dash(df):
    app = Dash(__name__)

    plot = PlotlyHelper(df)
    danceability_histogram = plot.create_histogram("danceability")
    energy_histogram = plot.create_histogram("energy")

    app.layout = html.Div(children=[
        html.H1(children="DV Final Playlist Visualized"),

        html.Div(children='''
            Creator: Group 1
            Songs: __________
        '''),

        dcc.Graph(
            id="dancability_histogram",
            figure=danceability_histogram
        ),

        dcc.Graph(
            id="energy_histogram",
            figure=energy_histogram
        )
    ])

    # Automatically open a window pointing to the Dash server
    # Delay by 1s so that Dash has time to start up the server
    Timer(1000, webbrowser.open("http://localhost:8050")).start()
    app.run_server(debug=True, use_reloader=False)
