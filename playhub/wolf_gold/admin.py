from django.contrib import admin

from .models import WolfGoldGiro, WolfGoldJogo, WolfGoldSessao


@admin.register(WolfGoldJogo)
class WolfGoldJogoAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug", "ativo", "saldo_inicial")


@admin.register(WolfGoldSessao)
class WolfGoldSessaoAdmin(admin.ModelAdmin):
    list_display = ("id", "apelido", "saldo", "atualizada_em")


@admin.register(WolfGoldGiro)
class WolfGoldGiroAdmin(admin.ModelAdmin):
    list_display = ("id", "modo", "aposta", "premio", "criada_em")
