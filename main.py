import asyncio

from tqdm import tqdm

import spotify
from src import spotify_custom, shuffle


# playlist_id = '2uBBMdBcJWHPIshXDpze05'
playlist_id = '0Ry939BofXEcuWuhtGOCMG'


@spotify_custom.with_spotify_scope
async def main(client, user):

    all_tracks = await spotify_custom.get_all_tracks_from_playlist(playlist_id, client)
    num_tracks = len(all_tracks)
    shuffler = shuffle.SequentialShuffler(num_tracks)
    shuffle_steps = shuffler.get_shuffle_steps()

    for old_index, new_index in tqdm(shuffle_steps, desc='Sending shuffling requests'):
        await user.reorder_tracks(playlist_id, old_index, new_index, 1)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
