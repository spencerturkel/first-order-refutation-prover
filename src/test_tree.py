from typing import FrozenSet, List, Tuple, TypeVar, Union

import pytest

from .tree import Tree

T = TypeVar('T')


@pytest.mark.parametrize('data', [
    (1, 2, 3),
    (1, Tree((2, 4)), 3),
])
def test_iter(data: Tuple[Union[T, Tree[T]]]):
    assert tuple(Tree(data)) == data


def test_typing() -> List[Tree[str]]:
    return [
        Tree((
            'P',
            'x',
            Tree((
                'f_y',
                'x',
            ))
        )),
    ]
