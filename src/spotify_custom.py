from typing import Optional

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


async def get_all_tracks_from_playlist(playlist_id, client):
    playlist_raw = await client.http.get_playlist(playlist_id)
    playlist = spotify.Playlist(client, playlist_raw)
    # 100 by default
    # with None it will get all tracks
    playlist.total_tracks = None
    all_tracks = await playlist.get_all_tracks()
    return all_tracks
