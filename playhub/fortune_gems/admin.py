from django.contrib import admin

from .models import FortuneGemsGiro, FortuneGemsJogo, FortuneGemsSessao


@admin.register(FortuneGemsJogo)
class FortuneGemsJogoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "slug",
        "ativo",
        "percentual_casa",
        "percentual_usuario",
        "saldo_inicial",
        "aposta_minima",
        "aposta_maxima",
    )
    fieldsets = (
        (None, {"fields": ("slug", "nome", "rtp_label", "ativo", "jackpot_exibicao")}),
        ("Limites", {"fields": ("saldo_inicial", "aposta_minima", "aposta_maxima")}),
        (
            "Chances (casa × usuário)",
            {
                "fields": ("percentual_casa", "percentual_usuario"),
                "description": "Sincroniza com o jogo do catálogo vinculado (slug / play_mesa_slug).",
            },
        ),
    )


@admin.register(FortuneGemsSessao)
class FortuneGemsSessaoAdmin(admin.ModelAdmin):
    list_display = ("id", "jogo", "apelido", "saldo", "atualizada_em")
    list_filter = ("jogo",)


@admin.register(FortuneGemsGiro)
class FortuneGemsGiroAdmin(admin.ModelAdmin):
    list_display = ("id", "sessao", "aposta", "premio", "carretel_1", "carretel_2", "carretel_3", "criada_em")
