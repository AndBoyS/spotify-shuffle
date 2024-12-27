from unittest import TestCase

from src import shuffle


class TestSequentialShuffler(TestCase):
    def test_idx_to_postpone(self) -> None:
        num_items = 100
        idx_to_postpone = list(range(50, 80))
        shuffler = shuffle.SequentialShuffler(
            num_items, idx_to_postpone=idx_to_postpone
        )

        len_idx_to_postpone = len(idx_to_postpone)
        for old_index, new_index in shuffler.mapping.items():
            if old_index in idx_to_postpone:
                assert new_index >= num_items - len_idx_to_postpone
            else:
                assert new_index < num_items - len_idx_to_postpone
