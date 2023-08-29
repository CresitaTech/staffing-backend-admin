import re
import time
import uuid
import pandas as pd
from django.db import connection
from io import BytesIO
from django.core.files import File
from django.db.models import Q
from django.utils.html import format_html
from rest_framework.generics import ListAPIView
from rest_framework.permissions import DjangoModelPermissions

from candidates.filters import CandidateFilter
from candidates.models import Candidates, activityStatusModel, placementCardModel, candidatesSubmissionModel, \
    rtrModel, emailTemplateModel, mailModel, candidateStageModel , importFileModel
from rest_framework import viewsets, generics

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from candidates.serializers import CandidateSerializer, ActivityStatusSerializer, SubmissionSerializer, \
    PlacementCardSerializer, RTRSerializer, EmailTemplateSerializer, CandidateMailSerializer, CandidateWriteSerializer, \
    ActivityStatusWriteSerializer, \
    SubmissionWriteSerializer, PlacementCardWriteSerializer, RTRWriteSerializer, CandidateStageSerializer, \
    CandidateMailWriteSerializer, ImportFileSerializer, CandidateWriteFileSerializer , CandidatesDropdownListSerializer
from rest_framework.response import Response
from rest_framework import status
from candidates.utils import sendMail, sendRTRMail, sendSubmissionMail ,generate_doc , sendCandidateBDMMail , sendBDMMail ,sendClientMail
from comman_utils.utils import handle_file_upload, download_csv
from interviewers.models import designationModel
from interviewers.serializers import DesignationSerializer
from interviews.models import Mails
from clients.models import clientModel
from django.template.loader import render_to_string
from candidatesdocumentrepositery.models import candidatesRepositeryModel
from jobdescriptions.models import jobModel
from jobdescriptions.serializers import JobDescriptionListSerializer
from users.models import User
from users.serializers import UserSerializer


class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidates.objects.none()
    serializer_class = CandidateSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, ]  # SearchFilter,
    ordering_fields = ['first_name' , 'created_at']
    ordering = ['first_name' , 'created_at']
    filter_fields = ["first_name", "company_name", "created_at", ]
    search_fields = ['first_name' , 'skills_1' , 'skills_2']
    filter_class = CandidateFilter
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
            queryset = Candidates.objects.all()
        elif userGroup is not None and userGroup == 'BDM MANAGER':
            queryset = Candidates.objects.filter(job_description_id__created_by_id=request.user.id)
            # print(str(queryset.query))
        elif userGroup is not None and userGroup == 'RECRUITER MANAGER':
            queryset = Candidates.objects.all()
            # print(str(queryset.query))
        elif userGroup is not None and userGroup == 'RECRUITER':
            #queryset = Candidates.objects.filter(created_by_id=request.user.id)
            # print(str(queryset.query))
            queryset = Candidates.objects.all()
        else:
            queryset = Candidates.objects.none()

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CandidateSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CandidateSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = CandidateWriteSerializer(data=request.data)
        if serializeObj.is_valid():
            obj = serializeObj.save(created_by_id = request.user.id , updated_by_id = request.user.id)
            print(serializeObj.data)
            stage_id = str(serializeObj.data['stage']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            cursor = connection.cursor()
            cursor.execute("SELECT stage_name from candidates_stages WHERE id=%s", [stage_id])
            stage = cursor.fetchone()
            activityStatusModel.objects.create(candidate_name_id = obj.id ,activity_status=stage[0], created_by_id=request.user.id,
                      updated_by_id=request.user.id)
            candidatesRepositeryModel.objects.create(candidate_name_id=obj.id, resume=serializeObj.data['resume'],
                                                     created_by_id=request.user.id,
                                                     repo_name=str(request.data['first_name']) + ' Repo',
                                                     updated_by_id=request.user.id)
             
            if stage[0].strip() == 'SendOut':
                sendClientMail(request, stage_id, obj.id)
            elif stage[0].strip() != 'Candidate Added':
                sendBDMMail(request, obj.id, stage[0].strip())
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            # obj = Candidates.objects.get(pk=pk)
            obj = Candidates.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except Candidates.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = CandidateWriteSerializer(candObj)
        return Response(serializeObj.data)

    def partial_update(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = CandidateWriteSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            obj = serializeObj.save(updated_by_id=request.user.id)
            stage_id = str(serializeObj.data['stage']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            cursor = connection.cursor()
            cursor.execute("SELECT stage_name from candidates_stages WHERE id=%s", [stage_id])
            stage = cursor.fetchone()
            print(len(activityStatusModel.objects.filter(candidate_name_id=obj.id).order_by('-created_at')))
            #print(str(activityStatusModel.objects.filter(candidate_name_id=obj.id).order_by('-created_at')[0].activity_status))
            print(stage[0].strip())
            if len(activityStatusModel.objects.filter(candidate_name_id=obj.id).order_by('-created_at')) > 0:
                if str(activityStatusModel.objects.filter(candidate_name_id=obj.id).order_by('-created_at')[0].activity_status) != stage[0].strip():
                    activityStatusModel.objects.create(candidate_name_id=obj.id, activity_status=stage[0],
                                                   created_by_id=request.user.id,
                                                   updated_by_id=request.user.id)
                    if stage[0].strip() == 'SendOut':
                        sendClientMail(request, stage_id, obj.id)
                    elif stage[0].strip() != 'Candidate Added':
                        sendBDMMail(request, obj.id ,stage[0].strip())
            else:
                activityStatusModel.objects.create(candidate_name_id=obj.id, activity_status=stage[0],
                                                   created_by_id=request.user.id,
                                                   updated_by_id=request.user.id)
                if stage[0].strip() == 'SendOut':
                    sendClientMail(request, stage_id, obj.id)
                elif stage[0].strip() != 'Candidate Added':
                    sendBDMMail(request, obj.id, stage[0].strip())
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = CandidateWriteSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            obj = serializeObj.save(updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        candObj = self.get_object(pk)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ActivityStatusSet(viewsets.ModelViewSet):
    queryset = activityStatusModel.objects.all()
    serializer_class = ActivityStatusSerializer
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ["candidate_name__first_name", "created_at"]
    search_fields = ['candidate_name__first_name' ,'created_at']
    ordering_fields = ['candidate_name__first_name' , 'created_at']
    ordering = ['candidate_name__first_name' , 'created_at']
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        #candidateObj = activityStatusModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ActivityStatusSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ActivityStatusSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = ActivityStatusWriteSerializer(data=request.data)
        if serializeObj.is_valid():
            stage_id = str(serializeObj.validated_data['activity_status']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            cursor = connection.cursor()
            cursor.execute("SELECT stage_name from candidates_stages WHERE id=%s", [stage_id])
            stage = cursor.fetchone()
            serializeObj.save(activity_status=str(stage[0]), created_by_id=request.user.id,
                              updated_by_id=request.user.id)

            candidate_id = str(serializeObj.data['candidate_name']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
                
            Candidates.objects.filter(id=candidate_id).update(stage_id=stage_id , updated_by_id = request.user.id)

            if stage[0].strip() == 'SendOut':
                sendClientMail(request, request.data['activity_status'], serializeObj.data['candidate_name'])
            elif stage[0].strip() != 'Candidate Added':
                Candidates.objects.filter(id=candidate_id).update(stage_id=request.data['activity_status'])
                sendBDMMail(request, candidate_id, stage[0].strip())
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return activityStatusModel.objects.get(pk=pk)
        except activityStatusModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = ActivityStatusWriteSerializer(candObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = ActivityStatusWriteSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id = request.user.id)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        candObj = self.get_object(pk)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlacementCardSet(viewsets.ModelViewSet):
    queryset = placementCardModel.objects.all()
    serializer_class = PlacementCardSerializer
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ["candidate_name__first_name", "created_at"]
    search_fields = ['candidate_name__first_name' ,'created_at']
    ordering_fields = ['candidate_name__first_name' , 'created_at']
    ordering = ['candidate_name__first_name' , 'created_at']
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        #candidateObj = placementCardModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PlacementCardSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PlacementCardSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = PlacementCardWriteSerializer(data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(created_by_id = request.user.id , updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return placementCardModel.objects.get(pk=pk)
        except placementCardModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = PlacementCardWriteSerializer(candObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = PlacementCardWriteSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        candObj = self.get_object(pk)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubmissionSet(viewsets.ModelViewSet):
    queryset = candidatesSubmissionModel.objects.all()
    serializer_class = SubmissionSerializer
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ["candidate_name__first_name", "created_at"]
    search_fields = ['candidate_name__first_name' ,'created_at']

    def list(self, request):
        #candidateObj = candidatesSubmissionModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubmissionSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SubmissionSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = SubmissionWriteSerializer(data=request.data)
        if serializeObj.is_valid():
            serializeObj.save()
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return candidatesSubmissionModel.objects.get(pk=pk)
        except candidatesSubmissionModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = SubmissionWriteSerializer(candObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = SubmissionWriteSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save()
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        candObj = self.get_object(pk)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RTRSet(viewsets.ModelViewSet):
    queryset = rtrModel.objects.all()
    serializer_class = RTRSerializer
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ["candidate_name__first_name", "created_at"]
    search_fields = ['candidate_name__first_name' ,'created_at']
    ordering_fields = ['candidate_name__first_name' , 'created_at']
    ordering = ['candidate_name__first_name' , 'created_at']
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        #candidateObj = rtrModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RTRSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = RTRSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = RTRWriteSerializer(data=request.data)
        if serializeObj.is_valid():
            obj = serializeObj.save()
            print(obj.id)
            if '-' in str(obj.id):
                obj.id = str(obj.id).replace('-' , '')
            s = generate_doc(obj.id)
            
            candidate_id = str(obj.candidate_name_id).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            cursor = connection.cursor()
            print(obj.candidate_name_id)
            print(obj)
            #print(serializeObj.validated_data)
            print(candidate_id)
            cursor.execute("SELECT first_name , last_name , job_description_id FROM osms_candidates where id=%s",
                           [candidate_id])
            candidate = cursor.fetchone()
            print(candidate)
            
            cursor.execute("SELECT job_title, client_name_id FROM osms_job_description where id=%s",
                           [candidate[2]])
            jd = cursor.fetchone()
            if jd is not None:
                cursor.execute("SELECT company_name FROM osms_clients where id=%s",
                               [jd[1]])
                client = cursor.fetchone()
                filename = str(candidate[0])+ '_' +str(candidate[1]) + str(uuid.uuid4()) + ".docx"
                serializeObj.save(rtr_doc=File(name=filename, file=BytesIO(s)) , created_by_id = request.user.id , updated_by_id = request.user.id)
                
                
                context_email = {'sender_name': request.user.first_name + ' ' + request.user.last_name,
                                 'candidate_name': candidate[0]}
                mail = Mails()
                mail.subject = "RTR Document: "+ jd[0]+'-'+client[0]
                mail.from_email = request.user.email
                mail.email = serializeObj.data['email']
                mail.resume = None
                mail.jd = serializeObj.data['rtr_doc']
                mail.message = render_to_string('rtr_email.html', context_email)
                mail.condidate_email = None
                setattr(mail , 'cc_email' , request.user.email)
                sendRTRMail(request, mail)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return rtrModel.objects.get(pk=pk)
        except rtrModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = RTRWriteSerializer(candObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = RTRWriteSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            obj = serializeObj.save()
            print(obj.id)
            if '-' in str(obj.id):
                obj.id = str(obj.id).replace('-' , '')
            s = generate_doc(obj.id)
            
            candidate_id = str(obj.candidate_name_id).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            cursor = connection.cursor()
            print(obj.candidate_name_id)
            print(obj)
            #print(serializeObj.validated_data)
            print(candidate_id)
            cursor.execute("SELECT first_name , last_name , job_description_id FROM osms_candidates where id=%s",
                           [candidate_id])
            candidate = cursor.fetchone()
            print(candidate)
            cursor.execute("SELECT job_title, client_name_id FROM osms_job_description where id=%s",
                           [candidate[2]])
            jd = cursor.fetchone()
            if jd is not None:
                cursor.execute("SELECT company_name FROM osms_clients where id=%s",
                               [jd[1]])
                client = cursor.fetchone()
                filename = str(candidate[0])+ '_' +str(candidate[1]) + str(uuid.uuid4()) + ".docx"
                serializeObj.save(rtr_doc=File(name=filename, file=BytesIO(s)) , updated_by_id = request.user.id)
                
                
                context_email = {'sender_name': request.user.first_name + ' ' + request.user.last_name,
                                 'candidate_name': candidate[0]}
                mail = Mails()
                mail.subject = "RTR Document: "+ jd[0]+'-'+client[0]
                mail.from_email = request.user.email
                mail.email = serializeObj.data['email']
                mail.resume = None
                mail.jd = serializeObj.data['rtr_doc']
                mail.message = render_to_string('rtr_email.html', context_email)
                mail.condidate_email = None
                setattr(mail , 'cc_email' , request.user.email)
                sendRTRMail(request, mail)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        candObj = self.get_object(pk)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailTemplateSet(viewsets.ModelViewSet):
    queryset = emailTemplateModel.objects.all()
    serializer_class = EmailTemplateSerializer
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ["template_name", "created_at"]
    search_fields = ['template_name' ,'created_at']
    ordering_fields = ['template_name' , 'created_at']
    ordering = ['template_name' , 'created_at']
    permission_classes = [DjangoModelPermissions]

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
            return emailTemplateModel.objects.get(pk=pk)
        except emailTemplateModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = EmailTemplateSerializer(candObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = EmailTemplateSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        candObj = self.get_object(pk)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CandidateMailSet(viewsets.ModelViewSet):
    queryset = mailModel.objects.all()
    serializer_class = CandidateMailSerializer
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ["candidate_template__template_name",'vendor_template__template_name' ,  "created_at"]
    search_fields = ['candidate_template__template_name' ,'vendor_template__template_name' ,'created_at']
    ordering_fields = ['candidate_template__template_name' ,'vendor_template__template_name' , 'created_at']
    ordering = ['candidate_template__template_name' ,'vendor_template__template_name', 'created_at']
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        #candidateObj = mailModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CandidateMailSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CandidateMailSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = CandidateMailWriteSerializer(data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(created_by_id = request.user.id , updated_by_id = request.user.id)
            if (serializeObj.data['tag'] == 'Candidate'):
                send_candidate_mail(request, serializeObj.data)
            elif (serializeObj.data['tag'] == 'Vendor'):
                send_vendor_mail(request, serializeObj.data)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return mailModel.objects.get(pk=pk)
        except mailModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = CandidateMailWriteSerializer(candObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = CandidateMailWriteSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        candObj = self.get_object(pk)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
        
class CandidateStageViewSet(viewsets.ModelViewSet):
    # permission_classes = [DjangoObjectPermissions]
    queryset = candidateStageModel.objects.all()
    serializer_class = CandidateStageSerializer


class ExportCandidateModel(generics.ListAPIView):

    def get(self, request, format=None):
        response = download_csv(Candidates, request, Candidates.objects.all())
        return response


"""
Method is used for sending rtr mails by passing object
"""


def send_rtr_mail(request, obj):
    cursor = connection.cursor()
    cursor.execute("SELECT first_name , last_name , id FROM osms_candidates where primary_email=%s",
                   [obj.email_to])
    condidate = cursor.fetchone()
    context_email = {'sender_name': request.user.first_name + ' ' + request.user.last_name,
                     'candidate_name': condidate[0] + ' ' + condidate[1],
                     'email_body': obj.body}
    cursor.execute("SELECT rtr_doc FROM candidates_rtr where candidate_name_id=%s",
                   [condidate[2]])
    rtr = cursor.fetchone()
    mail = Mails()
    mail.subject = obj.subject
    mail.from_email = obj.email_from
    mail.email = obj.email_to
    mail.resume = None
    mail.jd = rtr[0]
    mail.message = render_to_string('rtr_email.html', context_email)
    mail.condidate_email = None
    if obj.cc_email != None:
        # print(obj.mail_cc)
        if ',' in obj.cc_email:
            cc_emails = obj.cc_email.strip().split(',')
            setattr(mail, 'cc_emails', cc_emails)
        else:
            setattr(mail, 'cc_email', obj.cc_email)

    sendRTRMail(request, mail)


"""
Method used for sending submission mail to client
"""


def send_submission_mail(request, obj):
    cursor = connection.cursor()
    cursor.execute("SELECT * from osms_clients WHERE primary_email =%s", [obj.client_email])
    client = cursor.fetchone()
    context_email = {'sender_name': request.user.first_name + ' ' + request.user.last_name,
                     'client_name': client[1] + ' ' + client[2],
                     'email_body': obj.email_body}
    mail = Mails()
    mail.subject = obj.email_subject
    mail.from_email = obj.email_from
    mail.email = obj.client_email
    mail.resume = None
    mail.jd = obj.email_attachment
    mail.message = render_to_string('candidates_submission.html', context_email)
    mail.condidate_email = None
    if obj.email_cc != None:
        # print(obj.mail_cc)
        if ',' in obj.email_cc:
            cc_emails = obj.email_cc.strip().split(',')
            setattr(mail, 'cc_emails', cc_emails)
        else:
            setattr(mail, 'cc_email', obj.email_cc)

    sendSubmissionMail(request, mail)
    new_rank = client[len(client) - 1] + 1
    clientModel.objects.filter(id=int(client[0])).update(rank=new_rank)

        
"""
Method for sending mails to indiviual or bulk mail request
"""
        
def send_candidate_mail(request , obj):
    print(obj)
    template_id = str(obj['candidate_template']).replace('UUID', ''). \
        replace('(\'', '').replace('\')', '').replace('-', '')
    cursor = connection.cursor()
    cursor.execute("SELECT subject , body , signature FROM osms_email_templates where id=%s",
                   [template_id])
    template = cursor.fetchone()
    subject = str(template[0])
    body = str(template[1])
    signature = str(template[2])
    # print(body)
    if ',' in obj['email_to']:
        emails_to = obj['email_to'].strip().rstrip(',').split(',')
        for email_to in emails_to:
            email = email_to.strip()
            subject = str(template[0])
            body = str(template[1])
            signature = str(template[2])
            print(email_to)
            print(body)
            matches = re.findall('{(.*?)}', body)
            print(matches)
            for item in matches:
                print(item)
                if str(item) == 'designation':
                    cursor.execute('SELECT designation_id FROM osms_candidates where primary_email=%s',
                                   [email])
                    designation = cursor.fetchone()
                    cursor.execute('SELECT name FROM interviewers_designation where id=%s',
                                   [designation[0]])
                    designation_name = cursor.fetchone()
                    tag = '{' + item + '}'
                    # print(candidate[0])
                    body = body.replace(tag, str(designation_name[0]))
                    continue

                cursor.execute('SELECT ' + str(item) + ' FROM osms_candidates where primary_email=%s',
                               [email])
                candidate = cursor.fetchone()
                print(candidate)
                tag = '{' + item + '}'
                # print(candidate[0])
                if candidate[0] is not None:
                    body = body.replace(tag, candidate[0])
                else:
                    body = body.replace(tag, '')
            print(body)

            matches = re.findall('{(.*?)}', subject)
            print(matches)
            for item in matches:
                print(item)
                if str(item) == 'designation':
                    cursor.execute('SELECT designation_id FROM osms_candidates where primary_email=%s',
                                   [email])
                    designation = cursor.fetchone()
                    cursor.execute('SELECT name FROM interviewers_designation where id=%s',
                                   [designation[0]])
                    designation_name = cursor.fetchone()
                    tag = '{' + item + '}'
                    # print(candidate[0])
                    subject = subject.replace(tag, str(designation_name[0]))
                    continue
                    
                cursor.execute('SELECT ' + str(item) + ' FROM osms_candidates where primary_email=%s',
                               [email])
                candidate = cursor.fetchone()
                tag = '{' + item + '}'
                
                if candidate[0] is not None:
                    subject = subject.replace(tag, candidate[0])
                else:
                    subject = subject.replace(tag, '')

            body = format_html(
                '<pre  style=\"text-align:left;font-size: medium;font-family: sans-serif;;background: no-repeat;border: none;white-space:pre-wrap;\">' + body + '</pre>')
            body = body + format_html(
                '<pre style=\"text-align:left;font-size: medium;font-family: sans-serif;;background: no-repeat;border: none;white-space:pre-wrap;\">' + signature + '</pre><br>')

            context_email1 = {'body': body}
            mail = Mails()
            mail.subject = subject
            mail.from_email = request.user.email.strip()
            mail.email = email.strip()
            mail.jd = None
            mail.resume = obj['candidate_attachment']
            mail.message = render_to_string('email_template.html', context_email1)
            mail.condidate_email = None
            setattr(mail, 'cc_email', request.user.email.strip())
            sendMail(request, mail)
            time.sleep(5)

    else:
        matches = re.findall('{(.*?)}', body)
        # print(matches)
        for item in matches:
            print(item)
            if str(item) == 'designation':
                cursor.execute('SELECT designation_id FROM osms_candidates where primary_email=%s',
                               [obj['email_to']])
                designation = cursor.fetchone()
                cursor.execute('SELECT name FROM interviewers_designation where id=%s',
                               [designation[0]])
                designation_name = cursor.fetchone()
                tag = '{' + item + '}'
                # print(candidate[0])
                body = body.replace(tag, str(designation_name[0]))
                continue
                
            cursor.execute('SELECT ' + str(item) + ' FROM osms_candidates where primary_email=%s',
                           [obj['email_to']])
            candidate = cursor.fetchone()
            print(candidate)
            tag = '{' + item + '}'
            if candidate[0] is not None:
                body = body.replace(tag, candidate[0])
            else:
                body = body.replace(tag, '')

        matches = re.findall('{(.*?)}', subject)
        print(matches)
        for item in matches:
            print(item)
            if str(item) == 'designation':
                cursor.execute('SELECT designation_id FROM osms_candidates where primary_email=%s',
                               [obj['email_to']])
                designation = cursor.fetchone()
                cursor.execute('SELECT name FROM interviewers_designation where id=%s',
                               [designation[0]])
                designation_name = cursor.fetchone()
                tag = '{' + item + '}'
                # print(candidate[0])
                subject = subject.replace(tag, str(designation_name[0]))
                continue
                
            cursor.execute('SELECT ' + str(item) + ' FROM osms_candidates where primary_email=%s',
                           [obj['email_to']])
            candidate = cursor.fetchone()
            tag = '{' + item + '}'
            
            if candidate[0] is not None:
                subject = subject.replace(tag, candidate[0])
            else:
                subject = subject.replace(tag, '')

        body = format_html(
            '<pre  style=\"text-align:left;font-size: medium;font-family: sans-serif;;background: no-repeat;border: none;white-space:pre-wrap;\">' + body + '</pre>')
        body = body + format_html(
            '<pre style=\"text-align:left;font-size: medium;font-family: sans-serif;;background: no-repeat;border: none;white-space:pre-wrap;\">' + signature + '</pre><br>')

        context_email1 = {'body': body}

        print(obj['email_to'].strip())
        mail = Mails()
        mail.subject = subject
        mail.from_email = request.user.email.strip()
        mail.email = obj['email_to'].strip()
        mail.jd = None
        mail.resume = obj['candidate_attachment']
        mail.message = render_to_string('email_template.html', context_email1)
        mail.condidate_email = None
        setattr(mail, 'cc_email', request.user.email.strip())
        sendMail(request, mail)
        
def send_vendor_mail(request , obj):
    print(obj)
    template_id = str(obj['vendor_template']).replace('UUID', ''). \
        replace('(\'', '').replace('\')', '').replace('-', '')
    cursor = connection.cursor()
    cursor.execute("SELECT subject , body , signature  FROM osms_vendor_templates where id=%s",
                   [template_id])
    template = cursor.fetchone()
    subject = str(template[0])
    body = str(template[1])
    signature = str(template[2])
    # unsubscribe_url = str(template[3])
    # print(body)
    if ',' in obj['email_to']:
        emails_to = obj['email_to'].strip().rstrip(',').split(',')
        for email_to in emails_to:
            email = email_to.strip()
            subject = str(template[0])
            body = str(template[1])
            signature = str(template[2])
            # unsubscribe_url = str(template[3])
            print(email_to)
            matches = re.findall('{(.*?)}', body)
            # print(matches)
            for item in matches:
                print(item)
                cursor = connection.cursor()
                cursor.execute('SELECT ' + str(item) + ' FROM osms_vendors where primary_email=%s',
                               [email])
                vendor = cursor.fetchone()
                print(vendor)
                tag = '{' + item + '}'
                # print(candidate[0])
                if vendor[0] is not None:
                    body = body.replace(tag, vendor[0])
                else:
                    body = body.replace(tag, '')
            print(body)

            matches = re.findall('{(.*?)}', subject)
            print(matches)
            for item in matches:
                print(item)
                cursor.execute('SELECT ' + str(item) + ' FROM osms_vendors where primary_email=%s',
                               [email])
                vendor = cursor.fetchone()
                tag = '{' + item + '}'
                
                if vendor[0] is not None:
                    subject = subject.replace(tag, vendor[0])
                else:
                    subject = subject.replace(tag, '')

            body = format_html(
                '<pre  style=\"text-align:left;font-size: medium;font-family: sans-serif;;background: no-repeat;border: none;white-space:pre-wrap;\">' + body + '</pre>')
            body = body + format_html(
                '<pre style=\"text-align:left;font-size: medium;font-family: sans-serif;;background: no-repeat;border: none;white-space:pre-wrap;\">' + signature + '</pre><br>')

            context_email1 = {'body': body}
            mail = Mails()
            mail.subject = subject
            mail.from_email = request.user.email.strip()
            mail.email = email.strip()
            mail.jd = None
            mail.resume = obj['vendor_attachment']
            mail.message = render_to_string('email_template.html', context_email1)
            mail.condidate_email = None
            setattr(mail, 'cc_email', request.user.email.strip())
            sendMail(request, mail)
            time.sleep(5)

    else:
        matches = re.findall('{(.*?)}', body)
        # print(matches)
        for item in matches:
            print(item)
            cursor.execute('SELECT ' + str(item) + ' FROM osms_vendors where primary_email=%s',
                           [obj['email_to']])
            vendor = cursor.fetchone()
            tag = '{' + item + '}'
            
            if vendor[0] is not None:
                body = body.replace(tag, vendor[0])
            else:
                body = body.replace(tag, '')

        matches = re.findall('{(.*?)}', subject)
        print(matches)
        for item in matches:
            print(item)
            cursor.execute('SELECT ' + str(item) + ' FROM osms_vendors where primary_email=%s',
                           [obj['email_to']])
            vendor = cursor.fetchone()
            tag = '{' + item + '}'
            
            if vendor[0] is not None:
                subject = subject.replace(tag, vendor[0])
            else:
                subject = subject.replace(tag, '')

        body = format_html(
            '<pre  style=\"text-align:left;font-size: medium;font-family: sans-serif;;background: no-repeat;border: none;white-space:pre-wrap;\">' + body + '</pre>')
        body = body + format_html(
            '<pre style=\"text-align:left;font-size: medium;font-family: sans-serif;;background: no-repeat;border: none;white-space:pre-wrap;\">' + signature + '</pre><br>')
        context_email1 = {'body': body}

        print(obj['email_to'].strip())
        mail = Mails()
        mail.subject = subject
        mail.from_email = request.user.email.strip()
        mail.email = obj['email_to'].strip()
        mail.jd = None
        mail.resume = obj['vendor_attachment']
        mail.message = render_to_string('email_template.html', context_email1)
        mail.condidate_email = None
        setattr(mail, 'cc_email', request.user.email.strip())
        sendMail(request, mail)


class ExportCandidateModel(generics.ListAPIView):
    queryset = Candidates.objects.none()
    serializer_class = CandidateSerializer

    def get(self, request, format=None):
        response = download_csv(Candidates, request, Candidates.objects.all())
        return response


class ImportCandidates(generics.ListAPIView):
    queryset = importFileModel.objects.all()
    serializer_class = ImportFileSerializer
    permission_classes = []

    def post(self, request, format=None):
        fileObj = ImportFileSerializer(data=request.data)
        if fileObj.is_valid():
            fileObj.save(created_by_id = request.user.id , updated_by_id = request.user.id)
        queryset = Candidates.objects.all()
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

        model_instances = [Candidates(
            first_name=record['first_name'],
            last_name=record['last_name'],
            date_of_birth=record['date_of_birth'],
            primary_email=record['primary_email'],
            secondary_email=record['secondary_email'],
            primary_phone_number=record['primary_phone_number'],
            secondary_phone_number=record['secondary_phone_number'],
            company_name=record['company_name'],
            designation=fileObj.data['data_fields']['designation'],
            skills_1=record['skills_1'],
            skills_2=record['skills_2'],
            min_salary=record['min_salary'],
            max_salary=record['min_salary'],
            min_rate=record['min_rate'],
            max_rate=record['min_rate'],
            qualification=record['qualification'],
            visa=record['visa'],
            current_location=record['current_location'],
            total_experience=record['total_experience'],
            reason_for_job_change=record['reason_for_job_change'],
            rtr_done=record['rtr_done'],
            willing_to_work_on_our_w2=record['willing_to_work_on_our_w2'],
            open_for_relocation=record['open_for_relocation'],
            rank=record['rank'],
            total_experience_in_usa=record['total_experience_in_usa'],
            any_offer_in_hand=record['any_offer_in_hand'],
            remarks=record['remarks'],
            stage=fileObj.data['data_fields']['stage'],
            job_description=fileObj.data['data_fields']['job_description'],
            recruiter_name=record['recruiter_name'],
            created_by=request.user.id,
            updated_by=request.user.id
            #created_at=record['created_at'],
            #updated_at=record['updated_at'],
        ) for record in df_records]

        Candidates.objects.bulk_create(model_instances)

        # print(field_names)
        return Response(fileObj.data)

class GetCandidatesList(generics.ListAPIView):
    queryset = jobModel.objects.none()

    def get(self, request, format=None):
        sql = "SELECT id, first_name , last_name FROM osms_candidates"
        queryset = jobModel.objects.raw(sql)
        serializer = CandidatesDropdownListSerializer(queryset, many=True)
        return Response(serializer.data)
    