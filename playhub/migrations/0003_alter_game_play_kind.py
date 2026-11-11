from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("playhub", "0002_game_play_kind_game_play_mesa_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="play_kind",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "Somente vitrine"),
                    ("roleta", "Roleta (API)"),
                    ("slot", "Slot (API)"),
                ],
                default="",
                max_length=20,
                verbose_name="modo jogável",
            ),
        ),
        migrations.AlterField(
            model_name="game",
            name="play_mesa_slug",
            field=models.SlugField(
                blank=True,
                help_text="Slug da mesa (roleta) ou do jogo slot quando play_kind=roleta/slot.",
                max_length=80,
                verbose_name="mesa vinculada (roleta)",
            ),
        ),
    ]
