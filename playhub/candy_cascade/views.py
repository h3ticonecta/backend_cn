from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from playhub.candy_cascade.models import CandyCascadeGiro
from playhub.candy_cascade.serializers import CriarSessaoSerializer, GirarSerializer
from playhub.candy_cascade.services import (
    CandyCascadeError,
    create_session,
    get_active_jogo,
    get_session,
    jogo_config_payload,
    play_spin,
    session_payload,
)


def _error_response(exc: CandyCascadeError):
    return Response(
        {"erro": {"codigo": exc.code, "mensagem": exc.message}},
        status=status.HTTP_400_BAD_REQUEST,
    )


class CandyCascadeConfigView(APIView):
    def get(self, request):
        slug = request.query_params.get("jogo", "").strip() or None
        try:
            jogo = get_active_jogo(slug)
        except CandyCascadeError as exc:
            return _error_response(exc)

        recentes = (
            CandyCascadeGiro.objects.filter(sessao__jogo=jogo)
            .order_by("-criada_em")[:6]
            .values("premio", "aposta", "modo", "criada_em")
        )
        historico = [
            {
                "premio": str(r["premio"]),
                "aposta": str(r["aposta"]),
                "modo": r["modo"],
                "em": r["criada_em"].isoformat(),
            }
            for r in recentes
        ]

        return Response({**jogo_config_payload(jogo), "historico_recente": historico})


class CandyCascadeSessaoCreateView(APIView):
    def post(self, request):
        ser = CriarSessaoSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        slug = (data.get("jogo_slug") or "").strip() or None
        try:
            jogo = get_active_jogo(slug)
            sessao = create_session(jogo, apelido=data.get("apelido", ""))
        except CandyCascadeError as exc:
            return _error_response(exc)
        return Response(session_payload(sessao), status=status.HTTP_201_CREATED)


class CandyCascadeSessaoDetailView(APIView):
    def get(self, request, sessao_id):
        try:
            sessao = get_session(sessao_id)
        except CandyCascadeError as exc:
            return _error_response(exc)
        return Response(session_payload(sessao))


class CandyCascadeGirarView(APIView):
    def post(self, request):
        ser = GirarSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        try:
            sessao = get_session(data["sessao_id"])
            result = play_spin(
                sessao,
                data["aposta"],
                extra_bet=data.get("aposta_extra", False),
                comprar_free_spins=data.get("comprar_free_spins", False),
            )
        except CandyCascadeError as exc:
            return _error_response(exc)
        return Response(result, status=status.HTTP_201_CREATED)