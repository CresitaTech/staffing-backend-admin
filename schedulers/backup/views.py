import csv
import io
import json
import re
from django.utils import timezone

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import authentication_classes, permission_classes
import ast
from django.http import HttpResponse

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, filters, generics
from rest_framework.filters import SearchFilter, OrderingFilter
from schedulers.models import CampaignUploadDataModel, CampaignListDataModel, \
    sendCleanRequestDataModel

from reports.tasks import database_daily_backup, generate_daily_submission_report_for_indian_recruiter, \
    generate_daily_job_report_for_indian_bdm, send_weekly_recruiter_submission_for_us, \
    send_weekly_bdm_jobs_report_for_us_bdm, send_weekly_recuiter_performance_report_for_us_bdm, \
    send_weekly_recruiter_submission_for_india, send_weekly_bdm_jobs_report_for_indian_bdm, \
    send_weekly_recuiter_performance_report_for_indian_bdm, generate_daily_job_report_for_us_bdm, \
    generate_daily_submission_report_for_us_recruiter, test_beat_task
from schedulers.serializers import JobsSerializer, ImportCampaignDataSerializer, SendCleanDataSerializer, \
    SendCleanRequestDataSerializer
from staffingapp import celery
import logging

# Get an instance of a logger
from vendors.models import vendorEmailTemplateModel, VendorListDataModel, VendorListModel
from vendors.serializers import VendorListSerializer, VendorListMiniSerializer

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
                elif jobs_data['country'] == 'India' and jobs_data[
                    'name'] == 'generate_daily_submission_report_for_indian_recruiter':
                    result = generate_daily_submission_report_for_indian_recruiter()
                elif jobs_data['country'] == 'India' and jobs_data[
                    'name'] == 'generate_daily_job_report_for_indian_bdm':
                    result = generate_daily_job_report_for_indian_bdm()

                elif jobs_data['country'] == 'US' and jobs_data[
                    'name'] == 'generate_daily_submission_report_for_us_recruiter':
                    result = generate_daily_submission_report_for_us_recruiter()
                elif jobs_data['country'] == 'US' and jobs_data['name'] == 'generate_daily_job_report_for_us_bdm':
                    result = generate_daily_job_report_for_us_bdm()

                elif jobs_data['country'] == 'India' and jobs_data[
                    'name'] == 'send_weekly_recuiter_performance_report_for_indian_bdm':
                    result = send_weekly_recuiter_performance_report_for_indian_bdm()
                elif jobs_data['country'] == 'India' and jobs_data[
                    'name'] == 'send_weekly_bdm_jobs_report_for_indian_bdm':
                    result = send_weekly_bdm_jobs_report_for_indian_bdm()
                elif jobs_data['country'] == 'India' and jobs_data[
                    'name'] == 'send_weekly_recruiter_submission_for_india':
                    result = send_weekly_recruiter_submission_for_india()

                elif jobs_data['country'] == 'US' and jobs_data[
                    'name'] == 'send_weekly_recuiter_performance_report_for_us_bdm':
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


class ImportCampaignData(viewsets.ModelViewSet):
    queryset = VendorListModel.objects.all()
    serializer_class = VendorListMiniSerializer
    permission_classes = []
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ["template_name__template_name", "created_at"]
    search_fields = ['template_name__template_name', 'list_name', 'created_at']
    ordering_fields = ['template_name__template_name', 'created_at']
    ordering = ['template_name__template_name', 'created_at']

    def list(self, request):
        # candidateObj = emailTemplateModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = VendorListMiniSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = VendorListMiniSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        user = request.user  # get the current login user details
        logger.info(user)
        logger.info(request.data)
        serializeObj = VendorListSerializer(data=request.data)
        paramFile = io.TextIOWrapper(request.FILES['upload_file'].file)
        portfolio1 = csv.DictReader(paramFile)
        list_of_dict = list(portfolio1)
        logger.info("template_name: " + request.data['template_name'])
        template_id = request.data['template_name']
        if serializeObj.is_valid():
            campaign = serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id, status="New",
                                         template_name_id=template_id)
            logger.info(campaign.id)

            logger.info("list_of_dict: " + str(list_of_dict))
            model_instances = []
            for row in list_of_dict:
                logger.info(row)
                template_object = vendorEmailTemplateModel.objects.get(id=template_id)
                subject = str(template_object.subject)
                body = str(template_object.body)
                signature = str(template_object.signature)
                matches = re.findall('{(.*?)}', body)
                if len(matches) > 0:
                    for item in matches:
                        logger.info(item)
                        tag = '{' + item + '}'
                        if getattr(row, item) is not None:
                            body = body.replace(tag, getattr(row, item))
                        else:
                            body = body.replace(tag, '')
                    logger.info(body)
                matches = re.findall('{(.*?)}', subject)
                if len(matches) > 0:
                    for item in matches:
                        logger.info(item)
                        tag = '{' + item + '}'
                        if getattr(row, item) is not None:
                            subject = subject.replace(tag, getattr(row, item))
                        else:
                            subject = subject.replace(tag, '')
                    logger.info(subject)
                # body = format_html('<div class="email-body">'+body+'</div>')
                # body = body + format_html('<div>'+signature+'</div>')
                body = '<div style="font-family: Arial, Helvetica, sans-serif;">' + str(
                    body) + '<div></br></br></div>' + str(signature) + '</div>'

                model_instances.append(VendorListDataModel(
                    list=campaign,
                    template=template_object,
                    email_body=body,
                    email_subject=subject,
                    email_to=row['email'],
                    created_by_id=request.user.id,
                    updated_by_id=request.user.id
                ))
            logger.info(model_instances)
            logger.info('imported successfully')
            VendorListDataModel.objects.bulk_create(model_instances)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)

        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return VendorListModel.objects.get(pk=pk)
        except VendorListModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        vendorListObj = self.get_object(pk)
        vendorListObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class sendCleanWebhook(viewsets.ModelViewSet):
    queryset = sendCleanRequestDataModel.objects.all()
    serializer_class = SendCleanDataSerializer
    permission_classes = []
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ["send", "created_at"]
    search_fields = ['send', 'delivered', 'created_at']
    ordering_fields = ['send', 'created_at']
    ordering = ['send', 'created_at']

    def list(self, request):
        # candidateObj = emailTemplateModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SendCleanDataSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SendCleanDataSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        user = request.user  # get the current login user details
        logger.info(user)
        logger.info("Send Clean Webhokk Request Data: " + str(request.data))
        serializeObj = SendCleanDataSerializer(data=request.data)
        if serializeObj.is_valid():
            campaign = serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id)
            logger.info(campaign.id)

            return Response(serializeObj.data, status=status.HTTP_201_CREATED)

        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
def sendCleanWebhookPost(request):
    if request.method == 'GET':
        return HttpResponse("God bless you, SendClean", status=status.HTTP_201_CREATED)
    else:
        logger.info("Webhook Request Data: " + str(request.data))
        s1 = json.dumps(request.data)
        json_object = json.loads(s1)
        logger.info("Webhook Request json_object: " + str(json_object))

        for key, value in json_object.items():
            logger.info(key)
            logger.info(value)
            if key == 'sarvtes_events':
                result = ast.literal_eval(value)
                logger.info("Total items: " + str(len(result)))
                for i in range(len(result)):
                    logger.info(result[i])
                    logger.info(result[i]['_id'])

                    info = sendCleanRequestDataModel()
                    info.record_id = result[i]['_id']
                    info.user_id = result[i]['user_id']
                    info.smtp_name = result[i]['smtp_name']
                    info.x_unique_id = result[i]['x_unique_id']
                    info.ts = result[i]['ts']
                    info.msg = result[i]['msg']
                    info.sarvtes_events = result[i]
                    info.event = result[i]['event']

                    info.save()

                return HttpResponse("God bless you, SendClean", status=status.HTTP_201_CREATED)
        #jobs_serializer = SendCleanRequestDataSerializer(data=request.data)
        #if jobs_serializer.is_valid():
        #    jobs_serializer.save(created_by_id=request.user.id, updated_by_id=request.user.id)

        return Response("Something goes wrong", status=status.HTTP_400_BAD_REQUEST)