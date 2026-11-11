from playhub.models import Game


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
    return None


def card_payload(game: Game, *, roleta_mesa: dict | None = None) -> dict:
    from playhub.serializers import GameSerializer

    data = {
        "card": GameSerializer(game).data,
        "play": play_meta_for_game(game),
    }
    if roleta_mesa is not None:
        data["roleta"] = roleta_mesa
    return data
