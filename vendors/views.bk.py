import json
import re
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.core import mail
from django.core.mail.backends.smtp import EmailBackend
import redis
from django.shortcuts import render

# Create your views here.
from django.utils.html import format_html
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from staffingapp import settings
from vendors.models import vendorModel, vendorEmailTemplateModel, emailConfigurationModel, VendorListModel, \
    VendorListDataModel , MailEventsModel
from vendors.serializers import VendorSerializer, EmailTemplateSerializer, EmailConfigurationSerializer, \
    VendorListSerializer, VendorListWriteSerializer , VendorListDataSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, filters , generics
from rest_framework.filters import SearchFilter, OrderingFilter
from vendors.filters import VendorFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from comman_utils.utils import handle_file_upload, download_csv, get_mail_object
from candidates.models import importFileModel
from candidates.serializers import ImportFileSerializer
import pandas as pd
from rest_framework.permissions import DjangoModelPermissions
from users.models import User
from users.serializers import UserSerializer


class VendorViewSet(viewsets.ModelViewSet):

    queryset = vendorModel.objects.all()
    serializer_class = VendorSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, ]  # SearchFilter,
    ordering_fields = ['contact_person_first_name', 'created_at']
    ordering = ['contact_person_first_name', 'created_at']
    filter_fields = ["contact_person_first_name", "company_name", "created_at"]
    search_fields = ['=contact_person_first_name' , 'company_name' , 'contact_person_last_name']
    filter_class = VendorFilter
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        candObj = User.objects.get(pk=request.user.id)
        serializeObj = UserSerializer(candObj)
        # print(serializeObj.data)
        groups = dict(serializeObj.data)
        # print(groups)
        # print(len(groups))
        userGroupDict = None
        userGroup = None
        if len(groups['groups']) > 0:
            # print(groups['groups'])
            # print(groups['groups'][0])
            # userGroupDict = None
            userGroupDict = dict(groups['groups'][0])
        if userGroupDict is not None:
            userGroup = userGroupDict['name']
        print(userGroup)
        
        if userGroup is not None and userGroup == 'ADMIN':
            queryset = vendorModel.objects.all()
        elif userGroup is not None and userGroup == 'BDM MANAGER':
            queryset = vendorModel.objects.filter(created_by_id=request.user.id)
            # print(str(queryset.query))
        elif userGroup is not None and userGroup == 'RECRUITER MANAGER':
            queryset = vendorModel.objects.all()
            # print(str(queryset.query))
        elif userGroup is not None and userGroup == 'RECRUITER':
            #queryset = vendorModel.objects.none()
            queryset = vendorModel.objects.filter(created_by_id=request.user.id)
            # print(str(queryset.query))
        else:
            queryset = vendorModel.objects.none()

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = VendorSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = VendorSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = VendorSerializer(data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(created_by_id = request.user.id , updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return vendorModel.objects.get(pk=pk)
        except vendorModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        vendorObj = self.get_object(pk)
        serializeObj = VendorSerializer(vendorObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        vendorObj = self.get_object(pk)
        serializeObj = VendorSerializer(vendorObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        vendorObj = self.get_object(pk)
        vendorObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class EmailTemplateViewSet(viewsets.ModelViewSet):

    queryset = vendorEmailTemplateModel.objects.all()
    serializer_class = EmailTemplateSerializer
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ["template_name", "created_at"]
    search_fields = ['template_name' ,'created_at']
    ordering_fields = ['template_name' , 'created_at']
    ordering = ['template_name' , 'created_at']

    def list(self, request):
        #candidateObj = emailTemplateModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EmailTemplateSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = EmailTemplateSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = EmailTemplateSerializer(data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(created_by_id = request.user.id , updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return vendorEmailTemplateModel.objects.get(pk=pk)
        except vendorEmailTemplateModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        templateObj = self.get_object(pk)
        serializeObj = EmailTemplateSerializer(templateObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        templateObj = self.get_object(pk)
        serializeObj = EmailTemplateSerializer(templateObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        templateObj = self.get_object(pk)
        templateObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SendVendorListMail(generics.ListAPIView):
    queryset = VendorListDataModel.objects.none()

    def get(self, request, format=None):
        if request.query_params.get('list_id'):
            email_objects = VendorListDataModel.objects.filter(list_id = request.query_params.get('list_id'))
            print(email_objects)
            if len(email_objects) > 0:
                try:
                    mail_setting = emailConfigurationModel.objects.get(created_by_id=request.user.id)
                    VendorListModel.objects.filter(id=request.query_params.get('list_id')).update(status='In Progress')
                    for email_object in email_objects:
                        headers = {'Content-Type': 'application/json',
                                   'X-Server-API-Key': 'WW05O9S9jzKgSsEOJMZyLPun'}
                        url = "https://mail.opallius.com/api/v1/send/message"
                        email_cc = []
                        if mail_setting.email_cc is not None:
                            email_cc = str(mail_setting.email_cc).strip().split(',')
                        email_object_str = getattr(email_object, 'email_body')
                        email_object_replace1  = email_object_str.replace("<p>", "<div>")
                        email_object_replace2 = email_object_replace1.replace("</p>", "</div>")
                        postdata = {
                            "html_body": email_object_replace2,
                            "subject": getattr(email_object, 'email_subject'),
                            "from": mail_setting.first_name + '<' + mail_setting.email + '>',
                            "to": [getattr(email_object, 'email_to')],
                            "cc": email_cc
                        }
                        response = requests.post(url, json=postdata, headers=headers, verify=False)
                        print(response.status_code)
                        print(response.text)
                    print("Email Send Successfully !!!!!!!!!!!!!!!")
                    VendorListModel.objects.filter(id=request.query_params.get('list_id')).update(status='Sent')
                    return Response(data = {'msg': "Success"} , status=status.HTTP_200_OK)
                except Exception as e:
                    print(e)
                    VendorListModel.objects.filter(id=request.query_params.get('list_id')).update(status='Failed')
                    return Response(data = {'msg': str(e)} , status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_mass_mail(request , redis_instance , list_obj):
    con = mail.get_connection()
    con.open()
    try:
        print('Django connected to the SMTP server')
        print(request.user.id)
        mail_setting = emailConfigurationModel.objects.get(created_by_id=request.user.id)
        mail_obj = EmailBackend(
            host=mail_setting.host_name,
            port=mail_setting.port,
            password=mail_setting.password,
            username=mail_setting.email,
            use_tls=True,
            timeout=20
        )
        print(json.loads(redis_instance.get(list_obj.list_name)))
        email_objects = json.loads(redis_instance.get(list_obj.list_name))
        for email_object in email_objects:
            msg = mail.EmailMessage(
                subject=email_object['subject'],
                body=email_object['body'],
                from_email=request.user.email,
                to=[email_object['email']],
                connection=con,
            )
            msg.content_subtype = 'html'
            mail_obj.send_messages([msg])
            print('Message has been sent... successfullyy !!!!!!!!!')

        mail_obj.close()
        con.close()
        print('SMTP server closed')
        return True

    except Exception as _error:
        con.close()
        print('Error in sending mail >> {}'.format(_error))
        return False

class VendorListSet(viewsets.ModelViewSet):

    queryset = VendorListModel.objects.all()
    serializer_class = VendorListSerializer
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ["template_name__template_name", "created_at"]
    search_fields = ['template_name__template_name' ,'list_name' , 'created_at']
    ordering_fields = ['template_name__template_name' , 'created_at']
    ordering = ['template_name__template_name' , 'created_at']

    def list(self, request):
        #candidateObj = emailTemplateModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = VendorListSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = VendorListSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        print(request.data['list_data'])
        list_data = request.data['list_data'].split(',')
        serializeObj = VendorListWriteSerializer(data=request.data)
        if serializeObj.is_valid():
            list_obj = serializeObj.save(created_by_id = request.user.id , updated_by_id = request.user.id , status = "New")
            if len(list_data) > 0:
                model_instances = []
                for vendor_id in list_data:
                    print(vendor_id)
                    template_object = vendorEmailTemplateModel.objects.get(id=serializeObj.data['template_name'])
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
                    #body = format_html('<div class="email-body">'+body+'</div>')
                    #body = body + format_html('<div>'+signature+'</div>')
                    body = '<div style="font-family: Arial, Helvetica, sans-serif;">' + str(body) + '<div></br></br></div>' + str(signature) + '</div>'
                    model_instances.append(VendorListDataModel(
                        list_id=list_obj.id,
                        template_id=serializeObj.data['template_name'],
                        vendor_id=vendor_id,
                        email_body = body,
                        email_subject = subject,
                        email_to = vendor_object.primary_email,
                        created_by_id=request.user.id,
                        updated_by_id=request.user.id
                    ))
                VendorListDataModel.objects.bulk_create(model_instances)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return VendorListModel.objects.get(pk=pk)
        except VendorListModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        email_objects = VendorListDataModel.objects.filter(list_id = pk)
        serializeObj = VendorListDataSerializer(email_objects, many=True)
        return Response(serializeObj.data)

    def update(self, request, pk):
        vendorListObj = self.get_object(pk)
        serializeObj = VendorListWriteSerializer(vendorListObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        vendorListObj = self.get_object(pk)
        vendorListObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
class ExportVendorModel(generics.ListAPIView):

    def get(self, request, format=None):
        response = download_csv(vendorModel, request, vendorModel.objects.all())
        return response
        
class ImportVendorModel(generics.ListAPIView):
    queryset = importFileModel.objects.all()
    serializer_class = ImportFileSerializer
    permission_classes = []

    def post(self, request, format=None):
        fileObj = ImportFileSerializer(data=request.data)
        if fileObj.is_valid():
            fileObj.save(created_by_id = request.user.id , updated_by_id = request.user.id)
        queryset = vendorModel.objects.all()
        opts = queryset.model._meta
        field_names = [field.name for field in opts.fields]
        gendf = pd.DataFrame(columns=field_names)
        print(fileObj.data['file'])
        file_path = '.' +str(fileObj.data['file'])
        df = pd.read_csv(file_path, delimiter=",")
        print(df.head())
        json_obj = json.loads(fileObj.data['data_fields'])
        print(json_obj)
        for i in range(len(gendf.columns)):
            print(gendf.columns[i])
            # print(request.data.get(gendf.columns[i]))
            if gendf.columns[i] in json_obj:
                print("======")
                try:
                    gendf[gendf.columns[i]] = df[json_obj[gendf.columns[i]]]
                except:
                    pass
            else:
                print("===: ")
                gendf[gendf.columns[i]] = None

                # print(df[request.data[gendf.columns[i]]])
        print("=================")
        print(gendf.head())
        df_records = gendf.to_dict('records')

        model_instances = [vendorModel(
            contact_person_first_name=record['contact_person_first_name'],
            contact_person_last_name=record['contact_person_last_name'],
            designation=record['designation'],
            primary_email=record['primary_email'],
            alternate_email=record['alternate_email'],
            phone_number=record['phone_number'],
            company_name=record['company_name'],
            company_address=record['company_address'],
            specialised_in=record['specialised_in'],
            about_company=record['about_company'],
            created_by_id=request.user.id,
            updated_by_id=request.user.id
        ) for record in df_records]

        vendorModel.objects.bulk_create(model_instances)

        # print(field_names)
        return Response(fileObj.data)
        
class EmailConfigurationSet(viewsets.ModelViewSet):

    queryset = emailConfigurationModel.objects.all()
    serializer_class = EmailConfigurationSerializer
    permission_classes = []

    def create(self, request):
        serializeObj = EmailConfigurationSerializer(data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(created_by_id = request.user.id , updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)


class GetEmailConfig(generics.ListAPIView):
    serializer_class = EmailConfigurationSerializer
    queryset = emailConfigurationModel.objects.all()

    def get(self, request, format=None):
        repoObj = emailConfigurationModel.objects.filter(created_by_id=request.user.id)
        serializer = EmailConfigurationSerializer(repoObj, many=True)
        """server, rows = get_mail_object(self, request)
        subject = "Mail configure successfully"
        message = "Your mail has been successfully configured"

        # create message object instance
        msg = MIMEMultipart()
        # setup the parameters of the message
        msg['From'] = rows['email']
        msg['To'] = rows['email']
        msg['Subject'] = subject
        # attach image to message body
        msg.attach(MIMEImage(file("google.jpg").read()))
        msg.attach(MIMEText(message, 'plain'))
        # create server
        # send the message via the server.
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
"""
        return Response(serializer.data)
            
class GetVendorListData(viewsets.ModelViewSet):

    queryset = VendorListDataModel.objects.all()
    serializer_class = VendorListDataSerializer
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ["template__template_name", "created_at" , 'list__list_name']
    search_fields = ['template__template_name' ,'list__list_name' ,'email_to', 'vendor__contact_person_first_name' , 'vendor__contact_person_last_name' , 'vendor__primary_email']
    ordering_fields = ['template__template_name' , 'created_at']
    ordering = ['template__template_name' , 'created_at']

    def list(self, request):
        list_id = request.GET.get('list_id', None)
        queryset=VendorListDataModel.objects.filter(list_id = list_id)
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = VendorListDataSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = VendorListDataSerializer(self.queryset, many=True)
        return Response(serializer.data)
            
@csrf_exempt
@api_view(['POST'])
def add_mail_event(request, *args, **kwargs):
    print(request.data)
    if request.data is not None and request.data != '':
        MailEventsModel.objects.create(maildata = request.data)
        return Response(data= {'msg':"Success"}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@csrf_exempt
def get_vendor_fields(request, *args, **kwargs):
        print(request.data)
        queryset = vendorModel.objects.all()
        opts = queryset.model._meta
        field_names = [field.name for field in opts.fields]
        gendf = pd.DataFrame(columns=field_names)
        return Response(gendf)
        
class VendorBulkDeleteView(ListAPIView):
    model = None
    queryset = vendorModel.objects.none()
    serializer_class = VendorSerializer
    
    def post(self, request, *args, **kwargs):
        delete_ids = request.data['delete_ids'].split(',')  # should validate
        vendorModel.objects.filter(id__in=delete_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)