from rest_framework import serializers
from candidatesdocumentrepositery.models import candidatesRepositeryModel

class CandidateDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = candidatesRepositeryModel
        fields="__all__"
        depth = 1
        
class CandidateDocumentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = candidatesRepositeryModel
        fields = "__all__"