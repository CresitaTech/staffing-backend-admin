import json
from django.utils import timezone

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from reports.tasks import database_daily_backup, generate_daily_submission_report_for_indian_recruiter, \
    generate_daily_job_report_for_indian_bdm, send_weekly_recruiter_submission_for_us, \
    send_weekly_bdm_jobs_report_for_us_bdm, send_weekly_recuiter_performance_report_for_us_bdm, \
    send_weekly_recruiter_submission_for_india, send_weekly_bdm_jobs_report_for_indian_bdm, \
    send_weekly_recuiter_performance_report_for_indian_bdm, generate_daily_job_report_for_us_bdm, \
    generate_daily_submission_report_for_us_recruiter, test_beat_task
from schedulers.serializers import JobsSerializer
from staffingapp import celery
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

def index():
    print('Home Pa0ge')


@api_view(['GET', 'POST'])
def jobs(request):
    if request.method == 'GET':
        # return json.load(celery.app.conf.beat_schedule);
        data = [{'name': 'test_beat_task'},
                {'name': 'database_daily_backup'},
                {'name': 'generate_daily_submission_report_for_indian_recruiter'},
                {'name': 'generate_daily_job_report_for_indian_bdm'},

                {'name': 'generate_daily_submission_report_for_us_recruiter'},
                {'name': 'generate_daily_job_report_for_us_bdm'},

                {'name': 'send_weekly_recuiter_performance_report_for_indian_bdm'},
                {'name': 'send_weekly_bdm_jobs_report_for_indian_bdm'},
                {'name': 'send_weekly_recruiter_submission_for_india'},

                {'name': 'send_weekly_recuiter_performance_report_for_us_bdm'},
                {'name': 'send_weekly_bdm_jobs_report_for_us_bdm'},
                {'name': 'send_weekly_recruiter_submission_for_us'}]
        return JsonResponse(data, safe=False)
        # 'safe=False' for objects serialization

    elif request.method == 'POST':
        jobs_data = JSONParser().parse(request)
        jobs_serializer = JobsSerializer(data=jobs_data)
        if jobs_serializer.is_valid():
            # jobs_serializer.save()
            # logger.info(f"Celery beat is alive, it is currently {jobs_serializer.data['name']} UTC")
            # response = jobs_data['name']
            result = None
            try:
                if jobs_data['name'] == 'test_beat_task':
                    result = test_beat_task()
                elif jobs_data['country'] == 'India' and jobs_data['name'] == 'generate_daily_submission_report_for_indian_recruiter':
                    result = generate_daily_submission_report_for_indian_recruiter()
                elif jobs_data['country'] == 'India' and jobs_data['name'] == 'generate_daily_job_report_for_indian_bdm':
                    result = generate_daily_job_report_for_indian_bdm()

                elif jobs_data['country'] == 'US' and jobs_data['name'] == 'generate_daily_submission_report_for_us_recruiter':
                    result = generate_daily_submission_report_for_us_recruiter()
                elif jobs_data['country'] == 'US' and jobs_data['name'] == 'generate_daily_job_report_for_us_bdm':
                    result = generate_daily_job_report_for_us_bdm()

                elif jobs_data['country'] == 'India' and jobs_data['name'] == 'send_weekly_recuiter_performance_report_for_indian_bdm':
                    result = send_weekly_recuiter_performance_report_for_indian_bdm()
                elif jobs_data['country'] == 'India' and jobs_data['name'] == 'send_weekly_bdm_jobs_report_for_indian_bdm':
                    result = send_weekly_bdm_jobs_report_for_indian_bdm()
                elif jobs_data['country'] == 'India' and jobs_data['name'] == 'send_weekly_recruiter_submission_for_india':
                    result = send_weekly_recruiter_submission_for_india()

                elif jobs_data['country'] == 'US' and jobs_data['name'] == 'send_weekly_recuiter_performance_report_for_us_bdm':
                    result = send_weekly_recuiter_performance_report_for_us_bdm()
                elif jobs_data['country'] == 'US' and jobs_data['name'] == 'send_weekly_bdm_jobs_report_for_us_bdm':
                    result = send_weekly_bdm_jobs_report_for_us_bdm()
                elif jobs_data['country'] == 'US' and jobs_data['name'] == 'send_weekly_recruiter_submission_for_us':
                    result = send_weekly_recruiter_submission_for_us()
                else:
                    result = 'Function does not exist'

                logger.info("result: " + result)
                # or the same with getattr:
            except AttributeError:
                # do domething or just...
                result = 'Function does not exist'
                logger.info('Function does not exist')
            except NameError:
                # do domething or just...
                result = 'Module does not exist'
                logger.info('Module does not exist')

            message = 'Celery beat is alive, it is currently ' + jobs_data['name'] + ' UTC'
            return JsonResponse({'message': result}, status=status.HTTP_201_CREATED)
        return JsonResponse(jobs_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def jobs_detail(request, pk):
    """    try:
        tutorial = APILogsModel.objects.get(pk=pk)
    except APILogsModel.DoesNotExist:
        return JsonResponse({'message': 'The APILogsModel does not exist'}, status=status.HTTP_404_NOT_FOUND)
"""
    if request.method == 'GET':
        jobs_serializer = JobsSerializer()
        return JsonResponse(jobs_serializer.data)
