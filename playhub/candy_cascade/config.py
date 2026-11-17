"""Constantes do slot demo (nome provisório: Candy Cascade)."""

from decimal import Decimal

DISPLAY_NAME = "Candy Cascade"
DEFAULT_SLUG = "candy-cascade"
"""Slug do card na grade PlayHub (título Sweet Bonanza)."""
CARD_CATALOG_SLUG = "sweet-bonanza"

JOG_SLUG_ALIASES: dict[str, str] = {
    CARD_CATALOG_SLUG: DEFAULT_SLUG,
}


def resolve_jogo_slug(slug: str | None) -> str | None:
    if not slug:
        return None
    raw = slug.strip()
    return JOG_SLUG_ALIASES.get(raw, raw)

COLS = 6
ROWS = 5
CLUSTER_MIN = 8
MAX_WIN_MULT = Decimal("5000")

INITIAL_BALANCE = Decimal("1000.00")
BET_MIN = Decimal("0.20")
BET_MAX = Decimal("20.00")
BET_STEPS: tuple[Decimal, ...] = (
    Decimal("0.20"),
    Decimal("0.50"),
    Decimal("1.00"),
    Decimal("2.00"),
    Decimal("5.00"),
    Decimal("10.00"),
    Decimal("20.00"),
)

FREE_SPINS_AWARD = 10
FREE_SPINS_RETRIGGER = 5
SCATTER_FOR_BONUS = 4
SCATTER_RETRIGGER_MIN = 3
BUY_FREE_SPINS_MULT = Decimal("100")
EXTRA_BET_MARKUP = Decimal("0.25")

# Pagamento scatter na grade (múltiplos da aposta total)
SCATTER_PAY: dict[int, Decimal] = {
    4: Decimal("3"),
    5: Decimal("5"),
    6: Decimal("100"),
}

# Paytable: símbolo -> (8-9, 10-11, 12+)
PAYTABLE: dict[str, tuple[Decimal, Decimal, Decimal]] = {
    "grape": (Decimal("0.25"), Decimal("0.40"), Decimal("0.80")),
    "cherry": (Decimal("0.30"), Decimal("0.50"), Decimal("1.00")),
    "lemon": (Decimal("0.35"), Decimal("0.60"), Decimal("1.20")),
    "melon": (Decimal("0.40"), Decimal("0.70"), Decimal("1.50")),
    "plum": (Decimal("0.50"), Decimal("0.90"), Decimal("2.00")),
    "jelly": (Decimal("1.00"), Decimal("2.00"), Decimal("4.00")),
    "ribbon": (Decimal("1.50"), Decimal("3.00"), Decimal("6.00")),
    "heart": (Decimal("2.50"), Decimal("5.00"), Decimal("12.00")),
    "star": (Decimal("5.00"), Decimal("10.00"), Decimal("25.00")),
}

SYMBOL_LABELS: dict[str, str] = {
    "grape": "Uva",
    "cherry": "Cereja",
    "lemon": "Limão",
    "melon": "Melão",
    "plum": "Ameixa",
    "jelly": "Gelatina",
    "ribbon": "Fita doce",
    "heart": "Coração",
    "star": "Estrela",
    "scatter": "Pirulito (Scatter)",
    "bomb": "Bomba doce (Multiplicador)",
}

NORMAL_SYMBOLS = tuple(PAYTABLE.keys())
SPECIAL = frozenset({"scatter", "bomb"})

BASE_WEIGHTS: dict[str, int] = {
    "grape": 22,
    "cherry": 20,
    "lemon": 18,
    "melon": 16,
    "plum": 14,
    "jelly": 10,
    "ribbon": 8,
    "heart": 6,
    "star": 4,
    "scatter": 5,
}

MULTIPLIER_VALUES: tuple[int, ...] = (2, 3, 5, 8, 10, 12, 15, 20, 25, 50, 100)
MULT_WEIGHTS: dict[int, int] = {2: 30, 3: 22, 5: 18, 8: 12, 10: 8, 12: 5, 15: 3, 20: 2, 25: 1, 50: 1, 100: 1}

BOMB_WEIGHT_FREE_SPIN = 6