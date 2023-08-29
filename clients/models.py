import uuid

from django.db import models
from ckeditor.fields import RichTextField


class ClientModelManager(models.Manager):
    def backup_clients(self, obj):
        ClientModelBackup.objects.create(
            first_name=obj.first_name,
            last_name=obj.last_name,
            primary_email=obj.primary_email,
            secondary_email=obj.secondary_email,
            primary_phone_number=obj.primary_phone_number,
            secondary_phone_number=obj.secondary_phone_number,
            skype_id=obj.skype_id,
            linkedin_id=obj.linkedin_id,
            primary_skills=obj.primary_skills,
            secondary_skills=obj.secondary_skills,
            company_name=obj.company_name,
            company_tin_number=obj.company_tin_number,
            company_address=obj.company_address,
            total_employee=obj.total_employee,
            about_company=obj.about_company,
            country=obj.country,
            rank=obj.rank,
            created_by=obj.created_by,
            updated_by=obj.updated_by,
            created_at=obj.created_at,
            updated_at=obj.updated_at
        )
        obj.delete()

# Create your models here.
class clientModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    primary_email = models.CharField(max_length=255, null=True)
    secondary_email = models.CharField(max_length=255, null=True , blank=True)
    primary_phone_number = models.CharField(max_length=255, null=True)
    secondary_phone_number = models.CharField(max_length=255, null=True , blank=True )
    skype_id =  models.CharField(max_length=255 , null=True , blank=True)
    linkedin_id = models.CharField(max_length=255 , null=True , blank=True)
    primary_skills = models.CharField(max_length=255 , null=True , blank=True)
    secondary_skills = models.CharField(max_length=255 , null=True , blank=True)
    company_name = models.CharField(max_length=255, null=True)
    company_tin_number = models.CharField(max_length=255, null=True , blank=True)
    total_employee = models.IntegerField(null=True , blank=True)
    company_address = models.CharField(max_length=255, null=True , blank=True)
    about_company = RichTextField(null=True , blank=True)
    country = models.CharField(max_length=255 , null=True , blank=True)
    rank = models.IntegerField(null=True, blank=True, default=0)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'osms_clients'
        verbose_name = "Client"
        verbose_name_plural = "Clients List"

    def __str__(self):
        return str(self.company_name)
    
    objects = ClientModelManager()
    

class ClientModelBackup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    primary_email = models.CharField(max_length=255, null=True)
    secondary_email = models.CharField(max_length=255, null=True , blank=True)
    primary_phone_number = models.CharField(max_length=255, null=True)
    secondary_phone_number = models.CharField(max_length=255, null=True , blank=True )
    skype_id =  models.CharField(max_length=255 , null=True , blank=True)
    linkedin_id = models.CharField(max_length=255 , null=True , blank=True)
    primary_skills = models.CharField(max_length=255 , null=True , blank=True)
    secondary_skills = models.CharField(max_length=255 , null=True , blank=True)
    company_name = models.CharField(max_length=255, null=True)
    company_tin_number = models.CharField(max_length=255, null=True , blank=True)
    total_employee = models.IntegerField(null=True , blank=True)
    company_address = models.CharField(max_length=255, null=True , blank=True)
    about_company = RichTextField(null=True , blank=True)
    country = models.CharField(max_length=255 , null=True , blank=True)
    rank = models.IntegerField(null=True, blank=True, default=0)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'osms_clients_backup'
        verbose_name = "Client BackUp"
        verbose_name_plural = "Clients List BackUp"
