import datetime
from rest_framework import serializers
from clients.serializers import ClientSerializer
from candidates.models import Candidates, candidatesSubmissionModel, activityStatusModel, \
    placementCardModel, rtrModel, emailTemplateModel, mailModel
from clients.models import clientModel
from jobdescriptions.models import jobModel
from users.models import User


class RecruiterPerformanceSummarySerializer(serializers.ModelSerializer):
    # job_description = JobDescriptionListSerializer()

    created_at = serializers.SerializerMethodField(method_name='get_date')

    class Meta:
        model = Candidates
        fields = ["first_name", "last_name", "total_experience",
                  "visa", "recruiter_name", 'min_salary', 'max_salary', 'min_rate','max_rate', "stage",
                  "job_description", "created_at", "created_by"
                  ]
        depth = 2


    def get_date(self, instance):
        date = datetime.datetime.now()
        return date.strftime("%m/%d/%Y")


class RecruiterPerformanceSummaryGraphSerializer(serializers.ModelSerializer):
    # job_description = JobDescriptionListSerializer()
    first_name = serializers.CharField(max_length=200)
    total_count = serializers.CharField(max_length=200)
    stage_name = serializers.CharField(max_length=200)
    created_by_id = serializers.CharField(max_length=200)

    created_at = serializers.SerializerMethodField(method_name='get_date')
    # stage_count = serializers.IntegerField(source='stage.count', read_only=True)

    class Meta:
        model = Candidates
        fields = ["first_name", "total_count", "stage_name", "created_at" , 'created_by_id']
        depth = 2

    def get_date(self, instance):
        date = datetime.datetime.now()
        return date.strftime("%Y-%m-%d")


class BdmPerformanceSummarySerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    candidate_name = serializers.CharField(max_length=200)
    primary_email = serializers.CharField(max_length=200)
    primary_phone_number = serializers.CharField(max_length=200)
    company_name = serializers.CharField(max_length=200)
    total_experience = serializers.CharField(max_length=200)
    rank = serializers.CharField(max_length=200)
    job_title = serializers.CharField(max_length=200)
    skills_1 = serializers.CharField(max_length=200)
    min_rate = serializers.CharField(max_length=200)
    max_rate = serializers.CharField(max_length=200)
    min_salary = serializers.CharField(max_length=200)
    max_salary = serializers.CharField(max_length=200)
    client_name = serializers.CharField(max_length=200)
    location = serializers.CharField(max_length=200)
    bdm_name = serializers.CharField(max_length=200)
    visa = serializers.CharField(max_length=200)
    job_type = serializers.CharField(max_length=200)
    status = serializers.CharField(max_length=200)
    recruiter_name = serializers.CharField(max_length=200)
    submission_date = serializers.DateTimeField(format='%Y-%m-%d')
    job_date = serializers.DateTimeField(format='%Y-%m-%d')

    # submission_date = serializers.SerializerMethodField(method_name='get_date')
    # job_date = serializers.SerializerMethodField(method_name='get_date')

    class Meta:
        model = Candidates
        fields = ["id", "candidate_name", "primary_email", "primary_phone_number",
                  "company_name", "total_experience", "rank","job_title", "skills_1","visa","job_type",
                  'min_rate','max_rate', "min_salary","max_salary", "client_name", "location", "bdm_name",
                  "status", "recruiter_name", "submission_date", "job_date"
                  ]

    def get_date(self, instance):
        date = datetime.datetime.now()
        return date.strftime("%Y-%m-%d")


class BdmPerformanceSummaryGraphSerializer(serializers.ModelSerializer):
    # job_description = JobDescriptionListSerializer()
    first_name = serializers.CharField(max_length=200)
    total_count = serializers.CharField(max_length=200)
    stage_name = serializers.CharField(max_length=200)
    created_by_id = serializers.CharField(max_length=200)

    created_at = serializers.SerializerMethodField(method_name='get_date')
    # stage_count = serializers.IntegerField(source='stage.count', read_only=True)

    class Meta:
        model = Candidates
        fields = ["first_name", "total_count", "stage_name", "created_at" , 'created_by_id']
        depth = 2

    def get_date(self, instance):
        date = datetime.datetime.now()
        return date.strftime("%Y-%m-%d")


class UserObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        write_only_fields = ('password',)


############################# Job Summary ###############################

class JobSummaryTableSerializer(serializers.ModelSerializer):
    #job_description = JobDescriptionListSerializer()
    id = serializers.CharField(max_length=200)
    job_title = serializers.CharField(max_length=200)
    client_name = serializers.CharField(max_length=200)
    Job_ID = serializers.CharField(max_length=200)
    employment_type = serializers.CharField(max_length=200)
    min_salary =  serializers.CharField(max_length=200)
    max_salary = serializers.CharField(max_length=200)
    min_rate = serializers.CharField(max_length=200)
    max_rate = serializers.CharField(max_length=200)
    bdm_name = serializers.CharField(max_length=200)
    job_date = serializers.CharField(max_length=200)
    Client_Interview = serializers.CharField(max_length=200)
    Offered = serializers.CharField(max_length=200)
    Submission = serializers.CharField(max_length=200)
    Rejected_By_Team = serializers.CharField(max_length=200)
    Sendout_Reject = serializers.CharField(max_length=200)
    Offer_Rejected = serializers.CharField(max_length=200)
    Shortlisted = serializers.CharField(max_length=200)
    Internal_Interview = serializers.CharField(max_length=200)
    Awaiting_Feedback = serializers.CharField(max_length=200)
    Placed = serializers.CharField(max_length=200)
    Rejected_By_Client = serializers.CharField(max_length=200)
    Submission_Reject = serializers.CharField(max_length=200)
    SendOut = serializers.CharField(max_length=200)

    class Meta:
        model = Candidates
        fields = ["id" , "job_title" , "client_name" , "bdm_name" , "job_date" ,"Job_ID","employment_type","min_salary","max_salary","min_rate","max_rate",
                    "Client_Interview" , "Offered" ,"Submission" ,"Rejected_By_Team", "Sendout_Reject", 
                    "Offer_Rejected", "Shortlisted" ,"Internal_Interview","Awaiting_Feedback","Placed",
                    "Rejected_By_Client" , "Submission_Reject" , "SendOut"
                  ]

    def get_date(self, instance):
        date = datetime.datetime.now()
        return date.strftime("%m/%d/%Y")


class JobSummarySerializer(serializers.ModelSerializer):
    #job_description = JobDescriptionListSerializer()
    id = serializers.CharField(max_length=200)
    job_title = serializers.CharField(max_length=200)
    client_name = serializers.CharField(max_length=200)
    Job_ID = serializers.CharField(max_length=200)
    employment_type = serializers.CharField(max_length=200)
    min_salary =  serializers.CharField(max_length=200)
    max_salary = serializers.CharField(max_length=200)
    min_rate = serializers.CharField(max_length=200)
    max_rate = serializers.CharField(max_length=200)
    bdm_name = serializers.CharField(max_length=200)
    job_date = serializers.CharField(max_length=200)
    Client_Interview = serializers.CharField(max_length=200)
    Offered = serializers.CharField(max_length=200)
    Submission = serializers.CharField(max_length=200)
    Rejected_By_Team = serializers.CharField(max_length=200)
    Sendout_Reject = serializers.CharField(max_length=200)
    Offer_Rejected = serializers.CharField(max_length=200)
    Shortlisted = serializers.CharField(max_length=200)
    Internal_Interview = serializers.CharField(max_length=200)
    Awaiting_Feedback = serializers.CharField(max_length=200)
    Placed = serializers.CharField(max_length=200)
    Rejected_By_Client = serializers.CharField(max_length=200)
    Submission_Reject = serializers.CharField(max_length=200)
    SendOut = serializers.CharField(max_length=200)

    class Meta:
        model = Candidates
        fields = ["id" , "job_title" , "client_name" , "bdm_name" , "job_date" ,"Job_ID","employment_type","min_salary","max_salary","min_rate","max_rate",
                    "Client_Interview" , "Offered" ,"Submission" ,"Rejected_By_Team", "Sendout_Reject", 
                    "Offer_Rejected", "Shortlisted" ,"Internal_Interview","Awaiting_Feedback","Placed",
                    "Rejected_By_Client" , "Submission_Reject" , "SendOut"
                  ]

    def get_date(self, instance):
        date = datetime.datetime.now()
        return date.strftime("%m/%d/%Y")


class JobSummaryGraphSerializer(serializers.ModelSerializer):
    # job_description = JobDescriptionListSerializer()
    job_title = serializers.CharField(max_length=200)
    total_count = serializers.CharField(max_length=200)
    stage_name = serializers.CharField(max_length=200)
    created_at = serializers.CharField(max_length=200)
    job_id = serializers.CharField(max_length=200)

    # created_at = serializers.SerializerMethodField(method_name='get_date')
    # stage_count = serializers.IntegerField(source='stage.count', read_only=True)

    class Meta:
        model = Candidates
        fields = ["job_title", "total_count", "stage_name", "created_at" ,"job_id"]
        depth = 2


class ClientSummarySerializer(serializers.ModelSerializer):
    # job_description = JobDescriptionListSerializer()
    id = serializers.CharField(max_length=200)
    client_name = serializers.CharField(max_length=200)
    job_title = serializers.CharField(max_length=200)
    submissions = serializers.CharField(max_length=200)
    placed = serializers.CharField(max_length=200)

    class Meta:
        model = clientModel
        fields = ["id", "client_name", "job_title", "submissions", "placed"]


class TopFivePlacementSerializer(serializers.ModelSerializer):
    # job_description = JobDescriptionListSerializer()
    id = serializers.CharField(max_length=200)
    candidate_name = serializers.CharField(max_length=200)
    client_name = serializers.CharField(max_length=200)
    status = serializers.CharField(max_length=200)

    class Meta:
        model = Candidates
        fields = ["id", "candidate_name", "client_name", "status"]


class ClientDropdownListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    company_name = serializers.CharField(max_length=200)

    class Meta:
        model = clientModel
        fields = ["id", "company_name"]


class JobsDropdownListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    job_title = serializers.CharField(max_length=200)
    client_name = serializers.CharField(max_length=200)

    class Meta:
        model = jobModel
        fields = ["id", "job_title" , "client_name"]


class ClientDashboardListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    created_at = serializers.CharField(max_length=200)
    job_title = serializers.CharField(max_length=200)
    company_name = serializers.CharField(max_length=200)
    default_assignee_name = serializers.CharField(max_length=200)
    assinged_date = serializers.CharField(max_length=200)

    class Meta:
        model = jobModel
        fields = ["id", "created_at", "job_title", "company_name", "default_assignee_name" , "assinged_date"]
        
class AssingedDashboardListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    assinged_date = serializers.CharField(max_length=200)
    job_title = serializers.CharField(max_length=200)
    company_name = serializers.CharField(max_length=200)
    primary_recruiter_name = serializers.CharField(max_length=200)
    secondary_recruiter_name = serializers.CharField(max_length=200)
    assignee_name = serializers.CharField(max_length=200)
    posted_date = serializers.CharField(max_length=200)

    class Meta:
        model = jobModel
        fields = ["id", "assinged_date", "posted_date", "job_title", "company_name","assignee_name",
                  "primary_recruiter_name" ,"secondary_recruiter_name"]



class ActiveClientSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    active_clients = serializers.CharField(max_length=200)

    class Meta:
        model = jobModel
        fields = ["id", "active_clients"]


class TotalRecordSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    total_records = serializers.CharField(max_length=200)

    class Meta:
        model = jobModel
        fields = ["id", "total_records"]


class JobFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = jobModel
        fields = "__all__"
        
class JobsByBDMTableSerializer(serializers.ModelSerializer):
    #job_description = JobDescriptionListSerializer()

    class Meta:
        model = jobModel
        fields = "__all__"
        depth = 1

    def get_date(self, instance):
        date = datetime.datetime.now()
        return date.strftime("%m/%d/%Y")
