import uuid

from django.db import models
# Create your models here.
from candidates.models import Candidates

def content_resume(instance, filename):
    if instance.resume:
        return 'candidates-documentery/resume/{0}'.format(str(instance.candidate_name)+str(instance.candidate_name_id)+filename)

def content_driving_license(instance, filename):
    if instance.driving_license:
        return 'candidates-documentery/driving-license/{0}'.format(str(instance.candidate_name)+str(instance.candidate_name_id)+filename)

def content_offer_letter(instance, filename):
    if instance.offer_letter:
        return 'candidates-documentery/offer-letter/{0}'.format(str(instance.candidate_name)+str(instance.candidate_name_id)+filename)

def content_passport(instance, filename):
    if instance.passport:
        return 'candidates-documentery/passport/{0}'.format(str(instance.candidate_name)+str(instance.candidate_name_id)+filename)

def content_rtr(instance, filename):
    if instance.rtr:
        return 'candidates-documentery/rtr/{0}'.format(str(instance.candidate_name)+str(instance.candidate_name_id)+filename)

def content_salary_slip(instance, filename):
    if instance.salary_slip:
        return 'candidates-documentery/salary-slip/{0}'.format(str(instance.candidate_name)+str(instance.candidate_name_id)+filename)
        
def content_i94_document(instance, filename):
    if instance.i94_document:
        return 'candidates-documentery/i94-document/{0}'.format(str(instance.candidate_name)+str(instance.candidate_name_id)+filename)

def content_visa_copy(instance, filename):
    if instance.visa_copy:
        return 'candidates-documentery/visa-copy/{0}'.format(str(instance.candidate_name)+str(instance.candidate_name_id)+filename)

def content_educational_document(instance, filename):
    if instance.educational_document:
        return 'candidates-documentery/educational-document/{0}'.format(str(instance.candidate_name)+str(instance.candidate_name_id)+filename)

def content_certification_doc(instance, filename):
    if instance.certification_doc:
        return 'candidates-documentery/certification-document/{0}'.format(str(instance.candidate_name)+str(instance.candidate_name_id)+filename)

def content_additional_qualification_doc(instance, filename):
    if instance.additional_qualification_doc:
        return 'candidates-documentery/additional-qualification-document/{0}'.format(str(instance.candidate_name)+str(instance.candidate_name_id)+filename)


class candidatesRepositeryModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    repo_name = models.CharField(max_length=255, null= True)
    candidate_name = models.ForeignKey(Candidates, null=True, on_delete=models.CASCADE)
    resume = models.FileField(upload_to=content_resume , null=True , blank=True)
    driving_license = models.FileField(upload_to=content_driving_license , null=True , blank=True)
    offer_letter = models.FileField(upload_to=content_offer_letter, null=True , blank=True)
    passport = models.FileField(upload_to=content_passport, null=True , blank=True)
    rtr = models.FileField(upload_to=content_rtr, null=True , blank=True)
    salary_slip = models.FileField(upload_to=content_salary_slip, null=True ,blank=True)
    i94_document = models.FileField(upload_to=content_i94_document, null=True ,blank=True)
    visa_copy = models.FileField(upload_to=content_visa_copy, null=True ,blank=True)
    educational_document = models.FileField(upload_to=content_educational_document, null=True ,blank=True)
    certification_doc = models.FileField(upload_to=content_certification_doc, null=True, blank=True)
    additional_qualification_doc = models.FileField(upload_to=content_additional_qualification_doc, null=True,
                                                    blank=True)
    description = models.TextField(null=True , blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'osms_candidates_repositery'
        verbose_name = "Candidate Repositery"
        verbose_name_plural = "Candidates Repositeries"