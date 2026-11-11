from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from playhub.roulette.models import RoletaRodada
from playhub.roulette.serializers import CriarSessaoSerializer, GirarSerializer
from playhub.roulette.services import (
    RoletaError,
    create_session,
    get_active_mesa,
    get_session,
    mesa_config_payload,
    play_round,
    session_payload,
)


def _error_response(exc: RoletaError):
    return Response(
        {"erro": {"codigo": exc.code, "mensagem": exc.message}},
        status=status.HTTP_400_BAD_REQUEST,
    )


class RoletaConfigView(APIView):
    """GET /api/v1/roleta/ — contrato e mesa ativa."""

    def get(self, request):
        slug = request.query_params.get("mesa", "").strip() or None
        try:
            mesa = get_active_mesa(slug)
        except RoletaError as exc:
            return _error_response(exc)

        recentes = (
            RoletaRodada.objects.filter(sessao__mesa=mesa)
            .order_by("-criada_em")[:10]
            .values("numero_sorteado", "cor", "criada_em")
        )
        historico = [
            {
                "numero": r["numero_sorteado"],
                "cor": r["cor"],
                "em": r["criada_em"].isoformat(),
            }
            for r in recentes
        ]

        return Response(
            {
                **mesa_config_payload(mesa),
                "historico_recente": historico,
            }
        )


class RoletaSessaoCreateView(APIView):
    """POST /api/v1/roleta/sessoes/ — nova sessão com fichas demo."""

    def post(self, request):
        ser = CriarSessaoSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        slug = (data.get("mesa_slug") or "").strip() or None

        try:
            mesa = get_active_mesa(slug)
            sessao = create_session(mesa, apelido=data.get("apelido", ""))
        except RoletaError as exc:
            return _error_response(exc)

        return Response(session_payload(sessao), status=status.HTTP_201_CREATED)


class RoletaSessaoDetailView(APIView):
    """GET /api/v1/roleta/sessoes/{uuid}/"""

    def get(self, request, sessao_id):
        try:
            sessao = get_session(sessao_id)
        except RoletaError as exc:
            return _error_response(exc)
        return Response(session_payload(sessao))


class RoletaGirarView(APIView):
    """POST /api/v1/roleta/girar/ — apostas + sorteio em uma transação."""

    def post(self, request):
        ser = GirarSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        try:
            sessao = get_session(data["sessao_id"])
            result = play_round(sessao, data["apostas"])
        except RoletaError as exc:
            return _error_response(exc)

        return Response(result, status=status.HTTP_201_CREATED)
