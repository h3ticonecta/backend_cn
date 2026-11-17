"""Percentuais configuráveis de chance casa vs. usuário (demo)."""

from __future__ import annotations

import secrets
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

DEFAULT_PERCENTUAL_CASA = Decimal("55.00")
DEFAULT_PERCENTUAL_USUARIO = Decimal("45.00")


def validate_chance_pair(casa: Decimal, usuario: Decimal) -> None:
    if casa < 0 or casa > 100 or usuario < 0 or usuario > 100:
        raise ValidationError("Percentuais devem estar entre 0 e 100.")
    if (casa + usuario).quantize(Decimal("0.01")) != Decimal("100.00"):
        raise ValidationError(
            "A soma do percentual da casa e do usuário deve ser exatamente 100%."
        )


def roll_favor_usuario(percentual_usuario: Decimal) -> bool:
    """True quando o sorteio desta rodada deve favorecer o jogador."""
    scaled = int((percentual_usuario * 100).to_integral_value())
    scaled = max(0, min(10_000, scaled))
    return secrets.randbelow(10_000) < scaled


def chances_payload(casa: Decimal, usuario: Decimal) -> dict[str, str]:
    return {
        "percentual_casa": str(casa),
        "percentual_usuario": str(usuario),
    }


class ChancePercentMixin(models.Model):
    percentual_casa = models.DecimalField(
        "percentual chance casa (%)",
        max_digits=5,
        decimal_places=2,
        default=DEFAULT_PERCENTUAL_CASA,
        help_text="Probabilidade (0–100) de o resultado favorecer a casa em cada rodada/giro.",
    )
    percentual_usuario = models.DecimalField(
        "percentual chance usuário (%)",
        max_digits=5,
        decimal_places=2,
        default=DEFAULT_PERCENTUAL_USUARIO,
        help_text="Deve somar 100% com o percentual da casa.",
    )

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        validate_chance_pair(self.percentual_casa, self.percentual_usuario)