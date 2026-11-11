import uuid
from decimal import Decimal

from django.db import models


class WolfGoldJogo(models.Model):
    slug = models.SlugField(unique=True, default="wolf-gold")
    nome = models.CharField(max_length=120, default="Wolf Gold")
    rtp_label = models.CharField(max_length=20, default="96.0%")
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("10000.00"))
    aposta_minima = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.25"))
    aposta_maxima = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("125.00"))
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "jogo Wolf Gold"
        verbose_name_plural = "jogos Wolf Gold"

    def __str__(self) -> str:
        return self.nome


class WolfGoldSessao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jogo = models.ForeignKey(WolfGoldJogo, on_delete=models.PROTECT, related_name="sessoes")
    apelido = models.CharField(max_length=40, blank=True)
    saldo = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.JSONField(default=dict, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-atualizada_em"]
        verbose_name = "sessão Wolf Gold"
        verbose_name_plural = "sessões Wolf Gold"


class WolfGoldGiro(models.Model):
    sessao = models.ForeignKey(WolfGoldSessao, on_delete=models.CASCADE, related_name="giros")
    modo = models.CharField(max_length=20, default="base")
    aposta = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    premio = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    grade = models.JSONField(default=list)
    saldo_antes = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_depois = models.DecimalField(max_digits=12, decimal_places=2)
    detalhes = models.JSONField(default=dict, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criada_em"]
        verbose_name = "giro Wolf Gold"
        verbose_name_plural = "giros Wolf Gold"
