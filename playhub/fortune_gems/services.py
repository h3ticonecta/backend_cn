from decimal import Decimal, InvalidOperation

from django.db import transaction

from playhub.fortune_gems.engine import SYMBOL_IDS, evaluate_spin, paytable_payload, spin_reels
from playhub.fortune_gems.models import FortuneGemsGiro, FortuneGemsJogo, FortuneGemsSessao


class FortuneGemsError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def get_active_jogo(slug: str | None = None) -> FortuneGemsJogo:
    qs = FortuneGemsJogo.objects.filter(ativo=True)
    if slug:
        jogo = qs.filter(slug=slug).first()
    else:
        jogo = qs.order_by("pk").first()
    if not jogo:
        raise FortuneGemsError("jogo_indisponivel", "Slot Fortune Gems indisponível.")
    return jogo


def jogo_config_payload(jogo: FortuneGemsJogo) -> dict:
    return {
        "jogo": {
            "slug": jogo.slug,
            "nome": jogo.nome,
            "rtp": jogo.rtp_label,
            "saldo_inicial": str(jogo.saldo_inicial),
            "aposta_minima": str(jogo.aposta_minima),
            "aposta_maxima": str(jogo.aposta_maxima),
            "jackpot_exibicao": str(jogo.jackpot_exibicao),
        },
        "simbolos": paytable_payload(),
        "linhas_ativas": 5,
    }


def create_session(jogo: FortuneGemsJogo, apelido: str = "") -> FortuneGemsSessao:
    return FortuneGemsSessao.objects.create(
        jogo=jogo,
        apelido=apelido[:40],
        saldo=jogo.saldo_inicial,
    )


def get_session(session_id) -> FortuneGemsSessao:
    try:
        return FortuneGemsSessao.objects.select_related("jogo").get(pk=session_id)
    except FortuneGemsSessao.DoesNotExist as exc:
        raise FortuneGemsError("sessao_invalida", "Sessão não encontrada.") from exc


def session_payload(sessao: FortuneGemsSessao) -> dict:
    ultimo = sessao.giros.order_by("-criada_em").first()
    return {
        "sessao_id": str(sessao.id),
        "apelido": sessao.apelido,
        "jogo_slug": sessao.jogo.slug,
        "saldo": str(sessao.saldo),
        "ultimo_giro": (
            {
                "carreteis": [ultimo.carretel_1, ultimo.carretel_2, ultimo.carretel_3],
                "premio": str(ultimo.premio),
                "aposta": str(ultimo.aposta),
                "criada_em": ultimo.criada_em.isoformat(),
            }
            if ultimo
            else None
        ),
    }


def _parse_aposta(raw) -> Decimal:
    try:
        val = Decimal(str(raw))
    except (InvalidOperation, TypeError) as exc:
        raise FortuneGemsError("aposta_invalida", "Valor de aposta inválido.") from exc
    if val <= 0:
        raise FortuneGemsError("aposta_invalida", "Aposta deve ser maior que zero.")
    return val.quantize(Decimal("0.01"))


@transaction.atomic
def play_spin(sessao: FortuneGemsSessao, aposta_raw) -> dict:
    sessao = FortuneGemsSessao.objects.select_for_update().select_related("jogo").get(pk=sessao.pk)
    aposta = _parse_aposta(aposta_raw)
    jogo = sessao.jogo

    if aposta < jogo.aposta_minima or aposta > jogo.aposta_maxima:
        raise FortuneGemsError(
            "aposta_fora_limite",
            f"Aposta fora do limite ({jogo.aposta_minima}–{jogo.aposta_maxima}).",
        )
    if sessao.saldo < aposta:
        raise FortuneGemsError("saldo_insuficiente", "Saldo insuficiente para esta aposta.")

    saldo_antes = sessao.saldo
    reels = spin_reels()
    for sym in reels:
        if sym not in SYMBOL_IDS:
            raise FortuneGemsError("erro_interno", "Símbolo inválido no sorteio.")

    premio, ganhou, motivo = evaluate_spin(reels, aposta)
    saldo_depois = (saldo_antes - aposta + premio).quantize(Decimal("0.01"))

    giro = FortuneGemsGiro.objects.create(
        sessao=sessao,
        aposta=aposta,
        carretel_1=reels[0],
        carretel_2=reels[1],
        carretel_3=reels[2],
        premio=premio,
        saldo_antes=saldo_antes,
        saldo_depois=saldo_depois,
    )
    sessao.saldo = saldo_depois
    sessao.save(update_fields=["saldo", "atualizada_em"])

    return {
        "giro_id": giro.pk,
        "carreteis": list(reels),
        "aposta": str(aposta),
        "premio": str(premio),
        "ganhou": ganhou,
        "motivo": motivo,
        "saldo": str(saldo_depois),
        "saldo_antes": str(saldo_antes),
    }
