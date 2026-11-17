from django.urls import path

from . import views

urlpatterns = [
    path("", views.CandyCascadeConfigView.as_view(), name="candy-cascade-config"),
    path("sessoes/", views.CandyCascadeSessaoCreateView.as_view(), name="candy-cascade-sessoes"),
    path(
        "sessoes/<uuid:sessao_id>/",
        views.CandyCascadeSessaoDetailView.as_view(),
        name="candy-cascade-sessao",
    ),
    path("girar/", views.CandyCascadeGirarView.as_view(), name="candy-cascade-girar"),
]