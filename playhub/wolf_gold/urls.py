from django.urls import path

from . import views

urlpatterns = [
    path("", views.WolfGoldConfigView.as_view(), name="wolf-gold-config"),
    path("sessoes/", views.WolfGoldSessaoCreateView.as_view(), name="wolf-gold-sessoes"),
    path("sessoes/<uuid:sessao_id>/", views.WolfGoldSessaoDetailView.as_view(), name="wolf-gold-sessao"),
    path("girar/", views.WolfGoldGirarView.as_view(), name="wolf-gold-girar"),
]
