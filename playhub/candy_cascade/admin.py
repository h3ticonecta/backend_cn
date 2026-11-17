from django.contrib import admin

from .models import CandyCascadeGiro, CandyCascadeJogo, CandyCascadeSessao


@admin.register(CandyCascadeJogo)
class CandyCascadeJogoAdmin(admin.ModelAdmin):
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
        ("Chances (casa × usuário)", {"fields": ("percentual_casa", "percentual_usuario")}),
    )


@admin.register(CandyCascadeSessao)
class CandyCascadeSessaoAdmin(admin.ModelAdmin):
    list_display = ("id", "apelido", "saldo", "atualizada_em")


@admin.register(CandyCascadeGiro)
class CandyCascadeGiroAdmin(admin.ModelAdmin):
    list_display = ("id", "modo", "aposta", "premio", "criada_em")