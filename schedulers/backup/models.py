import uuid

from django.db import models
# Create your models here.
from vendors.models import vendorEmailTemplateModel
from ckeditor.fields import RichTextField


class CampaignUploadDataModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    list_name = models.CharField(max_length=255 , unique=True , null=True)
    list_size = models.CharField(max_length=255 , null=True , blank=True)
    list_description = models.CharField(max_length=255 , null= True , blank=True)
    template_name = models.ForeignKey(vendorEmailTemplateModel, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length= 255 , null=True , blank=True)
    upload_file = models.FileField(upload_to='campaign_data/', null=True, blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaign_upload_data'


class CampaignListDataModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    campaign_name = models.ForeignKey(CampaignUploadDataModel, null=True, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255 , null=True , blank=True)
    email = models.CharField(max_length=255 , null= True , blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaign_list_data'


"""class sendCleanDataModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False, unique=True)
    send = models.CharField(max_length=255, null=True, blank=True)
    delivered = models.CharField(max_length=255, null=True, blank=True)
    marked_as_spam = models.CharField(max_length=255, null=True, blank=True)
    soft_bounced = models.CharField(max_length=255, null=True, blank=True)
    hard_bounced = models.CharField(max_length=255, null=True, blank=True)
    opened = models.CharField(max_length=255, null=True, blank=True)
    clicked = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'send_clean_dashboard'"""


class sendCleanRequestDataModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False, unique=True)
    record_id = models.CharField(max_length=255, null=True, blank=True)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    smtp_name = models.CharField(max_length=255, null=True, blank=True)
    x_unique_id = models.CharField(max_length=255, null=True, blank=True)
    ts = models.CharField(max_length=255, null=True, blank=True)
    msg = RichTextField(null=True, blank=True)
    sarvtes_events = RichTextField(null=True, blank=True)
    event = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'send_clean_request_data'