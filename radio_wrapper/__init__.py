import json
import requests


class RadioWrapper(object):

    def __init__(self, *args, **kwargs):
        super(RadioWrapper, self).__init__(*args, **kwargs)

    def _make_request(self, url, params=None):
        response = requests.get(url, data=params)
        return response

    def _parse_json(self, requests_object):
        return requests_object.json()

    def get_playlist(self, url_path, date=None, limit=None,
                     list_id="songs", title_id="title", 
                     artist_id="artist", album_id="album"):
        """
        Returns json list of songs
            * date is a datetime oboject
        """
        playlist = []

        if date:
            url_path += "{}-{}-{}".format(date.year, date.month, date.day)

        playlist_request = self._make_request(url_path)
        playlist_json = self._parse_json(playlist_request)

        for song in playlist_json.get(list_id, []):
            if limit and len(playlist) >= limit:
                continue
            # We just want artist, title, album
            playlist.append({
                "title": song.get(title_id, ""),
                "artist": song.get(artist_id, ""),
                "album": song.get(album_id, ""),
            })
        return playlist
