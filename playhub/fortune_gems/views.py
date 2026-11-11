from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from playhub.fortune_gems.models import FortuneGemsGiro
from playhub.fortune_gems.serializers import CriarSessaoSerializer, GirarSerializer
from playhub.fortune_gems.services import (
    FortuneGemsError,
    create_session,
    get_active_jogo,
    get_session,
    jogo_config_payload,
    play_spin,
    session_payload,
)


def _error_response(exc: FortuneGemsError):
    return Response(
        {"erro": {"codigo": exc.code, "mensagem": exc.message}},
        status=status.HTTP_400_BAD_REQUEST,
    )


class FortuneGemsConfigView(APIView):
    """GET /api/v1/slots/fortune-gems/ — config e histórico recente global."""

    def get(self, request):
        slug = request.query_params.get("jogo", "").strip() or None
        try:
            jogo = get_active_jogo(slug)
        except FortuneGemsError as exc:
            return _error_response(exc)

        recentes = (
            FortuneGemsGiro.objects.filter(sessao__jogo=jogo)
            .order_by("-criada_em")[:8]
            .values("carretel_1", "carretel_2", "carretel_3", "premio", "aposta", "criada_em")
        )
        historico = [
            {
                "carreteis": [r["carretel_1"], r["carretel_2"], r["carretel_3"]],
                "premio": str(r["premio"]),
                "aposta": str(r["aposta"]),
                "em": r["criada_em"].isoformat(),
            }
            for r in recentes
        ]

        return Response({**jogo_config_payload(jogo), "historico_recente": historico})


class FortuneGemsSessaoCreateView(APIView):
    def post(self, request):
        ser = CriarSessaoSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        slug = (data.get("jogo_slug") or "").strip() or None
        try:
            jogo = get_active_jogo(slug)
            sessao = create_session(jogo, apelido=data.get("apelido", ""))
        except FortuneGemsError as exc:
            return _error_response(exc)
        return Response(session_payload(sessao), status=status.HTTP_201_CREATED)


class FortuneGemsSessaoDetailView(APIView):
    def get(self, request, sessao_id):
        try:
            sessao = get_session(sessao_id)
        except FortuneGemsError as exc:
            return _error_response(exc)
        return Response(session_payload(sessao))


class FortuneGemsGirarView(APIView):
    def post(self, request):
        ser = GirarSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        try:
            sessao = get_session(data["sessao_id"])
            result = play_spin(sessao, data["aposta"])
        except FortuneGemsError as exc:
            return _error_response(exc)
        return Response(result, status=status.HTTP_201_CREATED)
