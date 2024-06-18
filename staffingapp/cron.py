from datetime import datetime

import sys
from django.utils import timezone
import logging
from django.core.management import call_command

from schedulers.views import parse_recruiter_calls_data
from staffingapp import settings

from comman_utils.utils import get_current_day_start_and_end_datetime, get_weekly_report_start_and_end_datetime
from reports.views import send_recruiter_email, send_bdm_email, send_weeklly_recuiter_performance_report, \
    send_weekly_recruiter_submission, send_weekly_bdm_jobs, send_recruiter_summary_report, send_last_48hours_bdm_jobs, \
    bdm_daily_submission_report, send_weekly_recruiter_submission_follow_up, send_weekly_bdm_jobs_summary, \
    send_daily_bdm_jobs_summary

logger = logging.getLogger(__name__)


def heartbeat_check(*args, **options):
    now = timezone.now()
    """start_date, end_date = get_current_day_start_and_end_datetime()
    logger.info("get_current_day_start_and_end_datetime : " + str(start_date) + ' - ' + str(end_date) )
    start_date, end_date = get_weekly_report_start_and_end_datetime(args[0])
    logger.info("get_weekly_report_start_and_end_datetime : " + str(start_date) + ' - ' + str(end_date))

    logger.info("IsProd received: " + str(args[1]) )
    logger.info("Arg received: " + str(options))"""

    date_and_time = now.strftime("%Y-%m-%d, %H:%M:%S")
    logger.info(f"Celery beat is alive, it is currently {date_and_time} UTC")
    return 'Celery beat is alive, it is currently ' + date_and_time + ' UTC'


def database_daily_backup():
    if settings.DEBUG is True:
        return f"Could not be backed up: Debug is True"
    else:
        try:
            call_command("dbbackup")
            return f"Backed up successfully: {datetime.now()}"
        except:
            return f"Could not be backed up: {datetime.now()}"


def generate_daily_submission_report_for_recruiter(*args, **options):
    response = send_recruiter_email(args[0], args[1])
    logger.info('send_recruiter_email successfully generated ===========> ')
    return response


def generate_daily_job_report_for_bdm(*args, **options):
    response = send_bdm_email(args[0], args[1])
    logger.info('send_bdm_email successfully generated ===========> ')
    return response


def generate_daily__recruiter_summary_report(*args, **options):
    response = send_recruiter_summary_report(args[0], args[1])
    logger.info('send_recruiter_summary_report successfully generated ===========> ')
    return response


def generate_bdm_daily_submission_report(*args, **options):
    response = bdm_daily_submission_report(args[0], args[1])
    logger.info('bdm_daily_submission_report successfully generated ===========> ')
    return response


def generate_send_weekly_recruiter_submission_follow_up(*args, **options):
    response = send_weekly_recruiter_submission_follow_up(args[0], args[1])
    logger.info('send_weekly_recruiter_submission_follow_up successfully generated ===========> ')
    return response


def send_daily_bdm_jobs_summary_report(*args, **options):
    response = send_daily_bdm_jobs_summary(args[0], args[1])
    logger.info('send_daily_bdm_jobs_summary successfully generated')
    return response


# Weekly mail scheduler
def sendmail_for_weekly_recuiter_performance_report(*args, **options):
    response = send_weeklly_recuiter_performance_report(args[0], args[1])
    logger.info('weekly recruiter performance report successfully generated')
    return response


def sendmail_for_weekly_recruiter_submission(*args, **options):
    response = send_weekly_recruiter_submission(args[0], args[1])
    logger.info('weekly recruiter performance report successfully generated')
    return response


def sendmail_for_weekly_bdm_jobs(*args, **options):
    response = send_weekly_bdm_jobs(args[0], args[1])
    logger.info('weekly recruiter performance report successfully generated')
    return response


def send_weekly_bdm_jobs_summary_report(*args, **options):
    response = send_weekly_bdm_jobs_summary(args[0], args[1])
    logger.info('weekly bdm jobs summary report successfully generated')
    return response


def sendmail_last_48hours_bdm_jobs(*args, **options):
    response = send_last_48hours_bdm_jobs(args[0], args[1])
    logger.info('send_last_48hours_bdm_jobs report successfully generated')
    return response


def parse_recruiter_calls_data_jobs(*args, **options):
    response = parse_recruiter_calls_data(args[0], args[1])
    logger.info('parse_recruiter_calls_data_jobs report successfully generated')
    return response


#Daily Candidate Submissions
from schedulers.views import EmailCandidateSubmission
def send_daily_candidate_submissions_report():
    response = EmailCandidateSubmission()
    logger.info('send_daily_candidate_submissions report successfully generated')
    return response
    
    