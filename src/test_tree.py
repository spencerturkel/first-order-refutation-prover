from typing import Tuple, TypeVar, Union

import pytest

from .tree import Tree

T = TypeVar('T')


@pytest.mark.parametrize('data', [
    (1, 2, 3),
    (1, Tree((2, 4)), 3),
])
def test_iter(data: Tuple[Union[T, Tree[T]]]):
    assert tuple(Tree(data)) == data
