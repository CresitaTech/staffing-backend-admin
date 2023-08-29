import csv
import io
import json
import re
import os
from django.utils import timezone
import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import authentication_classes, permission_classes
import ast
from django.http import HttpResponse
import shutil

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, filters, generics
from rest_framework.filters import SearchFilter, OrderingFilter

from candidates.models import Candidates
from clients.models import clientModel
from comman_utils import utils
from schedulers.models import CampaignUploadDataModel, CampaignListDataModel, \
    sendCleanRequestDataModel, RecruiterCallsModel, AgentCallsDataModel

from reports.tasks import database_daily_backup, generate_daily_submission_report_for_indian_recruiter, \
    generate_daily_job_report_for_indian_bdm, send_weekly_recruiter_submission_for_us, \
    send_weekly_bdm_jobs_report_for_us_bdm, send_weekly_recuiter_performance_report_for_us_bdm, \
    send_weekly_recruiter_submission_for_india, send_weekly_bdm_jobs_report_for_indian_bdm, \
    send_weekly_recuiter_performance_report_for_indian_bdm, generate_daily_job_report_for_us_bdm, \
    generate_daily_submission_report_for_us_recruiter, test_beat_task
from schedulers.serializers import JobsSerializer, ImportCampaignDataSerializer, SendCleanDataSerializer, \
    SendCleanRequestDataSerializer, DownloadCandidateByStatusSerializer, AgentCallsDataModelSerializer
from schedulers.utils import getCustomerCalls
# from schedulers.utils import getCustomerCalls
from staffingapp import celery
import logging

# Get an instance of a logger
from vendors.models import vendorEmailTemplateModel, VendorListDataModel, VendorListModel, vendorModel
from vendors.serializers import VendorListSerializer, VendorListMiniSerializer, VendorListWriteSerializer

logger = logging.getLogger(__name__)


def parse_recruiter_calls_data(country='India', isProd=False): # request
    today_date = utils.get_current_datetime()
    # start_date = str(datetime.date.today() - datetime.timedelta(days=7))
    start_date, end_date = utils.month_date_range()
    df = []
    """df = getCustomerCalls()
    logger.info("Prased DF Data: " + str(df))

    df_records = df.to_dict('records')
    logger.info(df_records)
    model_instances = [RecruiterCallsModel(
        recruiter_name=record['recruiter_name'],
        attempted_calls=record['attempted_calls'],
        connected_calls=record['connected_calls'],
        missed_calls=record['missed_calls']
    ) for record in df_records]

    RecruiterCallsModel.objects.bulk_create(model_instances)
    logger.info("Successfully inserted...")"""

    # return render(request, "recruiter_weekly_submission_follow_up_report.html",
    #              {'data': finalOutput, 'summaryOutput': summaryOutput})
    return str(df)
    # return render(request, df)


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

    def create(self, request):
        data_type = request.data['data_type']
        logger.info(data_type)
        serializeObj = VendorListWriteSerializer(data=request.data)

        template_id = request.data['template_name']
        if serializeObj.is_valid():
            campaign = serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id, status="New",
                                         template_name_id=template_id)
            logger.info("List inserted ID: " + str(campaign.id))

            template_object = vendorEmailTemplateModel.objects.get(id=serializeObj.data['template_name'])
            model_instances = []
            if data_type == "Candidate":
                list_data = request.data['list_data'].split(',')
                logger.info(list_data)
                for vendor_id in list_data:
                    print(vendor_id)
                    # template_object = vendorEmailTemplateModel.objects.get(id=serializeObj.data['template_name'])
                    vendor_object = Candidates.objects.get(id=vendor_id)
                    subject = str(template_object.subject)
                    body = str(template_object.body)
                    signature = str(template_object.signature)
                    matches = re.findall('{(.*?)}', body)
                    if len(matches) > 0:
                        for item in matches:
                            print(item)
                            tag = '{' + item + '}'
                            if getattr(vendor_object, item) is not None:
                                body = body.replace(tag, getattr(vendor_object, item))
                            else:
                                body = body.replace(tag, '')
                        print(body)
                    matches = re.findall('{(.*?)}', subject)
                    if len(matches) > 0:
                        for item in matches:
                            print(item)
                            tag = '{' + item + '}'
                            if getattr(vendor_object, item) is not None:
                                subject = subject.replace(tag, getattr(vendor_object, item))
                            else:
                                subject = subject.replace(tag, '')
                        print(subject)
                    # body = format_html('<div class="email-body">'+body+'</div>')
                    # body = body + format_html('<div>'+signature+'</div>')
                    body = '<div style="font-family: Arial, Helvetica, sans-serif;">' + str(
                        body) + '<div></br></br></div>' + str(signature) + '</div>'
                    model_instances.append(VendorListDataModel(
                        list_id=campaign.id,
                        template_id=serializeObj.data['template_name'],
                        record_id=vendor_id,
                        email_body=body,
                        email_subject=subject,
                        email_to=vendor_object.primary_email,
                        created_by_id=request.user.id,
                        updated_by_id=request.user.id
                    ))
                VendorListDataModel.objects.bulk_create(model_instances)

            elif data_type == "Vendor":
                list_data = request.data['list_data'].split(',')
                logger.info(list_data)
                for vendor_id in list_data:
                    print(vendor_id)
                    # template_object = vendorEmailTemplateModel.objects.get(id=serializeObj.data['template_name'])
                    vendor_object = vendorModel.objects.get(id=vendor_id)
                    subject = str(template_object.subject)
                    body = str(template_object.body)
                    signature = str(template_object.signature)
                    matches = re.findall('{(.*?)}', body)
                    if len(matches) > 0:
                        for item in matches:
                            print(item)
                            tag = '{' + item + '}'
                            if getattr(vendor_object, item) is not None:
                                body = body.replace(tag, getattr(vendor_object, item))
                            else:
                                body = body.replace(tag, '')
                        print(body)
                    matches = re.findall('{(.*?)}', subject)
                    if len(matches) > 0:
                        for item in matches:
                            print(item)
                            tag = '{' + item + '}'
                            if getattr(vendor_object, item) is not None:
                                subject = subject.replace(tag, getattr(vendor_object, item))
                            else:
                                subject = subject.replace(tag, '')
                        print(subject)
                    # body = format_html('<div class="email-body">'+body+'</div>')
                    # body = body + format_html('<div>'+signature+'</div>')
                    body = '<div style="font-family: Arial, Helvetica, sans-serif;">' + str(
                        body) + '<div></br></br></div>' + str(signature) + '</div>'
                    model_instances.append(VendorListDataModel(
                        list_id=campaign.id,
                        template_id=serializeObj.data['template_name'],
                        record_id=vendor_id,
                        email_body=body,
                        email_subject=subject,
                        email_to=vendor_object.primary_email,
                        created_by_id=request.user.id,
                        updated_by_id=request.user.id
                    ))
                VendorListDataModel.objects.bulk_create(model_instances)
            elif data_type == 'Client':
                list_data = request.data['list_data'].split(',')
                logger.info(list_data)
                for vendor_id in list_data:
                    # template_object = vendorEmailTemplateModel.objects.get(id=serializeObj.data['template_name'])
                    vendor_object = clientModel.objects.get(id=vendor_id)
                    subject = str(template_object.subject)
                    body = str(template_object.body)
                    signature = str(template_object.signature)
                    matches = re.findall('{(.*?)}', body)
                    if len(matches) > 0:
                        for item in matches:
                            print(item)
                            tag = '{' + item + '}'
                            if getattr(vendor_object, item) is not None:
                                body = body.replace(tag, getattr(vendor_object, item))
                            else:
                                body = body.replace(tag, '')
                        print(body)
                    matches = re.findall('{(.*?)}', subject)
                    if len(matches) > 0:
                        for item in matches:
                            print(item)
                            tag = '{' + item + '}'
                            if getattr(vendor_object, item) is not None:
                                subject = subject.replace(tag, getattr(vendor_object, item))
                            else:
                                subject = subject.replace(tag, '')
                        print(subject)
                    # body = format_html('<div class="email-body">'+body+'</div>')
                    # body = body + format_html('<div>'+signature+'</div>')
                    body = '<div style="font-family: Arial, Helvetica, sans-serif;">' + str(
                        body) + '<div></br></br></div>' + str(signature) + '</div>'
                    model_instances.append(VendorListDataModel(
                        list_id=campaign.id,
                        template_id=serializeObj.data['template_name'],
                        record_id=vendor_id,
                        email_body=body,
                        email_subject=subject,
                        email_to=vendor_object.primary_email,
                        created_by_id=request.user.id,
                        updated_by_id=request.user.id
                    ))
                VendorListDataModel.objects.bulk_create(model_instances)

            elif data_type == "Custom":
                logger.info(data_type)
                logger.info(campaign.upload_file)
                paramFile = io.TextIOWrapper(request.FILES['upload_file'].file)
                portfolio1 = csv.DictReader(paramFile)
                list_of_dict = list(portfolio1)

                logger.info("list_of_dict: " + str(list_of_dict))
                model_instances = []
                file = "/home/admin/projectDir/staffingapp/media/" + str(campaign.upload_file)
                reader = pd.read_csv(file)
                for _, row in reader.iterrows():
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
                        list_id=campaign.id,
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

            elif data_type == "Rechurn":
                list_data = request.data['list_data'].split(',')
                logger.info(list_data)
                for vendor_id in list_data:
                    print(vendor_id)
                    # template_object = vendorEmailTemplateModel.objects.get(id=serializeObj.data['template_name'])
                    vendor_object = clientModel.objects.get(id=vendor_id)
                    subject = str(template_object.subject)
                    body = str(template_object.body)
                    signature = str(template_object.signature)
                    matches = re.findall('{(.*?)}', body)
                    if len(matches) > 0:
                        for item in matches:
                            print(item)
                            tag = '{' + item + '}'
                            if getattr(vendor_object, item) is not None:
                                body = body.replace(tag, getattr(vendor_object, item))
                            else:
                                body = body.replace(tag, '')
                        print(body)
                    matches = re.findall('{(.*?)}', subject)
                    if len(matches) > 0:
                        for item in matches:
                            print(item)
                            tag = '{' + item + '}'
                            if getattr(vendor_object, item) is not None:
                                subject = subject.replace(tag, getattr(vendor_object, item))
                            else:
                                subject = subject.replace(tag, '')
                        print(subject)
                    # body = format_html('<div class="email-body">'+body+'</div>')
                    # body = body + format_html('<div>'+signature+'</div>')
                    body = '<div style="font-family: Arial, Helvetica, sans-serif;">' + str(
                        body) + '<div></br></br></div>' + str(signature) + '</div>'
                    model_instances.append(VendorListDataModel(
                        list_id=campaign.id,
                        template_id=serializeObj.data['template_name'],
                        vendor_id=vendor_id,
                        email_body=body,
                        email_subject=subject,
                        email_to=vendor_object.primary_email,
                        created_by_id=request.user.id,
                        updated_by_id=request.user.id
                    ))
                VendorListDataModel.objects.bulk_create(model_instances)
            else:
                return Response("Unsupported data found", status=status.HTTP_400_BAD_REQUEST)

            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def create_backup(self, request, format=None):
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


def download_resume_by_candidate(request):

    user_id = '6865b387fbed4d8cbfbe248d8aee96b2'
    start_date = '2022-08-01 00:00:00'

    queryset = Candidates.objects.raw(
        "SELECT ca.id, ca.first_name, ca.last_name, s.stage_name, u.first_name as recruiter_name, ca.resume, ca.resume_raw_data FROM "
        "`osms_candidates` as ca, candidates_jobs_stages as cjs, candidates_stages as s, users_user as u WHERE "
        "ca.id = cjs.candidate_name_id AND cjs.stage_id = s.id AND s.stage_name = 'Candidate Added' AND "
        "ca.created_by_id = u.id AND u.id = %s AND cjs.submission_date >= %s",
        [user_id, start_date])

    if queryset is not None:
        logger.info(str(queryset.query))
    # queryset = self.filter_queryset(queryset)
    serializer = DownloadCandidateByStatusSerializer(queryset, many=True)
    soutput = []

    UUID_PATTERN = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)
    is_uuid = False
    is_resume = True
    for i in range(len(serializer.data)):
        if UUID_PATTERN.match(serializer.data[i]['resume']):
            is_uuid = True
        else:
            is_uuid = False

        if serializer.data[i]['resume_raw_data']:
            is_resume = False
        rows = {
            'first_name': str(serializer.data[i]['first_name']),  # .split('.')[0]
            'last_name': serializer.data[i]['last_name'],
            'stage_name': serializer.data[i]['stage_name'],
            'recruiter_name': serializer.data[i]['recruiter_name'],
            'resume': serializer.data[i]['resume'],
            'is_resume': is_resume,
            'resume_raw_data': serializer.data[i]['resume_raw_data'],
            'total': len(serializer.data)
        }
        filename = serializer.data[i]['resume']
        if filename != "" and filename is not None:
            source =  '/home/admin/projectDir/staffingapp/media/' + serializer.data[i]['resume']
            destination = '/home/admin/projectDir/staffingapp/download/hemant'
            try:
                #dest1 = shutil.copy2(source, destination)
                #metadata = os.stat(dest1)
                #logger.info(metadata)
                logger.info("File copied.")
            except Exception as e:
                logger.info("Error Found: " + str(e.message))
                pass
            # Executed if error in the
            # try block

        soutput.append(rows)

    logger.info(serializer.data)
    return render(request, "download_resume_by_candidate.html", {'data': soutput })


class tataCallsWebhook(viewsets.ModelViewSet):
    queryset = AgentCallsDataModel.objects.all()
    serializer_class = AgentCallsDataModelSerializer
    permission_classes = []

    def list(self, request):
        # candidateObj = emailTemplateModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AgentCallsDataModelSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = AgentCallsDataModelSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        logger.debug("Tata calls Webhook Request Data: " + str(request.data))
        serializeObj = AgentCallsDataModelSerializer(data=request.data)
        if serializeObj.is_valid():
            recruiter = serializeObj.save()
            obj = AgentCallsDataModel.objects.get(pk=recruiter.id)

            caller_id_number = obj.caller_id_number
            call_to_number = obj.call_to_number
            caller_id_number = caller_id_number[-10:]
            call_to_number = call_to_number[-10:]
            obj.call_to_number = call_to_number
            obj.caller_id_number = caller_id_number
            obj.save()

            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = AgentCallsDataModelSerializer(candObj)
        return Response(serializeObj.data)