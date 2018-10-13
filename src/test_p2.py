"""Test p2.py"""

from typing import List

import pytest

from . import p2


@pytest.mark.parametrize(
    'fSets, indices',  # noqa
    [([], [])]
)
def test_findIncSets(fSets: List[List[str]],
                     indices: List[int]) -> None:  # noqa
    assert p2.findIncSet(fSets) == indices
