# Radio to Spotify

Build Spotify playlists from radio station JSON feeds.

Given a URL with a radio station's recent playlist in JSON format ([example](http://www.thecurrent.org/playlist/json/)), script automatically adds songs to a given Spotify playlist up to a defined song count. [Example result playlist](https://open.spotify.com/user/mschmitt23/playlist/7fvYdggouYM4jcyI6ojkm8).

Works best when called every 5-15 minutes, such as via a cron job.

### Requirements:

* Python [requests](http://docs.python-requests.org/en/master/) library
* Spotify account
* Spotify target playlist ID
* Spotify API app with permissions to read & modify account playlists

### Get started:

1. Create a Spotify developer account and app - [link](https://developer.spotify.com/) 
1. [Authorize your Spotify account](https://developer.spotify.com/web-api/authorization-guide/) with the new app and obtain your refresh token
1. Add your app's client, secret keys and refresh token to `config.py`
1. Create a target Spotify playlist and add the ID to `config.py` (or provide it manually when calling the script)
1. Find the radio station playlist URL and either add it to `config.py` (or provide it manually when calling the script)
1. Call the script `python radio_to_spotify.py`
