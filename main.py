import argparse
import asyncio

from tqdm import tqdm

import spotify
from src import spotify_custom, shuffle


parser = argparse.ArgumentParser(
    description = 'Shuffle spotify playlist',
)
parser.add_argument('playlist_id', type=str,
                    help='Playlist id')
parser.add_argument('postpone_recent', type=bool, default=True, nargs='?',
                    help='Move recently listened tracks to the end of the playlist')

args = parser.parse_args()
playlist_id = args.playlist_id
postpone_recent = args.postpone_recent


@spotify_custom.with_spotify_scope
async def main(
        playlist_id,
        postpone_recent=True,
        *,
        client,
        user
        ):

    def get_track_name(track: spotify.Track) -> str:
        artist = track.artist.name or 'Unknown artist'
        return f'{track.name} - {artist}'

    all_tracks = await spotify_custom.get_all_tracks_from_playlist(playlist_id, client)
    num_tracks = len(all_tracks)

    idx_to_postpone = None

    if postpone_recent:
        recent_track_dicts = await user.recently_played(limit=50)
        all_tracks_names = [get_track_name(track) for track in all_tracks]
        recent_tracks_names = [get_track_name(d['track']) for d in recent_track_dicts]
        idx_to_postpone = [all_tracks_names.index(track_name) for track_name in recent_tracks_names
                           if track_name in all_tracks_names]

    shuffler = shuffle.SequentialShuffler(
        num_tracks,
        idx_to_postpone=idx_to_postpone,
    )
    shuffle_steps = shuffler.get_shuffle_steps()

    for old_index, new_index in tqdm(shuffle_steps, desc='Sending shuffling requests'):
        await user.reorder_tracks(playlist_id, old_index, new_index, 1)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(
        main(playlist_id, postpone_recent)
    )
