import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
from collections import OrderedDict
from numpy.random import choice

class SpotifyHelper(object):
    def __init__(self):
        self.auth_manager = SpotifyClientCredentials()
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    def get_playlist(self, playlist_id: str) -> dict:
        '''Gets a playlist (nested_dict) from a playlist_id'''
        return self.sp.playlist(playlist_id)
    
    def get_track_data_from_playlist(self, playlist: dict) -> OrderedDict[str]:
        '''Returns the track data from songs inside of a playlist (nested_dict)'''
        track_data = OrderedDict()
        for item in playlist['tracks']['items']:
            # data from the track
            track = {}
            track['name'] = item['track']['name']
            track['popularity'] = item['track']['popularity']
            track['explicit'] = item['track']['explicit']

            # data from album
            track['date'] = item['track']['album']['release_date'].split('-')[0]

            # data from artist
            artists = []
            genres = []
            for artist_data in item['track']['artists']:
                # get the artist name
                artists.append(artist_data['name'])
                # get the genres associated w/the artist
                genres.extend(self.sp.artist(artist_data['id'])['genres'])
            track['artists'] = artists
            track['genres'] = genres
            
            # append track to track_data by track ID.
            track_data[item['track']['id']] = track
        
        return track_data
    
    def get_track_data_from_playlist_ids(self, playlist_id: str) -> list[str]:
        '''# Returns the song IDs from songs inside of a playlist (nested_dict), given a playlist_id'''
        playlist = self.get_playlist(playlist_id)

        return self.get_track_data_from_playlist(playlist)
    
    
    def get_audio_features_from_track_ids(self, track_ids: list[str]) -> dict:
        '''Get audio features for one or multiple tracks based upon their song IDs.
        Note: max # of songs retrievable is 100.'''

        return {id: self.sp.audio_features(id) for id in track_ids}
        # audio_features = self.sp.audio_features(track_ids)

    def merge_track_data_and_audio_features(self, track_data: OrderedDict, audio_features: OrderedDict) -> OrderedDict:
        assert track_data.keys() == audio_features.keys()

        main_track_data = OrderedDict()
        for id in track_data.keys():
            data_merged = {}
            data_merged.update(track_data[id])
            data_merged.update(audio_features[id][0])
            main_track_data[id] = data_merged
        
        return main_track_data

    def dict_to_df(self, d: dict, rearrange_cols: bool=True) -> pd.DataFrame:
        # convert ordered dict into DatFrame
        df = pd.DataFrame.from_dict(d, orient='index') 

        if rearrange_cols == True:
            # re-order the columns to have 'name' near the front
            cols = list(df.columns)
            cols.remove('name')
            cols.insert(0, 'name')
            df = df[cols]

        return df

    def get_main_track_data(self, playlist_id: str, as_df: bool=True) -> dict:
        track_data = self.get_track_data_from_playlist_ids(playlist_id)
        audio_features = self.get_audio_features_from_track_ids(list(track_data.keys()))
        
        main_track_data = self.merge_track_data_and_audio_features(track_data, audio_features)
        
        if as_df:
            df = self.dict_to_df(main_track_data, rearrange_cols=True)
            return df
        else: 
            return main_track_data
        
    def get_recommendations_from_track_ids(self, track_ids: list[str]):
        seed_tracks = list(choice(track_ids, size=5))
        recs_data = self.sp.recommendations(seed_tracks=seed_tracks)['tracks']
        track_recs = [r['name'] for r in recs_data]

        return track_recs

# Example playlist ID for input: 3FACwN2Ta8kXFcbquQ2u6K
if __name__ == '__main__':
    # instantiate the helper class
    spot = SpotifyHelper()
    # get track data
    df = spot.get_main_track_data('3FACwN2Ta8kXFcbquQ2u6K')
    # get song recommendations
    track_recs = spot.get_recommendations_from_track_ids(list(df.index))

    # send the track data to csv (NOTE: FOLLOW THIS FORMAT TO EXPORT AS CSV)
    df.to_csv('test.csv', index=True, index_label='id')
    # print out the song recommendations
    print(track_recs)

