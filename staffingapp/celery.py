from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffingapp.settings')
app = Celery('staffingapp')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


app.conf.beat_schedule = {
    # Execute the Speed Test every 10 minutes
    'test_beat_task': {
        'task': 'test_beat_task',
        'schedule': crontab(minute='25', hour='19'),
    },
    # Everyday at 19:30
    "database_daily_backup": {
        "task": "database_daily_backup",
        "schedule": crontab(hour=23, minute=59)
    },
    'generate_daily_submission_report_for_indian_recruiter': {
        'task': 'generate_daily_submission_report_for_indian_recruiter',
        # 'schedule': crontab(minute='*/1'),
        'schedule': crontab(minute='00', hour='09', day_of_week='mon,tue,wed,thu,fri'),
    },
    'generate_daily_job_report_for_indian_bdm': {
        'task': 'generate_daily_job_report_for_indian_bdm',
        'schedule': crontab(minute='00', hour='09', day_of_week='mon,tue,wed,thu,fri'),
        # 'schedule': crontab(minute='*/1'),
    },
    'generate_daily_submission_report_for_us_recruiter': {
        'task': 'generate_daily_submission_report_for_us_recruiter',
        # 'schedule': crontab(minute='*/1'),
        'schedule': crontab(minute='00', hour='17', day_of_week='tue,wed,thu,fri,sat'),
    },
    'generate_daily_job_report_for_us_bdm': {
        'task': 'generate_daily_job_report_for_us_bdm',
        'schedule': crontab(minute='00', hour='17', day_of_week='tue,wed,thu,fri,sat'),
        # 'schedule': crontab(minute='*/1'),
    },
    # weekly report once in a week
    'send_weekly_recuiter_performance_report_for_indian_bdm': {
        'task': 'send_weekly_recuiter_performance_report_for_indian_bdm',
        'schedule': crontab(minute='00', hour='09', day_of_week='sat'),
    },
    'send_weekly_recuiter_performance_report_for_us_bdm': {
        'task': 'send_weekly_recuiter_performance_report_for_us_bdm',
        'schedule': crontab(minute='00', hour='17', day_of_week='sun'),
    },

    # bdm job summary report weekly
    'send_weekly_bdm_jobs_report_for_indian_bdm': {
        'task': 'send_weekly_bdm_jobs_report_for_indian_bdm',
        'schedule': crontab(minute='00', hour='09', day_of_week='sat'),
    },
    'send_weekly_bdm_jobs_report_for_us_bdm': {
        'task': 'send_weekly_bdm_jobs_report_for_us_bdm',
        'schedule': crontab(minute='00', hour='17', day_of_week='sun'),
    },

    # recruiter submission summary report weekly
    'send_weekly_recruiter_submission_for_india': {
        'task': 'send_weekly_recruiter_submission_for_india',
        'schedule': crontab(minute='00', hour='09', day_of_week='sat'),
    },
    'send_weekly_recruiter_submission_for_us': {
        'task': 'send_weekly_recruiter_submission_for_us',
        'schedule': crontab(minute='00', hour='17', day_of_week='sun'),
    },

    # Mail Sending facility
    # This method will run in every 30 sec
    #'send_mass_email': {
    #    'task': 'send_mass_email',
    #    'schedule': 10.0
    #}
    # 'options': {
    #    'expires': 5.0,
    # },
}
