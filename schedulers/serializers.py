from rest_framework import serializers

from candidates.models import Candidates
from schedulers.models import CampaignUploadDataModel, CampaignListDataModel, \
    sendCleanRequestDataModel, AgentCallsDataModel


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


class AgentCallsDataModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentCallsDataModel
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


class DownloadCandidateByStatusSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    stage_name = serializers.CharField(read_only=True)
    recruiter_name = serializers.CharField(read_only=True)
    resume = serializers.CharField(read_only=True)
    resume_raw_data = serializers.CharField(read_only=True)

    class Meta:
        model = Candidates
        fields = ['id' , 'first_name' ,'last_name', 'stage_name' , 'recruiter_name' , 'resume', 'resume_raw_data']

