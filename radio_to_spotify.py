import sys

import config
from radio_wrapper import RadioWrapper
from spotify_wrapper import Spotify


def fetch_radio_playlist(radio_playlist_url):
    radio = RadioWrapper()
    return radio.get_playlist(radio_playlist_url)

def update_spotify_playlist(track_list, playlist_id):
    spotify = Spotify(config.SPOTIFY_CLIENT, config.SPOTIFY_SECRET)
    spotify.authenticate(config.SPOTIFY_REFRESH_CODE)
    spotify.get_user_info()

    new_tracks = []
    existing_tracks = []

    existing_tracks = spotify.get_playlist_track_uris(playlist_id)
    for track in track_list:
        if len(new_tracks) >= config.SPOTIFY_MAX_PLAYLIST_LENGTH:
            break
        try:
            spotify_track = spotify.find_a_track(
                track["title"],
                track["artist"],
                track["album"],
            )
        except Spotify.SpotifyException:
            spotify_track = None

        if not spotify_track or spotify_track.get("uri", "N/A") == "NA":
            # Remove album for a wider search
            spotify_track = spotify.find_a_track(track["title"], track["artist"])

        if spotify_track and spotify_track.has_key("uri"):
            if spotify_track["uri"] == existing_tracks[0]:
                break
            if (
                    spotify_track["uri"] not in existing_tracks and 
                    spotify_track["uri"] not in new_tracks
                ):
                new_tracks.append(spotify_track["uri"])
        else:
            print "Found 0 results for {} - {} - {}".format(
                track["title"], track["artist"], track["album"])

    if len(new_tracks) > 0:
        tracks_to_delete = existing_tracks[config.SPOTIFY_MAX_PLAYLIST_LENGTH - len(new_tracks):]
        if len(tracks_to_delete) > 0:
            spotify.remove_tracks_from_playlist(playlist_id, tracks_to_delete)
        spotify.prepend_tracks_to_playlist(playlist_id, new_tracks)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        radio_playlist_url = sys.argv[1]
    else:
        radio_playlist_url = config.RADIO_STATION_PLAYLIST_URL
    if len(sys.argv) > 2:
        spotify_playlist_id = sys.argv[2]
    else:
        spotify_playlist_id = config.SPOTIFY_CURRENT_PLAYLIST_ID
        
    radio_playlist = fetch_radio_playlist(radio_playlist_url)
    update_spotify_playlist(radio_playlist, spotify_playlist_id)
