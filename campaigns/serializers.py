from rest_framework import serializers

from campaigns.models import CampaignListModel, CampaignModel, CampaignListDataModel, CampaignListMappingDataModel, \
    CampaignListUploadDataModel, CustomFieldsModel


class FieldsMappingSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)


class CampaignListSerializer(serializers.ModelSerializer):
    # list_mapping = FieldsMappingSerializer()
    class Meta:
        model = CampaignListModel
        fields = "__all__"
        # fields = ["id", "list_name", "list_size", "list_description", "status", "data_type", "upload_file",
        # "list_mapping", "created_by", "created_at"]


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignModel
        fields = "__all__"
        depth = 2


class CampaignWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignModel
        fields = "__all__"


class CampaignListDataModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignListDataModel
        fields = "__all__"


class CampaignListMappingDataModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignListMappingDataModel
        fields = "__all__"
        depth = 2


class CampaignEmailListDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignListUploadDataModel
        fields = "__all__"
        # fields = ["id", "first_name", "last_name", "email"]


class CustomFieldsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomFieldsModel
        fields = "__all__"