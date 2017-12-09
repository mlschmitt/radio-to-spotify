import json
from time import sleep
from base64 import b64encode
from urllib import urlencode

import requests


SPOTIFY_BASE_URL = "https://api.spotify.com/"
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/"

SPOTIFY_AUTH_PATH = "api/token"
SPOTIFY_USER_PATH = "v1/me"
SPOTIFY_SEARCH_PATH = "v1/search"


class SpotifyException(Exception):

    def __init__(self, requests_object, *args, **kwargs):
        super(SpotifyException, self).__init__(*args, **kwargs)
        self.status_code = requests_object.status_code
        self.message = requests_object.text

    def __str__(self):
        return "SpotifyException: {} - {}".format(self.status_code, self.message)

class Spotify(object):

    REQUEST_TRACK_LIMIT = 100

    def __init__(self, client, secret, *args, **kwargs):
        super(Spotify, self).__init__(*args, **kwargs)
        self.base_url = SPOTIFY_BASE_URL
        self.client = client
        self.secret = secret
        self.access_token = None
        self.user_id = None

    def _make_request(self, path, method="GET", params=None, headers=None, override_url=None):
        if override_url:
            url = "{}{}".format(override_url, path)
        else:
            url = "{}{}".format(self.base_url, path)

        if not headers.has_key("Authorization"):
            headers["Authorization"] = "Bearer {}".format(self.access_token)

        if method == "GET":
            response = requests.get(url, data=params, headers=headers)
        elif method == "POST":
            response = requests.post(url, data=params, headers=headers)
        elif method == "PUT":
            response = requests.put(url, data=params, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, data=params, headers=headers)
        if response.status_code in (200, 201):
            return self._parse_response(response)
        raise SpotifyException(response)

    def _parse_response(self, r_object):
        return r_object.json()

    def _encode_text(self, text):
        return text.encode("utf-8")


    def authenticate(self, refresh_token):
        """
        Authenticate a new session using the provided refresh_token.
        Stores access_token in class to be used on future requests.
        """
        auth_header = b64encode("{}:{}".format(self.client, self.secret))
        auth = self._make_request(
            path=SPOTIFY_AUTH_PATH,
            method="POST",
            params={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            headers={
                "Authorization": "Basic {}".format(auth_header)
            },
            override_url=SPOTIFY_AUTH_URL
        )
        self.access_token = auth["access_token"]
        return auth


    def get_user_info(self):
        """
        Fetch the current user's ID
        """
        user_info = self._make_request(
            path=SPOTIFY_USER_PATH,
        )
        self.user_id = user_info["id"]


    def find_a_track(self, title, artist, album=None):
        """
        Search for a track on Spotify given a song title, artist name,
        and optionally an album title. Returns top track match
        """
        search_query = "artist:{} track:{}".format(
            self._encode_text(artist), self._encode_text(title))
        if album:
            search_query += " album: {}".format(self._encode_text(album))  

        params = {
            "q": search_query,
            "type": "track",
            "limit": 1
        }

        path = "{}?{}".format(SPOTIFY_SEARCH_PATH, urlencode(params))
        tracks = self._make_request(
            path=path
        )
        if len(tracks["tracks"]["items"]) > 0:
            return tracks["tracks"]["items"][0]
        return None

    def get_playlist(self, playlist_id, fields=None):
        tracks = []
        total = 1
        offset = 0

        path = "v1/users/{}/playlists/{}/tracks".format(self.user_id, playlist_id)
        if fields:
            path += "?fields={}".format(fields)

        while total > offset:
            data = self._make_request(
                path=path,
                params={
                    "limit": self.REQUEST_TRACK_LIMIT,
                    "offset": offset,
                }
            )
            total = data["total"]
            offset += self.REQUEST_TRACK_LIMIT
            tracks = tracks + [track for track in data["items"]]
        return tracks

    def get_playlist_track_ids(self, playlist_id):
        tracks = self.get_playlist(playlist_id, fields="total,items(track.id)")
        return [track["track"]["id"] for track in tracks]

    def get_playlist_track_uris(self, playlist_id):
        tracks = self.get_playlist(playlist_id, fields="total,items(track.uri)")
        return [track["track"]["uri"] for track in tracks]

    def add_tracks_to_playlist(self, playlist_id, tracks_to_add):
        path = "v1/users/{}/playlists/{}/tracks".format(
            self.user_id, playlist_id
        )
        return self._make_request(
            path=path,
            method="PUT",
            params=json.dumps({"uris": tracks_to_add}),
            headers={"Content-Type": "application/json"},
        )
    
    def remove_tracks_from_playlist(self, playlist_id, tracks_to_remove):
        track_limit = self.REQUEST_TRACK_LIMIT - 1
        path = "v1/users/{}/playlists/{}/tracks".format(
            self.user_id, playlist_id
        )
        while len(tracks_to_remove) > 0:
            subselection_tracks = tracks_to_remove[:track_limit]
            del tracks_to_remove[:track_limit]
            subselection_tracks = [{"uri": track} for track in subselection_tracks]
            self._make_request(
                path=path,
                method="DELETE",
                params=json.dumps({"tracks": subselection_tracks}),
                headers={"Content-Type": "application/json"},
            )
            sleep(5)

    def prepend_tracks_to_playlist(self, playlist_id, tracks_to_add):
        path = "v1/users/{}/playlists/{}/tracks?position=0".format(
            self.user_id, playlist_id
        )
        return self._make_request(
            path=path,
            method="POST",
            params=json.dumps({"uris": tracks_to_add}),
            headers={"Content-Type": "application/json"},
        )

    def append_tracks_to_playlist(self, playlist_id, tracks_to_add):
        path = "v1/users/{}/playlists/{}/tracks".format(
            self.user_id, playlist_id
        )
        return self._make_request(
            path=path,
            method="POST",
            params=json.dumps({"uris": tracks_to_add}),
            headers={"Content-Type": "application/json"},
        )
