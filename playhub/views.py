from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Game, HeroBanner, LiveSession, Promotion, Provider
from .serializers import (
    CATEGORY_CHOICES,
    GameSerializer,
    HeroBannerSerializer,
    LiveSessionSerializer,
    PromotionSerializer,
    ProviderSerializer,
)


class GameListView(generics.ListAPIView):
    serializer_class = GameSerializer

    def get_queryset(self):
        qs = Game.objects.filter(is_active=True).select_related("provider")
        category = self.request.query_params.get("category", "").strip()

        if category == "populares":
            qs = qs.filter(is_featured=True)
        elif category == "novos":
            qs = qs.filter(Q(is_new=True) | Q(badge=Game.Badge.NOVO))
        elif category and category not in ("todos", ""):
            qs = qs.filter(category=category)

        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(provider__name__icontains=search)
            )

        return qs


class CategoryListView(APIView):
    def get(self, request):
        return Response(CATEGORY_CHOICES)


class ProviderListView(generics.ListAPIView):
    serializer_class = ProviderSerializer

    def get_queryset(self):
        return Provider.objects.filter(is_active=True)


class LiveSessionListView(generics.ListAPIView):
    serializer_class = LiveSessionSerializer

    def get_queryset(self):
        return LiveSession.objects.filter(is_active=True)


class PromotionListView(generics.ListAPIView):
    serializer_class = PromotionSerializer

    def get_queryset(self):
        return Promotion.objects.filter(is_active=True)


class HeroBannerView(APIView):
    def get(self, request):
        hero = HeroBanner.objects.filter(is_active=True).order_by("-id").first()
        if not hero:
            return Response(None)
        return Response(HeroBannerSerializer(hero).data)


class HomeAggregateView(APIView):
    """Payload único para alimentar a landing PlayHub."""

    def get(self, request):
        games_qs = Game.objects.filter(is_active=True).select_related("provider")
        return Response(
            {
                "categories": CATEGORY_CHOICES,
                "games": GameSerializer(games_qs, many=True).data,
                "popular_ids": list(
                    games_qs.filter(is_featured=True).values_list("slug", flat=True)
                ),
                "new_ids": list(
                    games_qs.filter(is_new=True).values_list("slug", flat=True)
                ),
                "providers": [
                    p["name"]
                    for p in ProviderSerializer(
                        Provider.objects.filter(is_active=True), many=True
                    ).data
                ],
                "live": LiveSessionSerializer(
                    LiveSession.objects.filter(is_active=True), many=True
                ).data,
                "promotions": PromotionSerializer(
                    Promotion.objects.filter(is_active=True), many=True
                ).data,
                "hero": (
                    HeroBannerSerializer(hero).data
                    if (hero := HeroBanner.objects.filter(is_active=True).first())
                    else None
                ),
            }
        )
