"""Configuração do slot Wolf Gold (demo, símbolos originais)."""

from decimal import Decimal

LINES_COUNT = 25
ROWS = 3
REELS = 5

INITIAL_BALANCE = Decimal("10000.00")
BET_MIN = Decimal("0.25")
BET_MAX = Decimal("125.00")  # até 5.00 por linha × 25 linhas

FREE_SPINS_AWARD = 5
FREE_SPINS_RETRIGGER = 3
SCATTERS_TO_BONUS = 3
MONEY_TO_RESPIN = 6

JACKPOT_MINI_MULT = Decimal("20")
JACKPOT_MAJOR_MULT = Decimal("50")
JACKPOT_MEGA_MULT = Decimal("1000")

MONEY_MULTIPLIERS = (
    Decimal("0.4"),
    Decimal("1"),
    Decimal("2"),
    Decimal("3"),
    Decimal("5"),
    Decimal("8"),
    Decimal("10"),
    Decimal("15"),
    Decimal("20"),
    Decimal("50"),
    Decimal("100"),
)

SPECIAL = frozenset({"wild", "scatter", "money"})

# Paytable: multiplicador da aposta por linha (3, 4, 5 iguais da esquerda)
PAYTABLE: dict[str, tuple[int, int, int]] = {
    "wolf": (50, 100, 500),
    "buffalo": (30, 80, 300),
    "eagle": (20, 60, 200),
    "puma": (15, 40, 150),
    "a": (8, 20, 60),
    "k": (6, 15, 50),
    "q": (5, 12, 40),
    "j": (4, 10, 30),
}

# Pesos de aparição (células normais)
SYMBOL_WEIGHTS: dict[str, int] = {
    "wolf": 4,
    "buffalo": 6,
    "eagle": 8,
    "puma": 10,
    "a": 14,
    "k": 16,
    "q": 18,
    "j": 20,
    "wild": 5,
    "scatter": 4,
    "money": 3,
}

# 25 linhas clássicas 5×3 (índices de linha 0=topo, 1=meio, 2=base)
PAYLINES: tuple[tuple[int, int, int, int, int], ...] = (
    (1, 1, 1, 1, 1),
    (0, 0, 0, 0, 0),
    (2, 2, 2, 2, 2),
    (0, 1, 2, 1, 0),
    (2, 1, 0, 1, 2),
    (0, 0, 1, 0, 0),
    (2, 2, 1, 2, 2),
    (1, 0, 0, 0, 1),
    (1, 2, 2, 2, 1),
    (0, 1, 1, 1, 0),
    (2, 1, 1, 1, 2),
    (1, 1, 0, 1, 1),
    (1, 1, 2, 1, 1),
    (0, 1, 0, 1, 0),
    (2, 1, 2, 1, 2),
    (1, 0, 1, 0, 1),
    (1, 2, 1, 2, 1),
    (0, 2, 0, 2, 0),
    (2, 0, 2, 0, 2),
    (0, 2, 2, 2, 0),
    (2, 0, 0, 0, 2),
    (1, 0, 2, 0, 1),
    (1, 2, 0, 2, 1),
    (0, 0, 2, 0, 0),
    (2, 2, 0, 2, 2),
)

SYMBOL_LABELS: dict[str, str] = {
    "wolf": "Lobo",
    "buffalo": "Búfalo",
    "eagle": "Águia",
    "puma": "Puma",
    "a": "Ás",
    "k": "Rei",
    "q": "Dama",
    "j": "Valete",
    "wild": "Lobo dourado (Wild)",
    "scatter": "Montanhas & Lua (Scatter)",
    "money": "Moeda lunar (Money)",
}
