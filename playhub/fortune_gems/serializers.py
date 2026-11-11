from rest_framework import serializers


class CriarSessaoSerializer(serializers.Serializer):
    jogo_slug = serializers.CharField(required=False, allow_blank=True, max_length=80)
    apelido = serializers.CharField(required=False, allow_blank=True, max_length=40)


class GirarSerializer(serializers.Serializer):
    sessao_id = serializers.UUIDField()
    aposta = serializers.DecimalField(max_digits=12, decimal_places=2)
