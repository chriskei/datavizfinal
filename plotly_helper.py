import webbrowser
import plotly.express as px
import pandas as pd
from dash import Dash, html, dcc
from threading import Timer
from wordcloud_helper import generate_wordcloud

# Provides access to Plotly express functionality such as creating returnable graph figures
# Currently instantiated with a specific data frame to reduce the number of times we pass df around,
# we MAY want to change this to be more like a generic library/SpotifyHelper in the future
class PlotlyHelper(object):
    def __init__(self, df):
        self.df = df
    
    # Creates a histogram using the values in self.df from the specified category
    def create_histogram(self, category: str):
        return px.histogram(self.df, x=category)

    # Creates a violin plot using the values in self.df from the specified category
    # if multiple args are passed in, plots it on the same figure
    def create_violin(self, category: str, *args):
        if args:
            categories = [category]
            for arg in args:
                categories.append(arg)
            return px.violin(self.df, x=categories, box=True)
        else:
            return px.violin(self.df, x=category, box=True)

    def create_genre_bar(self):
        genre_bank = ["rap", "metal", "latin", "edm", "rock", "pop", "folk", "hip hop", 
        "country", "jazz", "classical", "r&b", "dance", "indie", "soul"]
        genre_dict = dict.fromkeys(genre_bank, 0)
        # count genres in each song
        for song in self.df.genres:
            for genre in genre_bank:
                if genre in song:
                    genre_dict[genre] += 1
        
        # only keep genres with a nonzero count 
        for genre in genre_bank:
            if genre_dict[genre] == 0:
                genre_dict.pop(genre)

        genre_df = pd.DataFrame.from_dict(genre_dict, orient='index', columns=["Count"])
        return px.bar(genre_df, y="Count", text_auto=True, labels={
            "index": "Genre"
        })


# Creates and runs a Dash app with certain Plotly graphs from the specified df
# We WILL need to change this to be more generic in the future OR aggregate all data into one df
def run_dash(df):
    app = Dash(__name__)

    plot = PlotlyHelper(df)
    artist_wordcloud = generate_wordcloud(df, "artists")
    loudness_histogram = plot.create_histogram("loudness")
    tempo_histogram = plot.create_histogram("tempo")
    mood_violin = plot.create_violin("danceability", "energy", "valence")
    year_histogram = plot.create_histogram("date").update_xaxes(categoryorder='category ascending')
    genre_bar = plot.create_genre_bar()

    app.layout = html.Div(children=[
        html.H1(children="DV Final Playlist Visualized"),

        html.Div(children='''
            Creator: Group 1
            Songs: __________
        '''),

        html.Img(
            id="artist_wordcloud",
            src=app.get_asset_url(artist_wordcloud),
            width=400,
            height=400
        ),

        dcc.Graph(
            id="year_histogram",
            figure=year_histogram
        ),

        dcc.Graph(
            id="mood_violin",
            figure=mood_violin
        ),

        dcc.Graph(
            id="loudness_histogram",
            figure=loudness_histogram
        ),

        dcc.Graph(
            id="tempo_histogram",
            figure=tempo_histogram
        ),

        dcc.Graph(
            id="genre_bar",
            figure=genre_bar
        )
    ])

    # Automatically open a window pointing to the Dash server
    # Delay by 1s so that Dash has time to start up the server
    Timer(1000, webbrowser.open("http://localhost:8050")).start()
    app.run_server(debug=True)
