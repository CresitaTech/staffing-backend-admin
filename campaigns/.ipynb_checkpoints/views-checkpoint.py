import csv
import io
import json
import re
import threading
import uuid
from django.db import connection
from time import gmtime, strftime

from django.core.mail import EmailMessage

from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, filters, generics
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import F
from rest_framework.permissions import DjangoModelPermissions
from django_filters.rest_framework import DjangoFilterBackend

from campaigns.models import CampaignListModel, CampaignModel, CampaignListDataModel, CampaignListMappingDataModel, \
    CampaignListUploadDataModel, CustomFieldsModel
from campaigns.serializers import CampaignListSerializer, CampaignSerializer, CampaignWriteSerializer, \
    CampaignEmailListDataSerializer, CampaignListMappingDataModelSerializer, CustomFieldsModelSerializer
from candidates.models import Candidates
from clients.models import clientModel
import pandas as pd
import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Get an instance of a logger
from staffingapp.settings import SENDCLEAN_EMAIL_HOST, SENDCLEAN_EMAIL_PORT, SENDCLEAN_EMAIL_HOST_USER, \
    SENDCLEAN_EMAIL_HOST_PASSWORD
from vendors.models import vendorEmailTemplateModel, VendorListDataModel, VendorListModel, vendorModel, \
    emailConfigurationModel, EmailModel
from vendors.serializers import VendorListSerializer, VendorListMiniSerializer, VendorListWriteSerializer


import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


def index():
    print('Home Pa0ge')


class CampaignListController(viewsets.ModelViewSet):
    queryset = CampaignListModel.objects.all()
    serializer_class = CampaignListSerializer
    permission_classes = []
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ["list_name", "created_at"]
    search_fields = ['list_name', 'status', 'created_at']
    ordering_fields = ['list_name', 'created_at']
    ordering = ['list_name', 'created_at']

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CampaignListSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CampaignListSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        data_type = request.data['data_type']
        logger.info(request.data)
        serializeObj = CampaignListSerializer(data=request.data)
        model_instances = []
        if serializeObj.is_valid():
            listObj = serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id)
            logger.info("List inserted ID: " + str(listObj.id))
            list_mapping = request.data['list_mapping']
            list_mapping = json.loads(list_mapping)

            logger.info(list_mapping)
            logger.info(list_mapping.keys())
            # empty dictionary
            reverse_dic = {}
            # reverse_dic.add('list_name_id', '')
            for key in list_mapping.keys():
                logger.info(list_mapping[key])
                if list_mapping[key]:
                    reverse_dic[list_mapping[key]] = key
            model_instances = []
            logger.info(reverse_dic)
            if data_type == "Custom":
                file = None
                file = "/home/admin/projectDir/staffingapp/media/" + str(listObj.upload_file)
                logger.info("File path: " + file)
                df = pd.read_csv(file)
                logger.info(df)
                savedDic = {}
                csvRowData = []
                listIds = []
                rowData = []
                for _, row in df.iterrows():
                    for key in reverse_dic.keys():
                        savedDic[key] = str(row[reverse_dic[key]])
                        # csvRowData.append(row[reverse_dic[key]])
                    savedDic['id'] = str(uuid.uuid4()).replace('-', '')
                    savedDic['list_name_id'] = str(listObj.id).replace('-', '')
                    savedDic['created_at'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    savedDic['updated_at'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    rowData.append(list(savedDic.values()))

                logger.info(rowData)
                logger.info(savedDic.keys())
                dicCols = tuple(savedDic)
                logger.info(dicCols)
                dicColsList = list(dicCols)
                for i in range(len(dicColsList)):
                    dicColsList[i] = "%s"
                # dicColsList = list(map(lambda x: x.replace(dicColsList[x], '%s'), dicColsList))
                dicColsValues = tuple(dicColsList)
                logger.info(dicColsValues)
                cursor = connection.cursor()
                query = 'INSERT INTO campaign_lists_upload_data ' + str(dicCols).replace("'", "") + '  VALUES ' + str(dicColsValues).replace("'", "")
                logger.info(query)
                cursor.executemany(query, rowData)

                """model = CampaignListUploadDataModel(
                    id=uuid.uuid4(),
                    key=row[list_mapping[key]],
                    last_name=row['last_name'],
                    email=row['email'],
                    list_name=listObj
                )
                model_instances.append(model)
                    # model.save()
                CampaignListUploadDataModel.objects.bulk_create(model_instances)"""

            else:
                list_data = request.data['list_data'].split(',')
                logger.info(list_data)
                for list_id in list_data:
                    model_instances.append(CampaignListDataModel(
                        list_name=listObj,
                        record_id=str(list_id).replace("-", ""),
                        data_type=data_type
                    ))
                CampaignListDataModel.objects.bulk_create(model_instances)

            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return CampaignListModel.objects.get(pk=pk)
        except CampaignListModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        vendorListObj = self.get_object(pk)
        vendorListObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CampaignController(viewsets.ModelViewSet):
    queryset = CampaignModel.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = []
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ["campaign_name", "created_at"]
    search_fields = ['campaign_name', 'status', 'created_at']
    ordering_fields = ['campaign_name', 'created_at']
    ordering = ['campaign_name', 'created_at']

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CampaignSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CampaignSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        logger.info("Campaign Request: " + str(request.data))
        serializeObj = CampaignWriteSerializer(data=request.data)
        if serializeObj.is_valid():
            campaignObj = serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id, status="Active")
            logger.info("campaign inserted ID: " + str(campaignObj.id))
            logger.info("List ID: " + str(campaignObj.list_name_id))
            logger.info("Template ID: " + str(campaignObj.template_name_id))
            listObj = CampaignListModel.objects.get(id=campaignObj.list_name_id)
            logger.info("List Data type: " + str(listObj.data_type))

            template_object = vendorEmailTemplateModel.objects.get(id=campaignObj.template_name_id)
            model_instances = []
            if listObj.data_type == "Candidate":
                records = CampaignListDataModel.objects.filter(list_name_id=campaignObj.list_name_id)
                logger.info(records)
                for record in records:
                    logger.info(record)
                    # template_object = vendorEmailTemplateModel.objects.get(id=serializeObj.data['template_name'])
                    vendor_object = Candidates.objects.get(id=record.record_id)
                    subject = str(template_object.subject)
                    body = str(template_object.body)
                    signature = str(template_object.signature)
                    matches = re.findall('{(.*?)}', body)
                    if len(matches) > 0:
                        for item in matches:
                            logger.info(item)
                            tag = '{' + item + '}'
                            if getattr(vendor_object, item) is not None:
                                body = body.replace(tag, getattr(vendor_object, item))
                            else:
                                body = body.replace(tag, '')
                        logger.info(body)
                    matches = re.findall('{(.*?)}', subject)
                    if len(matches) > 0:
                        for item in matches:
                            logger.info(item)
                            tag = '{' + item + '}'
                            if getattr(vendor_object, item) is not None:
                                subject = subject.replace(tag, getattr(vendor_object, item))
                            else:
                                subject = subject.replace(tag, '')
                        logger.info(subject)
                    # body = format_html('<div class="email-body">'+body+'</div>')
                    # body = body + format_html('<div>'+signature+'</div>')
                    body = '<div style="font-family: Arial, Helvetica, sans-serif;">' + str(
                        body) + '<div></br></br></div>' + str(signature) + '</div>'
                    model_instances.append(CampaignListMappingDataModel(
                        list_name_id=listObj.id,
                        campaign_name_id=campaignObj.id,
                        template_name_id=template_object.id,
                        record_id=str(record.record_id).replace("-", ""),
                        email_body=body,
                        email_subject=subject,
                        email_to=vendor_object.primary_email,
                        created_by_id=request.user.id,
                        updated_by_id=request.user.id
                    ))
                CampaignListMappingDataModel.objects.bulk_create(model_instances)

            elif listObj.data_type == "Vendor":
                records = CampaignListDataModel.objects.filter(list_name_id=campaignObj.list_name_id)
                logger.info(records)
                for record in records:
                    logger.info(record)
                    # template_object = vendorEmailTemplateModel.objects.get(id=serializeObj.data['template_name'])
                    vendor_object = vendorModel.objects.get(id=record.record_id)
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
                    model_instances.append(CampaignListMappingDataModel(
                        list_name_id=listObj.id,
                        campaign_name_id=campaignObj.id,
                        template_name_id=template_object.id,
                        record_id=str(record.record_id).replace("-", ""),
                        email_body=body,
                        email_subject=subject,
                        email_to=vendor_object.primary_email,
                        created_by_id=request.user.id,
                        updated_by_id=request.user.id
                    ))
                CampaignListMappingDataModel.objects.bulk_create(model_instances)

            elif listObj.data_type == 'Client':
                records = CampaignListDataModel.objects.filter(list_name_id=campaignObj.list_name_id)
                logger.info(records)
                for record in records:
                    # template_object = vendorEmailTemplateModel.objects.get(id=serializeObj.data['template_name'])
                    vendor_object = clientModel.objects.get(id=record.record_id)
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
                    model_instances.append(CampaignListMappingDataModel(
                        list_name_id=listObj.id,
                        campaign_name_id=campaignObj.id,
                        template_name_id=template_object.id,
                        record_id=str(record.record_id).replace("-", ""),
                        email_body=body,
                        email_subject=subject,
                        email_to=vendor_object.primary_email,
                        created_by_id=request.user.id,
                        updated_by_id=request.user.id
                    ))
                CampaignListMappingDataModel.objects.bulk_create(model_instances)

            elif listObj.data_type == "Custom":
                model_instances = []
                cursor = connection.cursor()
                query = """SELECT * FROM campaign_lists_upload_data WHERE list_name_id = %s"""
                # set variable in query
                cursor.execute(query, (str(listObj.id).replace("-", ""),))
                columnNames = [column[0] for column in cursor.description]
                logger.info(columnNames)
                records = cursor.fetchall()
                insertObject = []
                for record in records:
                    insertObject.append(dict(zip(columnNames, record)))
                logger.info(insertObject)
                logger.info("Total rows are:  ", len(records))
                logger.info("Printing each row: " + str(records))
                for row in insertObject:
                    logger.info(row)
                    subject = str(template_object.subject)
                    body = str(template_object.body)
                    signature = str(template_object.signature)
                    matches = re.findall('{(.*?)}', body)
                    if len(matches) > 0:
                        for item in matches:
                            logger.info(item)
                            tag = '{' + item + '}'
                            logger.info("tag: " + str(tag))
                            logger.info("item: " + str(item))
                            logger.info("tag: " + str(row.get(item) ))
                            if row.get(item) is not None:
                                body = body.replace(tag, row.get(item))
                            else:
                                body = body.replace(tag, '')
                        logger.info(body)
                    matches = re.findall('{(.*?)}', subject)
                    if len(matches) > 0:
                        for item in matches:
                            logger.info(item)
                            tag = '{' + item + '}'
                            if row.get(item) is not None:
                                subject = subject.replace(tag, row.get(item) )
                            else:
                                subject = subject.replace(tag, '')
                        logger.info(subject)
                    # body = format_html('<div class="email-body">'+body+'</div>')
                    # body = body + format_html('<div>'+signature+'</div>')
                    body = '<div style="font-family: Arial, Helvetica, sans-serif;">' + str(
                        body) + '<div></br></br></div>' + str(signature) + '</div>'

                    model_instances.append(CampaignListMappingDataModel(
                        list_name_id=listObj.id,
                        campaign_name_id=campaignObj.id,
                        template_name_id=template_object.id,
                        email_body=body,
                        email_subject=subject,
                        email_to=row.get('EMAIL'), # getattr(row, 'EMAIL')
                        created_by_id=request.user.id,
                        updated_by_id=request.user.id
                    ))
                logger.info(model_instances)
                logger.info('imported successfully')
                CampaignListMappingDataModel.objects.bulk_create(model_instances)
                return Response(serializeObj.data, status=status.HTTP_201_CREATED)

            else:
                return Response("Unsupported data found", status=status.HTTP_400_BAD_REQUEST)

            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return CampaignModel.objects.get(pk=pk)
        except CampaignModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        vendorListObj = self.get_object(pk)
        vendorListObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CampaignEmailListData(viewsets.ModelViewSet):
    queryset = CampaignListModel.objects.all()
    serializer_class = CampaignEmailListDataSerializer
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ["first_name", "last_name", 'email']
    search_fields = ["first_name", "last_name", 'email']
    ordering_fields = ["first_name", "last_name", 'email']
    ordering = ["first_name", "last_name", 'email']

    def list(self, request):
        queryset = None
        list_id = request.GET.get('list_id', None)
        listObj = CampaignListModel.objects.get(id=list_id)
        uid = str(listObj.id).replace("-", "")
        if listObj.data_type == "Candidate":
            candidateIds = CampaignListDataModel.objects.values('record_id').filter(list_name=listObj)
            queryset = Candidates.objects.values('id', 'first_name', 'last_name')\
                .annotate(email=F('primary_email'))\
                .filter(id__in=candidateIds)
        elif listObj.data_type == "Client":
            clientIds = CampaignListDataModel.objects.values('record_id').filter(list_name=listObj)
            queryset = clientModel.objects.values('id', 'first_name', 'last_name') \
                .annotate(email=F('primary_email')) \
                .filter(id__in=clientIds)
        elif listObj.data_type == "Vendor":
            vendorIds = CampaignListDataModel.objects.values('record_id').filter(list_name=listObj)
            queryset = vendorModel.objects.values('id') \
                .annotate(first_name=F('contact_person_first_name'), last_name=F('contact_person_last_name'), email=F('primary_email')) \
                .filter(id__in=vendorIds)
        elif listObj.data_type == "Custom":
            queryset = CampaignListUploadDataModel.objects.filter(list_name=listObj)
        if queryset is not None:
            logger.info("CampaignEmailListData List: " + str(queryset.query))

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CampaignEmailListDataSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CampaignEmailListDataSerializer(self.queryset, many=True)
        return Response(serializer.data)


class CampaignEmailListMappingData(viewsets.ModelViewSet):
    queryset = CampaignListMappingDataModel.objects.all()
    serializer_class = CampaignListMappingDataModelSerializer
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ["template_name__template_name", "created_at", 'list_name__list_name']
    search_fields = ['template_name__template_name', 'list_name__list_name', 'email_to']
    ordering_fields = ['template_name__template_name', 'created_at']
    ordering = ['template_name__template_name', 'created_at']

    def list(self, request):
        campaign_id = request.GET.get('campaign_id', None)
        queryset = CampaignListMappingDataModel.objects.filter(campaign_name_id=campaign_id)
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CampaignListMappingDataModelSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CampaignListMappingDataModelSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def get_object(self, pk):
        try:
            return CampaignListMappingDataModel.objects.get(pk=pk)
        except CampaignListMappingDataModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        clientObj = self.get_object(pk)
        serializeObj = CampaignListMappingDataModelSerializer(clientObj)
        return Response(serializeObj.data)


class EmailThread(threading.Thread):
    def __init__(self, email, sender, receiver, message):
        self.email = email
        self.message = message
        self.sender = sender
        self.receiver = receiver
        threading.Thread.__init__(self)

    def run(self):
        logger.info("MailSending from: " + str(self.sender) + " To: " + str(self.receiver))
        # self.email.send(fail_silently=False)
        context = ssl.create_default_context()
        try:
            server = smtplib.SMTP_SSL(SENDCLEAN_EMAIL_HOST, SENDCLEAN_EMAIL_PORT, context=context)
            server.login(SENDCLEAN_EMAIL_HOST_USER, SENDCLEAN_EMAIL_HOST_PASSWORD)
            server.sendmail(
                self.sender, self.receiver, self.message.as_string()
            )
            logger.info("Successfully sent email")
        except Exception as e:
            logger.info("Error: unable to send email: " + str(e))

        """        with smtplib.SMTP_SSL(SENDCLEAN_EMAIL_HOST, SENDCLEAN_EMAIL_PORT, context=context) as server:
            server.login(SENDCLEAN_EMAIL_HOST_USER, SENDCLEAN_EMAIL_HOST_PASSWORD)
            server.sendmail(
                self.sender, self.receiver, self.message.as_string()
            )
            print("Successfully sent email")"""


class SendCampaignListMail(generics.ListAPIView):
    queryset = CampaignListMappingDataModel.objects.none()

    def get(self, request, format=None):
        if request.query_params.get('campaign_id'):
            campaign_id = request.GET.get('campaign_id', None)
            list_id = request.query_params.get('list_id', None)
            logger.info("campaign_id: " + str(campaign_id))
            campaign_id = str(campaign_id).replace("-", "")
            list_id = str(list_id).replace("-", "")
            email_objects = CampaignListMappingDataModel.objects.filter(campaign_name_id=campaign_id)
            logger.info("email_objects: " + str(email_objects))
            if len(email_objects) > 0:
                try:
                    mail_setting = emailConfigurationModel.objects.get(created_by_id=request.user.id)
                    logger.info("mail_setting: " + str(mail_setting))
                    CampaignModel.objects.filter(id=campaign_id).update(status='In Progress')
                    for email_object in email_objects:
                        logger.info("email_object: " + str(email_object))
                        logger.info("email_object: " + email_object.email_subject)
                        email_cc = None
                        if mail_setting.email_cc is not None:
                            email_cc = str(mail_setting.email_cc).strip() # .split(',')
                        email_object_str = getattr(email_object, 'email_body')
                        email_object_replace1 = email_object_str.replace("<p>", "<div>")
                        email_object_replace2 = email_object_replace1.replace("</p>", "</div>")

                        email = EmailModel()
                        email.subject = email_object.email_subject
                        email.email_from = str(mail_setting.first_name) + '< ' + str(mail_setting.email) + ' >'
                        email.email_to = getattr(email_object, 'email_to')
                        email.email_cc = email_cc
                        email.campaign_id = request.query_params.get('list_id')
                        email.message = email_object_replace2
                        email.created_by = request.user
                        email.updated_by = request.user
                        email.status = False
                        email.save()
                        logger.info("Email Successfully saved.")

                        mail = EmailMessage(subject=str(email_object.email_subject),
                                              body=email_object_replace2,
                                              from_email=mail_setting.email,
                                              to=[getattr(email_object, 'email_to')])
                        mail.content_subtype = 'html'

                        logger.info("mail_setting.first_name: " + str(mail_setting.first_name))
                        logger.info("mail_setting.first_name: " + str(mail_setting.email))

                        message = MIMEMultipart("alternative")
                        message["Subject"] = str(email_object.email_subject)
                        message["From"] = mail_setting.email
                        message["To"] = getattr(email_object, 'email_to')
                        sender = mail_setting.email
                        receiver = getattr(email_object, 'email_to')

                        html_message = MIMEText(email_object_replace2, "html")

                        # Add HTML/plain-text parts to MIMEMultipart message
                        # The email client will try to render the last part first
                        message.attach(html_message)

                        # email.cc = [email_cc]
                        # sender.send()
                        # logger.info("MailSending from......." + str(mail_setting.email))
                        EmailThread(mail, sender, receiver, message).start()

                    print("Email Send Successfully !!!!!!!!!!!!!!!")
                    CampaignModel.objects.filter(id=campaign_id).update(status='Sent')
                    return Response(data={'msg': "Success"}, status=status.HTTP_200_OK)
                except Exception as e:
                    CampaignModel.objects.filter(id=campaign_id).update(status='Failed')
                    return Response(data={'msg': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomFieldsViewSet(viewsets.ModelViewSet):
    queryset = CustomFieldsModel.objects.all()
    serializer_class = CustomFieldsModelSerializer
    permission_classes = [DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, ]  # SearchFilter,
    ordering_fields = ['field_name', 'field_type', 'created_at']
    ordering = ['field_name', 'field_type', 'created_at']
    filter_fields = ["field_name", "field_type", "created_at"]
    search_fields = ['field_name', 'field_type', 'created_at']

    def list(self, request):
        queryset = CustomFieldsModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CustomFieldsModelSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CustomFieldsModelSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        logger.info('New Client Create data: ' + str(request.data))
        serializeObj = CustomFieldsModelSerializer(data=request.data)
        if serializeObj.is_valid():
            obj = serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id)
            cursor = connection.cursor()
            query = "ALTER TABLE campaign_lists_upload_data ADD " + obj.field_name + " VARCHAR(100)"
            logger.info(obj.field_name)
            cursor.execute(query)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        logger.error('CustomFieldsModelSerializer Error: ' + str(serializeObj.errors))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return CustomFieldsModel.objects.get(pk=pk)
        except CustomFieldsModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        clientObj = self.get_object(pk)
        serializeObj = CustomFieldsModelSerializer(clientObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        logger.info('Update Client Data: ' + str(request.data))
        clientObj = self.get_object(pk)
        serializeObj = CustomFieldsModelSerializer(clientObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        logger.error('Client Update Serialized Error: ' + str(serializeObj.errors))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        clientObj = self.get_object(pk)
        #cursor = connection.cursor()
        #query = "ALTER TABLE campaign_lists_upload_data DROP COLUMN " + clientObj.field_name
        #logger.info(clientObj.field_name)
        #cursor.execute(query)
        clientObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)