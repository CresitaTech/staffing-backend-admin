import logging

from rest_framework import serializers
from datetime import datetime
from django.utils import timezone

from staffingapp import settings

logger = logging.getLogger(__name__)


from candidates.models import Candidates, candidatesSubmissionModel, activityStatusModel, \
    placementCardModel, rtrModel, emailTemplateModel, mailModel, candidateStageModel, importFileModel, \
    candidatesJobDescription, internalCandidatesJobDescription


class FileSerializer(serializers.Serializer):
    file = serializers.FileField(max_length=None, allow_empty_file=False)


class CandidateSerializer(serializers.ModelSerializer):
    # job_description = JobDescriptionListSerializer()
    # resume = serializers.FileField(max_length=None, allow_empty_file=False)
    class Meta:
        model = Candidates
        fields = "__all__"
        depth = 1


class CandidateExportSerializer(serializers.ModelSerializer):
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
    certification_doc = serializers.FileField(max_length=None, allow_empty_file=False, required=False)
    additional_qualification_doc = serializers.FileField(max_length=None, allow_empty_file=False, required=False)

    class Meta:
        model = Candidates
        fields = "__all__"
        # read_only_fields = ['driving_license', 'offer_letter', 'passport', 'rtr', 'salary_slip', 'i94_document',
        #                    'visa_copy','educational_document', 'certification_doc', 'additional_qualification_doc']


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

    # status = serializers.CharField(read_only=True)
    # submission_date = serializers.CharField(read_only=True)
    # updated_at = serializers.CharField(read_only=True)
    # updated_by_name = serializers.CharField(read_only=True)
    # visa = serializers.CharField(read_only=True)
    # min_rate = serializers.CharField(read_only=True)
    # max_rate = serializers.CharField(read_only=True)
    # min_salary = serializers.CharField(read_only=True)
    # max_salary = serializers.CharField(read_only=True)

    class Meta:
        model = Candidates
        fields = ["id", "first_name", "last_name"]
        """fields = ["id", "first_name", "last_name", 'status', 'submission_date', 'updated_at',
                  'updated_by_name', 'visa', 'min_rate', 'max_rate', 'min_salary', 'max_salary']"""


class CandidatesSubmissionForJobListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)

    status = serializers.CharField(read_only=True)
    submission_date = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)
    updated_by_name = serializers.CharField(read_only=True)
    created_by_name = serializers.CharField(read_only=True)
    visa = serializers.CharField(read_only=True)
    min_rate = serializers.CharField(read_only=True)
    max_rate = serializers.CharField(read_only=True)
    min_salary = serializers.CharField(read_only=True)
    max_salary = serializers.CharField(read_only=True)

    class Meta:
        model = Candidates
        fields = ["id", "first_name", "last_name", 'status', 'submission_date', 'updated_at',
                  'updated_by_name', 'created_by_name', 'visa', 'min_rate', 'max_rate', 'min_salary', 'max_salary']



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


class InternalCandidateJobsStagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = internalCandidatesJobDescription
        fields = "__all__"
        depth = 2


class InternalCandidateJobsStagesWriteSerializer(serializers.ModelSerializer):
    # send_out_date = serializers.SerializerMethodField()
    # submission_date = DateTimeFieldWihTZ(format='%Y-%m-%dT%H:%M:%S')
    # submission_date = serializers.SerializerMethodField()
    class Meta:
        model = internalCandidatesJobDescription
        fields = "__all__"

    def get_send_out_date(self, instance):
        request = self.context.get('request')
        logger.error('request.data.send_out_date===========: ' + str(request.data['send_out_date']))
        if request.data['send_out_date'] != None:
            return str(request.data['send_out_date']) + 'T' + str(datetime.now().time())
        return request.data['send_out_date']


    def get_submission_date(self, instance):
        request = self.context.get('request')
        updated_submission_date = str(request.data['submission_date']) + 'T' + str(datetime.now().time())
        logger.error('request.data.submission_date===========: ' + str(updated_submission_date) )
        # temp_date = datetime.strptime(updated_submission_date, "%Y-%m-%d %H:%M:%S.%f").timestamp()
        # logger.error('request.data.temp_date===========: ' + str(temp_date) )

        return updated_submission_date


class CandidatesForSubmissionJobSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    job_title = serializers.CharField(read_only=True)
    company_name = serializers.CharField(read_only=True)
    submission_date = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    recruiter_name = serializers.CharField(read_only=True)

    class Meta:
        model = candidatesJobDescription
        fields = ["id", "job_title", "company_name", "submission_date", "status", "recruiter_name" ]


class DateTimeFieldWihTZ(serializers.DateTimeField):
    '''Class to make output of a DateTime Field timezone aware
    '''
    def to_representation(self, value):
        value = timezone.localtime(value)
        local_tz_datetime = super(DateTimeFieldWihTZ, self).to_representation(value)
        logger.error('to_representation.submission_date===========: ' + str(local_tz_datetime) )
        return local_tz_datetime


class CandidateJobsStagesWriteSerializer(serializers.ModelSerializer):
    # send_out_date = serializers.SerializerMethodField()
    # submission_date = DateTimeFieldWihTZ(format='%Y-%m-%dT%H:%M:%S')
    # submission_date = serializers.SerializerMethodField()

    class Meta:
        model = candidatesJobDescription
        fields = "__all__"

    def get_send_out_date(self, instance):
        request = self.context.get('request')
        logger.error('request.data.send_out_date===========: ' + str(request.data['send_out_date']))
        if request.data['send_out_date'] != None:
            return str(request.data['send_out_date']) + 'T' + str(datetime.now().time())
        return request.data['send_out_date']


    def get_submission_date(self, instance):
        request = self.context.get('request')
        updated_submission_date = str(request.data['submission_date']) + 'T' + str(datetime.now().time())
        logger.error('request.data.submission_date===========: ' + str(updated_submission_date) )
        # temp_date = datetime.strptime(updated_submission_date, "%Y-%m-%d %H:%M:%S.%f").timestamp()
        # logger.error('request.data.temp_date===========: ' + str(temp_date) )

        return updated_submission_date
