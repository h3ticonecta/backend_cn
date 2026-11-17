from django.contrib import admin

from playhub.roulette.models import RoletaAposta, RoletaMesa, RoletaRodada, RoletaSessao


class RoletaApostaInline(admin.TabularInline):
    model = RoletaAposta
    extra = 0
    readonly_fields = ("tipo", "numero", "valor", "ganhou", "pagamento")


@admin.register(RoletaMesa)
class RoletaMesaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "slug",
        "ativa",
        "percentual_casa",
        "percentual_usuario",
        "saldo_inicial",
        "aposta_minima",
        "aposta_maxima",
    )
    list_filter = ("ativa",)
    prepopulated_fields = {"slug": ("nome",)}
    fieldsets = (
        (None, {"fields": ("slug", "nome", "variante", "ativa")}),
        (
            "Limites",
            {
                "fields": (
                    "saldo_inicial",
                    "aposta_minima",
                    "aposta_maxima",
                    "max_apostas_por_giro",
                )
            },
        ),
        (
            "Chances (casa × usuário)",
            {
                "fields": ("percentual_casa", "percentual_usuario"),
                "description": "Sincroniza com o jogo do catálogo que usa esta mesa (play_mesa_slug).",
            },
        ),
    )


@admin.register(RoletaSessao)
class RoletaSessaoAdmin(admin.ModelAdmin):
    list_display = ("id", "apelido", "mesa", "saldo", "criada_em")
    list_filter = ("mesa",)
    search_fields = ("id", "apelido")
    readonly_fields = ("id", "criada_em", "atualizada_em")


@admin.register(RoletaRodada)
class RoletaRodadaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sessao",
        "numero_sorteado",
        "cor",
        "total_apostado",
        "total_pago",
        "criada_em",
    )
    list_filter = ("cor",)
    inlines = [RoletaApostaInline]
    readonly_fields = ("criada_em",)


@admin.register(RoletaAposta)
class RoletaApostaAdmin(admin.ModelAdmin):
    list_display = ("rodada", "tipo", "numero", "valor", "ganhou", "pagamento")
    list_filter = ("tipo", "ganhou")
