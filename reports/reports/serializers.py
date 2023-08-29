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

class RecruitersPerformanceSummarySerializer(serializers.ModelSerializer):
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
    submission_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    job_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    # submission_date = serializers.SerializerMethodField(method_name='get_date')
    # job_date = serializers.SerializerMethodField(method_name='get_date')

    class Meta:
        model = Candidates
        fields = ["id", "candidate_name", "primary_email", "primary_phone_number",
                  "company_name", "total_experience", "rank","job_title", "skills_1","visa","job_type",
                  'min_rate','max_rate', "min_salary","max_salary", "client_name", "location", "bdm_name",
                  "status", "recruiter_name", "submission_date", "job_date" , "created_at"
                  ]

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
    submission_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    job_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    first_assingment_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    # submission_date = serializers.SerializerMethodField(method_name='get_date')
    # job_date = serializers.SerializerMethodField(method_name='get_date')

    class Meta:
        model = Candidates
        fields = ["id", "candidate_name", "primary_email", "primary_phone_number",
                  "company_name", "total_experience", "rank","job_title", "skills_1","visa","job_type",
                  'min_rate','max_rate', "min_salary","max_salary", "client_name", "location", "bdm_name",
                  "status", "recruiter_name", "submission_date", "job_date" , "first_assingment_date" , "created_at"
                  ]

    def get_date(self, instance):
        date = datetime.datetime.now()
        return date.strftime("%Y-%m-%d")


class BdmPerformanceSummaryCSVSerializer(serializers.ModelSerializer):
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
    submission_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    job_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    first_assingment_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    activity_status = serializers.CharField(max_length=200)
    last_updated_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")


    class Meta:
        model = Candidates
        fields = ["id", "candidate_name", "primary_email", "primary_phone_number",
                  "company_name", "total_experience", "rank","job_title", "skills_1","visa","job_type",
                  'min_rate','max_rate', "min_salary","max_salary", "client_name", "location", "bdm_name",
                  "status", "recruiter_name", "submission_date", "job_date" , "first_assingment_date" ,
                  "created_at", "activity_status", "last_updated_date"
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


class JobSubmissionsByClientTableSerializer(serializers.ModelSerializer):
    # job_description = JobDescriptionListSerializer()
    id = serializers.CharField(max_length=200)
    job_title = serializers.CharField(max_length=200)
    client_name = serializers.CharField(max_length=200)
    Job_ID = serializers.CharField(max_length=200)
    employment_type = serializers.CharField(max_length=200)
    min_salary = serializers.CharField(max_length=200)
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
    total_jobs = serializers.CharField(max_length=200)

    class Meta:
        model = Candidates
        fields = ["id", "job_title", "total_jobs", "client_name", "bdm_name", "job_date", "Job_ID", "employment_type",
                  "min_salary", "max_salary", "min_rate", "max_rate",
                  "Client_Interview", "Offered", "Submission", "Rejected_By_Team", "Sendout_Reject",
                  "Offer_Rejected", "Shortlisted", "Internal_Interview", "Awaiting_Feedback", "Placed",
                  "Rejected_By_Client", "Submission_Reject", "SendOut"
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


class JobSummaryCSVSerializer(serializers.ModelSerializer):
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
    status = serializers.CharField(max_length=200)
    assigned_recruiter_name = serializers.CharField(max_length=200)
    first_assignment_date = serializers.CharField(max_length=200)

    class Meta:
        model = Candidates
        fields = ["id" , "job_title" , "client_name" , "bdm_name" , "job_date" ,"Job_ID","employment_type","min_salary","max_salary","min_rate","max_rate",
                    "Client_Interview" , "Offered" ,"Submission" ,"Rejected_By_Team", "Sendout_Reject",
                    "Offer_Rejected", "Shortlisted" ,"Internal_Interview","Awaiting_Feedback","Placed",
                    "Rejected_By_Client" , "Submission_Reject" , "SendOut",
                  "status", "assigned_recruiter_name", "first_assignment_date"
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
    bdm_name = serializers.CharField(max_length=200)
    # created_at = serializers.SerializerMethodField(method_name='get_date')
    # stage_count = serializers.IntegerField(source='stage.count', read_only=True)

    class Meta:
        model = Candidates
        fields = ["job_title", "total_count", "stage_name", "created_at" ,"job_id" , 'bdm_name']
        depth = 2


class JobSubmissionsByClientGraphSerializer(serializers.ModelSerializer):
    # job_description = JobDescriptionListSerializer()
    company_name = serializers.CharField(max_length=200)
    total_count = serializers.CharField(max_length=200)
    stage_name = serializers.CharField(max_length=200)
    created_at = serializers.CharField(max_length=200)
    job_id = serializers.CharField(max_length=200)
    bdm_name = serializers.CharField(max_length=200)
    # created_at = serializers.SerializerMethodField(method_name='get_date')
    # stage_count = serializers.IntegerField(source='stage.count', read_only=True)

    class Meta:
        model = Candidates
        fields = ["company_name", "total_count", "stage_name", "created_at" ,"job_id" , 'bdm_name']
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


class TopClientSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    client_name = serializers.CharField(max_length=200)
    stage = serializers.CharField(max_length=200)
    job_title = serializers.CharField(max_length=200)

    class Meta:
        model = clientModel
        fields = ["id", "client_name", "stage", "job_title"] # , "submissions", "placed"


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
    posted_date = serializers.CharField(max_length=200)
    status = serializers.CharField(max_length=200)
    job_title = serializers.CharField(max_length=200)
    total_submissions = serializers.CharField(read_only=True)
    placed = serializers.CharField(read_only=True)
    company_name = serializers.CharField(max_length=200)
    bdm_name = serializers.CharField(read_only=True)
    assignee_name = serializers.CharField(max_length=200)
    assinged_date = serializers.CharField(max_length=200)

    class Meta:
        model = jobModel
        fields = ["id", "posted_date", "status" , "job_title","total_submissions","placed", "company_name",
                  "assignee_name" , "assinged_date" , "bdm_name"]

class MyCandidateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    candidate_name = serializers.CharField(max_length=200)
    job_title = serializers.CharField(max_length=200)
    current_status = serializers.CharField(max_length=200)
    client_name = serializers.CharField(max_length=200)
    bdm_name = serializers.CharField(max_length=200)
    last_updated = serializers.CharField(max_length=200)
    submission_date = serializers.CharField(max_length=200)

    class Meta:
        model = Candidates
        fields = ["id", "candidate_name", "current_status" , "job_title", "client_name",
                  "submission_date" , "last_updated" , "bdm_name"]

class AssingedDashboardListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    assinged_date = serializers.CharField(read_only=True)
    job_title = serializers.CharField(max_length=200)
    company_name = serializers.CharField(read_only=True)
    primary_recruiter_name = serializers.CharField(read_only=True)
    secondary_recruiter_name = serializers.CharField(read_only=True)
    assignee_name = serializers.CharField(read_only=True)
    posted_date = serializers.CharField(read_only=True)

    class Meta:
        model = jobModel
        fields = "__all__"

class AssingedDashboardSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    assinged_date = serializers.CharField(read_only=True)
    job_title = serializers.CharField(max_length=200)
    company_name = serializers.CharField(read_only=True)
    primary_recruiter_name = serializers.CharField(read_only=True)
    secondary_recruiter_name = serializers.CharField(read_only=True)
    assignee_name = serializers.CharField(read_only=True)
    posted_date = serializers.CharField(read_only=True)

    class Meta:
        model = jobModel
        fields = ['id' , 'assinged_date' , 'posted_date' , 'job_title','company_name' , 'primary_recruiter_name',
                    'secondary_recruiter_name', 'assignee_name']



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

class JobsByBDMGraphSerializer(serializers.ModelSerializer):
    total_count = serializers.CharField(read_only=True)
    month = serializers.CharField(read_only=True)
    bdm_name = serializers.CharField(read_only=True)
    created_at = serializers.CharField(read_only=True)
    bdm_id = serializers.CharField(read_only=True)
    # job_description = JobDescriptionListSerializer()
    # created_at = serializers.SerializerMethodField(method_name='get_date')
    # stage_count = serializers.IntegerField(source='stage.count', read_only=True)

    class Meta:
        model = jobModel
        fields = ['total_count' , 'month' , 'bdm_name' , 'created_at' , 'bdm_id']
        depth = 1

class ActiveJobsAgingSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    job_id = serializers.CharField(read_only=True)
    job_title = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    company_name = serializers.CharField(read_only=True)
    posted_date = serializers.CharField(read_only=True)
    first_submission_date = serializers.CharField(read_only=True)
    first_assingment_date= serializers.CharField(read_only=True)
    job_age = serializers.CharField(read_only=True)
    bdm_name = serializers.CharField(read_only=True)
    primary_recruiter_name = serializers.CharField(read_only=True)
    secondary_recruiter_name = serializers.CharField(read_only=True)
    # job_description = JobDescriptionListSerializer()
    # created_at = serializers.SerializerMethodField(method_name='get_date')
    # stage_count = serializers.IntegerField(source='stage.count', read_only=True)

    class Meta:
        model = jobModel
        fields = ['id' , 'job_id' , 'job_title' , 'status' , 'company_name','primary_recruiter_name','secondary_recruiter_name',
                  'posted_date' ,'first_submission_date','first_assingment_date','job_age' ,'bdm_name']

class UnassignedJobsSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    job_id = serializers.CharField(read_only=True)
    job_title = serializers.CharField(read_only=True)
    company_name = serializers.CharField(read_only=True)
    posted_date = serializers.CharField(read_only=True)
    bdm_name = serializers.CharField(read_only=True)

    class Meta:
        model = jobModel
        fields = ['id' , 'job_id' , 'job_title' , 'company_name',
                  'posted_date' ,'bdm_name']

class ClientRevenueSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    client_name_value = serializers.CharField(read_only=True)
    expected_revenue = serializers.CharField(read_only=True)
    actual_revenue = serializers.CharField(read_only=True)

    class Meta:
        model = jobModel
        fields = ['id' , 'client_name_value' , 'expected_revenue' , 'actual_revenue']


class BdmEmailReportSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    job_title = serializers.CharField(read_only=True)
    bdm_name = serializers.CharField(read_only=True)
    client_name = serializers.CharField(read_only=True)
    job_id = serializers.CharField(read_only=True)
    bdm_location = serializers.CharField(read_only=True)
    job_posted_date = serializers.CharField(read_only=True)
    min_salary = serializers.CharField(max_length=200)
    max_salary = serializers.CharField(max_length=200)
    min_rate = serializers.CharField(max_length=200)
    max_rate = serializers.CharField(max_length=200)
    candidates_name = serializers.CharField(max_length=200)
    submission_dates = serializers.CharField(max_length=200)

    class Meta:
        model = jobModel
        fields = ['id', 'bdm_name', 'job_title', 'client_name', 'job_id', 'bdm_location',
                  'job_posted_date', 'min_salary', 'max_salary', 'min_rate', 'max_rate',
                  'candidates_name', 'submission_dates']


class BdmJobsAssignmentReportSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    job_title = serializers.CharField(read_only=True)
    bdm_name = serializers.CharField(read_only=True)
    client_name = serializers.CharField(read_only=True)
    job_id = serializers.CharField(read_only=True)
    bdm_location = serializers.CharField(read_only=True)
    job_posted_date = serializers.CharField(read_only=True)
    min_salary = serializers.CharField(max_length=200)
    max_salary = serializers.CharField(max_length=200)
    min_rate = serializers.CharField(max_length=200)
    max_rate = serializers.CharField(max_length=200)
    candidates_name = serializers.CharField(max_length=200)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = jobModel
        fields = ['id', 'bdm_name', 'job_title', 'client_name', 'job_id', 'bdm_location',
                  'job_posted_date', 'min_salary', 'max_salary', 'min_rate', 'max_rate',
                  'candidates_name', 'created_at'
                  ]


class BdmJobsReportSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    job_title = serializers.CharField(read_only=True)
    bdm_name = serializers.CharField(read_only=True)
    client_name = serializers.CharField(read_only=True)
    job_id = serializers.CharField(read_only=True)
    bdm_location = serializers.CharField(read_only=True)
    job_posted_date = serializers.CharField(read_only=True)
    min_salary = serializers.CharField(max_length=200)
    max_salary = serializers.CharField(max_length=200)
    min_rate = serializers.CharField(max_length=200)
    max_rate = serializers.CharField(max_length=200)

    class Meta:
        model = jobModel
        fields = ['id', 'bdm_name', 'job_title', 'client_name', 'job_id', 'bdm_location',
                  'job_posted_date', 'min_salary', 'max_salary', 'min_rate', 'max_rate'
                  ]


class RecruiterEmailReportSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    recruiter_name = serializers.CharField(read_only=True)
    bdm_name = serializers.CharField(read_only=True)
    client_name = serializers.CharField(read_only=True)
    candidate_name = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)
    job_title = serializers.CharField(read_only=True)
    submission_date = serializers.CharField(read_only=True)
    min_salary = serializers.CharField(max_length=200)
    max_salary = serializers.CharField(max_length=200)
    min_rate = serializers.CharField(max_length=200)
    max_rate = serializers.CharField(max_length=200)
    created_at = serializers.CharField(max_length=200)

    primary_email = serializers.CharField(max_length=200)
    primary_phone_number = serializers.CharField(max_length=200)
    # position = serializers.CharField(max_length=200)

    class Meta:
        model = jobModel
        fields = ['id', 'recruiter_name', 'bdm_name', 'candidate_name', 'location', 'client_name', 'job_title',
                  'submission_date', 'min_salary', 'max_salary', 'min_rate', 'max_rate',
                  'primary_email', 'primary_phone_number', 'created_at']


class RecruiterSubmissionReportSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    recruiter_name = serializers.CharField(read_only=True)
    bdm_name = serializers.CharField(read_only=True)
    client_name = serializers.CharField(read_only=True)
    candidate_name = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)
    job_title = serializers.CharField(read_only=True)
    submission_date = serializers.CharField(read_only=True)
    min_salary = serializers.CharField(max_length=200)
    max_salary = serializers.CharField(max_length=200)
    min_rate = serializers.CharField(max_length=200)
    max_rate = serializers.CharField(max_length=200)
    created_at = serializers.CharField(max_length=200)

    primary_email = serializers.CharField(max_length=200)
    primary_phone_number = serializers.CharField(max_length=200)
    stage_name = serializers.CharField(max_length=200)

    class Meta:
        model = jobModel
        fields = ['id', 'recruiter_name', 'bdm_name', 'candidate_name', 'location', 'client_name', 'job_title',
                  'submission_date', 'min_salary', 'max_salary', 'min_rate', 'max_rate',
                  'primary_email', 'primary_phone_number', 'created_at', 'stage_name']


class RecruiterSubmissionFollowUpReportSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    recruiter_name = serializers.CharField(read_only=True)
    bdm_name = serializers.CharField(read_only=True)
    client_name = serializers.CharField(read_only=True)
    candidate_name = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)
    job_title = serializers.CharField(read_only=True)
    submission_date = serializers.CharField(read_only=True)
    min_salary = serializers.CharField(max_length=200)
    max_salary = serializers.CharField(max_length=200)
    min_rate = serializers.CharField(max_length=200)
    max_rate = serializers.CharField(max_length=200)
    created_at = serializers.CharField(max_length=200)

    primary_email = serializers.CharField(max_length=200)
    primary_phone_number = serializers.CharField(max_length=200)
    stage_name = serializers.CharField(max_length=200)
    job_type = serializers.CharField(max_length=200)
    location = serializers.CharField(max_length=200)
    updated_at = serializers.CharField(max_length=200)

    class Meta:
        model = jobModel
        fields = ['id', 'recruiter_name', 'bdm_name', 'candidate_name', 'location', 'client_name', 'job_title',
                  'submission_date', 'min_salary', 'max_salary', 'min_rate', 'max_rate',
                  'primary_email', 'primary_phone_number', 'created_at', 'stage_name', 'job_type', 'location', 'updated_at']


class BdmSubmissionFollowUpReportSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    bdm_name = serializers.CharField(read_only=True)
    total_submissions = serializers.CharField(max_length=200)

    class Meta:
        model = jobModel
        fields = ['id', 'bdm_name', 'total_submissions']


class BdmDailySubmissionReportSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    recruiter_name = serializers.CharField(read_only=True)
    bdm_name = serializers.CharField(read_only=True)
    client_name = serializers.CharField(read_only=True)
    candidate_name = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)
    job_title = serializers.CharField(read_only=True)
    submission_date = serializers.CharField(read_only=True)
    min_salary = serializers.CharField(max_length=200)
    max_salary = serializers.CharField(max_length=200)
    min_rate = serializers.CharField(max_length=200)
    max_rate = serializers.CharField(max_length=200)
    created_at = serializers.CharField(max_length=200)
    total_experience = serializers.CharField(max_length=200)
    primary_email = serializers.CharField(max_length=200)
    primary_phone_number = serializers.CharField(max_length=200)
    stage_name = serializers.CharField(max_length=200)
    job_type = serializers.CharField(max_length=200)
    location = serializers.CharField(max_length=200)
    updated_at = serializers.CharField(max_length=200)
    resume = serializers.CharField(max_length=200)
    created_by_id = serializers.CharField(max_length=200)

    class Meta:
        model = jobModel
        fields = ['id', 'recruiter_name', 'bdm_name', 'candidate_name', 'location', 'client_name', 'job_title',
                  'submission_date', 'min_salary', 'max_salary', 'min_rate', 'max_rate', 'total_experience',
                  'primary_email', 'primary_phone_number', 'created_at', 'stage_name', 'job_type',
                  'location', 'updated_at', 'resume', 'created_by_id']


class UserReportSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    first_name = serializers.CharField(max_length=200)

    class Meta:
        model = User
        fields = ('id', 'first_name') # 'user_countries',


class WeekendEmailReportSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    recruiter_name = serializers.CharField(read_only=True)
    bdm_name = serializers.CharField(read_only=True)
    total_jobs = serializers.CharField(read_only=True)
    total_candidates = serializers.CharField(read_only=True)
    total_jobs_worked = serializers.CharField(read_only=True)

    class Meta:
        model = jobModel
        fields = ['id' , 'recruiter_name' ,'bdm_name', 'total_jobs' , 'total_candidates' , 'total_jobs_worked']

