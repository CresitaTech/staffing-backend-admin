import uuid

from django.db import models
from ckeditor.fields import RichTextField
from clients.models import clientModel
from datetime import datetime
# Create your models here.

def create_id():
    today_date = datetime.today().strftime('%Y%m%d')
    if jobModel.objects.count() != 0:
        last_inserted_id = jobModel.objects.latest('id').id
        latest_id = last_inserted_id + 1
        if (last_inserted_id):
            return 'OP-JDID' +str(today_date) +str(latest_id).zfill(2)
        else:
            return 'OP-JDID' +str(today_date) +'01'
    else:
        return 'OP-JDID' +str(today_date) +'01'


class jobModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    job_id = models.CharField(max_length=255 , default=create_id,  null=True)
    client_name = models.ForeignKey(clientModel , null=True , on_delete=models.SET_NULL)
    end_client_name = models.CharField(max_length=255, null=True , blank=True)
    priority = models.BooleanField(null=True , blank=True)
    industry_experience = models.CharField(max_length=255, null=True , blank=True)
    nice_to_have_skills = models.CharField(max_length=255, null=True , blank=True)
    job_title = models.CharField(max_length=255)
    job_description = RichTextField(null=True ,  blank=True)
    job_pdf = models.FileField(upload_to='jds/', null=True)
    job_recruiter_pdf = models.FileField(upload_to='jds-recruiters/', null=True)
    visa_type = models.CharField(max_length=255, null=True , blank=True)
    no_of_requests = models.IntegerField(null=True , blank=True)
    roles_and_responsibilities = RichTextField(null=True , blank=True)
    min_years_of_experience = models.DecimalField(max_digits=50, decimal_places=2, null=True , blank=True)
    max_years_of_experience = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    key_skills = models.CharField(max_length=255, null=True , blank=True)
    education_qualificaion = models.CharField(max_length=255, null=True , blank=True)
    start_date = models.DateField(null=True , blank=True)
    employment_type = models.CharField(max_length=255, null=True , blank=True)
    employment_type_description = RichTextField(null=True ,  blank=True)
    contract_duration = models.CharField(max_length=255, null=True ,blank=True)
    location = models.CharField(max_length=255, null=True ,blank=True)
    min_salary = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    max_rate = models.DecimalField(max_digits=50, decimal_places=2, null=True , blank=True)
    min_rate = models.DecimalField(max_digits=50, decimal_places=2, null=True , blank=True)
    min_client_rate = models.DecimalField(max_digits=50, decimal_places=2, null=True , blank=True)
    max_client_rate = models.DecimalField(max_digits=50, decimal_places=2, null=True , blank=True)
    key_fields = models.CharField(max_length=255, null=True , blank=True)
    status = models.CharField(max_length=255 , null=True , blank=True)
    country = models.CharField(max_length=255 , null=True , blank=True)
    projected_revenue = models.DecimalField(max_digits=50, decimal_places=2, null=True , blank=True)
    default_assignee = models.ForeignKey('users.User', related_name='default_assignee', null=True,
                                          on_delete=models.SET_NULL)
    revenue_frequency = models.CharField(max_length=255, null=True , blank=True)
    job_posted_date = models.DateField(null=True , blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True, on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'osms_job_description'
        verbose_name = "Job Description"
        verbose_name_plural = "Job Descriptions"
        get_latest_by = ['id']

    def __str__(self):
        return str(self.client_name) + '-' +str(self.job_title)

    objects = models.Manager()


class jobAssingmentModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    primary_recruiter_name = models.ForeignKey('users.User', null=True , related_name='assinged_primary_recruiter' ,on_delete=models.SET_NULL)
    primary_recruiter_email = models.CharField(max_length=255, null=True)
    secondary_recruiter_name = models.ForeignKey('users.User',related_name='assinged_secondary_recruiter' ,null=True , on_delete=models.SET_NULL)
    secondary_recruiter_email = models.CharField(max_length=255, null=True , blank=True)
    assignee_name = models.CharField(max_length=255, null=True)
    assignee_email = models.CharField(max_length=255, null=True)
    job_id = models.ForeignKey(jobModel , null=True , on_delete=models.SET_NULL)
    remarks = RichTextField(null=True ,  blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True, on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_description_assingment'
        verbose_name = "Job Description Assingment"
        verbose_name_plural = "Assingment List"

    objects = models.Manager()


class jobSubmissionModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    candidate_name = models.ForeignKey('candidates.Candidates' , null=True , on_delete=models.SET_NULL)
    recruiter_name = models.ForeignKey('users.User',related_name='submitted_recruiter' ,null=True , on_delete=models.SET_NULL)
    recruiter_email = models.CharField(max_length=255, null=True)
    assignee_name = models.CharField(max_length=255, null=True)
    assignee_email = models.CharField(max_length=255, null=True)
    remarks = RichTextField(null=True , blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True, on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_description_submission'
        verbose_name = "Job Description Submission"
        verbose_name_plural = "Submission List"

    objects = models.Manager()