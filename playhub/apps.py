from django.apps import AppConfig


class PlayhubConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "playhub"
    verbose_name = "PlayHub"

    def ready(self) -> None:
        from playhub.game_chance_sync import connect_chance_sync_signals

        connect_chance_sync_signals()
