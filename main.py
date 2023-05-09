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

    def get_recent_tracks_in_playlist(
            recent_track_dicts: List[dict],
            all_playlist_tracks: List[spotify.Track],
            playlist_id: str,
            ) -> List[spotify.Track]:
        # Filter tracks that were in playlist at the moment of listening
        playlist_uri = f'spotify:playlist:{playlist_id}'
        recent_tracks = [d['track'] for d in recent_track_dicts
                         if d['context'].uri == playlist_uri]

        # Filter tracks that are in playlist now
        all_playlist_uris = [track.uri for track in all_playlist_tracks]
        recent_tracks = [track for track in recent_tracks
                         if track.uri in all_playlist_uris]

        return recent_tracks

    def early_shuffling_check(
            recent_tracks: List[spotify.Track],
            all_playlist_tracks: List[spotify.Track],
            num_tracks_to_check: int = 10,
            ) -> None:

        recent_tracks = recent_tracks[:num_tracks_to_check]

        all_playlist_urls = [track.uri for track in all_playlist_tracks]

        recent_tracks_idx = [all_playlist_urls.index(track.uri) for track in recent_tracks]
        # Checking monotonicity
        # order is from most recent to the least recent
        condition = all(i >= j for i, j in zip(recent_tracks_idx, recent_tracks_idx[1:]))

        if not condition:
            print('''
            Recent tracks are not in the correct order, 
            its possible that the playlist has been shuffled
            without listening to at least one song between runs of this script
            Still proceed?
            ''')
            output = input('yes/[no]').lower().strip()
            if output != 'yes':
                raise ValueError('Script aborted')

    def get_idx_to_postpone(
            recent_tracks: List[spotify.Track],
            all_tracks: List[spotify.Track],
            postpone_previous_amount: int,
            ) -> List[int]:

        if not recent_tracks:
            return []

        # The most recent track is the first one in the list
        # we filtered out the tracks not from the playlist
        most_recent_track_uri = recent_tracks[0].uri
        all_playlist_uris = [track.uri for track in all_playlist_tracks]

        last_idx = all_playlist_uris.index(most_recent_track_uri)
        first_idx = max(last_idx - postpone_previous_amount, 0)
        return list(range(first_idx, last_idx))


    all_playlist_tracks = await spotify_custom.get_all_tracks_from_playlist(playlist_id, client)
    num_tracks = len(all_playlist_tracks)

    idx_to_postpone = None

    if postpone_previous_amount > 0:
        # Cant get more than 50 tracks,
        # so we need to be sneaky
        recent_track_dicts = await user.recently_played(limit=50)
        recent_tracks_in_playlist = get_recent_tracks_in_playlist(
            recent_track_dicts,
            all_playlist_tracks,
            playlist_id,
        )
        early_shuffling_check(recent_tracks_in_playlist, all_playlist_tracks)
        idx_to_postpone = get_idx_to_postpone(
            recent_tracks_in_playlist,
            all_playlist_tracks,
            postpone_previous_amount,
        )

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
