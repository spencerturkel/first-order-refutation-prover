from typing import List

from .tree import Left, Right, Tree, TreeF


def test_typing() -> List[Tree[str]]:
    return [
        Tree(TreeF('P', [
            Left('x'),
            Right(Tree(TreeF('f_y', [
                Right(Tree(TreeF('x', []))),
            ]))),
            Right(Tree(TreeF('g', []))),
            Left('z'),
        ])),
    ]
