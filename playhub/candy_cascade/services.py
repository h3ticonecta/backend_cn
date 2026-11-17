from decimal import Decimal, InvalidOperation

from django.db import transaction

from playhub.candy_cascade import engine
from playhub.candy_cascade.config import (
    BET_STEPS,
    BUY_FREE_SPINS_MULT,
    CARD_CATALOG_SLUG,
    DISPLAY_NAME,
    EXTRA_BET_MARKUP,
    FREE_SPINS_AWARD,
    resolve_jogo_slug,
)
from playhub.models import Game
from playhub.candy_cascade.models import CandyCascadeGiro, CandyCascadeJogo, CandyCascadeSessao
from playhub.chance_config import chances_payload, roll_favor_usuario


class CandyCascadeError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def get_active_jogo(slug: str | None = None) -> CandyCascadeJogo:
    qs = CandyCascadeJogo.objects.filter(ativo=True)
    resolved = resolve_jogo_slug(slug)
    jogo = qs.filter(slug=resolved).first() if resolved else qs.order_by("pk").first()
    if not jogo:
        raise CandyCascadeError("jogo_indisponivel", f"{DISPLAY_NAME} indisponível.")
    return jogo


def jogo_config_payload(jogo: CandyCascadeJogo) -> dict:
    from playhub.candy_cascade.config import (
        BUY_FREE_SPINS_MULT,
        COLS,
        FREE_SPINS_AWARD,
        FREE_SPINS_RETRIGGER,
        MAX_WIN_MULT,
        ROWS,
        SCATTER_FOR_BONUS,
    )

    card = (
        Game.objects.filter(is_active=True, slug=CARD_CATALOG_SLUG).first()
        or Game.objects.filter(is_active=True, play_mesa_slug=jogo.slug).first()
    )
    titulo_card = card.title if card else jogo.nome
    card_slug = card.slug if card else CARD_CATALOG_SLUG

    return {
        "jogo": {
            "slug": jogo.slug,
            "card_slug": card_slug,
            "nome": jogo.nome,
            "titulo_card": titulo_card,
            "nome_exibicao_modal": titulo_card,
            "client_route": "#/sweet-bonanza",
            "rtp": jogo.rtp_label,
            "saldo_inicial": str(jogo.saldo_inicial),
            "aposta_minima": str(jogo.aposta_minima),
            "aposta_maxima": str(jogo.aposta_maxima),
            "grade": {"colunas": COLS, "linhas": ROWS},
            "cluster_minimo": 8,
            "aviso_demo": "Jogo de demonstração. Sem dinheiro real.",
            "chances": chances_payload(jogo.percentual_casa, jogo.percentual_usuario),
            "opcoes": {
                "apostas_permitidas": engine.bet_steps_payload(),
                "aposta_extra_markup": str(EXTRA_BET_MARKUP),
                "comprar_free_spins_mult": str(BUY_FREE_SPINS_MULT),
                "max_ganho_por_giro": str(MAX_WIN_MULT),
            },
            "bonus": {
                "scatters_para_ativar": SCATTER_FOR_BONUS,
                "free_spins_iniciais": FREE_SPINS_AWARD,
                "retrigger_giros": FREE_SPINS_RETRIGGER,
            },
        },
        "simbolos": engine.paytable_payload(),
        "regras_resumo": [
            "Pay anywhere: 8+ símbolos iguais pagam.",
            "Cascata após cada ganho.",
            "4+ scatters ativam free spins (pagamento scatter incluído).",
            "Bombas somam multiplicador ao fim da cascata nos free spins.",
        ],
    }


def _ensure_state(sessao: CandyCascadeSessao) -> dict:
    state = dict(sessao.estado or {})
    for k, v in engine.default_state().items():
        state.setdefault(k, v)
    return state


def create_session(jogo: CandyCascadeJogo, apelido: str = "") -> CandyCascadeSessao:
    return CandyCascadeSessao.objects.create(
        jogo=jogo,
        apelido=apelido[:40],
        saldo=jogo.saldo_inicial,
        estado=engine.default_state(),
    )


def get_session(session_id) -> CandyCascadeSessao:
    try:
        return CandyCascadeSessao.objects.select_related("jogo").get(pk=session_id)
    except CandyCascadeSessao.DoesNotExist as exc:
        raise CandyCascadeError("sessao_invalida", "Sessão não encontrada.") from exc


def session_payload(sessao: CandyCascadeSessao) -> dict:
    state = _ensure_state(sessao)
    return {
        "sessao_id": str(sessao.id),
        "apelido": sessao.apelido,
        "jogo_slug": sessao.jogo.slug,
        "saldo": str(sessao.saldo),
        "estado": state,
    }


def _parse_aposta(raw) -> Decimal:
    try:
        val = Decimal(str(raw)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError) as exc:
        raise CandyCascadeError("aposta_invalida", "Valor de aposta inválido.") from exc
    if val not in BET_STEPS:
        allowed = ", ".join(str(b) for b in BET_STEPS)
        raise CandyCascadeError(
            "aposta_invalida",
            f"Aposta deve ser um dos valores permitidos: {allowed}.",
        )
    return val


def _spin_cost(
    aposta: Decimal, *, extra_bet: bool, comprar_free_spins: bool, in_free_spin: bool
) -> Decimal:
    if comprar_free_spins:
        return (aposta * BUY_FREE_SPINS_MULT).quantize(Decimal("0.01"))
    if in_free_spin:
        return Decimal("0")
    base = aposta
    if extra_bet:
        base = (base * (Decimal("1") + EXTRA_BET_MARKUP)).quantize(Decimal("0.01"))
    return base


def _run_with_bias(jogo, fn):
    favor = roll_favor_usuario(jogo.percentual_usuario)
    for _ in range(30):
        result = fn()
        won = result.premio_total > 0 or result.free_spins_ganhos > 0
        if favor and won:
            return result
        if not favor and not won:
            return result
    return fn()


@transaction.atomic
def play_spin(
    sessao: CandyCascadeSessao,
    aposta_raw,
    *,
    extra_bet: bool = False,
    comprar_free_spins: bool = False,
) -> dict:
    sessao = CandyCascadeSessao.objects.select_for_update().select_related("jogo").get(pk=sessao.pk)
    jogo = sessao.jogo
    state = _ensure_state(sessao)
    aposta = _parse_aposta(aposta_raw)

    if aposta < jogo.aposta_minima or aposta > jogo.aposta_maxima:
        raise CandyCascadeError(
            "aposta_fora_limite",
            f"Aposta fora do limite ({jogo.aposta_minima}–{jogo.aposta_maxima}).",
        )

    in_free = state.get("mode") == "free_spin" and int(state.get("free_spins_left", 0)) > 0
    custo = _spin_cost(aposta, extra_bet=extra_bet, comprar_free_spins=comprar_free_spins, in_free_spin=in_free)
    saldo_antes = sessao.saldo

    if custo > 0 and saldo_antes < custo:
        raise CandyCascadeError("saldo_insuficiente", "Saldo insuficiente para esta ação.")

    saldo_liquido = (saldo_antes - custo).quantize(Decimal("0.01"))
    aposta_ref = Decimal(str(state.get("aposta_ref") or aposta))

    if comprar_free_spins:
        state["mode"] = "free_spin"
        state["free_spins_left"] = int(state.get("free_spins_left", 0)) + FREE_SPINS_AWARD
        state["free_spins_total"] = "0.00"
        state["aposta_ref"] = str(aposta)
        state["extra_bet"] = extra_bet
        spin_result = engine.play_round(
            aposta=aposta,
            free_spin=True,
            extra_scatter=extra_bet,
            start_free=True,
        )
    else:
        if in_free:
            free_spin = True
            ref = aposta_ref
        else:
            free_spin = False
            ref = aposta
            state["aposta_ref"] = str(aposta)
            state["extra_bet"] = extra_bet

        def _do_spin():
            return engine.play_round(
                aposta=ref,
                free_spin=free_spin,
                extra_scatter=bool(state.get("extra_bet")) or extra_bet,
            )

        spin_result = _run_with_bias(jogo, _do_spin)

    premio = spin_result.premio_total
    saldo_depois = (saldo_liquido + premio).quantize(Decimal("0.01"))

    if spin_result.free_spins_ganhos:
        state["mode"] = "free_spin"
        state["free_spins_left"] = int(state.get("free_spins_left", 0)) + spin_result.free_spins_ganhos
        if not state.get("aposta_ref"):
            state["aposta_ref"] = str(aposta)

    consumed_free = in_free or comprar_free_spins
    if consumed_free:
        total_fs = Decimal(str(state.get("free_spins_total", "0"))) + premio
        state["free_spins_total"] = str(total_fs.quantize(Decimal("0.01")))
        state["free_spins_left"] = max(0, int(state["free_spins_left"]) - 1)
    if state.get("mode") == "free_spin" and int(state.get("free_spins_left", 0)) <= 0:
        state["mode"] = "base"
        state["free_spins_total"] = "0.00"

    sessao.saldo = saldo_depois
    sessao.estado = state
    sessao.save(update_fields=["saldo", "estado", "atualizada_em"])

    modo = "free_spin" if in_free or comprar_free_spins else spin_result.detalhes.get("modo", "base")

    giro = CandyCascadeGiro.objects.create(
        sessao=sessao,
        modo=modo,
        aposta=custo,
        premio=premio,
        grade=engine.grid_to_serializable(spin_result.grade_final),
        saldo_antes=saldo_antes,
        saldo_depois=saldo_depois,
        detalhes={
            "cascatas": spin_result.passos,
            "free_spins_ganhos": spin_result.free_spins_ganhos,
            "extra_bet": extra_bet,
            "comprar_free_spins": comprar_free_spins,
        },
    )

    return {
        "giro_id": giro.pk,
        "modo": state.get("mode", modo),
        "aposta_cobrada": str(custo),
        "premio": str(premio),
        "saldo": str(sessao.saldo),
        "cascatas": spin_result.passos,
        "grade": engine.grid_to_serializable(spin_result.grade_final),
        "multiplicadores": engine.mults_to_serializable(spin_result.mults_final),
        "estado": session_payload(sessao)["estado"],
        "aviso_demo": "Jogo de demonstração. Sem dinheiro real.",
    }