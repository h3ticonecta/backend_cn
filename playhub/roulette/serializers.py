from rest_framework import serializers


class ApostaSerializer(serializers.Serializer):
    tipo = serializers.CharField(max_length=20)
    valor = serializers.DecimalField(max_digits=12, decimal_places=2)
    numero = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        max_value=36,
    )


class CriarSessaoSerializer(serializers.Serializer):
    mesa_slug = serializers.SlugField(required=False, allow_blank=True)
    apelido = serializers.CharField(max_length=40, required=False, allow_blank=True)


class GirarSerializer(serializers.Serializer):
    sessao_id = serializers.UUIDField()
    apostas = ApostaSerializer(many=True)
