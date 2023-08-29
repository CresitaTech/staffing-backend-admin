from django.utils import timezone
from celery import shared_task
import logging
from celery.signals import task_failure
from django.core.mail import mail_admins
import socket

from reports.views import send_bdm_email, send_recruiter_email, send_weeklly_recuiter_performance_report, \
    send_daily_recuiter_performance_report, send_weekend_bdm_email

logger = logging.getLogger(__name__)


@shared_task(name="test_beat_task")
def test_beat_task():
    now = timezone.now()
    date_and_time = now.strftime("%Y-%m-%d, %H:%M:%S")
    logger.info(f"Celery beat is alive, it is currently {date_and_time} UTC")
    return 'Celery beat is alive, it is currently '+date_and_time+' UTC'


@task_failure.connect()
def celery_task_failure_email(**kwargs):
    """ celery 4.0 onward has no method to send emails on failed tasks
    so this event handler is intended to replace it
    """

    subject = "[Django][{queue_name}@{host}] Error: Task {sender.name} ({task_id}): {exception}".format(
        queue_name="celery",  # `sender.queue` doesn't exist in 4.1?
        host=socket.gethostname(),
        **kwargs
    )

    message = """Task {sender.name} with id {task_id} raised exception:
    {exception!r}
    
    Task was called with args: {args} kwargs: {kwargs}.
    
    The contents of the full traceback was:
    
    {einfo}
    """.format(
        **kwargs
    )

    mail_admins(subject, message)


@shared_task(name="generate_daily_submission_report_for_indian_recruiter")
def generate_daily_submission_report_for_indian_recruiter():
    response = send_recruiter_email('India')
    logger.info('Sales forecast bar graph successfully generated')
    return response


@shared_task(name="generate_daily_job_report_for_indian_bdm")
def generate_daily_job_report_for_indian_bdm():
    response = send_bdm_email('India')
    logger.info('Sales forecast bar graph successfully generated')
    return response


@shared_task(name="generate_daily_submission_report_for_us_recruiter")
def generate_daily_submission_report_for_us_recruiter():
    response = send_recruiter_email('US')
    logger.info('Sales forecast bar graph successfully generated')
    return response


@shared_task(name="generate_daily_job_report_for_us_bdm")
def generate_daily_job_report_for_us_bdm():
    response = send_bdm_email('US')
    logger.info('Sales forecast bar graph successfully generated')
    return response

# send weekly job performance report
@shared_task(name="send_weekly_bdm_job_report_for_indian_bdm")
def send_weekly_bdm_job_report_for_indian_bdm():
    response = send_weekend_bdm_email('India')
    logger.info('weekly recruiter performance report successfully generated')
    return response


@shared_task(name="send_weekly_bdm_job_report_for_us_bdm")
def send_weekly_bdm_job_report_for_us_bdm():
    response = send_weekend_bdm_email('US')
    logger.info('daily recruiter performance report successfully generated')
    return response


# weekly report
@shared_task(name="send_weekly_recuiter_performance_report_for_indian_bdm")
def send_weekly_recuiter_performance_report_for_indian_bdm():
    response = send_weeklly_recuiter_performance_report('India')
    logger.info('weekly recruiter performance report successfully generated')
    return response


@shared_task(name="send_weekly_recuiter_performance_report_for_us_bdm")
def send_weekly_recuiter_performance_report_for_us_bdm():
    response = send_weeklly_recuiter_performance_report('US')
    logger.info('weekly recruiter performance report successfully generated')
    return response
