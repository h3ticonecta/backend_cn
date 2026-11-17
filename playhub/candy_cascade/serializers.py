from rest_framework import serializers


class CriarSessaoSerializer(serializers.Serializer):
    jogo_slug = serializers.CharField(required=False, allow_blank=True, max_length=80)
    apelido = serializers.CharField(required=False, allow_blank=True, max_length=40)


class GirarSerializer(serializers.Serializer):
    sessao_id = serializers.UUIDField()
    aposta = serializers.DecimalField(max_digits=12, decimal_places=2)
    aposta_extra = serializers.BooleanField(required=False, default=False)
    extra_bet = serializers.BooleanField(required=False, default=False)
    comprar_free_spins = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        extra = attrs.get("aposta_extra") or attrs.get("extra_bet", False)
        attrs["aposta_extra"] = bool(extra)
        return attrs