import logging
import os

from parsers.models import ParserModel
from parsers.serializers import ParserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, filters, generics
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.permissions import AllowAny

from parsers.utils import extract_text_from_doc, extract_name, extract_mobile_number, extract_email, extract_skills, \
    extract_education, extract_text_from_pdf
from staffingapp.settings import MEDIA_URL, BASE_DIR
from users.models import User
from users.serializers import UserSerializer
from resume_parser import resumeparse
import spacy

logger = logging.getLogger(__name__)


"""class ParserViewSet(viewsets.ModelViewSet):
    queryset = ParserModel.objects.all()
    serializer_class = ParserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, ]  # SearchFilter,
    ordering_fields = ['job_title', 'created_at']
    ordering = ['job_title', 'created_at']
    filter_fields = ["job_title", "created_at"]
    search_fields = ['=job_title']
    permission_classes = [AllowAny]

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

        if userGroup is not None and userGroup == 'ADMIN':
            queryset = ParserModel.objects.all()
        elif userGroup is not None and userGroup == 'BDM MANAGER':
            queryset = ParserModel.objects.filter(created_by_id=request.user.id)
            # print(str(queryset.query))
        elif userGroup is not None and userGroup == 'RECRUITER MANAGER':
            queryset = ParserModel.objects.all()
            # print(str(queryset.query))
        elif userGroup is not None and userGroup == 'RECRUITER':
            # queryset = vendorModel.objects.none()
            queryset = ParserModel.objects.filter(created_by_id=request.user.id)
            # print(str(queryset.query))
        else:
            queryset = ParserModel.objects.none()

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ParserSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ParserSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = ParserSerializer(data=request.data)
        if serializeObj.is_valid():
            obj = serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id)
            logger.info(obj.resume)
            file_path = '/home/admin/projectDir/staging/staffingapp/media/'+str(obj.resume)  # full path to text.
            logger.info(file_path)

            text = "None"
            for page in extract_text_from_pdf(file_path):
                text += ' ' + page

            # print(text)

            # text = extract_text_from_doc("resume.docx");
            logger.info(text)
            logger.info(extract_name(text))
            logger.info(extract_mobile_number(text))
            logger.info(extract_email(text))
            # logger.info(extract_skills(text))
            logger.info(extract_education(text))

            data = resumeparse.read_file(file_path)
            logger.info(data)

            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return ParserModel.objects.get(pk=pk)
        except ParserModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        vendorObj = self.get_object(pk)
        serializeObj = ParserSerializer(vendorObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        vendorObj = self.get_object(pk)
        serializeObj = ParserSerializer(vendorObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        vendorObj = self.get_object(pk)
        vendorObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)"""

