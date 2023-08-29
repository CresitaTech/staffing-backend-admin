import uuid

from django.db import models

# Create your models here.


class OfferLettersModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    candidate_name = models.CharField(max_length=255, null=True)
    years_of_exp = models.IntegerField(null=True , blank=True)
    skill_set = models.CharField(max_length=255, null=True)
    contact_no = models.CharField(max_length=255, null=True , blank=True)
    email = models.CharField(max_length=255, null=True)
    date_of_birth = models.DateField(null=True)
    degree =  models.CharField(max_length=255 , null=True , blank=True)
    percentage = models.CharField(max_length=255 , null=True , blank=True)
    university_name = models.CharField(max_length=255 , null=True , blank=True)
    pan_no = models.CharField(max_length=255 , null=True , blank=True)
    qualification_completion = models.CharField(max_length=255, null=True)
    current_location = models.CharField(max_length=255, null=True , blank=True)
    tentative_joining_date = models.DateField(null=True)
    client_name = models.CharField(max_length=255, null=True , blank=True)
    client_location = models.CharField(max_length=255 , null=True , blank=True)
    ecms_id = models.CharField(max_length=255 , null=True , blank=True)
    candidate_ctc = models.CharField(max_length=255 , null=True , blank=True)
    client_rate = models.CharField(max_length=255 , null=True , blank=True)
    joining_date = models.DateField(null=True)
    contract_duration = models.CharField(max_length=255 , null=True , blank=True)
    expected_start_date = models.DateField(null=True)
    bgc_steps = models.CharField(max_length=255 , null=True , blank=True)
    expected_working_hours = models.CharField(max_length=255 , null=True , blank=True)
    laptop_provided = models.CharField(max_length=255 , null=True , blank=True)
    resume = models.FileField(null=True, upload_to='offerletter_candidate_resume-attachments/')
    offer_letter_pdf = models.FileField(upload_to='offer_letters/', null=True)
    provident_fund = models.BooleanField(default=False)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'osms_offerletters'
        verbose_name = "OfferLetters"
        verbose_name_plural = "OfferLetters List"

    def __str__(self):
        return str(self.candidate_name)