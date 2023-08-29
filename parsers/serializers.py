from rest_framework import serializers

from parsers.models import ParserModel


class ParserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParserModel
        fields = "__all__"
