from django.contrib import admin

from .models import WolfGoldGiro, WolfGoldJogo, WolfGoldSessao


@admin.register(WolfGoldJogo)
class WolfGoldJogoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "slug",
        "ativo",
        "percentual_casa",
        "percentual_usuario",
        "saldo_inicial",
    )
    fieldsets = (
        (None, {"fields": ("slug", "nome", "rtp_label", "ativo")}),
        ("Limites", {"fields": ("saldo_inicial", "aposta_minima", "aposta_maxima")}),
        (
            "Chances (casa × usuário)",
            {
                "fields": ("percentual_casa", "percentual_usuario"),
                "description": "Sincroniza com o jogo do catálogo vinculado (slug / play_mesa_slug).",
            },
        ),
    )


@admin.register(WolfGoldSessao)
class WolfGoldSessaoAdmin(admin.ModelAdmin):
    list_display = ("id", "apelido", "saldo", "atualizada_em")


@admin.register(WolfGoldGiro)
class WolfGoldGiroAdmin(admin.ModelAdmin):
    list_display = ("id", "modo", "aposta", "premio", "criada_em")
