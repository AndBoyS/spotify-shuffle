import argparse
import asyncio
from typing import List

from tqdm import tqdm

import spotify
from src import spotify_custom, shuffle


parser = argparse.ArgumentParser(
    description = 'Shuffle spotify playlist',
)
parser.add_argument('playlist_id', type=str,
                    help='Playlist id')
parser.add_argument('postpone_previous_amount', type=int, default=200, nargs='?',
                    help='Move the specified amount of recently listened tracks to the end of the playlist')

args = parser.parse_args()
playlist_id = args.playlist_id
postpone_previous_amount = args.postpone_previous_amount


@spotify_custom.with_spotify_scope
async def main(
        playlist_id: str,
        postpone_previous_amount: int = 200,
        *,
        client: spotify.Client,
        user: spotify_custom.User,
        ):

    def get_track_name(track: spotify.Track) -> str:
        artist = track.artist.name or 'Unknown artist'
        return f'{track.name} - {artist}'

    def get_recent_tracks_idx(
            all_tracks: List[spotify.Track],
            recent_track_dicts: List[dict],
            postpone_previous_amount: int,
            ) -> List[int]:
        all_tracks_names = [get_track_name(track) for track in all_tracks]
        recent_tracks_names = [get_track_name(d['track']) for d in recent_track_dicts]
        recent_tracks_idx = [all_tracks_names.index(track_name) for track_name in recent_tracks_names
                             if track_name in all_tracks_names]
        if recent_tracks_idx:
            # The most recent track is the first one in the list
            # we filtered out the tracks not from the playlist
            # this script should work fine if at least one song has been listened between runs of this script
            last_idx = recent_tracks_idx[0]
            first_idx = max(last_idx - postpone_previous_amount, 0)
            return list(range(first_idx, last_idx))
        else:
            return []

    all_tracks = await spotify_custom.get_all_tracks_from_playlist(playlist_id, client)
    num_tracks = len(all_tracks)

    idx_to_postpone = None

    if postpone_previous_amount > 0:
        recent_track_dicts = await user.recently_played(limit=50)
        idx_to_postpone = get_recent_tracks_idx(all_tracks, recent_track_dicts, postpone_previous_amount)

    shuffler = shuffle.SequentialShuffler(
        num_tracks,
        idx_to_postpone=idx_to_postpone,
    )
    shuffle_steps = shuffler.get_shuffle_steps()

    for old_index, new_index in tqdm(shuffle_steps, desc='Sending shuffling requests'):
        await user.reorder_tracks(playlist_id, old_index, new_index, 1)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(
        main(playlist_id, postpone_previous_amount)
    )
