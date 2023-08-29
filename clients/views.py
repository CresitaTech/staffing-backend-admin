from uuid import uuid4

from django.db import connection
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
import copy

from candidates.models import Candidates
from clients.models import clientModel,ClientModelManager,ClientModelBackup
from clients.serializers import ClientSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework import generics
from rest_framework import status
from rest_framework import viewsets, filters
from rest_framework.filters import SearchFilter, OrderingFilter
from clients.filters import ClientFilter
from django_filters.rest_framework import DjangoFilterBackend
from comman_utils.utils import handle_file_upload, download_csv
from comman_utils.GetObjectQuerySet import GetObjectQuerySet
from users.models import User
from users.serializers import UserSerializer
from django.db.models import Q
from candidates.models import importFileModel
from candidates.serializers import ImportFileSerializer
from rest_framework.permissions import DjangoModelPermissions
import pandas as pd
import logging
from rest_framework.generics import get_object_or_404

# Get an instance of a logger
logger = logging.getLogger(__name__)

class ClientViewSet(viewsets.ModelViewSet):

    queryset = clientModel.objects.none()
    serializer_class = ClientSerializer
    permission_classes = [DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, ]  # SearchFilter,
    ordering_fields = ['first_name', 'company_name' ,'created_at']
    ordering = ['first_name', 'company_name' , 'created_at']
    filter_fields = ["first_name", "company_name", "created_at"]
    search_fields = ['first_name' ,'company_name' ,'created_at']
    filter_class = ClientFilter
    
    def list(self, request):
        clientObj = User.objects.get(pk=request.user.id)
        serializeObj = UserSerializer(clientObj)
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
        logger.info('userGroup Data: %s' % userGroup)
        if userGroup is not None and userGroup == 'ADMIN':
            queryset = clientModel.objects.all()
        elif userGroup is not None and userGroup == 'BDM MANAGER':
            queryset = clientModel.objects.filter(created_by_id=request.user.id)
            # print(str(queryset.query))
        elif userGroup is not None and userGroup == 'RECRUITER MANAGER':
            queryset = clientModel.objects.all()
            #queryset = clientModel.objects.filter(
             #   Q(created_by_id__created_by_id=request.user.id) | Q(created_by_id=request.user.id))
            # print(str(queryset.query))
        elif userGroup is not None and userGroup == 'RECRUITER':
            queryset = clientModel.objects.none()
            #queryset = clientModel.objects.filter(created_by_id=request.user.id)
            # print(str(queryset.query))
        else:
            queryset = clientModel.objects.none()

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ClientSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ClientSerializer(self.queryset, many=True)
        logger.info('Client List: ' + str(serializer.data))
        return Response(serializer.data)

    def create(self, request):
        logger.info('New Client Create data: ' + str(request.data))
        serializeObj = ClientSerializer(data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(created_by_id = request.user.id , updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        logger.error('Client Post Serialized Error: ' + str(serializeObj.errors))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return clientModel.objects.get(pk=pk)
        except clientModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        clientObj = self.get_object(pk)
        serializeObj = ClientSerializer(clientObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        logger.info('Update Client Data: ' + str(request.data))
        clientObj = self.get_object(pk)
        serializeObj = ClientSerializer(clientObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        logger.error('Client Update Serialized Error: ' + str(serializeObj.errors))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        client_obj = get_object_or_404(clientModel, pk=pk)
        candObj1 = copy.copy(client_obj)
        clientModel.objects.backup_clients(candObj1)
        client_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenerateUUID(GetObjectQuerySet):
    def get(self, request):
        uuid = uuid4()
        print(uuid)
        cursor = connection.cursor()
        cursor.execute("SELECT id, primary_email FROM osms_candidates " )
        rows = cursor.fetchall()
        # print(rows)
        for row in rows:
            print(row[1])
            cursor = connection.cursor()
            cursor.execute("UPDATE osms_candidates SET id= %s WHERE id = %s ", [str(uuid), str(row[0])])

        return Response({"uuid": uuid, "users": "all"})
        
class ExportClientModel(generics.ListAPIView):

    def get(self, request, format=None):
        response = download_csv(clientModel, request, clientModel.objects.all())
        return response
        
class ImportClientModel(generics.ListAPIView):
    queryset = importFileModel.objects.all()
    serializer_class = ImportFileSerializer
    permission_classes = []

    def post(self, request, format=None):
        fileObj = ImportFileSerializer(data=request.data)
        if fileObj.is_valid():
            fileObj.save(created_by_id = request.user.id , updated_by_id = request.user.id)
        queryset = clientModel.objects.all()
        opts = queryset.model._meta
        field_names = [field.name for field in opts.fields]
        gendf = pd.DataFrame(columns=field_names)
        print(fileObj.data['file'])
        file_path = '.' +str(fileObj.data['file'])
        df = pd.read_csv(file_path, delimiter=",")
        print(df.head())
        json  = fileObj.data['data_fields']
        print(json)
        for i in range(len(gendf.columns)):
            print(gendf.columns[i])
            # print(request.data.get(gendf.columns[i]))
            if request.data.get(gendf.columns[i]) is not None:
                print("======")
                try:
                    gendf[gendf.columns[i]] = df[request.data.get(gendf.columns[i])]
                except:
                    pass
            else:
                print("===: ")
                gendf[gendf.columns[i]] = None

                # print(df[request.data[gendf.columns[i]]])
        print("=================")
        print(gendf.head())
        df_records = gendf.to_dict('records')

        model_instances = [clientModel(
            first_name=record['first_name'],
            last_name=record['last_name'],
            primary_email=record['primary_email'],
            secondary_email=record['secondary_email'],
            primary_phone_number=record['primary_phone_number'],
            secondary_phone_number=record['secondary_phone_number'],
            skype_id=record['skype_id'],
            linkedin_id=record['linkedin_id'],
            primary_skills=record['primary_skills'],
            secondary_skills=record['secondary_skills'],
            company_name=record['company_name'],
            company_tin_number=record['company_tin_number'],
            total_employee=record['total_employee'],
            company_address=record['company_address'],
            about_company=record['about_company'],
            created_by=request.user.id,
            updated_by=request.user.id
            #created_at=record['created_at'],
            #updated_at=record['updated_at'],
        ) for record in df_records]

        clientModel.objects.bulk_create(model_instances)

        # print(field_names)
        return Response(fileObj.data)