from playhub.models import Game

SLOT_REGISTRY: dict[str, dict[str, str]] = {
    "fortune-gems": {
        "client_route": "#/fortune-gems",
        "api_prefix": "/api/v1/slots/fortune-gems/",
    },
    "wolf-gold": {
        "client_route": "#/wolf-gold",
        "api_prefix": "/api/v1/slots/wolf-gold/",
    },
}


def play_meta_for_game(game: Game) -> dict | None:
    if game.play_kind == Game.PlayKind.ROLETA:
        mesa = (game.play_mesa_slug or game.slug).strip() or "roleta-brasil"
        return {
            "kind": "roleta",
            "mesa_slug": mesa,
            "client_route": "#/roleta",
            "contrato": "/docs/contratos/roleta.md",
            "api": {
                "config": f"/api/v1/roleta/?mesa={mesa}",
                "sessoes": "/api/v1/roleta/sessoes/",
                "sessao_detail": "/api/v1/roleta/sessoes/{sessao_id}/",
                "girar": "/api/v1/roleta/girar/",
                "card": f"/api/v1/games/{game.slug}/",
            },
        }
    if game.play_kind == Game.PlayKind.SLOT:
        slot_slug = (game.play_mesa_slug or game.slug).strip() or "fortune-gems"
        slot = SLOT_REGISTRY.get(slot_slug, SLOT_REGISTRY["fortune-gems"])
        prefix = slot["api_prefix"]
        return {
            "kind": "slot",
            "slot_slug": slot_slug,
            "client_route": slot["client_route"],
            "api": {
                "config": f"{prefix}?jogo={slot_slug}",
                "sessoes": f"{prefix}sessoes/",
                "sessao_detail": f"{prefix}sessoes/{{sessao_id}}/",
                "girar": f"{prefix}girar/",
                "card": f"/api/v1/games/{game.slug}/",
            },
        }
    return None


def slot_config_for_slug(slot_slug: str) -> dict | None:
    if slot_slug == "wolf-gold":
        from playhub.wolf_gold.services import WolfGoldError, get_active_jogo, jogo_config_payload

        try:
            return jogo_config_payload(get_active_jogo(slot_slug))
        except WolfGoldError:
            return None
    if slot_slug in ("fortune-gems", ""):
        from playhub.fortune_gems.services import FortuneGemsError, get_active_jogo, jogo_config_payload

        slug = slot_slug or "fortune-gems"
        try:
            return jogo_config_payload(get_active_jogo(slug))
        except FortuneGemsError:
            return None
    return None


def card_payload(
    game: Game,
    *,
    roleta_mesa: dict | None = None,
    slot_config: dict | None = None,
) -> dict:
    from playhub.serializers import GameSerializer

    data = {
        "card": GameSerializer(game).data,
        "play": play_meta_for_game(game),
    }
    if roleta_mesa is not None:
        data["roleta"] = roleta_mesa
    if slot_config is not None:
        data["slot"] = slot_config
    return data
