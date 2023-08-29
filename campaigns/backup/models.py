import uuid

from django.db import models
# Create your models here
from ckeditor.fields import RichTextField

from vendors.models import vendorEmailTemplateModel, VendorListModel


class CampaignListModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    list_name = models.CharField(max_length=255 , unique=True , null=True)
    list_size = models.CharField(max_length=255 , null=True , blank=True)
    list_description = models.CharField(max_length=255 , null= True , blank=True)
    status = models.CharField(max_length= 255 , null=True , blank=True)
    data_type = models.CharField(max_length=255, null=True, blank=True)
    upload_file = models.FileField(upload_to='campaign_lists/', null=True, blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaign_lists'


class CampaignListUploadDataModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=255 , null=True, blank=True)
    last_name = models.CharField(max_length=255 , null=True , blank=True)
    email = models.CharField(max_length=255 , null= True , blank=True)
    list_name = models.ForeignKey(CampaignListModel, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaign_lists_upload_data'


class CampaignListDataModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    list_name = models.ForeignKey(CampaignListModel, on_delete=models.CASCADE, blank=True, null=True)
    record_id = models.CharField(max_length=255 , null=True , blank=True)
    data_type = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaign_lists_data'


class CampaignModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    campaign_name = models.CharField(max_length=255 , unique=True , null=True)
    campaign_description = models.CharField(max_length=255 , null= True , blank=True)
    list_name = models.ForeignKey(CampaignListModel, on_delete=models.CASCADE, blank=True, null=True)
    template_name = models.ForeignKey(vendorEmailTemplateModel, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length= 255 , null=True , blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaigns'


class CampaignListMappingDataModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    list_name = models.ForeignKey(VendorListModel, on_delete=models.CASCADE, blank=True, null=True)
    template_name = models.ForeignKey(vendorEmailTemplateModel, on_delete=models.CASCADE, blank=True, null=True)
    campaign_name = models.ForeignKey(CampaignModel, on_delete=models.CASCADE, blank=True, null=True)
    record_id = models.CharField(max_length=255, null=True, blank=True)
    email_body = models.TextField(null=True, blank=True)
    email_subject = models.TextField(null=True, blank=True)
    email_to = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaign_lists_mapping_data'

    objects = models.Manager()


class CustomFieldsModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    field_name = models.CharField(max_length=255 , null=False, blank=False)
    field_type = models.CharField(max_length=255 , null=False , blank=False)
    field_size = models.CharField(max_length=255 , null= False , blank=False)
    field_desc = models.CharField(max_length=255 , null= True , blank=True)
    field_scope = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'custom_fields'