from rest_framework import serializers

from schedulers.models import CampaignUploadDataModel, CampaignListDataModel, \
    sendCleanRequestDataModel


class JobsSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    country = serializers.CharField(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ImportCampaignDataSerializer(serializers.ModelSerializer):
    # data_fields = CandidateSerializer()
    class Meta:
        model = CampaignUploadDataModel
        fields = "__all__"


class SendCleanDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = sendCleanRequestDataModel
        fields = "__all__"


class SendCleanRequestDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = sendCleanRequestDataModel
        fields = "__all__"


class CampaignListDataSerializer(serializers.ModelSerializer):
    # data_fields = CandidateSerializer()
    class Meta:
        model = CampaignListDataModel
        fields = "__all__"