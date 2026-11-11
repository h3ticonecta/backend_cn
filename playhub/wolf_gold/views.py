from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from playhub.wolf_gold.models import WolfGoldGiro
from playhub.wolf_gold.serializers import CriarSessaoSerializer, GirarSerializer
from playhub.wolf_gold.services import (
    WolfGoldError,
    create_session,
    get_active_jogo,
    get_session,
    jogo_config_payload,
    play_action,
    session_payload,
)


def _error_response(exc: WolfGoldError):
    return Response(
        {"erro": {"codigo": exc.code, "mensagem": exc.message}},
        status=status.HTTP_400_BAD_REQUEST,
    )


class WolfGoldConfigView(APIView):
    def get(self, request):
        slug = request.query_params.get("jogo", "").strip() or None
        try:
            jogo = get_active_jogo(slug)
        except WolfGoldError as exc:
            return _error_response(exc)

        recentes = WolfGoldGiro.objects.filter(sessao__jogo=jogo).order_by("-criada_em")[:8]
        historico = [
            {
                "modo": g.modo,
                "premio": str(g.premio),
                "aposta": str(g.aposta),
                "em": g.criada_em.isoformat(),
            }
            for g in recentes
        ]
        return Response({**jogo_config_payload(jogo), "historico_recente": historico})


class WolfGoldSessaoCreateView(APIView):
    def post(self, request):
        ser = CriarSessaoSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        slug = (data.get("jogo_slug") or "").strip() or None
        try:
            jogo = get_active_jogo(slug)
            sessao = create_session(jogo, apelido=data.get("apelido", ""))
        except WolfGoldError as exc:
            return _error_response(exc)
        return Response(session_payload(sessao), status=status.HTTP_201_CREATED)


class WolfGoldSessaoDetailView(APIView):
    def get(self, request, sessao_id):
        try:
            sessao = get_session(sessao_id)
        except WolfGoldError as exc:
            return _error_response(exc)
        return Response(session_payload(sessao))


class WolfGoldGirarView(APIView):
    def post(self, request):
        ser = GirarSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        try:
            sessao = get_session(data["sessao_id"])
            result = play_action(sessao, data["aposta"], forcar=data.get("forcar"))
        except WolfGoldError as exc:
            return _error_response(exc)
        return Response(result, status=status.HTTP_201_CREATED)
