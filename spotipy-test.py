import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def parse_args():
    # Make sure the user enters a playlist id
    if len(sys.argv) != 2:
        print("Please add a playlist id as an argument when running")
        sys.exit()

    playlist_id = sys.argv[1] # Test playlist id: 3FACwN2Ta8kXFcbquQ2u6K 
    
    return playlist_id


if __name__ == "__main__":
    playlist_id = parse_args()
    
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)

    my_playlist = sp.playlist(playlist_id)
    print(my_playlist)