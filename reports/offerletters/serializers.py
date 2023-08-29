from rest_framework import serializers
from offerletters.models import OfferLettersModel


class OfferLettersSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferLettersModel
        fields="__all__"
