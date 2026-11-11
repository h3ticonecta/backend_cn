from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db import transaction

from playhub.wolf_gold import engine
from playhub.wolf_gold.config import (
    FREE_SPINS_AWARD,
    FREE_SPINS_RETRIGGER,
    LINES_COUNT,
    SCATTERS_TO_BONUS,
)
from playhub.wolf_gold.models import WolfGoldGiro, WolfGoldJogo, WolfGoldSessao


class WolfGoldError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def get_active_jogo(slug: str | None = None) -> WolfGoldJogo:
    qs = WolfGoldJogo.objects.filter(ativo=True)
    jogo = qs.filter(slug=slug).first() if slug else qs.order_by("pk").first()
    if not jogo:
        raise WolfGoldError("jogo_indisponivel", "Wolf Gold indisponível.")
    return jogo


def jogo_config_payload(jogo: WolfGoldJogo) -> dict:
    return {
        "jogo": {
            "slug": jogo.slug,
            "nome": jogo.nome,
            "rtp": jogo.rtp_label,
            "saldo_inicial": str(jogo.saldo_inicial),
            "aposta_minima": str(jogo.aposta_minima),
            "aposta_maxima": str(jogo.aposta_maxima),
            "linhas": LINES_COUNT,
            "jackpots": {"mini": "20x", "major": "50x", "mega": "1000x"},
        },
        "simbolos": engine.paytable_payload(),
        "paylines": engine.paylines_payload(),
    }


def _ensure_state(sessao: WolfGoldSessao) -> dict:
    state = dict(sessao.estado or {})
    for k, v in engine.default_state().items():
        state.setdefault(k, v)
    return state


def create_session(jogo: WolfGoldJogo, apelido: str = "") -> WolfGoldSessao:
    return WolfGoldSessao.objects.create(
        jogo=jogo,
        apelido=apelido[:40],
        saldo=jogo.saldo_inicial,
        estado=engine.default_state(),
    )


def get_session(session_id) -> WolfGoldSessao:
    try:
        return WolfGoldSessao.objects.select_related("jogo").get(pk=session_id)
    except WolfGoldSessao.DoesNotExist as exc:
        raise WolfGoldError("sessao_invalida", "Sessão não encontrada.") from exc


def _serialize_money(money: list | None) -> list | None:
    if money is None:
        return None
    return [str(v) if v is not None else None for v in money]


def session_payload(sessao: WolfGoldSessao) -> dict:
    state = _ensure_state(sessao)
    return {
        "sessao_id": str(sessao.id),
        "apelido": sessao.apelido,
        "jogo_slug": sessao.jogo.slug,
        "saldo": str(sessao.saldo),
        "estado": {**state, "money_grid": _serialize_money(state.get("money_grid"))},
    }


def _parse_aposta(raw) -> Decimal:
    try:
        val = Decimal(str(raw)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError) as exc:
        raise WolfGoldError("aposta_invalida", "Valor de aposta inválido.") from exc
    if val <= 0:
        raise WolfGoldError("aposta_invalida", "Aposta deve ser maior que zero.")
    return val


def _money_to_decimal(values: list | None) -> engine.MoneyGrid | None:
    if not values:
        return None
    return [Decimal(str(v)) if v is not None else None for v in values]


def _money_grid_to_display(values: engine.MoneyGrid) -> list[list[str]]:
    grid: list[list[str]] = []
    for c in range(5):
        col: list[str] = []
        for r in range(3):
            idx = r * 5 + c
            col.append("money" if values[idx] is not None else "j")
        grid.append(col)
    return grid


@transaction.atomic
def play_action(sessao: WolfGoldSessao, aposta_raw, *, forcar: dict | None = None) -> dict:
    if forcar and not settings.DEBUG:
        raise WolfGoldError("forcar_negado", "Modo de teste só em DEBUG.")

    sessao = WolfGoldSessao.objects.select_for_update().select_related("jogo").get(pk=sessao.pk)
    jogo = sessao.jogo
    state = _ensure_state(sessao)
    aposta_total = _parse_aposta(aposta_raw)

    if aposta_total < jogo.aposta_minima or aposta_total > jogo.aposta_maxima:
        raise WolfGoldError(
            "aposta_fora_limite",
            f"Aposta fora do limite ({jogo.aposta_minima}–{jogo.aposta_maxima}).",
        )

    line_bet = (aposta_total / LINES_COUNT).quantize(Decimal("0.01"))
    saldo_antes = sessao.saldo
    premio = Decimal("0")
    details: dict = {}
    aposta_cobrada = Decimal("0")
    modo_giro = state.get("mode", "base")
    grid: engine.Grid = []

    if modo_giro == "money_respin":
        money_grid = _money_to_decimal(state.get("money_grid"))
        if money_grid is None:
            state = engine.default_state()
            modo_giro = "base"
        else:
            ref = Decimal(str(state.get("aposta_total_ref") or aposta_total))
            money_grid, landed, jackpot = engine.money_respin_step(money_grid, ref)
            respins = 3 if landed else int(state.get("respins_left", 3)) - 1
            state["respins_left"] = respins
            state["money_grid"] = _serialize_money(money_grid)
            details["money_respin"] = {"respins_left": respins, "novo_money": landed}
            if jackpot:
                premio += jackpot
                details["jackpot"] = str(jackpot)
            grid = _money_grid_to_display(money_grid)
            if respins <= 0:
                premio += engine.sum_money_grid(money_grid)
                details["money_respin_fim"] = str(engine.sum_money_grid(money_grid))
                state = engine.default_state()
            else:
                state["mode"] = "money_respin"
    else:
        free_spin = modo_giro == "free_spin"
        if not free_spin:
            if saldo_antes < aposta_total:
                raise WolfGoldError("saldo_insuficiente", "Saldo insuficiente.")
            aposta_cobrada = aposta_total
            saldo_antes = (saldo_antes - aposta_total).quantize(Decimal("0.01"))

        forced = engine.parse_force_grid(forcar)
        if forced:
            grid, giant = forced, None
        else:
            grid, giant = engine.spin_base_grid(free_spin=free_spin)

        line_prize, wins = engine.evaluate_paylines(grid, line_bet)
        premio += line_prize
        if wins:
            details["linhas_vencedoras"] = wins
        if giant:
            details["giant_symbol"] = giant

        scatters = engine.count_symbol(grid, "scatter")
        if scatters >= SCATTERS_TO_BONUS:
            extra = FREE_SPINS_RETRIGGER if free_spin else FREE_SPINS_AWARD
            state["mode"] = "free_spin"
            state["free_spins_left"] = int(state.get("free_spins_left", 0)) + extra
            state["aposta_total_ref"] = str(aposta_total)
            details["free_spins"] = extra

        if free_spin and state.get("free_spins_left", 0) > 0:
            state["free_spins_left"] = int(state["free_spins_left"]) - 1
            details["free_spins_restantes"] = state["free_spins_left"]
            if state["free_spins_left"] <= 0:
                state["mode"] = "base"

        money_vals = engine.grid_to_money_values(grid, aposta_total)
        if engine.should_trigger_money_respin(money_vals) or (
            forcar and forcar.get("money_respin")
        ):
            money_vals = engine.start_money_respin_from_grid(grid, aposta_total)
            state["mode"] = "money_respin"
            state["money_grid"] = _serialize_money(money_vals)
            state["respins_left"] = 3
            state["aposta_total_ref"] = str(aposta_total)
            details["money_respin_inicio"] = True
            grid = _money_grid_to_display(money_vals)

    saldo_depois = (saldo_antes + premio).quantize(Decimal("0.01"))
    sessao.saldo = saldo_depois
    sessao.estado = state
    sessao.save(update_fields=["saldo", "estado", "atualizada_em"])

    WolfGoldGiro.objects.create(
        sessao=sessao,
        modo=state.get("mode", modo_giro),
        aposta=aposta_cobrada,
        premio=premio,
        grade=engine.grid_to_serializable(grid),
        saldo_antes=saldo_antes,
        saldo_depois=saldo_depois,
        detalhes=details,
    )

    return {
        "giro_id": sessao.giros.order_by("-criada_em").values_list("pk", flat=True).first(),
        "modo": state.get("mode", modo_giro),
        "grade": engine.grid_to_serializable(grid),
        "aposta": str(aposta_cobrada if aposta_cobrada else aposta_total),
        "premio": str(premio),
        "saldo": str(sessao.saldo),
        "estado": session_payload(sessao)["estado"],
        "detalhes": details,
    }
