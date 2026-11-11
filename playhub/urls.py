from django.urls import include, path

from . import views

urlpatterns = [
    path("v1/games/", views.GameListView.as_view(), name="game-list"),
    path("v1/games/<slug:slug>/", views.GameDetailView.as_view(), name="game-detail"),
    path("v1/categories/", views.CategoryListView.as_view(), name="category-list"),
    path("v1/providers/", views.ProviderListView.as_view(), name="provider-list"),
    path("v1/live/", views.LiveSessionListView.as_view(), name="live-list"),
    path("v1/promotions/", views.PromotionListView.as_view(), name="promotion-list"),
    path("v1/hero/", views.HeroBannerView.as_view(), name="hero"),
    path("v1/home/", views.HomeAggregateView.as_view(), name="home"),
    path("v1/roleta/", include("playhub.roulette.urls")),
    path("v1/slots/fortune-gems/", include("playhub.fortune_gems.urls")),
    path("v1/slots/wolf-gold/", include("playhub.wolf_gold.urls")),
]
