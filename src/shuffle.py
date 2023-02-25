import random
from typing import Any, List, Tuple


class SequentialShuffler:
    """
    Return the operations (from what positions to move the items to which, without swapping) to shuffle sequentially.
    """

    def __init__(self, num_items: int) -> None:
        self.num_items = num_items
        old_ids = list(range(num_items))
        new_ids = list(range(num_items))
        random.shuffle(new_ids)

        self.old_ids = old_ids
        self.mapping = dict(zip(old_ids, new_ids))

    def get_shuffle_steps(self) -> List[Tuple[int, int]]:
        """Returns the list of moving steps (old_index, new_index) to shuffle sequentially."""
        temp_order = self.old_ids.copy()
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
