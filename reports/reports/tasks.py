from datetime import datetime

from django.core.management import call_command
from django.utils import timezone
from celery import shared_task
import logging

from reports.views import send_bdm_email, send_recruiter_email, send_weeklly_recuiter_performance_report, \
    send_weekly_recruiter_submission, \
    send_weekly_bdm_jobs
from staffingapp import settings

logger = logging.getLogger(__name__)


@shared_task(name="test_beat_task")
def test_beat_task():
    now = timezone.now()
    date_and_time = now.strftime("%Y-%m-%d, %H:%M:%S")
    logger.info(f"Celery beat is alive, it is currently {date_and_time} UTC")
    return 'Celery beat is alive, it is currently '+date_and_time+' UTC'


@shared_task(name="database_daily_backup")
def database_daily_backup():
    if settings.DEBUG is True:
        return f"Could not be backed up: Debug is True"
    else:
        try:
            call_command("dbbackup")
            return f"Backed up successfully: {datetime.now()}"
        except:
            return f"Could not be backed up: {datetime.now()}"



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


# recruiter submission summary report weekly
@shared_task(name="send_weekly_recruiter_submission_for_india")
def send_weekly_recruiter_submission_for_india():
    response = send_weekly_recruiter_submission('India')
    logger.info('weekly recruiter performance report successfully generated')
    return response


@shared_task(name="send_weekly_recruiter_submission_for_us")
def send_weekly_recruiter_submission_for_us():
    response = send_weekly_recruiter_submission('US')
    logger.info('weekly recruiter performance report successfully generated')
    return response

# send weekly job performance report
@shared_task(name="send_weekly_bdm_jobs_report_for_indian_bdm")
def send_weekly_bdm_jobs_report_for_indian_bdm():
    response = send_weekly_bdm_jobs('India')
    logger.info('weekly recruiter performance report successfully generated')
    return response


@shared_task(name="send_weekly_bdm_jobs_report_for_us_bdm")
def send_weekly_bdm_jobs_report_for_us_bdm():
    response = send_weekly_bdm_jobs('US')
    logger.info('daily recruiter performance report successfully generated')
    return response
