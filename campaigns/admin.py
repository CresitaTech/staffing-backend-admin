from django.contrib import admin

# Register your models here.
from django.utils.log import AdminEmailHandler
from campaigns.tasks import report_error_task


class CeleryHandler(AdminEmailHandler):

    def send_mail(self, subject, message, *args, **kwargs):
        report_error_task().delay(subject, message, *args, **kwargs)