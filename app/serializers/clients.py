from rest_framework import serializers
from clients.models import clientModel


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = clientModel
        fields="__all__"
