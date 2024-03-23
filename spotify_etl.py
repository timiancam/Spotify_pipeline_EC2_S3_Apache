"""
Extracts track information from the Spotify "Top 50 - Global Playlist"
and uploads the data to an AWS S3 bucket as a .csv file
"""

import spotipy 
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
from decouple import config

def spotify_connection_handler():
    """
    Creates an authenticator for API calls to the Spotify database
    clientID and secret are stored within the .env file
    """
    
    cid = config('CLIENT_ID')
    secret = config('SECRET')
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    
    return sp

def get_playlist(sp):
    """
    Retrieves the name and tracks of playlist "Top 50 Global"
    """

    # Returns list where each element is the playlist track
    # Argument is for the spotify daily top 50 playlist
    playlist_tracks = sp.playlist_tracks('spotify:playlist:37i9dQZEVXbMDoHDwVN2tF')['items']
    
    playlist_name = sp.playlist('spotify:playlist:37i9dQZEVXbMDoHDwVN2tF')['name']
    
    return playlist_tracks, playlist_name

def get_audio_features(sp, playlist_tracks):
    """
    Retrieves audio feature information for each track in the playlist
    """
    
    # Argument is a list of track URIs
    raw_audio_features = sp.audio_features([track_object['track']['id'] for track_object in playlist_tracks])
    
    filtered_audio_features = {
        'danceability':     [element['danceability'] for element in raw_audio_features],
        'energy':           [element['energy'] for element in raw_audio_features],
        'loudness':         [element['loudness'] for element in raw_audio_features],
        'speechiness':      [element['speechiness'] for element in raw_audio_features],
        'acousticness':     [element['acousticness'] for element in raw_audio_features],
        'instrumentalness': [element['instrumentalness'] for element in raw_audio_features],
        'liveness':         [element['liveness'] for element in raw_audio_features],
        'valence':          [element['valence'] for element in raw_audio_features]
    }
    
    return filtered_audio_features

def create_dataframe(playlist_tracks, audio_features):
    """
    Creates a dataframe of the playlist tracks, audio features and genres
    Each index is a track in the playlist, information access via dictionary keys
    """
    
    dataframe = pd.DataFrame(data = {
        'track_URI':            [track_object['track']['id'] for track_object in playlist_tracks],
        'track_name':           [track_object['track']['name'] for track_object in playlist_tracks],
        'album_name':           [track_object['track']['album']['name'] for track_object in playlist_tracks],
        'album_image_URL':      [track_object['track']['album']['images'][0]['url'] for track_object in playlist_tracks],
        
        # URI format - spotify:artist:1pBLC0qVRTB5zVMuteQ9jJ
        # Nested list comprehension required as a track can have more than one artist
        'artists_URIs':         [[artist['uri'].split(':')[-1] for artist in track_object['track']['artists']] for track_object in playlist_tracks],
        'artists':              [[artist['name'] for artist in track_object['track']['artists']] for track_object in playlist_tracks],
        
        'danceability':         audio_features['danceability'],
        'energy':               audio_features['energy'], 
        'loudness':             audio_features['loudness'], 
        'speechiness':          audio_features['speechiness'],
        'acousticness':         audio_features['acousticness'], 
        'instrumentalness':     audio_features['instrumentalness'], 
        'liveness':             audio_features['liveness'], 
        'valence':              audio_features['valence']
    })

    return dataframe

def spotify_main():
    sp = spotify_connection_handler()
    
    playlist_tracks, playlist_name, = get_playlist(sp)
    
    audio_features = get_audio_features(sp, playlist_tracks)
    
    dataframe = create_dataframe(playlist_tracks, audio_features)
    
    dataframe.to_csv('s3://spotify-airflow-s3/spotify_global_top_50.csv')