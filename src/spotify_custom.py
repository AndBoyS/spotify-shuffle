import os
import time
from typing import Optional, List, Callable

from dateutil import parser
import spotify
from spotify import HTTPUserClient


class User(spotify.User):
    @classmethod
    async def from_token(
            cls,
            client: "spotify.Client",
            token: Optional[str],
            refresh_token: Optional[str] = None,
            ) -> spotify.User:
        """Create a :class:`User` object from an access token.

        Parameters
        ----------
        client : :class:`spotify.Client`
            The spotify client to associate the user with.
        token : :class:`str`
            The access token to use for http requests.
        refresh_token : :class:`str`
            Used to acquire new token when it expires.
        """
        client_id = client.http.client_id
        client_secret = client.http.client_secret

        http = HTTPUserClient(client_id, client_secret, token, refresh_token)
        data = await http.current_user()
        return cls(client, data=data, http=http)


async def get_all_tracks_from_playlist(
        playlist_id: str,
        client: spotify.Client,
        ) -> List[spotify.Track]:
    playlist_raw = await client.http.get_playlist(playlist_id)
    playlist = spotify.Playlist(client, playlist_raw)
    # 100 by default
    # with None it will get all tracks
    playlist.total_tracks = None
    all_tracks = await playlist.get_all_tracks()
    return all_tracks


def with_spotify_scope(func: Callable) -> Callable:
    """
    Decorator that inits spotify session
    Decorated functions must have keyword arguments client and user
    """

    async def wrapper(*args, **kwargs):
        client_id = os.environ['SPOTIFY_CLIENT_ID']
        secret = os.environ['SPOTIFY_CLIENT_SECRET']
        user_token = os.environ['SPOTIFY_REFRESH_TOKEN']
        redirect_uri = 'http://localhost:8888/callback'

        async with spotify.Client(client_id, secret) as client:
            oauth2 = spotify.OAuth2.from_client(client, redirect_uri)
            oauth2.set_scopes(
                playlist_modify_public=True,
                playlist_modify_private=True,
            )
            user = await User.from_token(client, user_token, user_token)
            await func(*args, **kwargs, client=client, user=user)
            await user.http.close()

    return wrapper


async def get_recent_tracks(
        user: spotify.User,
        limit: int = 50,
        ) -> List[spotify.Track]:

    def convert_str_to_unix_time(date_str: str) -> str:
        # Returns unix time in milliseconds
        date = (parser.parse(date_str))
        date_unix = date.timestamp() * 1e3
        return str(int(date_unix))

    max_limit_for_request = 50

    recently_played = []
    before_date_unix = None
    tracks_remaining = limit

    while tracks_remaining > 0:

        cur_limit = (tracks_remaining - 1) % max_limit_for_request + 1

        cur_recently_played = await user.recently_played(
            limit=cur_limit,
            before=before_date_unix,
        )
        before_date_str = cur_recently_played[-1]['played_at']
        before_date_unix = convert_str_to_unix_time(before_date_str)

        tracks_remaining -= cur_limit
        recently_played.extend(cur_recently_played)

    return [d['track'] for d in recently_played]
