import sys
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List
from collections import OrderedDict

class SpotifyHelper(object):
    def __init__(self):
        self.auth_manager = SpotifyClientCredentials()
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    def get_playlist(self, playlist_id: str) -> dict:
        '''Gets a playlist (nested_dict) from a playlist_id.'''
        return self.sp.playlist(playlist_id)
    
    def get_track_ids_from_playlist(self, playlist: dict) -> OrderedDict[str]:
        '''Returns the song IDs from songs inside of a playlist (nested_dict)'''
        track_ids = OrderedDict()
        for item in playlist['tracks']['items']:
            track_ids[item['track']['name']] = item['track']['id']
        
        return track_ids
    
    def get_track_ids_from_playlist_ids(self, playlist_id: str) -> List[str]:
        '''Returns the song IDs from songs inside of a playlist (nested_dict), given a playlist_id'''
        playlist = self.get_playlist(playlist_id)

        return self.get_track_ids_from_playlist(playlist)
    
    def get_audio_features_from_track_ids(self, track_ids: dict[str]) -> dict:
        '''Get audio features for one or multiple tracks based upon their Spotify IDs Parameters.
        Note: max # of songs retrievable is 100.'''
        return self.sp.audio_features(track_ids)

    # TODO: change keying by track ID, not name.
    # TODO: add more features:
        # genre (from artist)
        # popularity (from song)
        # release date (from album)
        # recommendations (check spotipy)
    def get_audio_features_from_playlist_id(self, playlist_id: str, as_df: bool=True) -> dict:
        track_ids = self.get_track_ids_from_playlist_ids(playlist_id)
        audio_features = self.get_audio_features_from_track_ids(track_ids.values())

        audio_features_new = []
        for name, af in zip(track_ids.keys(), audio_features):
            af['name'] = name
            audio_features_new.append(af)
        
        if as_df:
            df = pd.DataFrame(audio_features_new) 
            cols = list(df.columns)

            cols.remove('name')
            cols.insert(0, 'name')

            df = df[cols]
            return df
        else: 
            return audio_features_new
   

if __name__ == '__main__':
    # example playlist ID for input: '3FACwN2Ta8kXFcbquQ2u6K'
    
    spot = SpotifyHelper()
    df = spot.get_audio_features_from_playlist_id('3FACwN2Ta8kXFcbquQ2u6K')
    df.to_csv('test.csv', index=False)
