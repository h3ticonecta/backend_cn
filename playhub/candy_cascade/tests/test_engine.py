import random
from decimal import Decimal

from django.test import SimpleTestCase

from playhub.candy_cascade import engine
from playhub.candy_cascade.config import COLS, ROWS


class CandyCascadeEngineTests(SimpleTestCase):
    def test_cluster_payment_tiers(self):
        grid = [["cherry" for _ in range(ROWS)] for _ in range(COLS)]
        grid[0][0] = "plum"
        wins = engine.evaluate_clusters(grid, Decimal("1"))
        self.assertEqual(len(wins), 1)
        grape_win = next(w for w in wins if w.symbol == "cherry")
        self.assertGreaterEqual(grape_win.count, 8)

    def test_scatter_pay_threshold(self):
        pay = engine.scatter_pay(4, Decimal("10"))
        self.assertEqual(pay, Decimal("30.00"))

    def test_gravity_refill(self):
        rng = random.Random(42)
        grid, mults = engine.new_grid(free_spin=False, extra_scatter=False, rng=rng)
        wins = engine.evaluate_clusters(grid, Decimal("1"))
        if wins:
            engine.remove_cells(grid, mults, wins[0].cells)
            engine.gravity(grid, mults)
            for c in range(COLS):
                engine.refill_column(
                    c, grid, mults, free_spin=False, extra_scatter=False, rng=rng
                )
        self.assertTrue(all(grid[c][r] is not None for c in range(COLS) for r in range(ROWS)))

    def test_play_round_bounded(self):
        rng = random.Random(7)
        result = engine.play_round(aposta=Decimal("1"), free_spin=False, extra_scatter=False, rng=rng)
        cap = Decimal("5000")
        self.assertLessEqual(result.premio_total, cap)