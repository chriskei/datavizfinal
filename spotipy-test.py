import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

my_playlist = sp.playlist('3FACwN2Ta8kXFcbquQ2u6K')
print(my_playlist)