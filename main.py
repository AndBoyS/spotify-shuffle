import asyncio
import os

from tqdm import tqdm

import spotify
from src import spotify_custom, shuffle


client_id = os.environ['SPOTIFY_CLIENT_ID']
secret = os.environ['SPOTIFY_CLIENT_SECRET']
user_token = os.environ['SPOTIFY_REFRESH_TOKEN']
redirect_uri = 'http://localhost:8888/callback'

# playlist_id = '2uBBMdBcJWHPIshXDpze05'
playlist_id = '0Ry939BofXEcuWuhtGOCMG'


async def main():

    async with spotify.Client(client_id, secret) as client:

        oauth2 = spotify.OAuth2.from_client(client, redirect_uri)
        oauth2.set_scopes(
            playlist_modify_public=True,
            playlist_modify_private=True,
        )
        user = await spotify_custom.User.from_token(client, user_token, user_token)

        all_tracks = await spotify_custom.get_all_tracks_from_playlist(playlist_id, client)
        num_tracks = len(all_tracks)
        shuffler = shuffle.SequentialShuffler(num_tracks)
        shuffle_steps = shuffler.get_shuffle_steps()

        all_tracks_new_order = [None] * len(all_tracks)
        for old_i, new_i in shuffler.mapping.items():
            all_tracks_new_order[new_i] = all_tracks[old_i]

        for old_index, new_index in tqdm(shuffle_steps, desc='Sending shuffling requests'):
            await user.reorder_tracks(playlist_id, old_index, new_index, 1)

        await user.http.close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
