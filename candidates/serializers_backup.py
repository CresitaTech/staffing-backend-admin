from rest_framework import serializers

from candidates.models import Candidates, candidatesSubmissionModel, activityStatusModel, \
    placementCardModel, rtrModel, emailTemplateModel, mailModel, candidateStageModel , importFileModel


class FileSerializer(serializers.Serializer):
    file = serializers.FileField(max_length=None, allow_empty_file=False)


class CandidateSerializer(serializers.ModelSerializer):
    # job_description = JobDescriptionListSerializer()
    # resume = serializers.FileField(max_length=None, allow_empty_file=False)
    class Meta:
        model = Candidates
        fields = "__all__"
        depth = 1


class CandidateWriteSerializer(serializers.ModelSerializer):
    #created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
    #updated_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
    # job_description = JobDescriptionListSerializer()
    # resume = serializers.FileField(max_length=None, allow_empty_file=False)
    class Meta:
        model = Candidates
        fields = "__all__"


class CandidateWriteFileSerializer(serializers.ModelSerializer):
    # job_description = JobDescriptionListSerializer()
    # resume = serializers.FileField(max_length=None, allow_empty_file=False)
    class Meta:
        model = Candidates
        exclude = ('resume', )
        
class CandidatesDropdownListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    first_name = serializers.CharField(max_length=200)
    last_name = serializers.CharField(max_length=200)

    class Meta:
        model = Candidates
        fields = ["id", "first_name" , "last_name"]

class ActivityStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = activityStatusModel
        fields="__all__"
        depth = 1
        
class ActivityStatusWriteSerializer(serializers.ModelSerializer):
    # job_description = JobDescriptionListSerializer()
    # resume = serializers.FileField(max_length=None, allow_empty_file=False)
    class Meta:
        model = activityStatusModel
        fields = "__all__"


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = candidatesSubmissionModel
        fields="__all__"
        depth = 1
        
class SubmissionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = candidatesSubmissionModel
        fields="__all__"


class PlacementCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = placementCardModel
        fields="__all__"
        depth = 1
        
class PlacementCardWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = placementCardModel
        fields="__all__"


class RTRSerializer(serializers.ModelSerializer):
    class Meta:
        model = rtrModel
        fields="__all__"
        depth = 1
        
class RTRWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = rtrModel
        fields="__all__"
        

class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = emailTemplateModel
        fields="__all__"


class CandidateMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = mailModel
        fields="__all__"
        #depth = 1
        
class CandidateMailWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = mailModel
        fields="__all__"


class CandidateStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = candidateStageModel
        fields="__all__"
        
class ImportFileSerializer(serializers.ModelSerializer):
    #data_fields = CandidateSerializer()
    class Meta:
        model = importFileModel
        fields="__all__"
