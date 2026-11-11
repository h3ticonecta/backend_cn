from django.urls import path

from . import views

urlpatterns = [
    path("", views.FortuneGemsConfigView.as_view(), name="fortune-gems-config"),
    path("sessoes/", views.FortuneGemsSessaoCreateView.as_view(), name="fortune-gems-sessoes"),
    path("sessoes/<uuid:sessao_id>/", views.FortuneGemsSessaoDetailView.as_view(), name="fortune-gems-sessao"),
    path("girar/", views.FortuneGemsGirarView.as_view(), name="fortune-gems-girar"),
]
