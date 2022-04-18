import webbrowser
import plotly.express as px
import pandas as pd
from dash import Dash, html, dcc
from threading import Timer
from wordcloud_helper import generate_wordcloud

# Provides access to Plotly express functionality such as creating returnable graph figures
# Currently instantiated with a specific data frame to reduce the number of times we pass df around
class PlotlyHelper(object):
    def __init__(self, df, track_recs):
        self.df = df
        self.track_recs = track_recs
    
    # Creates a histogram using the values in self.df from the specified category
    def create_histogram(self, category: str):
        hist = px.histogram(self.df, x=category, template="simple_white")
        hist.update_layout(xaxis_title=None, yaxis_title=None)
        return hist

    # Creates a string display of major vs minor preference
    def create_mode(self):
        major_count = 0
        minor_count = 0

        for i in self.df.index:
            current_mode = self.df["mode"][i]
            if current_mode == 1:
                major_count += 1
            else:
                minor_count += 1
            
        counts_str = str(major_count) + " major - " + str(minor_count) + " minor"
        remark_str = "You have a good mix of emotions in your songs!"
        if (major_count / minor_count > 2):
            remark_str = "You like listening to happy, upbeat songs!"
        elif (minor_count / major_count > 2):
            remark_str = "You like listening to dark, sad songs!"

        return html.Div(children=[
            html.H2(children="Song Modality:", style={"font-size": "40px"}),
            html.H4(children=counts_str, style={"font-size": "40px", "margin": "0", "line-height": "0"}),
            html.H5(children=remark_str, style={"font-size": "30px"})
        ], style={"padding": "0 32px"})

    # Creates a string display of popularity
    def create_popularity(self):
        song_count = 0
        total_popularity = 0

        for i in self.df.index:
            song_count += 1
            total_popularity += self.df["popularity"][i]

        average_popularity = int(total_popularity / song_count)
        number_suffix = "th"
        if average_popularity % 10 == 2:
            number_suffix = "nd"
        elif average_popularity % 10 == 3:
            number_suffix = "rd"
        popularity_str = str(average_popularity) + number_suffix + " percentile"
        remark_str = "Keep listening to both independent and mainstream artists!"
        if average_popularity < 34:
            remark_str = "Great job supporting independent artists!"
        elif average_popularity > 67:
            remark_str = "You're up to date with the current top hits!"

        return html.Div(children=[
            html.H2(children="Average Popularity:", style={"font-size": "40px"}),
            html.H4(children=popularity_str, style={"font-size": "40px", "margin": "0", "line-height": "0"}),
            html.H5(children=remark_str, style={"font-size": "30px"})
        ], style={"margin-top": "16px", "margin-bottom": "120px", "padding": "0 32px"})

    # Creates a string display of recommended songs
    def create_recommendations(self):
        div_children = [
            html.H2(children="Song Recommendations", style={"font-size": "40px", "margin-bottom": "8px"}),
        ]

        for rec in self.track_recs:
            div_children.append(html.A(children=str(rec["name"]),
                                       href=rec["href"],
                                       target="_blank",
                                       style={"margin-right": "32px", "line-height": "1.5", "font-size": "30px"}))

        return html.Div(children=div_children, style={"margin": "64px 64px 96px"})

    # Creates a violin plot using the values in self.df from the specified category
    # if multiple args are passed in, plots it on the same figure
    def create_violin(self, category: str, *args):
        violin = None

        if args:
            categories = [category]
            for arg in args:
                categories.append(arg)
            violin = px.violin(self.df, x=categories, box=True, template="simple_white")
        else:
            violin = px.violin(self.df, x=category, box=True, template="simple_white")
        
        violin.update_layout(xaxis_title=None, yaxis_title=None)
        return violin

    def create_genre_bar(self):
        genre_bank = ["rap", "metal", "latin", "edm", "rock", "pop", "folk", "hip hop", 
        "country", "jazz", "classical", "r&b", "dance", "indie", "soul"]
        genre_dict = dict.fromkeys(genre_bank, 0)
        genre_dict["other"] = 0
        # count genres in each song
        for song in self.df.genres:
            is_in_genre_bank = False
            for genre in genre_bank:
                for song_genre in song:
                    if not is_in_genre_bank and genre in song_genre:
                        genre_dict[genre] += 1
                        is_in_genre_bank = True
                        break
                if is_in_genre_bank:
                    break
            if not is_in_genre_bank:
                genre_dict["other"] += 1
        
        # only keep genres with a nonzero count 
        genre_bank.append('other')
        for genre in genre_bank:
            if genre_dict[genre] == 0:
                genre_dict.pop(genre)

        genre_df = pd.DataFrame.from_dict(genre_dict, orient='index', columns=["Count"])
        bar = px.bar(genre_df, template="simple_white", labels={
            "index": "Genre"
        })
        bar.update_layout(xaxis_title=None, yaxis_title=None, showlegend=False)
        return bar
    
# Creates and runs a Dash app with certain Plotly graphs from the specified df
def run_dash(df, track_recs, playlist_name):
    app = Dash(__name__)
    playlist_name_header = playlist_name + " - Visualized"

    plot = PlotlyHelper(df, track_recs)
    artist_wordcloud = generate_wordcloud(df, "artists")
    loudness_histogram = plot.create_histogram("loudness")
    tempo_histogram = plot.create_histogram("tempo")
    mood_violin = plot.create_violin("danceability", "energy", "valence")
    year_histogram = plot.create_histogram("date").update_xaxes(categoryorder='category ascending').update_layout(xaxis_tickangle=-45)
    genre_bar = plot.create_genre_bar()
    duration_histogram = plot.create_histogram("duration")
    mode_visualization = plot.create_mode()
    popularity_visualization = plot.create_popularity()
    recommendations_visualization = plot.create_recommendations()

    app.layout = html.Div(children=[

        html.H1(children=playlist_name_header,
                style={"font-size": "100px", "text-align": "center", "text-decoration": "underline"}),

        html.Div(children=[
            # Left div
            html.Div(children=[
                html.H2(children="Artists", style={"font-size": "40px"}),
                html.Img(
                    id="artist_wordcloud",
                    src=app.get_asset_url(artist_wordcloud),
                    width=400,
                    height=400
                ),

                html.H2(children="Genre Distribution",
                        style={"font-size": "40px", "position": "relative", "top": "85px", "z-index": "1"}),
                dcc.Graph(
                    id="genre_bar",
                    figure=genre_bar
                ),

                html.H2(children="Year Released",
                        style={"font-size": "40px", "position": "relative", "top": "85px", "z-index": "1"}),
                dcc.Graph(
                    id="year_histogram",
                    figure=year_histogram
                ),

                html.H2(children="Song Duration (min)",
                        style={"font-size": "40px", "position": "relative", "top": "85px", "z-index": "1"}),
                dcc.Graph(
                    id="duration_histogram",
                    figure=duration_histogram
                )
            ], style={"width": "50%", "text-align": "center"}),

            # Right div
            html.Div(children=[
                mode_visualization,

                popularity_visualization,

                html.H2(children="Overall Mood",
                        style={"font-size": "40px", "position": "relative", "top": "85px", "z-index": "1"}),
                dcc.Graph(
                    id="mood_violin",
                    figure=mood_violin
                ),

                html.H2(children="Loudness (dB)",
                        style={"font-size": "40px", "position": "relative", "top": "85px", "z-index": "1"}),
                dcc.Graph(
                    id="loudness_histogram",
                    figure=loudness_histogram
                ),

                html.H2(children="Tempo (BPM)",
                        style={"font-size": "40px", "position": "relative", "top": "85px", "z-index": "1"}),
                dcc.Graph(
                    id="tempo_histogram",
                    figure=tempo_histogram
                )
            ], style={"width": "50%", "text-align": "center", "align-self": "end"}),
        ], style={"display": "flex" }),

        recommendations_visualization

    ], style={"font-family": "sans-serif", "color": "#004466"})

    # Automatically open a window pointing to the Dash server
    # Delay by 1s so that Dash has time to start up the server
    Timer(1000, webbrowser.open("http://localhost:8050")).start()
    app.run_server(debug=True, use_reloader=False)
