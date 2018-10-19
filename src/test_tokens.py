from typing import List

from .tokens import (BinaryToken, NotToken, ParenthesisToken, QuantifierToken,
                     Token)


def _test_token_sequences() -> List[List[Token]]:
    return [
        # (FORALL x (P x))
        [
            ParenthesisToken.LEFT, QuantifierToken.FORALL, 'x',
            ParenthesisToken.LEFT, 'P', 'x', ParenthesisToken.RIGHT,
            ParenthesisToken.RIGHT,
        ],
        # (EXISTS x (Q x))
        [
            ParenthesisToken.LEFT, QuantifierToken.EXISTS, 'x',
            ParenthesisToken.LEFT, 'Q', 'x', ParenthesisToken.RIGHT,
            ParenthesisToken.RIGHT
        ],
        # (AND (P x) (Q))
        [
            ParenthesisToken.LEFT, BinaryToken.AND,
            ParenthesisToken.LEFT, 'P', 'x', ParenthesisToken.RIGHT,
            ParenthesisToken.LEFT, 'Q', ParenthesisToken.RIGHT,
            ParenthesisToken.RIGHT
        ],
        # (IMPLIES (P x) (Q))
        [
            ParenthesisToken.LEFT, BinaryToken.IMPLIES,
            ParenthesisToken.LEFT, 'P', 'x', ParenthesisToken.RIGHT,
            ParenthesisToken.LEFT, 'Q', ParenthesisToken.RIGHT,
            ParenthesisToken.RIGHT
        ],
        # (OR (P x) (Q))
        [
            ParenthesisToken.LEFT, BinaryToken.OR,
            ParenthesisToken.LEFT, 'P', 'x', ParenthesisToken.RIGHT,
            ParenthesisToken.LEFT, 'Q', ParenthesisToken.RIGHT,
            ParenthesisToken.RIGHT
        ],
        # (NOT (P x))
        [
            ParenthesisToken.LEFT, NotToken.NOT,
            ParenthesisToken.LEFT, 'P', 'x', ParenthesisToken.RIGHT,
            ParenthesisToken.RIGHT
        ],
    ]
