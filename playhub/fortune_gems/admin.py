from django.contrib import admin

from .models import FortuneGemsGiro, FortuneGemsJogo, FortuneGemsSessao


@admin.register(FortuneGemsJogo)
class FortuneGemsJogoAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug", "ativo", "saldo_inicial", "aposta_minima", "aposta_maxima")


@admin.register(FortuneGemsSessao)
class FortuneGemsSessaoAdmin(admin.ModelAdmin):
    list_display = ("id", "jogo", "apelido", "saldo", "atualizada_em")
    list_filter = ("jogo",)


@admin.register(FortuneGemsGiro)
class FortuneGemsGiroAdmin(admin.ModelAdmin):
    list_display = ("id", "sessao", "aposta", "premio", "carretel_1", "carretel_2", "carretel_3", "criada_em")
