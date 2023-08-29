from rest_framework import serializers
from jobdescriptions.models import jobModel, jobSubmissionModel, jobAssingmentModel, jobNotesModel


class GetJobCurrentStatusSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    job_title = serializers.CharField(max_length=200)

    CandidateReview = serializers.CharField(max_length=200)
    RejectedByTeam = serializers.CharField(max_length=200)
    Submission = serializers.CharField(max_length=200)
    StillSubmission = serializers.CharField(max_length=200)
    ClientInterviewSecond = serializers.CharField(max_length=200)
    SendoutReject = serializers.CharField(max_length=200)
    ClientInterviewFirst = serializers.CharField(max_length=200)
    OfferRejected = serializers.CharField(max_length=200)
    Shortlisted = serializers.CharField(max_length=200)
    SecondInterviewReject = serializers.CharField(max_length=200)
    HoldbyClient = serializers.CharField(max_length=200)
    InterviewSelect = serializers.CharField(max_length=200)
    OfferBackout = serializers.CharField(max_length=200)
    HoldbyBDM = serializers.CharField(max_length=200)
    InternalInterview = serializers.CharField(max_length=200)
    InterviewBackout = serializers.CharField(max_length=200)
    FeedbackAwaited = serializers.CharField(max_length=200)
    InternalInterviewReject = serializers.CharField(max_length=200)
    Placed = serializers.CharField(max_length=200)
    Offered = serializers.CharField(max_length=200)
    InterviewReject = serializers.CharField(max_length=200)
    SubmissionReject = serializers.CharField(max_length=200)
    SendOut = serializers.CharField(max_length=200)

    ClientInterview = serializers.CharField(max_length=200)
    RejectedByClient = serializers.CharField(max_length=200)
    CandidateAdded = serializers.CharField(max_length=200)

    class Meta:
        model = jobModel
        fields = ["id", "job_title",
                  "CandidateReview", "RejectedByTeam", "Submission", "StillSubmission", "ClientInterviewSecond",
                  "SendoutReject",
                  "ClientInterviewFirst", "OfferRejected", "Shortlisted", "SecondInterviewReject", "HoldbyClient",
                  "InterviewSelect", "OfferBackout", "HoldbyBDM", "InternalInterview", "InterviewBackout",
                  "FeedbackAwaited",
                  "FeedbackAwaited", "InternalInterviewReject", "Placed", "Offered", "InterviewReject",
                  "SubmissionReject", "SendOut", "ClientInterview", "RejectedByClient", "CandidateAdded",

                  ]


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
    """assignment_date = serializers.DateTimeField(format='%Y')

    def to_representation(self, instance):
        format = "%Y-%m-%d %H:%M:%S"
        representation = super(JobAssingmentWriteSerializer, self).to_representation(instance)
        representation['assignment_date'] = instance.assignment_date.strftime(format)
        return representation"""

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


class ExportAssignmentHistoryModelSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    primary_recruiter = serializers.CharField(read_only=True)
    secondary_recruiter = serializers.CharField(read_only=True)
    assignee_name = serializers.CharField(read_only=True)
    created_at = serializers.CharField(read_only=True)

    class Meta:
        model = jobModel
        fields = ['id', 'primary_recruiter', 'secondary_recruiter', 'assignee_name', 'created_at']


class UnassignedJobsStatusSerializer(serializers.ModelSerializer):
    # id = serializers.CharField(read_only=True)
    secondary_recruiter_name = JobAssingmentWriteSerializer()
    number_of_unassigned_jobs = JobDescriptionWriteSerializer()

    class Meta:
        model = jobModel
        fields = ['secondary_recruiter_name', 'number_of_unassigned_jobs']
        depth = 1
