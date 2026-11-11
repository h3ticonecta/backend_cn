import uuid
from decimal import Decimal

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="WolfGoldJogo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(default="wolf-gold", unique=True)),
                ("nome", models.CharField(default="Wolf Gold", max_length=120)),
                ("rtp_label", models.CharField(default="96.0%", max_length=20)),
                ("saldo_inicial", models.DecimalField(decimal_places=2, default=Decimal("10000.00"), max_digits=12)),
                ("aposta_minima", models.DecimalField(decimal_places=2, default=Decimal("0.25"), max_digits=12)),
                ("aposta_maxima", models.DecimalField(decimal_places=2, default=Decimal("125.00"), max_digits=12)),
                ("ativo", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "jogo Wolf Gold",
                "verbose_name_plural": "jogos Wolf Gold",
            },
        ),
        migrations.CreateModel(
            name="WolfGoldSessao",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("apelido", models.CharField(blank=True, max_length=40)),
                ("saldo", models.DecimalField(decimal_places=2, max_digits=12)),
                ("estado", models.JSONField(blank=True, default=dict)),
                ("criada_em", models.DateTimeField(auto_now_add=True)),
                ("atualizada_em", models.DateTimeField(auto_now=True)),
                (
                    "jogo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sessoes",
                        to="wolf_gold.wolfgoldjogo",
                    ),
                ),
            ],
            options={
                "verbose_name": "sessão Wolf Gold",
                "verbose_name_plural": "sessões Wolf Gold",
                "ordering": ["-atualizada_em"],
            },
        ),
        migrations.CreateModel(
            name="WolfGoldGiro",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("modo", models.CharField(default="base", max_length=20)),
                ("aposta", models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=12)),
                ("premio", models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=12)),
                ("grade", models.JSONField(default=list)),
                ("saldo_antes", models.DecimalField(decimal_places=2, max_digits=12)),
                ("saldo_depois", models.DecimalField(decimal_places=2, max_digits=12)),
                ("detalhes", models.JSONField(blank=True, default=dict)),
                ("criada_em", models.DateTimeField(auto_now_add=True)),
                (
                    "sessao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="giros",
                        to="wolf_gold.wolfgoldsessao",
                    ),
                ),
            ],
            options={
                "verbose_name": "giro Wolf Gold",
                "verbose_name_plural": "giros Wolf Gold",
                "ordering": ["-criada_em"],
            },
        ),
    ]
