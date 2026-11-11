import uuid
from decimal import Decimal

from django.db import models
from django.utils import timezone


class RoletaMesa(models.Model):
    """Configuração da mesa de roleta (demo / play money)."""

    slug = models.SlugField(unique=True, default="roleta-brasil")
    nome = models.CharField(max_length=120, default="Roleta Brasil")
    variante = models.CharField(
        max_length=20,
        default="european",
        help_text="european = um único zero (0–36)",
    )
    saldo_inicial = models.DecimalField(
        "fichas iniciais",
        max_digits=12,
        decimal_places=2,
        default=Decimal("1000.00"),
    )
    aposta_minima = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("1.00"))
    aposta_maxima = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("500.00"))
    max_apostas_por_giro = models.PositiveSmallIntegerField(default=12)
    ativa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "mesa de roleta"
        verbose_name_plural = "mesas de roleta"

    def __str__(self) -> str:
        return self.nome


class RoletaSessao(models.Model):
    """Sessão de jogador (fichas demo), identificada por UUID."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mesa = models.ForeignKey(
        RoletaMesa,
        on_delete=models.PROTECT,
        related_name="sessoes",
    )
    apelido = models.CharField(max_length=40, blank=True)
    saldo = models.DecimalField(max_digits=12, decimal_places=2)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "sessão roleta"
        verbose_name_plural = "sessões roleta"
        ordering = ["-atualizada_em"]

    def __str__(self) -> str:
        return f"{self.apelido or self.id} — {self.saldo}"


class RoletaRodada(models.Model):
    """Um giro da roda com resultado e total de apostas."""

    class Status(models.TextChoices):
        CONCLUIDA = "concluida", "Concluída"

    sessao = models.ForeignKey(
        RoletaSessao,
        on_delete=models.CASCADE,
        related_name="rodadas",
    )
    numero_sorteado = models.PositiveSmallIntegerField()
    cor = models.CharField(max_length=10)
    total_apostado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_pago = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_antes = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_depois = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONCLUIDA)
    criada_em = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "rodada roleta"
        verbose_name_plural = "rodadas roleta"
        ordering = ["-criada_em"]

    def __str__(self) -> str:
        return f"#{self.pk} → {self.numero_sorteado} ({self.cor})"


class RoletaAposta(models.Model):
    """Aposta individual dentro de uma rodada."""

    rodada = models.ForeignKey(
        RoletaRodada,
        on_delete=models.CASCADE,
        related_name="apostas",
    )
    tipo = models.CharField(max_length=20)
    numero = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Obrigatório quando tipo=straight",
    )
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    ganhou = models.BooleanField(default=False)
    pagamento = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = "aposta roleta"
        verbose_name_plural = "apostas roleta"

    def __str__(self) -> str:
        return f"{self.tipo} {self.valor}"
