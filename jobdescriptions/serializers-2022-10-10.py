from rest_framework import serializers
from jobdescriptions.models import jobModel, jobSubmissionModel, jobAssingmentModel, jobNotesModel


class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = jobModel
        fields = "__all__"
        depth = 1
        # exclude=['created_by']


class JobDescriptionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = jobModel
        fields = "__all__"


class JobDescriptionNotesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = jobNotesModel
        fields = "__all__"
        depth = 1


class JobDescriptionNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = jobNotesModel
        fields = "__all__"


class JobDescriptionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = jobModel
        # fields = "__all__"
        fields = ['job_id', 'client_name', 'job_title']


class JobAssingmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = jobAssingmentModel
        fields = "__all__"
        depth = 1


class JobAssingmentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = jobAssingmentModel
        fields = "__all__"


class JobSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = jobSubmissionModel
        fields = "__all__"
        depth = 1


class JobSubmissionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = jobSubmissionModel
        fields = "__all__"


class UserDropDownListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)

    class Meta:
        model = jobModel
        fields = ['id', 'first_name', 'last_name', 'email']
