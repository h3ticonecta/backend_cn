from decimal import Decimal

from django.db import transaction

from playhub.roulette.models import RoletaAposta, RoletaMesa, RoletaRodada, RoletaSessao
from playhub.roulette.wheel import (
    ALLOWED_BET_TYPES,
    PAYOUT_RULES,
    bet_wins,
    number_color,
    payout_multiplier,
    spin_wheel,
)


class RoletaError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def get_active_mesa(slug: str | None = None) -> RoletaMesa:
    qs = RoletaMesa.objects.filter(ativa=True)
    if slug:
        mesa = qs.filter(slug=slug).first()
    else:
        mesa = qs.order_by("pk").first()
    if not mesa:
        raise RoletaError("mesa_indisponivel", "Nenhuma mesa de roleta ativa.")
    return mesa


def mesa_config_payload(mesa: RoletaMesa) -> dict:
    return {
        "mesa": {
            "slug": mesa.slug,
            "nome": mesa.nome,
            "variante": mesa.variante,
            "saldo_inicial": str(mesa.saldo_inicial),
            "aposta_minima": str(mesa.aposta_minima),
            "aposta_maxima": str(mesa.aposta_maxima),
            "max_apostas_por_giro": mesa.max_apostas_por_giro,
        },
        "tipos_aposta": [
            {
                "tipo": rule.bet_type,
                "multiplicador": str(rule.multiplier),
                "descricao": rule.label,
                "requer_numero": rule.bet_type == "straight",
            }
            for rule in PAYOUT_RULES
        ],
        "numeros": {
            "min": 0,
            "max": 36,
            "vermelhos": sorted(
                {n for n in range(1, 37) if number_color(n) == "red"}
            ),
        },
    }


def create_session(mesa: RoletaMesa, apelido: str = "") -> RoletaSessao:
    return RoletaSessao.objects.create(
        mesa=mesa,
        apelido=apelido[:40],
        saldo=mesa.saldo_inicial,
    )


def get_session(session_id) -> RoletaSessao:
    try:
        return RoletaSessao.objects.select_related("mesa").get(pk=session_id)
    except RoletaSessao.DoesNotExist as exc:
        raise RoletaError("sessao_invalida", "Sessão não encontrada.") from exc


def session_payload(sessao: RoletaSessao) -> dict:
    ultima = sessao.rodadas.order_by("-criada_em").first()
    return {
        "sessao_id": str(sessao.id),
        "apelido": sessao.apelido,
        "mesa_slug": sessao.mesa.slug,
        "saldo": str(sessao.saldo),
        "ultima_rodada": (
            {
                "id": ultima.pk,
                "numero": ultima.numero_sorteado,
                "cor": ultima.cor,
                "criada_em": ultima.criada_em.isoformat(),
            }
            if ultima
            else None
        ),
    }


def _validate_bet(bet: dict, mesa: RoletaMesa) -> tuple[str, int | None, Decimal]:
    tipo = bet.get("tipo", "").strip()
    if tipo not in ALLOWED_BET_TYPES:
        raise RoletaError("tipo_aposta_invalido", f"Tipo de aposta inválido: {tipo}")

    try:
        valor = Decimal(str(bet.get("valor")))
    except Exception as exc:
        raise RoletaError("valor_invalido", "Valor da aposta inválido.") from exc

    if valor <= 0:
        raise RoletaError("valor_invalido", "Valor da aposta deve ser positivo.")
    if valor < mesa.aposta_minima:
        raise RoletaError(
            "abaixo_minimo",
            f"Aposta mínima: {mesa.aposta_minima}",
        )
    if valor > mesa.aposta_maxima:
        raise RoletaError(
            "acima_maximo",
            f"Aposta máxima: {mesa.aposta_maxima}",
        )

    numero = bet.get("numero")
    if tipo == "straight":
        if numero is None:
            raise RoletaError("numero_obrigatorio", "Aposta straight exige 'numero' (0–36).")
        try:
            numero = int(numero)
        except (TypeError, ValueError) as exc:
            raise RoletaError("numero_invalido", "Número deve ser inteiro 0–36.") from exc
        if not 0 <= numero <= 36:
            raise RoletaError("numero_invalido", "Número deve estar entre 0 e 36.")
    else:
        numero = None
        if bet.get("numero") is not None:
            raise RoletaError("numero_proibido", f"Tipo '{tipo}' não aceita 'numero'.")

    return tipo, numero, valor


@transaction.atomic
def play_round(sessao: RoletaSessao, apostas: list[dict]) -> dict:
    mesa = sessao.mesa
    if not mesa.ativa:
        raise RoletaError("mesa_indisponivel", "Mesa indisponível.")

    if not apostas:
        raise RoletaError("sem_apostas", "Informe ao menos uma aposta.")

    if len(apostas) > mesa.max_apostas_por_giro:
        raise RoletaError(
            "muitas_apostas",
            f"Máximo de {mesa.max_apostas_por_giro} apostas por giro.",
        )

    parsed = [_validate_bet(b, mesa) for b in apostas]
    total_apostado = sum(v for _, _, v in parsed)

    sessao = RoletaSessao.objects.select_for_update().get(pk=sessao.pk)
    if sessao.saldo < total_apostado:
        raise RoletaError(
            "saldo_insuficiente",
            f"Saldo insuficiente. Disponível: {sessao.saldo}",
        )

    saldo_antes = sessao.saldo
    winning = spin_wheel()
    cor = number_color(winning)

    total_pago = Decimal("0")
    bet_results: list[dict] = []

    rodada = RoletaRodada.objects.create(
        sessao=sessao,
        numero_sorteado=winning,
        cor=cor,
        total_apostado=total_apostado,
        total_pago=Decimal("0"),
        saldo_antes=saldo_antes,
        saldo_depois=saldo_antes,
    )

    for tipo, numero, valor in parsed:
        ganhou = bet_wins(tipo, numero, winning)
        mult = payout_multiplier(tipo)
        pagamento = (valor * (mult + 1)) if ganhou else Decimal("0")
        total_pago += pagamento

        RoletaAposta.objects.create(
            rodada=rodada,
            tipo=tipo,
            numero=numero,
            valor=valor,
            ganhou=ganhou,
            pagamento=pagamento,
        )

        bet_results.append(
            {
                "tipo": tipo,
                "numero": numero,
                "valor": str(valor),
                "ganhou": ganhou,
                "pagamento": str(pagamento),
            }
        )

    saldo_depois = saldo_antes - total_apostado + total_pago
    sessao.saldo = saldo_depois
    sessao.save(update_fields=["saldo", "atualizada_em"])

    rodada.total_pago = total_pago
    rodada.saldo_depois = saldo_depois
    rodada.save(update_fields=["total_pago", "saldo_depois"])

    return {
        "rodada_id": rodada.pk,
        "resultado": {
            "numero": winning,
            "cor": cor,
        },
        "totais": {
            "apostado": str(total_apostado),
            "pago": str(total_pago),
            "lucro_liquido": str(total_pago - total_apostado),
        },
        "apostas": bet_results,
        "sessao": {
            "id": str(sessao.id),
            "saldo_antes": str(saldo_antes),
            "saldo_depois": str(saldo_depois),
        },
    }
