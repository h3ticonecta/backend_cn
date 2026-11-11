from django.urls import path

from . import views

urlpatterns = [
    path("", views.RoletaConfigView.as_view(), name="roleta-config"),
    path("sessoes/", views.RoletaSessaoCreateView.as_view(), name="roleta-sessao-create"),
    path(
        "sessoes/<uuid:sessao_id>/",
        views.RoletaSessaoDetailView.as_view(),
        name="roleta-sessao-detail",
    ),
    path("girar/", views.RoletaGirarView.as_view(), name="roleta-girar"),
]
