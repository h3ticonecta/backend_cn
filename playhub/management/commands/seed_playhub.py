from django.core.management.base import BaseCommand
from django.db import transaction

from playhub.models import Game, HeroBanner, LiveSession, Promotion, Provider

GAMES = [
    {
        "slug": "fortune-gems",
        "title": "Fortune Gems",
        "provider": "Pragmatic Play",
        "category": "slots",
        "badge": "hot",
        "rtp": "96.5%",
        "gradient": ["#5b21b6", "#db2777"],
        "icon": "💎",
        "is_featured": True,
        "play_kind": "slot",
        "play_mesa_slug": "fortune-gems",
    },
    {
        "slug": "roleta-brasil",
        "title": "Roleta Brasil",
        "provider": "Evolution",
        "category": "ao-vivo",
        "badge": "hot",
        "gradient": ["#065f46", "#047857"],
        "icon": "🎡",
        "is_featured": True,
        "play_kind": "roleta",
        "play_mesa_slug": "roleta-brasil",
    },
    {
        "slug": "aviator",
        "title": "Aviator",
        "provider": "Spribe",
        "category": "crash",
        "badge": "hot",
        "gradient": ["#dc2626", "#f97316"],
        "icon": "✈️",
        "is_featured": True,
    },
    {
        "slug": "blackjack-vip",
        "title": "Blackjack VIP",
        "provider": "Ezugi",
        "category": "mesa",
        "badge": "",
        "rtp": "99.2%",
        "gradient": ["#1e3a5f", "#0f172a"],
        "icon": "🃏",
    },
    {
        "slug": "gates-olympus",
        "title": "Gates of Olympus",
        "provider": "Pragmatic Play",
        "category": "slots",
        "badge": "jackpot",
        "gradient": ["#fbbf24", "#b45309"],
        "icon": "⚡",
        "is_featured": True,
    },
    {
        "slug": "crazy-time",
        "title": "Crazy Time",
        "provider": "Evolution",
        "category": "ao-vivo",
        "badge": "jackpot",
        "gradient": ["#7c3aed", "#2563eb"],
        "icon": "🎪",
        "is_featured": True,
    },
    {
        "slug": "spaceman",
        "title": "Spaceman",
        "provider": "Pragmatic Play",
        "category": "crash",
        "badge": "novo",
        "gradient": ["#312e81", "#6366f1"],
        "icon": "🚀",
        "is_new": True,
    },
    {
        "slug": "sweet-bonanza",
        "title": "Sweet Bonanza",
        "provider": "Pragmatic Play",
        "category": "slots",
        "badge": "",
        "rtp": "96.4%",
        "gradient": ["#ec4899", "#a855f7"],
        "icon": "🍬",
    },
    {
        "slug": "bac-bo",
        "title": "Bac Bo",
        "provider": "Evolution",
        "category": "mesa",
        "badge": "novo",
        "gradient": ["#0d9488", "#134e4a"],
        "icon": "🎲",
        "is_new": True,
    },
    {
        "slug": "wolf-gold",
        "title": "Wolf Gold",
        "provider": "Pragmatic Play",
        "category": "slots",
        "badge": "",
        "gradient": ["#78350f", "#eab308"],
        "icon": "🐺",
    },
    {
        "slug": "lightning-roulette",
        "title": "Lightning Roulette",
        "provider": "Evolution",
        "category": "ao-vivo",
        "badge": "hot",
        "gradient": ["#1d4ed8", "#fcd34d"],
        "icon": "⚡",
    },
    {
        "slug": "mines",
        "title": "Mines",
        "provider": "Spribe",
        "category": "crash",
        "badge": "",
        "gradient": ["#374151", "#6b7280"],
        "icon": "💣",
    },
]

PROVIDER_NAMES = [
    "Pragmatic Play",
    "Evolution",
    "Spribe",
    "Ezugi",
    "NetEnt",
    "Play'n GO",
    "Red Tiger",
    "PG Soft",
]

LIVE = [
    {"name": "Mega Roleta", "viewers": 1240, "dealer": "Ana"},
    {"name": "Blackjack Party", "viewers": 890, "dealer": "Carlos"},
    {"name": "Bac Bo Live", "viewers": 654, "dealer": "Julia"},
]

PROMOS = [
    {
        "title": "Cashback semanal",
        "description": "Até 15% de volta nas perdas em slots selecionados.",
        "tag": "Ativo",
    },
    {
        "title": "Torneio de slots",
        "description": "Prêmio total de R$ 50.000 — classifique-se no ranking.",
        "tag": "Limitado",
    },
    {
        "title": "Roleta ao vivo",
        "description": "Mesa exclusiva com dealer em português, 24h.",
        "tag": "Ao vivo",
    },
]


class Command(BaseCommand):
    help = "Popula o banco com dados iniciais da landing PlayHub (frontend)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Remove jogos, provedores, live, promoções e hero antes de inserir.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            Game.objects.all().delete()
            Provider.objects.all().delete()
            LiveSession.objects.all().delete()
            Promotion.objects.all().delete()
            HeroBanner.objects.all().delete()
            self.stdout.write("Dados anteriores removidos.")

        providers = {}
        for i, name in enumerate(PROVIDER_NAMES):
            prov, _ = Provider.objects.get_or_create(
                name=name,
                defaults={"sort_order": i},
            )
            providers[name] = prov

        for i, row in enumerate(GAMES):
            prov = providers[row["provider"]]
            grad = row["gradient"]
            Game.objects.update_or_create(
                slug=row["slug"],
                defaults={
                    "title": row["title"],
                    "provider": prov,
                    "category": row["category"],
                    "badge": row.get("badge", ""),
                    "rtp": row.get("rtp", ""),
                    "gradient_start": grad[0],
                    "gradient_end": grad[1],
                    "icon": row["icon"],
                    "is_featured": row.get("is_featured", False),
                    "is_new": row.get("is_new", False),
                    "play_kind": row.get("play_kind", ""),
                    "play_mesa_slug": row.get("play_mesa_slug", ""),
                    "sort_order": i,
                    "is_active": True,
                },
            )

        for i, row in enumerate(LIVE):
            LiveSession.objects.update_or_create(
                name=row["name"],
                defaults={
                    "dealer": row["dealer"],
                    "viewers": row["viewers"],
                    "sort_order": i,
                    "is_active": True,
                },
            )

        for i, row in enumerate(PROMOS):
            Promotion.objects.update_or_create(
                title=row["title"],
                defaults={
                    "description": row["description"],
                    "tag": row["tag"],
                    "sort_order": i,
                    "is_active": True,
                },
            )

        HeroBanner.objects.get_or_create(
            eyebrow="Bônus de boas-vindas",
            defaults={
                "title_prefix": "Até",
                "highlight": "R$ 5.000",
                "title_suffix": "+ 200 rodadas grátis",
                "subtitle": (
                    "Milhares de jogos online — slots, mesa, crash e cassino ao vivo. "
                    "Jogue com segurança, no desktop ou no celular."
                ),
                "cta_primary": "Reivindicar bônus",
                "cta_secondary": "Ver jogos em destaque",
                "trust_items": [
                    "🔒 Pagamentos seguros",
                    "⚡ Saques rápidos",
                    "📱 App mobile",
                ],
                "is_active": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("PlayHub: seed concluído."))
