from django.apps import AppConfig


class RoletaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "playhub.roulette"
    verbose_name = "Roleta"

    def ready(self) -> None:
        from playhub.roulette import admin as _roleta_admin  # noqa: F401
