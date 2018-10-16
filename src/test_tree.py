from typing import List

from .tree import Tree


def test_typing() -> List[Tree[str]]:
    return [
        Tree('P', [
            'x',
            Tree('f_y', ['x']),
            Tree('g', []),
            'z',
        ]),
    ]
