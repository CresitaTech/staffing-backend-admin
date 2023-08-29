import uuid
from django.db import models


# Create your models here.
class ParserModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    job_title = models.CharField(max_length=255)
    resume = models.FileField(upload_to='parsers/', null=True, blank=True)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'osms_parsers'
        verbose_name = "Parsers"
        verbose_name_plural = "Parsers"

