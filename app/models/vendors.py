import uuid

from django.db import models

# Create your models here.

class vendorModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    contact_person_first_name = models.CharField(max_length=255)
    contact_person_last_name = models.CharField(max_length=255 , null=True , blank=True)
    designation = models.CharField(max_length=255 , null=True , blank=True)
    primary_email = models.CharField(max_length=255)
    alternate_email = models.CharField(max_length=255, null=True , blank=True)
    phone_number = models.CharField(max_length=255 , null=True , blank=True)
    company_name = models.CharField(max_length=255, null=True , blank=True)
    company_address = models.CharField(max_length=255, null=True , blank=True)
    specialised_in = models.CharField(max_length=255 , null=True , blank=True)
    about_company = models.TextField(null=True , blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'osms_vendors'
        verbose_name = "Vendor"
        verbose_name_plural = "Vendors"


class vendorEmailTemplateModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    template_name = models.CharField(max_length=255, null=True , unique=True)
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
        db_table = 'osms_vendor_templates'
        verbose_name = "Email Template"
        verbose_name_plural = 'Email Templates'

    def __str__(self):
        return self.template_name


class vendorMailModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email_from = models.CharField(max_length=255 , null=True)
    email_to = models.TextField(null=True)
    cc_email = models.CharField(max_length=255 , null=True , blank=True)
    bcc_email = models.CharField(max_length=255 , null=True , blank=True)
    template = models.ForeignKey(vendorEmailTemplateModel ,null=True , on_delete=models.SET_NULL)
    attachment = models.FileField(upload_to='vendors-attachments/' , null=True , blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True , null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendors_mail'
        verbose_name = "Mail"
        
class emailConfigurationModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=255 , null=True , blank=True)
    last_name = models.CharField(max_length=255 , null=True , blank=True)
    host_name = models.CharField(max_length=255 , null=True , blank=True)
    email = models.CharField(max_length=255 , null=True , blank=True)
    email_cc = models.TextField(null=True , blank=True)
    send_by = models.CharField(max_length=255 , null=True , blank=True)
    password = models.CharField(max_length=255 , null=True , blank=True)
    port = models.CharField(max_length=255 , null=True , blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'osms_email_configurations'
        
class VendorListModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    list_name = models.CharField(max_length=255 , unique=True , null=True)
    template_name = models.ForeignKey(vendorEmailTemplateModel , on_delete=models.CASCADE , blank=True, null=True)
    list_size = models.CharField(max_length=255 , null=True , blank=True)
    list_description = models.CharField(max_length=255 , null= True , blank=True)
    status = models.CharField(max_length= 255 , null=True , blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendor_lists'
        
    objects = models.Manager()

class VendorListDataModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    list = models.ForeignKey(VendorListModel , on_delete=models.CASCADE , blank=True, null=True)
    template = models.ForeignKey(vendorEmailTemplateModel , on_delete=models.CASCADE , blank=True, null=True)
    vendor = models.ForeignKey(vendorModel , on_delete=models.CASCADE ,blank=True, null=True)
    email_body = models.TextField(null=True , blank=True)
    email_subject = models.TextField(null=True, blank=True)
    email_to = models.CharField(max_length=255 , null= True , blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendor_list_data'
        
    objects = models.Manager()
    
class MailEventsModel(models.Model):
    maildata = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mail_events'
    

