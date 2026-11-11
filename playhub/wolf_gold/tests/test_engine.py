from decimal import Decimal

from django.test import SimpleTestCase

from playhub.wolf_gold import engine
from playhub.wolf_gold.config import PAYLINES


class WolfGoldEngineTests(SimpleTestCase):
    def test_paylines_count(self):
        self.assertEqual(len(PAYLINES), 25)

    def test_wild_substitutes_on_line(self):
        grid = [
            ["wolf", "wild", "wild", "wolf", "wolf"],
            ["j", "j", "j", "j", "j"],
            ["k", "k", "k", "k", "k"],
        ]
        prize, wins = engine.evaluate_paylines(grid, Decimal("1"))
        self.assertGreater(prize, 0)
        self.assertTrue(wins)

    def test_scatter_does_not_count_as_line_win(self):
        grid = [
            ["scatter", "scatter", "scatter", "j", "j"],
            ["j", "j", "j", "j", "j"],
            ["k", "k", "k", "k", "k"],
        ]
        prize, wins = engine.evaluate_paylines(grid, Decimal("1"))
        self.assertEqual(prize, Decimal("0"))

    def test_money_respin_triggers_at_six(self):
        grid = [
            ["money", "money", "j", "j", "j"],
            ["money", "money", "j", "j", "j"],
            ["money", "money", "j", "j", "j"],
        ]
        values = engine.grid_to_money_values(grid, Decimal("25"))
        self.assertTrue(engine.should_trigger_money_respin(values))

    def test_money_sum_never_negative(self):
        values = [Decimal("1"), None, Decimal("2"), None] + [None] * 11
        total = engine.sum_money_grid(values)
        self.assertGreaterEqual(total, Decimal("0"))
