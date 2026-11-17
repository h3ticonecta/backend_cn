"""Engine 6×5 pay-anywhere com cascata (sem React)."""

from __future__ import annotations

import random
import secrets
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from playhub.candy_cascade.config import (
    BASE_WEIGHTS,
    BET_STEPS,
    BOMB_WEIGHT_FREE_SPIN,
    CLUSTER_MIN,
    COLS,
    FREE_SPINS_AWARD,
    FREE_SPINS_RETRIGGER,
    MAX_WIN_MULT,
    MULT_WEIGHTS,
    PAYTABLE,
    ROWS,
    SCATTER_FOR_BONUS,
    SCATTER_PAY,
    SCATTER_RETRIGGER_MIN,
    SPECIAL,
    SYMBOL_LABELS,
)

Grid = list[list[str]]
MultGrid = list[list[int | None]]


def paytable_payload() -> list[dict]:
    return [
        {
            "id": sym,
            "label": SYMBOL_LABELS.get(sym, sym),
            "pagamento_8_9": str(PAYTABLE[sym][0]),
            "pagamento_10_11": str(PAYTABLE[sym][1]),
            "pagamento_12_mais": str(PAYTABLE[sym][2]),
        }
        for sym in PAYTABLE
    ]


def bet_steps_payload() -> list[str]:
    return [str(b) for b in BET_STEPS]


def _tier_index(count: int) -> int:
    if count <= 9:
        return 0
    if count <= 11:
        return 1
    return 2


def _cluster_pay(sym: str, count: int) -> Decimal:
    tier = _tier_index(count)
    return PAYTABLE[sym][tier]


def empty_mult_grid() -> MultGrid:
    return [[None for _ in range(ROWS)] for _ in range(COLS)]


def _randbelow(n: int, rng: random.Random | None) -> int:
    if rng is not None:
        return rng.randrange(n)
    return secrets.randbelow(n)


def _pick_weighted(pool: dict[str, int], rng: random.Random | None) -> str:
    total = sum(pool.values())
    n = _randbelow(total, rng)
    acc = 0
    for sym, w in pool.items():
        acc += w
        if n < acc:
            return sym
    return next(reversed(pool))


def _pick_multiplier(rng: random.Random | None) -> int:
    total = sum(MULT_WEIGHTS.values())
    n = _randbelow(total, rng)
    acc = 0
    for mult, w in MULT_WEIGHTS.items():
        acc += w
        if n < acc:
            return mult
    return 2


def _weights_for_spin(*, free_spin: bool, extra_scatter: bool) -> dict[str, int]:
    w = dict(BASE_WEIGHTS)
    if extra_scatter:
        w["scatter"] = w.get("scatter", 5) * 2
    if free_spin:
        w["bomb"] = BOMB_WEIGHT_FREE_SPIN
    else:
        w.pop("bomb", None)
    return w


def new_grid(*, free_spin: bool, extra_scatter: bool, rng: random.Random | None) -> tuple[Grid, MultGrid]:
    pool = _weights_for_spin(free_spin=free_spin, extra_scatter=extra_scatter)
    grid: Grid = [[_pick_weighted(pool, rng) for _ in range(ROWS)] for _ in range(COLS)]
    mults = empty_mult_grid()
    if free_spin:
        for c in range(COLS):
            for r in range(ROWS):
                if grid[c][r] == "bomb":
                    mults[c][r] = _pick_multiplier(rng)
                    grid[c][r] = "bomb"
    return grid, mults


def refill_column(
    col: int,
    grid: Grid,
    mults: MultGrid,
    *,
    free_spin: bool,
    extra_scatter: bool,
    rng: random.Random | None,
) -> None:
    pool = _weights_for_spin(free_spin=free_spin, extra_scatter=extra_scatter)
    for r in range(ROWS):
        if grid[col][r] is None:
            sym = _pick_weighted(pool, rng)
            grid[col][r] = sym
            if sym == "bomb" and free_spin:
                mults[col][r] = _pick_multiplier(rng)
            else:
                mults[col][r] = None


def gravity(grid: Grid, mults: MultGrid) -> None:
    for c in range(COLS):
        symbols: list[str] = []
        mult_vals: list[int | None] = []
        for r in range(ROWS):
            if grid[c][r] is not None:
                symbols.append(grid[c][r])
                mult_vals.append(mults[c][r])
        missing = ROWS - len(symbols)
        for r in range(ROWS):
            if r < missing:
                grid[c][r] = None
                mults[c][r] = None
            else:
                idx = r - missing
                grid[c][r] = symbols[idx]
                mults[c][r] = mult_vals[idx]


def count_symbol(grid: Grid, sym: str) -> int:
    return sum(1 for c in range(COLS) for r in range(ROWS) if grid[c][r] == sym)


def scatter_pay(count: int, aposta: Decimal) -> Decimal:
    if count >= 6:
        mult = SCATTER_PAY[6]
    else:
        mult = SCATTER_PAY.get(count, Decimal("0"))
    if mult <= 0:
        return Decimal("0")
    return (aposta * mult).quantize(Decimal("0.01"))


@dataclass
class ClusterWin:
    symbol: str
    count: int
    cells: list[tuple[int, int]]
    premio: Decimal


def evaluate_clusters(grid: Grid, aposta: Decimal) -> list[ClusterWin]:
    counts: dict[str, list[tuple[int, int]]] = {}
    for c in range(COLS):
        for r in range(ROWS):
            sym = grid[c][r]
            if not sym or sym in SPECIAL:
                continue
            counts.setdefault(sym, []).append((c, r))
    wins: list[ClusterWin] = []
    for sym, cells in counts.items():
        n = len(cells)
        if n < CLUSTER_MIN:
            continue
        pay = (_cluster_pay(sym, n) * aposta).quantize(Decimal("0.01"))
        wins.append(ClusterWin(symbol=sym, count=n, cells=cells, premio=pay))
    return wins


def remove_cells(grid: Grid, mults: MultGrid, cells: list[tuple[int, int]]) -> None:
    for c, r in cells:
        grid[c][r] = None
        mults[c][r] = None


def visible_multipliers(mults: MultGrid) -> list[int]:
    values: list[int] = []
    for c in range(COLS):
        for r in range(ROWS):
            if mults[c][r] is not None:
                values.append(mults[c][r])
    return values


def sum_multiplier_factor(mults: MultGrid) -> int:
    vals = visible_multipliers(mults)
    if not vals:
        return 1
    return sum(vals)


def grid_to_serializable(grid: Grid) -> list[list[str | None]]:
    return [[grid[c][r] for r in range(ROWS)] for c in range(COLS)]


def mults_to_serializable(mults: MultGrid) -> list[list[int | None]]:
    return [[mults[c][r] for r in range(ROWS)] for c in range(COLS)]


def default_state() -> dict[str, Any]:
    return {
        "mode": "base",
        "free_spins_left": 0,
        "free_spins_total": "0.00",
        "aposta_ref": None,
        "extra_bet": False,
    }


@dataclass
class CascadeStep:
    wins: list[ClusterWin] = field(default_factory=list)
    premio_clusters: Decimal = Decimal("0")
    premio_scatter: Decimal = Decimal("0")
    grade: Grid | None = None
    multiplicadores: MultGrid | None = None


@dataclass
class SpinResult:
    passos: list[dict[str, Any]]
    premio_total: Decimal
    free_spins_ganhos: int
    grade_final: Grid
    mults_final: MultGrid
    detalhes: dict[str, Any]


def run_single_tumble_sequence(
    grid: Grid,
    mults: MultGrid,
    aposta: Decimal,
    *,
    free_spin: bool,
    extra_scatter: bool,
    rng: random.Random | None,
) -> tuple[list[dict[str, Any]], Decimal, int, Grid, MultGrid]:
    passos: list[dict[str, Any]] = []
    total = Decimal("0")
    free_spins_ganhos = 0

    while True:
        wins = evaluate_clusters(grid, aposta)
        if not wins:
            break

        removed: list[tuple[int, int]] = []
        win_rows: list[dict] = []
        for w in wins:
            removed.extend(w.cells)
            win_rows.append(
                {
                    "simbolo": w.symbol,
                    "contagem": w.count,
                    "premio": str(w.premio),
                    "celulas": w.cells,
                }
            )

        step_premio = sum((w.premio for w in wins), Decimal("0"))
        remove_cells(grid, mults, removed)

        passos.append(
            {
                "ganhos": win_rows,
                "premio_parcial": str(step_premio),
                "grade": grid_to_serializable(grid),
                "multiplicadores": mults_to_serializable(mults),
            }
        )
        total += step_premio

        gravity(grid, mults)
        for c in range(COLS):
            refill_column(c, grid, mults, free_spin=free_spin, extra_scatter=extra_scatter, rng=rng)

    scatter_n = count_symbol(grid, "scatter")
    premio_scatter = scatter_pay(scatter_n, aposta) if scatter_n >= 4 else Decimal("0")
    if premio_scatter > 0:
        passos.append(
            {
                "evento": "pagamento_scatter",
                "scatters": scatter_n,
                "premio_parcial": str(premio_scatter),
                "grade": grid_to_serializable(grid),
                "multiplicadores": mults_to_serializable(mults),
            }
        )
        total += premio_scatter

    mult_factor = sum_multiplier_factor(mults) if free_spin else 1
    if mult_factor > 1 and total > 0:
        boosted = (total * Decimal(mult_factor)).quantize(Decimal("0.01"))
        passos.append(
            {
                "evento": "multiplicadores_aplicados",
                "fator": mult_factor,
                "premio_antes": str(total),
                "premio_depois": str(boosted),
            }
        )
        total = boosted
        for c in range(COLS):
            for r in range(ROWS):
                if mults[c][r] is not None:
                    mults[c][r] = None

    if free_spin:
        if scatter_n >= SCATTER_RETRIGGER_MIN:
            free_spins_ganhos += FREE_SPINS_RETRIGGER
    elif scatter_n >= SCATTER_FOR_BONUS:
        free_spins_ganhos += FREE_SPINS_AWARD

    cap = (aposta * MAX_WIN_MULT).quantize(Decimal("0.01"))
    if total > cap:
        total = cap
        passos.append({"evento": "teto_maximo", "teto": str(cap)})

    return passos, total, free_spins_ganhos, grid, mults


def play_round(
    *,
    aposta: Decimal,
    free_spin: bool,
    extra_scatter: bool,
    rng: random.Random | None = None,
    start_free: bool = False,
) -> SpinResult:
    grid, mults = new_grid(free_spin=free_spin or start_free, extra_scatter=extra_scatter, rng=rng)
    if start_free:
        grid, mults = new_grid(free_spin=True, extra_scatter=extra_scatter, rng=rng)

    passos, premio, fs_gain, grid, mults = run_single_tumble_sequence(
        grid,
        mults,
        aposta,
        free_spin=free_spin or start_free,
        extra_scatter=extra_scatter,
        rng=rng,
    )

    detalhes = {
        "free_spins_ganhos": fs_gain,
        "modo": "free_spin" if free_spin or start_free else "base",
    }
    return SpinResult(
        passos=passos,
        premio_total=premio,
        free_spins_ganhos=fs_gain,
        grade_final=grid,
        mults_final=mults,
        detalhes=detalhes,
    )