import random
from typing import Any, List, Tuple, Optional, Dict


class SequentialShuffler:
    """
    Return the operations (from what positions to move the items to which, without swapping) to shuffle sequentially.
    """
    # Old index -> new index
    mapping: Dict[int, int]

    def __init__(
            self,
            num_items: int,
            idx_to_postpone: Optional[List[int]] = None,
            ) -> None:
        self.num_items = num_items
        self.idx_to_postpone = idx_to_postpone or []
        self.init_shuffle()

    def generate_random_mapping(
            self,
            input_idx: List[int],
            target_idx: List[int],
            ) -> Dict[int, int]:
        """
        Generate the random mapping from the input indexes to the target indexes.
        """
        target_idx = target_idx.copy()
        random.shuffle(target_idx)

        return dict(zip(input_idx, target_idx))

    def init_shuffle(self) -> None:
        """
        Initialize the random seed.
        """
        old_idx = list(range(self.num_items))

        if self.idx_to_postpone:
            first_target_idx = old_idx[:-len(self.idx_to_postpone)]  # not postponed
            postponed_target_idx = old_idx[-len(self.idx_to_postpone):]
        else:
            first_target_idx = old_idx
            postponed_target_idx = []

        mapping = self.generate_random_mapping(old_idx, first_target_idx)
        mapping.update(self.generate_random_mapping(self.idx_to_postpone, postponed_target_idx))

        self.mapping = mapping

    def get_shuffle_steps(self) -> List[Tuple[int, int]]:
        """
        Returns the list of moving steps (old_index, new_index) to shuffle sequentially.
        Needed for the Spotify API (https://developer.spotify.com/documentation/web-api/reference/playlists/reorder-playlists-tracks/)
        """
        temp_order = list(range(self.num_items))
        shuffle_steps = []

        # Sort the mapping by new indexes,
        idx_pairs_ordered = sorted(self.mapping.items(), key=lambda x: x[1])

        # The algorithm is such: put the element with the new index 0 at the beginning,
        # then put next (at the 1st index) the element with the new index 1, etc.
        for old_index, new_index in idx_pairs_ordered:
            old_index_corrected = temp_order.index(old_index)
            temp_order.remove(old_index)
            temp_order.insert(new_index, old_index)
            shuffle_steps.append((old_index_corrected, new_index))

        new_order = [old_index for old_index, new_index in idx_pairs_ordered]
        assert all([x == y for x, y in zip(temp_order, new_order)]), "The shuffle steps are not correct."

        return shuffle_steps
