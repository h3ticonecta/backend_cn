"""Roleta europeia (0–36)."""

import random
from dataclasses import dataclass
from decimal import Decimal

RED_NUMBERS = frozenset(
    {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
)

COLUMN_1 = frozenset({1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34})
COLUMN_2 = frozenset({2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35})
COLUMN_3 = frozenset({3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36})


def number_color(n: int) -> str:
    if n == 0:
        return "green"
    return "red" if n in RED_NUMBERS else "black"


def spin_wheel() -> int:
    return random.randint(0, 36)


@dataclass(frozen=True)
class PayoutRule:
    bet_type: str
    multiplier: Decimal
    label: str


PAYOUT_RULES: tuple[PayoutRule, ...] = (
    PayoutRule("straight", Decimal("35"), "Número exato (0–36)"),
    PayoutRule("red", Decimal("1"), "Vermelho"),
    PayoutRule("black", Decimal("1"), "Preto"),
    PayoutRule("odd", Decimal("1"), "Ímpar"),
    PayoutRule("even", Decimal("1"), "Par"),
    PayoutRule("low", Decimal("1"), "Baixo (1–18)"),
    PayoutRule("high", Decimal("1"), "Alto (19–36)"),
    PayoutRule("dozen_1", Decimal("2"), "1ª dúzia (1–12)"),
    PayoutRule("dozen_2", Decimal("2"), "2ª dúzia (13–24)"),
    PayoutRule("dozen_3", Decimal("2"), "3ª dúzia (25–36)"),
    PayoutRule("column_1", Decimal("2"), "1ª coluna"),
    PayoutRule("column_2", Decimal("2"), "2ª coluna"),
    PayoutRule("column_3", Decimal("2"), "3ª coluna"),
)

ALLOWED_BET_TYPES = frozenset(r.bet_type for r in PAYOUT_RULES)


def _straight_wins(selection: int, winning: int) -> bool:
    return selection == winning


def _color_wins(color: str, winning: int) -> bool:
    if winning == 0:
        return False
    return number_color(winning) == color


def _parity_wins(parity: str, winning: int) -> bool:
    if winning == 0:
        return False
    return (winning % 2 == 1) if parity == "odd" else (winning % 2 == 0)


def _range_wins(range_id: str, winning: int) -> bool:
    if winning == 0:
        return False
    if range_id == "low":
        return 1 <= winning <= 18
    return 19 <= winning <= 36


def _dozen_wins(dozen: str, winning: int) -> bool:
    if winning == 0:
        return False
    if dozen == "dozen_1":
        return 1 <= winning <= 12
    if dozen == "dozen_2":
        return 13 <= winning <= 24
    return 25 <= winning <= 36


def _column_wins(column: str, winning: int) -> bool:
    if winning == 0:
        return False
    col_map = {
        "column_1": COLUMN_1,
        "column_2": COLUMN_2,
        "column_3": COLUMN_3,
    }
    return winning in col_map[column]


def bet_wins(bet_type: str, selection: int | None, winning: int) -> bool:
    if bet_type == "straight":
        if selection is None:
            return False
        return _straight_wins(selection, winning)
    if bet_type in ("red", "black"):
        return _color_wins(bet_type, winning)
    if bet_type in ("odd", "even"):
        return _parity_wins(bet_type, winning)
    if bet_type in ("low", "high"):
        return _range_wins(bet_type, winning)
    if bet_type.startswith("dozen_"):
        return _dozen_wins(bet_type, winning)
    if bet_type.startswith("column_"):
        return _column_wins(bet_type, winning)
    return False


def payout_multiplier(bet_type: str) -> Decimal:
    for rule in PAYOUT_RULES:
        if rule.bet_type == bet_type:
            return rule.multiplier
    raise ValueError(f"Tipo de aposta inválido: {bet_type}")
