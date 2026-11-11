from django.contrib import admin

from .models import Game, HeroBanner, LiveSession, Promotion, Provider


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "provider",
        "category",
        "badge",
        "is_featured",
        "is_new",
        "is_active",
        "sort_order",
    )
    list_filter = ("category", "badge", "is_featured", "is_new", "is_active", "provider")
    search_fields = ("title", "slug", "provider__name")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("provider",)


@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ("name", "dealer", "viewers", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "dealer")


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("title", "tag", "is_active", "sort_order")
    list_filter = ("is_active", "tag")
    search_fields = ("title", "description")


@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ("eyebrow", "highlight", "is_active")
