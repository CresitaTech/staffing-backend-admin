import uuid

from django.db import models

# Create your models here.
from django.db import models
from ckeditor.fields import RichTextField
from candidates.models import Candidates
from interviewers.models import interviewersModel
from interviewers.models import timeslotsModel
from jobdescriptions.models import jobModel


class sourceModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    source = models.CharField(max_length=255 , null=True)
    remarks = models.TextField(null=True , blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interview_source'
        verbose_name = "Interview Mode"
        verbose_name_plural = "Interview Modes"

    def __str__(self):
        return self.source


class Mails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(null=True)
    condidate_email = models.EmailField(null=True)
    from_email = models.CharField(max_length=1000, null=True)
    subject = models.CharField(max_length=1000, null=True)
    message = models.TextField(null=True)
    resume = models.CharField(max_length=1000, null=True)
    jd = models.TextField(null=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)

    def Mails(self):
        return self


class ZoomObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    zoom_username = models.EmailField(null=True)
    zoom_password = models.CharField(max_length=1000, null=True)
    zoom_api_key = models.CharField(max_length=1000, null=True)
    zoom_api_secret = models.CharField(max_length=1000, null=True)
    zoom_token = models.TextField(null=True)
    meeting_topic = models.CharField(max_length=1000, null=True)
    meeting_agenda = models.TextField(null=True)
    meeting_time = models.DateField(null=True)
    meeting_time_zone = models.CharField(max_length=1000, null=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)


class interviewsModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    candidate_name = models.ForeignKey(Candidates, null=True , on_delete=models.SET_NULL)
    interviewer_name = models.ForeignKey(interviewersModel, null=True , on_delete=models.SET_NULL)
    time_slot = models.ForeignKey(timeslotsModel, null=True , on_delete=models.SET_NULL)
    time_zone = models.CharField(max_length=255 , null=True)
    meeting_time = models.DateField(null=True)
    source = models.ForeignKey(sourceModel , null=True , on_delete=models.SET_NULL)
    jd_attachment = models.ForeignKey(jobModel , null=True , on_delete=models.SET_NULL)
    status = models.CharField(max_length=255,default='New')
    remarks = RichTextField(null=True , blank=True)
    recruiter_name = models.CharField(max_length=255 , null=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'osms_interviews'
        verbose_name = "Interview"
        verbose_name_plural = "Interviews"

    def __str__(self):
        return str(self.candidate_name) + '-' + str(self.pk)

class feedbackModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    interview = models.ForeignKey(interviewsModel ,null=True , on_delete=models.SET_NULL)
    candidate_name = models.ForeignKey(Candidates , null=True , on_delete=models.SET_NULL)
    interview_date = models.DateField(null=True)
    time_slot = models.ForeignKey(timeslotsModel ,null=True , on_delete=models.SET_NULL)
    duration = models.CharField( max_length=255, null=True)
    forwarded = models.CharField( max_length=255, null=True)
    mail_from = models.CharField( max_length=255, null=True)
    mail_to = models.CharField( max_length=255, null=True)
    mail_subject = models.CharField( max_length=255, null=True)
    mail_cc = models.CharField( max_length=400, null=True , blank=True)
    feedback = RichTextField(null=True)
    attachment = models.FileField(null=True , blank=True , upload_to='feedback-attachments/')
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'osms_interviews_feedbacks'
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"