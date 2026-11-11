"""RNG e paytable do slot (ids alinhados ao frontend)."""

from __future__ import annotations

import secrets
from decimal import Decimal
from typing import TypedDict


class SymbolRule(TypedDict):
    id: str
    label: str
    multiplier: Decimal
    weight: int


SYMBOL_RULES: tuple[SymbolRule, ...] = (
    {"id": "7", "label": "MEGA JACKPOT", "multiplier": Decimal("500"), "weight": 2},
    {"id": "gem", "label": "Diamantes", "multiplier": Decimal("200"), "weight": 5},
    {"id": "bell", "label": "Sinos de Ouro", "multiplier": Decimal("100"), "weight": 8},
    {"id": "melon", "label": "Melancias", "multiplier": Decimal("50"), "weight": 12},
    {"id": "cherry", "label": "Cerejas Clássicas", "multiplier": Decimal("25"), "weight": 18},
    {"id": "lemon", "label": "Limão", "multiplier": Decimal("10"), "weight": 22},
    {"id": "grape", "label": "Uva", "multiplier": Decimal("10"), "weight": 22},
)

SYMBOL_IDS = {rule["id"] for rule in SYMBOL_RULES}
_WEIGHT_TOTAL = sum(r["weight"] for r in SYMBOL_RULES)


def paytable_payload() -> list[dict]:
    return [
        {
            "id": r["id"],
            "label": r["label"],
            "multiplicador": str(r["multiplier"]),
        }
        for r in SYMBOL_RULES
    ]


def _pick_symbol() -> str:
    n = secrets.randbelow(_WEIGHT_TOTAL)
    acc = 0
    for rule in SYMBOL_RULES:
        acc += rule["weight"]
        if n < acc:
            return rule["id"]
    return SYMBOL_RULES[-1]["id"]


def spin_reels() -> tuple[str, str, str]:
    return _pick_symbol(), _pick_symbol(), _pick_symbol()


def evaluate_spin(reels: tuple[str, str, str], aposta: Decimal) -> tuple[Decimal, bool, str]:
    a, b, c = reels
    if a == b == c:
        mult = next(r["multiplier"] for r in SYMBOL_RULES if r["id"] == a)
        return (aposta * mult).quantize(Decimal("0.01")), True, f"trinca_{a}"
    return Decimal("0.00"), False, ""
