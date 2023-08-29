from datetime import datetime

import requests
from django.core.mail import mail_admins
from django.utils import timezone
from celery import shared_task
import logging
from django.conf import settings
from django.core.management import call_command

from vendors.models import EmailModel, emailConfigurationModel

logger = logging.getLogger(__name__)


@shared_task
def report_error_task(subject, message, *args, **kwargs):
    mail_admins(subject, message, *args, **kwargs)


@shared_task
def backup():
    if settings.DEBUG is True:
        return f"Could not be backed up: Debug is True"
    else:
        try:
            call_command("dbbackup")
            return f"Backed up successfully: {datetime.datetime.now()}"
        except:
            return f"Could not be backed up: {datetime.datetime.now()}"


@shared_task(name="send_mass_email")
def send_mass_email():
    try:
        logger.info('Mail Sending Started................: ')
        queue_data = EmailModel.objects.filter(status=False).order_by('id')[:1]
        if queue_data.exists():
            for email_object in queue_data:
                headers = {'Content-Type': 'application/json',
                           'X-Server-API-Key': 'WW05O9S9jzKgSsEOJMZyLPun'}
                url = "https://mail.opallius.com/api/v1/send/message"

                email_object_str = getattr(email_object, 'message')
                email_object_replace1 = email_object_str.replace("<p>", "<div>")
                email_object_replace2 = email_object_replace1.replace("</p>", "</div>")

                postdata = {
                    "html_body": email_object_replace2,
                    "subject": getattr(email_object, 'subject'),
                    "from": getattr(email_object, 'email_from'),
                    "to": [getattr(email_object, 'email_to')],
                    "cc": [getattr(email_object, 'email_cc')]
                }
                logger.info('Sending Mail Object: ' + str(email_object))
                EmailModel.objects.filter(id=getattr(email_object, 'id')).update(status=True)

                response = requests.post(url, json=postdata, headers=headers, verify=False)
                logger.info('response.status_code: ' + str(response.status_code))
                logger.info('response.text: ' + str(response.text))
            return str("Email Successfully Sent")
        else:
            return str("Data Not Found")
    except Exception as e:
        return str("Email Sent Failed: " + str(e))

