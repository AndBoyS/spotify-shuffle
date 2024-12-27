import json
import os
import subprocess
import urllib.parse
from pathlib import Path

zshenv_path = Path.home() / ".zshenv"

client_id = os.environ["SPOTIFY_CLIENT_ID"]
client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]
redirect_uri = os.environ["SPOTIFY_REDIRECT_URI"]
redirect_uri_encoded = urllib.parse.quote_plus(redirect_uri)

scope = urllib.parse.quote_plus(
    "playlist-modify-public playlist-modify-private user-read-recently-played"
)

uri_for_access_code = f"https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}&scope={scope}&redirect_uri={redirect_uri_encoded}"

print(
    f"Head to the {uri_for_access_code} and copy the link you was redirected to after agreeing"
)
access_uri = input("Paste the link: ")
access_code = access_uri.replace(f"{redirect_uri}/?code=", "")

curl_for_refresh_token = f'curl -d client_id="{client_id}" -d client_secret="{client_secret}" -d grant_type=authorization_code -d code="{access_code}" -d redirect_uri="{redirect_uri_encoded}" https://accounts.spotify.com/api/token'
refresh_token = json.loads(subprocess.check_output(curl_for_refresh_token, shell=True))[
    "refresh_token"
]
print(f"New refresh token: {refresh_token}")
print(f"Update it in the {zshenv_path} (also you need to update it in termux .bashrc)")
