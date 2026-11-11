from rest_framework import serializers

from .models import Game, HeroBanner, LiveSession, Promotion, Provider

CATEGORY_CHOICES = [
    {"id": "todos", "label": "Todos"},
    {"id": "populares", "label": "Populares"},
    {"id": "slots", "label": "Slots"},
    {"id": "mesa", "label": "Mesa"},
    {"id": "ao-vivo", "label": "Ao vivo"},
    {"id": "crash", "label": "Crash"},
    {"id": "novos", "label": "Novos"},
]


class GameSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="slug")
    provider = serializers.CharField(source="provider.name")
    badge = serializers.SerializerMethodField()
    gradient = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = (
            "id",
            "title",
            "provider",
            "category",
            "badge",
            "rtp",
            "gradient",
            "icon",
        )

    def get_badge(self, obj: Game):
        return obj.badge or None

    def get_gradient(self, obj: Game):
        return [obj.gradient_start, obj.gradient_end]


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ("name",)


class LiveSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveSession
        fields = ("name", "dealer", "viewers")


class PromotionSerializer(serializers.ModelSerializer):
    desc = serializers.CharField(source="description")

    class Meta:
        model = Promotion
        fields = ("title", "desc", "tag")


class HeroBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroBanner
        fields = (
            "eyebrow",
            "title_prefix",
            "highlight",
            "title_suffix",
            "subtitle",
            "cta_primary",
            "cta_secondary",
            "trust_items",
        )
