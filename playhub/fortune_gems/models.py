import uuid
from decimal import Decimal

from django.db import models


class FortuneGemsJogo(models.Model):
    """Configuração do slot demo (play money)."""

    slug = models.SlugField(unique=True, default="fortune-gems")
    nome = models.CharField(max_length=120, default="Fortune Gems")
    rtp_label = models.CharField(max_length=20, default="96.5%")
    saldo_inicial = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("25450.00"),
    )
    aposta_minima = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("10.00"))
    aposta_maxima = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("1000.00"))
    jackpot_exibicao = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("1489200.50"),
        help_text="Valor ilustrativo do mega jackpot no header.",
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "jogo Fortune Gems"
        verbose_name_plural = "jogos Fortune Gems"

    def __str__(self) -> str:
        return self.nome


class FortuneGemsSessao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jogo = models.ForeignKey(FortuneGemsJogo, on_delete=models.PROTECT, related_name="sessoes")
    apelido = models.CharField(max_length=40, blank=True)
    saldo = models.DecimalField(max_digits=12, decimal_places=2)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-atualizada_em"]
        verbose_name = "sessão Fortune Gems"
        verbose_name_plural = "sessões Fortune Gems"

    def __str__(self) -> str:
        return f"{self.apelido or self.id} — {self.saldo}"


class FortuneGemsGiro(models.Model):
    sessao = models.ForeignKey(FortuneGemsSessao, on_delete=models.CASCADE, related_name="giros")
    aposta = models.DecimalField(max_digits=12, decimal_places=2)
    carretel_1 = models.CharField(max_length=16)
    carretel_2 = models.CharField(max_length=16)
    carretel_3 = models.CharField(max_length=16)
    premio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_antes = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_depois = models.DecimalField(max_digits=12, decimal_places=2)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criada_em"]
        verbose_name = "giro Fortune Gems"
        verbose_name_plural = "giros Fortune Gems"
