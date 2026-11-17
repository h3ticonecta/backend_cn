import uuid
from decimal import Decimal

from django.db import models

from playhub.candy_cascade.config import DISPLAY_NAME, DEFAULT_SLUG
from playhub.chance_config import ChancePercentMixin


class CandyCascadeJogo(ChancePercentMixin, models.Model):
    slug = models.SlugField(unique=True, default=DEFAULT_SLUG)
    nome = models.CharField(max_length=120, default=DISPLAY_NAME)
    rtp_label = models.CharField(max_length=20, default="96.0%")
    saldo_inicial = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("1000.00")
    )
    aposta_minima = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.20"))
    aposta_maxima = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("20.00"))
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "jogo Candy Cascade"
        verbose_name_plural = "jogos Candy Cascade"

    def __str__(self) -> str:
        return self.nome


class CandyCascadeSessao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jogo = models.ForeignKey(CandyCascadeJogo, on_delete=models.PROTECT, related_name="sessoes")
    apelido = models.CharField(max_length=40, blank=True)
    saldo = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.JSONField(default=dict, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-atualizada_em"]
        verbose_name = "sessão Candy Cascade"
        verbose_name_plural = "sessões Candy Cascade"


class CandyCascadeGiro(models.Model):
    sessao = models.ForeignKey(CandyCascadeSessao, on_delete=models.CASCADE, related_name="giros")
    modo = models.CharField(max_length=20, default="base")
    aposta = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    premio = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    grade = models.JSONField(default=list)
    detalhes = models.JSONField(default=dict, blank=True)
    saldo_antes = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_depois = models.DecimalField(max_digits=12, decimal_places=2)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criada_em"]
        verbose_name = "giro Candy Cascade"
        verbose_name_plural = "giros Candy Cascade"