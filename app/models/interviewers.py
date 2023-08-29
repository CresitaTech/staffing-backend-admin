import uuid

from django.db import models

# Create your models here.
class designationModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, null=True)
    remark = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interviewers_designation'
        verbose_name = "Designation"
        verbose_name_plural = "Designations"

    def __str__(self):
        return self.name


class timeslotsModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    time_slot = models.CharField(max_length=255 , null=True)
    remarks = models.TextField(max_length=255 ,null = True , blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interviewers_time_slots'
        verbose_name = "Time Slot"
        verbose_name_plural = "Time Slots"

    def __str__(self):
        return self.time_slot


class interviewersModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    designation = models.ForeignKey(designationModel, null=True, on_delete=models.SET_NULL)
    zoom_username = models.CharField(max_length=255, null=True)
    zoom_password = models.CharField(max_length=255, null=True)
    zoom_api_key = models.CharField(max_length=255, null=True)
    zoom_api_secret = models.CharField(max_length=255, null=True)
    zoom_token = models.TextField(null=True)
    primary_email = models.CharField (max_length=255 , null= True)
    secondary_email = models.CharField(max_length=255 , null=True , blank=True)
    phone_number = models.CharField(max_length=255, null=True , blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'osms_interviewers'
        verbose_name = "Interviewer"
        verbose_name_plural = "Interviewers List"

    def __str__(self):
        return self.first_name