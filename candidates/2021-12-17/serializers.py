from rest_framework import serializers

from candidates.models import Candidates, candidatesSubmissionModel, activityStatusModel, \
    placementCardModel, rtrModel, emailTemplateModel, mailModel, candidateStageModel, importFileModel, \
    candidatesJobDescription


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
    driving_license = serializers.FileField(max_length=None, allow_empty_file=False, required=False)
    offer_letter = serializers.FileField(max_length=None, allow_empty_file=False, required=False)
    passport = serializers.FileField(max_length=None, allow_empty_file=False, required=False)
    rtr = serializers.FileField(max_length=None, allow_empty_file=False, required=False)
    salary_slip = serializers.FileField(max_length=None, allow_empty_file=False, required=False)
    i94_document = serializers.FileField(max_length=None, allow_empty_file=False, required=False)
    visa_copy = serializers.FileField(max_length=None, allow_empty_file=False, required=False)
    educational_document = serializers.FileField(max_length=None, allow_empty_file=False, required=False)

    class Meta:
        model = Candidates
        fields = "__all__"
        read_only_fields = ['driving_license', 'offer_letter', 'passport', 'rtr', 'salary_slip', 'i94_document'
                                                                                                 'visa_copy',
                            'educational_document']


class CandidateWriteFileSerializer(serializers.ModelSerializer):
    # job_description = JobDescriptionListSerializer()
    # resume = serializers.FileField(max_length=None, allow_empty_file=False)
    class Meta:
        model = Candidates
        exclude = ('resume',)


class CandidatesDropdownListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    submission_date = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)
    updated_by_name = serializers.CharField(read_only=True)
    visa = serializers.CharField(read_only=True)
    min_rate = serializers.CharField(read_only=True)
    max_rate = serializers.CharField(read_only=True)
    min_salary = serializers.CharField(read_only=True)
    max_salary = serializers.CharField(read_only=True)

    class Meta:
        model = Candidates
        fields = ["id", "first_name", "last_name", 'status', 'submission_date', 'updated_at',
                  'updated_by_name', 'visa', 'min_rate', 'max_rate', 'min_salary', 'max_salary']


class ActivityStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = activityStatusModel
        fields = "__all__"
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
        fields = "__all__"
        depth = 1


class SubmissionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = candidatesSubmissionModel
        fields = "__all__"


class PlacementCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = placementCardModel
        fields = "__all__"
        depth = 1


class PlacementCardWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = placementCardModel
        fields = "__all__"


class RTRSerializer(serializers.ModelSerializer):
    class Meta:
        model = rtrModel
        fields = "__all__"
        depth = 1


class RTRWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = rtrModel
        fields = "__all__"


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = emailTemplateModel
        fields = "__all__"


class CandidateMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = mailModel
        fields = "__all__"
        # depth = 1


class CandidateMailWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = mailModel
        fields = "__all__"


class CandidateStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = candidateStageModel
        fields = "__all__"


class ImportFileSerializer(serializers.ModelSerializer):
    # data_fields = CandidateSerializer()
    class Meta:
        model = importFileModel
        fields = "__all__"


class CandidateJobsStagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = candidatesJobDescription
        fields = "__all__"
        depth = 2


class CandidateJobsStagesWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = candidatesJobDescription
        fields = "__all__"
