# Generated manually for Fortune Gems slot demo

import uuid
from decimal import Decimal

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FortuneGemsJogo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(default="fortune-gems", unique=True)),
                ("nome", models.CharField(default="Fortune Gems", max_length=120)),
                ("rtp_label", models.CharField(default="96.5%", max_length=20)),
                (
                    "saldo_inicial",
                    models.DecimalField(decimal_places=2, default=Decimal("25450.00"), max_digits=12),
                ),
                ("aposta_minima", models.DecimalField(decimal_places=2, default=Decimal("10.00"), max_digits=12)),
                ("aposta_maxima", models.DecimalField(decimal_places=2, default=Decimal("1000.00"), max_digits=12)),
                (
                    "jackpot_exibicao",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("1489200.50"),
                        help_text="Valor ilustrativo do mega jackpot no header.",
                        max_digits=14,
                    ),
                ),
                ("ativo", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "jogo Fortune Gems",
                "verbose_name_plural": "jogos Fortune Gems",
            },
        ),
        migrations.CreateModel(
            name="FortuneGemsSessao",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("apelido", models.CharField(blank=True, max_length=40)),
                ("saldo", models.DecimalField(decimal_places=2, max_digits=12)),
                ("criada_em", models.DateTimeField(auto_now_add=True)),
                ("atualizada_em", models.DateTimeField(auto_now=True)),
                (
                    "jogo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sessoes",
                        to="fortune_gems.fortunegemsjogo",
                    ),
                ),
            ],
            options={
                "verbose_name": "sessão Fortune Gems",
                "verbose_name_plural": "sessões Fortune Gems",
                "ordering": ["-atualizada_em"],
            },
        ),
        migrations.CreateModel(
            name="FortuneGemsGiro",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("aposta", models.DecimalField(decimal_places=2, max_digits=12)),
                ("carretel_1", models.CharField(max_length=16)),
                ("carretel_2", models.CharField(max_length=16)),
                ("carretel_3", models.CharField(max_length=16)),
                ("premio", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("saldo_antes", models.DecimalField(decimal_places=2, max_digits=12)),
                ("saldo_depois", models.DecimalField(decimal_places=2, max_digits=12)),
                ("criada_em", models.DateTimeField(auto_now_add=True)),
                (
                    "sessao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="giros",
                        to="fortune_gems.fortunegemssessao",
                    ),
                ),
            ],
            options={
                "verbose_name": "giro Fortune Gems",
                "verbose_name_plural": "giros Fortune Gems",
                "ordering": ["-criada_em"],
            },
        ),
    ]
