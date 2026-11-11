from django.db import models


class Provider(models.Model):
    name = models.CharField("nome", max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    sort_order = models.PositiveIntegerField("ordem", default=0)
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "provedor"
        verbose_name_plural = "provedores"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Game(models.Model):
    class Category(models.TextChoices):
        SLOTS = "slots", "Slots"
        MESA = "mesa", "Mesa"
        AO_VIVO = "ao-vivo", "Ao vivo"
        CRASH = "crash", "Crash"

    class Badge(models.TextChoices):
        NONE = "", "Nenhum"
        NOVO = "novo", "Novo"
        HOT = "hot", "Hot"
        JACKPOT = "jackpot", "Jackpot"

    class PlayKind(models.TextChoices):
        NONE = "", "Somente vitrine"
        ROLETA = "roleta", "Roleta (API)"
        SLOT = "slot", "Slot (API)"

    slug = models.SlugField("id", max_length=80, unique=True)
    title = models.CharField("título", max_length=200)
    provider = models.ForeignKey(
        Provider,
        on_delete=models.PROTECT,
        related_name="games",
        verbose_name="provedor",
    )
    category = models.CharField(
        "categoria",
        max_length=20,
        choices=Category.choices,
    )
    badge = models.CharField(
        "selo",
        max_length=20,
        choices=Badge.choices,
        blank=True,
        default=Badge.NONE,
    )
    rtp = models.CharField("RTP", max_length=20, blank=True)
    gradient_start = models.CharField("gradiente início", max_length=7, default="#1e1e2e")
    gradient_end = models.CharField("gradiente fim", max_length=7, default="#0f172a")
    icon = models.CharField("ícone (emoji)", max_length=16, default="🎰")
    is_featured = models.BooleanField("destaque (populares)", default=False)
    is_new = models.BooleanField("novo", default=False)
    is_active = models.BooleanField("ativo", default=True)
    play_kind = models.CharField(
        "modo jogável",
        max_length=20,
        choices=PlayKind.choices,
        blank=True,
        default=PlayKind.NONE,
    )
    play_mesa_slug = models.SlugField(
        "mesa vinculada (roleta)",
        max_length=80,
        blank=True,
        help_text="Slug da mesa (roleta) ou do jogo slot quando play_kind=roleta/slot.",
    )
    sort_order = models.PositiveIntegerField("ordem", default=0)

    class Meta:
        ordering = ["sort_order", "title"]
        verbose_name = "jogo"
        verbose_name_plural = "jogos"

    def __str__(self) -> str:
        return self.title


class LiveSession(models.Model):
    name = models.CharField("mesa / jogo", max_length=200)
    dealer = models.CharField("dealer", max_length=80)
    viewers = models.PositiveIntegerField("espectadores", default=0)
    is_active = models.BooleanField("ativo", default=True)
    sort_order = models.PositiveIntegerField("ordem", default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "sessão ao vivo"
        verbose_name_plural = "sessões ao vivo"

    def __str__(self) -> str:
        return self.name


class Promotion(models.Model):
    title = models.CharField("título", max_length=200)
    description = models.TextField("descrição")
    tag = models.CharField("etiqueta", max_length=50)
    is_active = models.BooleanField("ativo", default=True)
    sort_order = models.PositiveIntegerField("ordem", default=0)

    class Meta:
        ordering = ["sort_order", "title"]
        verbose_name = "promoção"
        verbose_name_plural = "promoções"

    def __str__(self) -> str:
        return self.title


class HeroBanner(models.Model):
    """Conteúdo do banner principal (registro único recomendado)."""

    eyebrow = models.CharField("texto superior", max_length=120)
    title_prefix = models.CharField("título (antes do destaque)", max_length=200)
    highlight = models.CharField("valor em destaque", max_length=80)
    title_suffix = models.CharField("título (após o destaque)", max_length=200)
    subtitle = models.TextField("subtítulo")
    cta_primary = models.CharField("botão principal", max_length=80)
    cta_secondary = models.CharField("botão secundário", max_length=80)
    trust_items = models.JSONField(
        "itens de confiança",
        default=list,
        help_text='Lista de strings, ex: ["🔒 Pagamentos seguros", ...]',
    )
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "banner hero"
        verbose_name_plural = "banners hero"

    def __str__(self) -> str:
        return self.eyebrow or "Hero"
