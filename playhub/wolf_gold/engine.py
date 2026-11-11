"""Engine matemática do Wolf Gold — RNG, linhas, bônus (sem UI)."""

from __future__ import annotations

import secrets
from decimal import Decimal
from typing import Any

from playhub.wolf_gold.config import (
    FREE_SPINS_AWARD,
    FREE_SPINS_RETRIGGER,
    JACKPOT_MAJOR_MULT,
    JACKPOT_MEGA_MULT,
    JACKPOT_MINI_MULT,
    LINES_COUNT,
    MONEY_MULTIPLIERS,
    MONEY_TO_RESPIN,
    PAYLINES,
    PAYTABLE,
    REELS,
    ROWS,
    SCATTERS_TO_BONUS,
    SPECIAL,
    SYMBOL_LABELS,
    SYMBOL_WEIGHTS,
)

Grid = list[list[str]]  # [col][row]
MoneyGrid = list[Decimal | None]  # 15 posições row-major


def paytable_payload() -> list[dict]:
    return [
        {
            "id": sym,
            "label": SYMBOL_LABELS[sym],
            "pago_3": PAYTABLE[sym][0],
            "pago_4": PAYTABLE[sym][1],
            "pago_5": PAYTABLE[sym][2],
        }
        for sym in PAYTABLE
    ]


def paylines_payload() -> list[list[int]]:
    return [list(p) for p in PAYLINES]


def _weight_total() -> int:
    return sum(SYMBOL_WEIGHTS.values())


def _pick_symbol(*, allow_money: bool = True) -> str:
    pool = SYMBOL_WEIGHTS if allow_money else {k: v for k, v in SYMBOL_WEIGHTS.items() if k != "money"}
    total = sum(pool.values())
    n = secrets.randbelow(total)
    acc = 0
    for sym, w in pool.items():
        acc += w
        if n < acc:
            return sym
    return "j"


def empty_grid() -> Grid:
    return [[_pick_symbol() for _ in range(ROWS)] for _ in range(REELS)]


def _cell(grid: Grid, col: int, row: int) -> str:
    return grid[col][row]


def _matches_symbol(sym: str, target: str) -> bool:
    if sym == "wild" and target not in SPECIAL:
        return True
    if sym == target:
        return True
    if target == "wild" and sym not in SPECIAL:
        return True
    return False


def _line_symbol(grid: Grid, line: tuple[int, ...]) -> str | None:
    first = _cell(grid, 0, line[0])
    if first in ("scatter", "money"):
        return None
    if first == "wild":
        for col in range(1, REELS):
            sym = _cell(grid, col, line[col])
            if sym not in SPECIAL:
                return sym
        return "wolf"
    return first


def evaluate_paylines(grid: Grid, line_bet: Decimal) -> tuple[Decimal, list[dict]]:
    total = Decimal("0")
    wins: list[dict] = []
    for idx, pattern in enumerate(PAYLINES):
        base_sym = _line_symbol(grid, pattern)
        if not base_sym:
            continue
        count = 1
        for col in range(1, REELS):
            sym = _cell(grid, col, pattern[col])
            if sym == "scatter" or sym == "money":
                break
            if _matches_symbol(sym, base_sym) or sym == "wild":
                count += 1
            else:
                break
        if count < 3:
            continue
        mult = PAYTABLE.get(base_sym, (0, 0, 0))[count - 3]
        if mult <= 0:
            continue
        prize = (line_bet * mult).quantize(Decimal("0.01"))
        total += prize
        wins.append(
            {
                "linha": idx + 1,
                "simbolo": base_sym,
                "contagem": count,
                "premio": str(prize),
                "padrao": list(pattern),
            }
        )
    return total.quantize(Decimal("0.01")), wins


def count_symbol(grid: Grid, sym: str) -> int:
    return sum(1 for c in range(REELS) for r in range(ROWS) if grid[c][r] == sym)


def apply_giant_reels(grid: Grid) -> tuple[Grid, str]:
    """Durante free spins: colunas 2–4 viram um símbolo gigante."""
    giant = _pick_symbol(allow_money=True)
    if giant in ("scatter", "money"):
        giant = "wolf"
    new = [col[:] for col in grid]
    for col in (1, 2, 3):
        for row in range(ROWS):
            new[col][row] = giant
    return new, giant


def spin_base_grid(*, free_spin: bool = False) -> tuple[Grid, str | None]:
    grid = empty_grid()
    giant = None
    if free_spin:
        grid, giant = apply_giant_reels(grid)
    return grid, giant


def pick_money_multiplier() -> Decimal:
    return secrets.choice(MONEY_MULTIPLIERS)


def grid_to_money_values(grid: Grid, total_bet: Decimal) -> MoneyGrid:
    values: MoneyGrid = [None] * (REELS * ROWS)
    for col in range(REELS):
        for row in range(ROWS):
            if grid[col][row] == "money":
                mult = pick_money_multiplier()
                idx = row * REELS + col
                values[idx] = (total_bet * mult).quantize(Decimal("0.01"))
    return values


def money_from_values(values: MoneyGrid) -> int:
    return sum(1 for v in values if v is not None)


def should_trigger_money_respin(values: MoneyGrid) -> bool:
    return money_from_values(values) >= MONEY_TO_RESPIN


def start_money_respin_from_grid(grid: Grid, total_bet: Decimal) -> MoneyGrid:
    values = grid_to_money_values(grid, total_bet)
    if money_from_values(values) < MONEY_TO_RESPIN:
        # força símbolos money em células sorteadas até 6 (demo raro falhar)
        need = MONEY_TO_RESPIN - money_from_values(values)
        positions = [i for i, v in enumerate(values) if v is None]
        secrets.SystemRandom().shuffle(positions)
        for pos in positions[:need]:
            mult = pick_money_multiplier()
            values[pos] = (total_bet * mult).quantize(Decimal("0.01"))
    return values


def money_respin_step(
    values: MoneyGrid, total_bet: Decimal
) -> tuple[MoneyGrid, bool, Decimal | None]:
    """Um respin: preenche vazios. Retorna (novo grid, houve novo money, valor mini/major)."""
    jackpot_granted: Decimal | None = None
    filled_before = money_from_values(values)
    empty = [i for i, v in enumerate(values) if v is None]
    landed = False
    for pos in empty:
        if secrets.randbelow(100) < 28:
            mult = pick_money_multiplier()
            values[pos] = (total_bet * mult).quantize(Decimal("0.01"))
            landed = True
    if not landed and empty:
        pos = secrets.choice(empty)
        mult = pick_money_multiplier()
        values[pos] = (total_bet * mult).quantize(Decimal("0.01"))
        landed = True

    filled_after = money_from_values(values)
    if filled_after == 15:
        jackpot_granted = (total_bet * JACKPOT_MEGA_MULT).quantize(Decimal("0.01"))

    if filled_before < filled_after and filled_after == 6:
        jackpot_granted = (jackpot_granted or Decimal("0")) + (
            total_bet * JACKPOT_MINI_MULT
        ).quantize(Decimal("0.01"))
    if filled_after >= 10 and filled_before < 10:
        jackpot_granted = (jackpot_granted or Decimal("0")) + (
            total_bet * JACKPOT_MAJOR_MULT
        ).quantize(Decimal("0.01"))

    return values, landed, jackpot_granted


def sum_money_grid(values: MoneyGrid) -> Decimal:
    return sum((v for v in values if v is not None), Decimal("0")).quantize(Decimal("0.01"))


def grid_to_serializable(grid: Grid) -> list[list[str]]:
    return [col[:] for col in grid]


def parse_force_grid(force: dict | None) -> Grid | None:
    if not force or "grid" not in force:
        return None
    g = force["grid"]
    if not isinstance(g, list) or len(g) != REELS:
        return None
    return [[str(cell) for cell in col] for col in g]


def default_state() -> dict[str, Any]:
    return {
        "mode": "base",
        "free_spins_left": 0,
        "giant_symbol": None,
        "aposta_total_ref": None,
        "money_grid": None,
        "respins_left": 0,
    }
