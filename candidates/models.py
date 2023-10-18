import logging
import uuid
from django.db import models
from ckeditor.fields import RichTextField
from interviewers.models import designationModel
from jobdescriptions.models import jobModel
from clients.models import clientModel
from staffingapp.settings import GLOBAL_ROLE, ROLE_CHOICES
from vendors.models import vendorEmailTemplateModel
from datetime import datetime
from django.utils import timezone
import datetime

logger = logging.getLogger(__name__)

STATUS_CHOICES = (
    ("Internal", "Internal"),
    ("External", "External")
)

class candidateStageModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    stage_name = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=10, choices=STATUS_CHOICES, default="External")
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True, default=3)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidates_stages'
        verbose_name = "Candidate Stage"
        verbose_name_plural = 'Candidate Stages'

    def __str__(self):
        return self.stage_name
    


class CandidateModelManager(models.Manager):
         
     def backup_candidate(self, obj, user, candidate_refer_id1,gunicorn_now1):
             
         backup_candidate =  CandidateModelBackup.objects.create(
            first_name=obj.first_name,
            last_name=obj.last_name,
            date_of_birth=obj.date_of_birth,
            primary_email=obj.primary_email,                     
            secondary_email=obj.secondary_email,
            primary_phone_number=obj.primary_phone_number,
          secondary_phone_number=obj.secondary_phone_number,
            company_name=obj.company_name,
            designation =obj.designation,
            skills_1=obj.skills_1,
            skills_2=obj.skills_2,
             min_salary=obj. min_salary,
             max_salary =obj.  max_salary,
             min_rate=obj. min_rate,
             max_rate=obj. max_rate,
            qualification =obj.qualification ,
            currency  =obj.currency ,
             visa=obj.  visa,
            current_location =obj.current_location,
              country =obj.  country ,
             total_experience =obj. total_experience ,
           reason_for_job_change=obj.reason_for_job_change,
             rtr_done =obj.  rtr_done ,
            willing_to_work_on_our_w2=obj.willing_to_work_on_our_w2,
           open_for_relocation  =obj.open_for_relocation ,
           rank=obj.rank,
            total_experience_in_usa =obj.total_experience_in_usa,
             employer_phone_number=obj. employer_phone_number,
            employer_name =obj.employer_name,
            employer_email=obj.employer_email,
            engagement_type =obj.engagement_type,
            any_offer_in_hand=obj.any_offer_in_hand,
             resume =obj. resume ,
           resume_raw_data =obj.resume_raw_data,
            remarks =obj.remarks ,
            certification=obj.certification,
           additional_qualification =obj.additional_qualification,
             stage=obj.stage,
            recruiter_name=obj.recruiter_name,
           created_by  =obj.created_by ,
            updated_by=obj.updated_by,
           created_at=obj. created_at,
            updated_at=obj.updated_at,
            candidate_refer_id=candidate_refer_id1,
             user_id = user.id,
            #  date_of_deletion = timezone.now()
               date_of_deletion = gunicorn_now1
         )

         job_descriptions = obj.job_description.all()
         backup_candidate.job_description.set(job_descriptions)
         obj.delete()


class Candidates(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    date_of_birth = models.CharField(max_length=255, null=True, blank=True)
    primary_email = models.CharField(max_length=255, null=True, unique=True)
    secondary_email = models.CharField(max_length=255, null=True, blank=True)
    primary_phone_number = models.CharField(max_length=255, null=True)
    secondary_phone_number = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    designation = models.ForeignKey(designationModel, related_name='designation', null=True, on_delete=models.SET_NULL)
    skills_1 = models.CharField(max_length=255, null=True, blank=True)
    skills_2 = models.CharField(max_length=255, null=True, blank=True)
    min_salary = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    min_rate = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    max_rate = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    qualification = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True)
    visa = models.CharField(max_length=255, null=True, blank=True)
    current_location = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    total_experience = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    reason_for_job_change = models.CharField(max_length=255, null=True, blank=True)
    rtr_done = models.CharField(max_length=255, null=True, blank=True)
    willing_to_work_on_our_w2 = models.CharField(max_length=255, null=True, blank=True)
    open_for_relocation = models.CharField(max_length=255, null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True, default=0)
    total_experience_in_usa = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    employer_phone_number = models.CharField(max_length=255, null=True, blank=True)
    employer_name = models.CharField(max_length=255, null=True, blank=True)
    employer_email = models.CharField(max_length=255, null=True, blank=True)
    engagement_type = models.CharField(max_length=255, null=True, blank=True)
    any_offer_in_hand = models.CharField(max_length=255, null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    resume_raw_data = RichTextField(null=True, blank=True)

    remarks = RichTextField(null=True, blank=True)
    certification = models.CharField(max_length=255, null=True)
    additional_qualification = models.CharField(max_length=255, null=True)

    stage = models.ForeignKey(candidateStageModel, null=True, blank=True, on_delete=models.SET_NULL)

    job_description = models.ManyToManyField(jobModel, blank=True)
    recruiter_name = models.CharField(max_length=255, null=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'osms_candidates'
        verbose_name = "Candidate"
        verbose_name_plural = "Candidates"

    def __str__(self):
        return str(self.first_name) + ' ' + str(self.last_name) + '-' + str(self.id)

    objects = models.Manager()
    objects_custom = CandidateModelManager()

class candidateResumesModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # candidates = models.ForeignKey(Candidates, on_delete=models.CASCADE, blank=True, null=True)
    candidates = models.ForeignKey(Candidates, null=True, blank=True, on_delete=models.SET_NULL)
    job_title = models.CharField(max_length=255, null=True)
    candidate_resume_data = RichTextField(null=True, blank=True)
    notes = RichTextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidates_resumes'
        verbose_name = "Candidate Resumes"
        verbose_name_plural = 'Candidate Resumes'

    def __str__(self):
        return self.job_title


class emailTemplateModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    template_name = models.CharField(max_length=255, null=True, unique=True)
    subject = models.CharField(max_length=255, null=True)
    body = models.TextField(null=True)
    signature = models.TextField(null=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'osms_email_templates'
        verbose_name = "Email Template"
        verbose_name_plural = 'Email Templates'

    def __str__(self):
        return self.template_name


class mailModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    tag = models.CharField(max_length=255, null=True)
    email_from = models.CharField(max_length=255, null=True)
    email_to = models.TextField(null=True)
    cc_email = models.CharField(max_length=255, null=True, blank=True)
    bcc_email = models.CharField(max_length=255, null=True, blank=True)
    candidate_template = models.ForeignKey(emailTemplateModel, null=True, on_delete=models.SET_NULL)
    vendor_template = models.ForeignKey(vendorEmailTemplateModel, null=True, on_delete=models.SET_NULL)
    vendor_attachment = models.FileField(upload_to='vendors-mail-attachments/', null=True, blank=True)
    candidate_attachment = models.FileField(upload_to='candidate-mail-attachments/', null=True, blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidates_mail'
        verbose_name = "Mail"


class rtrModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    candidate_name = models.ForeignKey(Candidates, null=True, default=None, on_delete=models.SET_NULL)
    job_id = models.ForeignKey(jobModel, null=True, blank=True, on_delete=models.SET_NULL)
    job_title = models.CharField(max_length=255, null=True)
    rate = models.CharField(max_length=255, null=True)
    consultant_full_legal_name = models.CharField(max_length=255, null=True)
    address = models.TextField(null=True, blank=True)
    last_4_ssn = models.CharField(max_length=255, null=True, blank=True)
    phone_no = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    rtr_doc = models.FileField(upload_to='rtrs/', null=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidates_rtr'
        verbose_name = "RTR"
        verbose_name_plural = 'RTR'


class rtrmailModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email_from = models.CharField(max_length=255, null=True)
    email_to = models.CharField(null=True, max_length=255)
    cc_email = models.CharField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=255, null=True)
    body = models.TextField(null=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rtr_mails'
        verbose_name = "RTR Mail"


class activityStatusModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    candidate_name = models.ForeignKey(Candidates, null=True, on_delete=models.SET_NULL)
    job_id = models.ForeignKey(jobModel, null=True, on_delete=models.SET_NULL)
    activity_status = models.CharField(max_length=255, null=True)
    notes = RichTextField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidates_activity_status'
        verbose_name = "Activity Status"
        verbose_name_plural = 'Candidates Activity Status'


class candidatesSubmissionModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    candidate_name = models.ForeignKey(Candidates, null=True, on_delete=models.SET_NULL)
    client_name = models.ForeignKey(clientModel, null=True, on_delete=models.SET_NULL)
    email_from = models.CharField(max_length=255, null=True)
    client_email = models.CharField(max_length=255, null=True)
    email_cc = models.CharField(max_length=255, null=True, blank=True)
    email_subject = models.CharField(max_length=255, null=True)
    email_body = models.TextField(null=True, blank=True)
    email_attachment = models.FileField(null=True, upload_to='submission-attachments/')
    recruiter_name = models.CharField(max_length=255, null=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidates_submission'
        verbose_name = "Submission"
        verbose_name_plural = 'Candidates Submissions'


class placementCardModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    candidate_name = models.ForeignKey(Candidates, null=True, on_delete=models.SET_NULL)
    job_id = models.ForeignKey(jobModel, null=True, blank=True, on_delete=models.SET_NULL)
    client_name = models.ForeignKey(clientModel, null=True, on_delete=models.SET_NULL)
    reminder_date = models.DateField(null=True)
    payment_amount = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True)
    remarks = models.TextField(null=True, blank=True)
    recruiter_name = models.CharField(max_length=255, null=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidates_placement_cards'
        verbose_name = "Placement Card"
        verbose_name_plural = 'Placement Cards'


class searchTermModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    search_term = models.TextField(max_length=255, null=True)
    search_date = models.CharField(max_length=255, null=True)
    user_name = models.CharField(max_length=255, null=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidates_search_terms'


class importFileModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    module = models.CharField(max_length=255, null=True)
    file = models.FileField(upload_to='imported-files/', null=True)
    data_fields = models.TextField(null=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'osms_imported_files'


class candidatesJobDescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    candidate_name = models.ForeignKey(Candidates, null=True, on_delete=models.CASCADE)
    job_description = models.ForeignKey(jobModel, null=True, on_delete=models.CASCADE)
    stage = models.ForeignKey(candidateStageModel, null=True, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(null=True)
    send_out_date = models.DateTimeField(null=True, blank=True)
    notes = RichTextField(null=True, blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    submitted_by = models.ForeignKey('users.User', related_name='%(class)s_submitted_by', null=True, 
                                     blank=True, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidates_jobs_stages'

    """@property
    def submission_date(self):
        submission_date = self.submission_date
        logger.error('submission_date===========: ' + str(submission_date))

        return submission_date + ' ' + datetime.now().time()

    @property
    def send_out_date(self):
        send_out_date = self.send_out_date
        logger.error('send_out_date===========: ' + str(send_out_date))

        return send_out_date + ' ' + datetime.now().time()"""


class internalCandidatesJobDescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    candidate_name = models.ForeignKey(Candidates, null=True, on_delete=models.CASCADE)
    job_description = models.ForeignKey(jobModel, null=True, on_delete=models.CASCADE)
    stage = models.ForeignKey(candidateStageModel, null=True, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(null=True)
    send_out_date = models.DateTimeField(null=True, blank=True)
    notes = RichTextField(null=True, blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'internal_candidates_jobs_stages'


#candidate backup model

class CandidateModelBackup(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    date_of_birth = models.CharField(max_length=255, null=True, blank=True)
    primary_email = models.CharField(max_length=255, null=True, unique=True)
    secondary_email = models.CharField(max_length=255, null=True, blank=True)
    primary_phone_number = models.CharField(max_length=255, null=True)
    secondary_phone_number = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    designation = models.ForeignKey(designationModel, related_name='designation_backup', null=True, on_delete=models.SET_NULL)
    skills_1 = models.CharField(max_length=255, null=True, blank=True)
    skills_2 = models.CharField(max_length=255, null=True, blank=True)
    min_salary = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    min_rate = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    max_rate = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    qualification = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True)
    visa = models.CharField(max_length=255, null=True, blank=True)
    current_location = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    total_experience = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    reason_for_job_change = models.CharField(max_length=255, null=True, blank=True)
    rtr_done = models.CharField(max_length=255, null=True, blank=True)
    willing_to_work_on_our_w2 = models.CharField(max_length=255, null=True, blank=True)
    open_for_relocation = models.CharField(max_length=255, null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True, default=0)
    total_experience_in_usa = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    employer_phone_number = models.CharField(max_length=255, null=True, blank=True)
    employer_name = models.CharField(max_length=255, null=True, blank=True)
    employer_email = models.CharField(max_length=255, null=True, blank=True)
    engagement_type = models.CharField(max_length=255, null=True, blank=True)
    any_offer_in_hand = models.CharField(max_length=255, null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    resume_raw_data = RichTextField(null=True, blank=True)

    remarks = RichTextField(null=True, blank=True)
    certification = models.CharField(max_length=255, null=True)
    additional_qualification = models.CharField(max_length=255, null=True)

    stage = models.ForeignKey(candidateStageModel, null=True, blank=True, on_delete=models.SET_NULL)

    job_description = models.ManyToManyField(jobModel, blank=True)
    recruiter_name = models.CharField(max_length=255, null=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    candidate_refer_id = models.CharField(max_length=255, null=True)
    user_id = models.CharField(max_length=255, null=True)
    date_of_deletion = models.CharField(max_length=255, null=True)


    class Meta:
        db_table = 'osms_candidates_backup'
        verbose_name = "Candidate Backup"
        verbose_name_plural = "Candidates Backup"