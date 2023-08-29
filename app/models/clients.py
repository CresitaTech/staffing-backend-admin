import uuid

from django.db import models
from ckeditor.fields import RichTextField

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
