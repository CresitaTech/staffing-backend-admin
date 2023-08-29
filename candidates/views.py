import datetime
import re
import time
import uuid
from dataclasses import fields
from itertools import chain
import copy
import pandas as pd
import ast
from django.db import connection
from io import BytesIO
from django.core.files import File
from django.db.models import Q
from django.utils.html import format_html
from docx.document import Document
from rest_framework.generics import ListAPIView
from rest_framework.permissions import DjangoModelPermissions
from django.http import HttpResponse
import csv
import os
from io import StringIO
from django.core.files import File
from django.http import HttpResponse, StreamingHttpResponse
from django.utils.text import slugify

from candidates.filters import CandidateFilter
from candidates.models import Candidates,CandidateModelManager,CandidateModelBackup, activityStatusModel, placementCardModel, candidatesSubmissionModel, \
    rtrModel, emailTemplateModel, mailModel, candidateStageModel, importFileModel, candidatesJobDescription, \
    candidateResumesModel, internalCandidatesJobDescription
from rest_framework import viewsets, generics

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from candidates.serializers import CandidateSerializer, ActivityStatusSerializer, SubmissionSerializer, \
    PlacementCardSerializer, RTRSerializer, EmailTemplateSerializer, CandidateMailSerializer, CandidateWriteSerializer, \
    ActivityStatusWriteSerializer, \
    SubmissionWriteSerializer, PlacementCardWriteSerializer, RTRWriteSerializer, CandidateStageSerializer, \
    CandidateMailWriteSerializer, ImportFileSerializer, CandidateWriteFileSerializer, CandidatesDropdownListSerializer, \
    CandidateJobsStagesSerializer, CandidateJobsStagesWriteSerializer, CandidateExportSerializer, \
    CandidatesSubmissionForJobListSerializer, CandidatesForSubmissionJobSerializer, \
    InternalCandidateJobsStagesSerializer, InternalCandidateJobsStagesWriteSerializer
from rest_framework.response import Response
from rest_framework import status
from candidates.utils import sendMail, sendRTRMail, sendSubmissionMail, generate_doc, sendCandidateBDMMail, sendBDMMail, \
    sendClientMail
from comman_utils.data_preprocessing import extractContent
from comman_utils.utils import handle_file_upload, download_csv, get_current_date
from interviewers.models import designationModel
from interviewers.serializers import DesignationSerializer
from interviews.models import Mails
from clients.models import clientModel
from django.template.loader import render_to_string
from candidatesdocumentrepositery.models import candidatesRepositeryModel
from jobdescriptions.models import jobModel, jobAssingmentModel
from jobdescriptions.serializers import JobDescriptionListSerializer, JobAssingmentSerializer
from jobdescriptions.utils import render_to_pdf
from django.conf import settings
from staffingapp.settings import GLOBAL_ROLE
from users.models import User
from users.serializers import UserSerializer
# import the logging library
import logging
from candidates import utils

# Get an instance of a logger
logger = logging.getLogger(__name__)

BASE_DIR = settings.BASE_DIR


class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidates.objects.none()
    serializer_class = CandidateSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, ]  # SearchFilter,
    ordering_fields = ['first_name', 'created_at']
    ordering = ['first_name', 'created_at']
    filter_fields = ["first_name", "company_name", "created_at", ]
    search_fields = ['first_name', 'last_name', 'skills_1', 'skills_2', 'job_description__job_title', 'primary_email',
                     'job_description__client_name__company_name', 'total_experience_in_usa']
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
        # print(userGroup)
        logger.info('userGroup Data: %s' % userGroup)
        uid = str(request.user.id).replace("-", "")

        if userGroup is not None and userGroup == 'ADMIN':
            if request.query_params.get('action'):
                queryset = Candidates.objects.filter(job_description__created_by_id=request.user.id)
            else:
                queryset = Candidates.objects.all()
        elif userGroup is not None and userGroup == 'BDM MANAGER':
            if request.query_params.get('action'):
                querysetJS = candidatesJobDescription.objects.values('candidate_name_id').exclude(
                    stage_id__stage_name='Candidate Added').filter(
                    job_description_id__in=jobModel.objects.filter(created_by_id=request.user.id))
                queryset = Candidates.objects.filter(id__in=querysetJS)
                # exclude(stage__stage_name='Candidate Added'). values('job_description_id').
                """queryset = Candidates.objects.raw(
                    "SELECT c.id, c.first_name, c.last_name, c.date_of_birth, c.primary_email, c.secondary_email, "
                    "c.primary_phone_number, c.secondary_phone_number, c.company_name, c.skills_1, c.skills_2, "
                    "c.max_salary, c.qualification, c.visa, c.current_location, c.total_experience, "
                    "c.reason_for_job_change, c.rtr_done, c.willing_to_work_on_our_w2, c.open_for_relocation, c.rank, "
                    "c.resume, c.remarks, c.status, c.recruiter_name, c.created_at, c.created_by_id, "
                    "c.updated_by_id, c.designation_id, c.any_offer_in_hand, c.total_experience_in_usa, "
                    "c.max_rate, c.min_rate, c.min_salary, c.employer_email, c.employer_name, c.employer_phone_number "
                    ", c.engagement_type, c.additional_qualification, c.certification, c.resume_raw_data FROM "
                    "osms_candidates as c, candidates_stages as s, osms_job_description as j , candidates_jobs_stages "
                    "as cjs WHERE j.id = cjs.job_description_id AND c.id = cjs.candidate_name_id AND cjs.stage_id = "
                    "s.id AND s.stage_name != 'Candidate Added' AND j.created_by_id = %s",
                    [uid])"""
            else:
                queryset = Candidates.objects.all()
        elif userGroup is not None and userGroup == 'RECRUITER MANAGER':
            if request.query_params.get('action'):
                queryset = Candidates.objects.filter(created_by_id=request.user.id)
            else:
                queryset = Candidates.objects.all()
        elif userGroup is not None and userGroup == 'RECRUITER':
            if request.query_params.get('action'):
                queryset = Candidates.objects.filter(
                    created_by_id=request.user.id)  # exclude(stage__stage_name='Candidate Added').
            else:
                queryset = Candidates.objects.all()
        else:
            queryset = Candidates.objects.none()

        logger.info('Query MyCandidate')
        logger.info(queryset.query)

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CandidateSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CandidateSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        df = pd.DataFrame()
        driving_license = None
        offer_letter = None
        passport = None
        rtr = None
        salary_slip = None
        i94_document = None
        visa_copy = None
        educational_document = None
        resume = None
        certification_doc = None
        additional_qualification_doc = None

        logger.info('New Candidate created request data: ' + str(request.data))
        logger.info('New Candidate job_descriptions length: ' + str(len(request.data['job_descriptions'])))

        if len(request.data['job_descriptions']) > 2:
            df = pd.DataFrame(ast.literal_eval(request.data['job_descriptions']))
            # request.data.pop('job_descriptions')
            # print(df) 
            job_descriptions = df['job'].tolist()
        else:
            request.data.pop('job_descriptions')
            job_descriptions = []

        serializeObj = CandidateWriteSerializer(data=request.data)
        if serializeObj.is_valid():
            logger.info('Serialized New Candidate Data: ' + str(serializeObj.validated_data))
            if 'driving_license' in serializeObj.validated_data:
                driving_license = serializeObj.validated_data['driving_license']
                serializeObj.validated_data.pop('driving_license')

            if 'offer_letter' in serializeObj.validated_data:
                offer_letter = serializeObj.validated_data['offer_letter']
                serializeObj.validated_data.pop('offer_letter')

            if 'passport' in serializeObj.validated_data:
                passport = serializeObj.validated_data['passport']
                serializeObj.validated_data.pop('passport')

            if 'rtr' in serializeObj.validated_data:
                rtr = serializeObj.validated_data['rtr']
                serializeObj.validated_data.pop('rtr')

            if 'salary_slip' in serializeObj.validated_data:
                salary_slip = serializeObj.validated_data['salary_slip']
                serializeObj.validated_data.pop('salary_slip')

            if 'i94_document' in serializeObj.validated_data:
                i94_document = serializeObj.validated_data['i94_document']
                serializeObj.validated_data.pop('i94_document')

            if 'visa_copy' in serializeObj.validated_data:
                visa_copy = serializeObj.validated_data['visa_copy']
                serializeObj.validated_data.pop('visa_copy')

            if 'educational_document' in serializeObj.validated_data:
                educational_document = serializeObj.validated_data['educational_document']
                serializeObj.validated_data.pop('educational_document')

            if 'certification_doc' in serializeObj.validated_data:
                certification_doc = serializeObj.validated_data['certification_doc']
                serializeObj.validated_data.pop('certification_doc')

            if 'additional_qualification_doc' in serializeObj.validated_data:
                additional_qualification_doc = serializeObj.validated_data['additional_qualification_doc']
                serializeObj.validated_data.pop('additional_qualification_doc')

            if 'resume' in serializeObj.validated_data:
                resume = serializeObj.validated_data['resume']
                # print(resume)
                # print(request.data['resume'])

            """            if 'resume_raw_data' in serializeObj.validated_data:
                resume_raw_data = serializeObj.validated_data['resume_raw_data']
                context = {'instance': serializeObj.validated_data}
                pdf = render_to_pdf('resume_raw_data_template.html', context)
                filename = str(serializeObj.validated_data['first_name']) + '-' + str(request.user.id) + ".pdf"

                obj = serializeObj.save(resume=File(name=filename, file=BytesIO(pdf.content)),
                                        updated_by_id=request.user.id, created_by_id=request.user.id,
                                        job_description=job_descriptions)
            else:
                logger.info("No need to create resume file")
                obj = serializeObj.save(updated_by_id=request.user.id, created_by_id=request.user.id,
                                        job_description=job_descriptions)"""

            obj = serializeObj.save(updated_by_id=request.user.id, created_by_id=request.user.id,
                                    job_description=job_descriptions)

            candidatesRepositeryModel.objects.create(candidate_name_id=obj.id, resume=resume,
                                                     driving_license=driving_license,
                                                     created_by_id=request.user.id, offer_letter=offer_letter,
                                                     passport=passport, rtr=rtr, salary_slip=salary_slip,
                                                     repo_name=str(request.data['first_name']) + ' ' + str(
                                                         request.data['last_name']) + ' Repo',
                                                     updated_by_id=request.user.id, i94_document=i94_document,
                                                     visa_copy=visa_copy,
                                                     educational_document=educational_document,
                                                     certification_doc=certification_doc,
                                                     additional_qualification_doc=additional_qualification_doc)
            logger.info("obj.resume: " + str(obj.resume))
            if obj.resume is not None:
                job_title = None
                if len(job_descriptions) > 0:
                    job = jobModel.objects.get(pk=job_descriptions[0])
                    job_title = job.job_title
                logger.info("obj.resume: " + str(obj.resume))
                notes = df['notes'].tolist()
                resume_data = extractContent(obj.resume)
                resumeObj = candidateResumesModel()
                resumeObj.candidates = obj
                resumeObj.job_title = job_title
                resumeObj.candidate_resume_data = resume_data
                resumeObj.notes = str(notes[0])
                resumeObj.save()

            if len(serializeObj.data['job_description']) > 0:
                i = 0
                job_description = df['job'].tolist()
                stages = df['status'].tolist()
                submission_dates = df['submission_date'].tolist()
                notes = df['notes'].tolist()
                send_out_dates = df['send_out_date'].tolist()
                stage_names = df['stage_name'].tolist()
                # print(notes)
                # print(len(notes))
                # print(send_out_dates)
                # print(len(send_out_dates))

                for item in range(0, len(df)):
                    logger.info('New Candidate created Job: ' + job_descriptions[i])
                    logger.info('New Candidate created Stage: ' + stages[i])
                    logger.info('New Candidate created Submission Date: ' + submission_dates[i])

                    activityStatusModel.objects.create(candidate_name_id=obj.id, activity_status=stage_names[i].strip(),
                                                       job_id_id=job_description[i],
                                                       created_by_id=request.user.id, updated_by_id=request.user.id)

                    submission_date_time = utils.get_datetime_from_date(submission_dates[i])
                    if send_out_dates[i] != None and send_out_dates[i] != "":
                        send_out_date_time = utils.get_datetime_from_date(send_out_dates[i])
                        candidatesJobDescription.objects.create(candidate_name_id=obj.id, stage_id=stages[i],
                                                                job_description_id=job_description[i],
                                                                send_out_date=send_out_dates[i],
                                                                created_by_id=request.user.id,
                                                                updated_by_id=request.user.id,
                                                                submission_date=submission_dates[i], notes=notes[i])
                    else:
                        candidatesJobDescription.objects.create(candidate_name_id=obj.id, stage_id=stages[i],
                                                                job_description_id=job_description[i],
                                                                send_out_date=None,
                                                                created_by_id=request.user.id,
                                                                updated_by_id=request.user.id,
                                                                submission_date=submission_dates[i], notes=notes[i])

                    if stage_names[i].strip() == "SendOut":
                        logger.info('Sending Send Out Mail ......')
                        sendClientMail(request, obj.id, job_description[i])

                    elif stage_names[i].strip() != "Candidate Added":
                        logger.info('Sending BDM Mail ......')
                        sendBDMMail(request, obj.id, stage_names[i].strip(), job_description[i], submission_dates[i],
                                    notes[i])

                    i = i + 1


            else:
                print("==================in else===============")
                activityStatusModel.objects.create(candidate_name_id=obj.id, activity_status='Candidate Added',
                                                   created_by_id=request.user.id, updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        logger.error('Candidate Post Serialized Error: ' + str(serializeObj.errors))
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
        serializeObj = CandidateWriteSerializer(candObj, data=request.data, partial=True)
        if serializeObj.is_valid():
            logger.info('Candidate Update Serialized Data: ' + str(serializeObj.validated_data))
            pk = str(pk).replace('UUID', '').replace('(\'', '').replace('\')', '').replace('-', '')
            RepoObj = candidatesRepositeryModel.objects.get(candidate_name_id=pk)

            if 'driving_license' in serializeObj.validated_data:
                RepoObj.driving_license = serializeObj.validated_data['driving_license']
            if 'offer_letter' in serializeObj.validated_data:
                RepoObj.offer_letter = serializeObj.validated_data['offer_letter']
            if 'passport' in serializeObj.validated_data:
                RepoObj.passport = serializeObj.validated_data['passport']
            if 'rtr' in serializeObj.validated_data:
                RepoObj.rtr = serializeObj.validated_data['rtr']
            if 'salary_slip' in serializeObj.validated_data:
                RepoObj.salary_slip = serializeObj.validated_data['salary_slip']
            if 'i94_document' in serializeObj.validated_data:
                RepoObj.i94_document = serializeObj.validated_data['i94_document']
            if 'visa_copy' in serializeObj.validated_data:
                RepoObj.visa_copy = serializeObj.validated_data['visa_copy']
            if 'educational_document' in serializeObj.validated_data:
                RepoObj.educational_document = serializeObj.validated_data['educational_document']
            if 'certification_doc' in serializeObj.validated_data:
                RepoObj.certification_doc = serializeObj.validated_data['certification_doc']
            if 'additional_qualification_doc' in serializeObj.validated_data:
                RepoObj.additional_qualification_doc = serializeObj.validated_data['additional_qualification_doc']
            if 'resume' in serializeObj.validated_data:
                RepoObj.resume = serializeObj.validated_data['resume']

            RepoObj.save()

            # if 'resume' in serializeObj.validated_data:
            #    pk = str(pk).replace('UUID', '').replace('(\'', '').replace('\')', '').replace('-', '')
            #    RepoObj = candidatesRepositeryModel.objects.get(candidate_name_id=pk)
            #    RepoObj.resume = serializeObj.validated_data['resume']
            #    RepoObj.save()
            serializeObj.save(updated_by_id=request.user.id)

            return Response(serializeObj.data, status=status.HTTP_200_OK)
        logger.error('Candidate Update Serialized Error: ' + str(serializeObj.errors))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = CandidateWriteSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            pk = str(pk).replace('UUID', '').replace('(\'', '').replace('\')', '').replace('-', '')
            RepoObj = candidatesRepositeryModel.objects.get(candidate_name_id=pk)

            if 'driving_license' in serializeObj.validated_data:
                RepoObj.driving_license = serializeObj.validated_data['driving_license']
            if 'offer_letter' in serializeObj.validated_data:
                RepoObj.offer_letter = serializeObj.validated_data['offer_letter']
            if 'passport' in serializeObj.validated_data:
                RepoObj.passport = serializeObj.validated_data['passport']
            if 'rtr' in serializeObj.validated_data:
                RepoObj.rtr = serializeObj.validated_data['rtr']
            if 'salary_slip' in serializeObj.validated_data:
                RepoObj.salary_slip = serializeObj.validated_data['salary_slip']
            if 'i94_document' in serializeObj.validated_data:
                RepoObj.i94_document = serializeObj.validated_data['i94_document']
            if 'visa_copy' in serializeObj.validated_data:
                RepoObj.visa_copy = serializeObj.validated_data['visa_copy']
            if 'educational_document' in serializeObj.validated_data:
                RepoObj.educational_document = serializeObj.validated_data['educational_document']
            if 'certification_doc' in serializeObj.validated_data:
                RepoObj.certification_doc = serializeObj.validated_data['certification_doc']
            if 'additional_qualification_doc' in serializeObj.validated_data:
                RepoObj.additional_qualification_doc = serializeObj.validated_data['additional_qualification_doc']
            if 'resume' in serializeObj.validated_data:
                RepoObj.resume = serializeObj.validated_data['resume']

            RepoObj.save()
            serializeObj.save(updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        candObj = self.get_object(pk)
        candObj1 = copy.copy(candObj)
        Candidates.objects_custom.backup_candidate(candObj1)
        candObj.delete()
        candidate_id = str(pk).replace('UUID', ''). \
            replace('(\'', '').replace('\')', '').replace('-', '')
        print(candidate_id)
        if candidatesJobDescription.objects.filter(candidate_name_id=candidate_id).count() > 0:
            candidatesJobDescription.objects.filter(candidate_name_id=candidate_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ActivityStatusSet(viewsets.ModelViewSet):
    queryset = activityStatusModel.objects.all()
    serializer_class = ActivityStatusSerializer
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ["candidate_name__first_name", "created_at"]
    search_fields = ['candidate_name__first_name', 'created_at']
    ordering_fields = ['candidate_name__first_name', 'created_at']
    ordering = ['candidate_name__first_name', 'created_at']
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        # candidateObj = activityStatusModel.objects.all()
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
            serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        logger.error('Candidate Activity Post Serialized Error: ' + str(serializeObj.errors))
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
            serializeObj.save(updated_by_id=request.user.id)
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
    search_fields = ['candidate_name__first_name', 'created_at']
    ordering_fields = ['candidate_name__first_name', 'created_at']
    ordering = ['candidate_name__first_name', 'created_at']
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        # candidateObj = placementCardModel.objects.all()
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
        logger.info('Candidate Placement Card Post Data: ' + str(request.data))
        if serializeObj.is_valid():
            serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        logger.error('Candidate Placement Card Post Serialized Error: ' + str(serializeObj.errors))
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
        logger.info('Candidate Placement Card Put Data: ' + str(request.data))
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        logger.error('Candidate Placement Card Post Serialized Error: ' + str(serializeObj.errors))
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
    search_fields = ['candidate_name__first_name', 'created_at']

    def list(self, request):
        # candidateObj = candidatesSubmissionModel.objects.all()
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
    search_fields = ['candidate_name__first_name', 'created_at']
    ordering_fields = ['candidate_name__first_name', 'created_at']
    ordering = ['candidate_name__first_name', 'created_at']
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        # candidateObj = rtrModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RTRSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = RTRSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        logger.info('Candidate RTR Post Data: ' + str(request.data))
        serializeObj = RTRWriteSerializer(data=request.data)
        if serializeObj.is_valid():
            obj = serializeObj.save()
            print(obj.id)
            if '-' in str(obj.id):
                obj.id = str(obj.id).replace('-', '')
            s = generate_doc(obj.id)

            candidate_id = str(obj.candidate_name_id).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            cursor = connection.cursor()
            print(obj.candidate_name_id)
            print(obj)
            # print(serializeObj.validated_data)
            print(candidate_id)
            cursor.execute("SELECT first_name , last_name  FROM osms_candidates where id=%s",
                           [candidate_id])
            candidate = cursor.fetchone()
            print(candidate)
            filename = str(candidate[0]) + '_' + str(candidate[1]) + str(uuid.uuid4()) + ".docx"
            serializeObj.save(rtr_doc=File(name=filename, file=BytesIO(s)), created_by_id=request.user.id,
                              updated_by_id=request.user.id)
            logger.info('Candidate RTR Saved Successfully: ' + str(serializeObj.data))
            if serializeObj.data['job_id']:
                logger.info('Sending RTR mail ...')
                jd_id = str(obj.job_id_id).replace('UUID', ''). \
                    replace('(\'', '').replace('\')', '').replace('-', '')
                cursor.execute("SELECT job_title, client_name_id FROM osms_job_description where id=%s",
                               [jd_id])
                jd = cursor.fetchone()
                cursor.execute("SELECT company_name FROM osms_clients where id=%s",
                               [jd[1]])
                client = cursor.fetchone()
                context_email = {'sender_name': request.user.first_name + ' ' + request.user.last_name,
                                 'candidate_name': candidate[0]}
                mail = Mails()
                mail.subject = "RTR Document: " + jd[0] + '-' + client[0]
                mail.from_email = request.user.email
                mail.email = serializeObj.data['email']
                mail.resume = None
                mail.jd = serializeObj.data['rtr_doc']
                mail.message = render_to_string('rtr_email.html', context_email)
                mail.condidate_email = None
                setattr(mail, 'cc_email', request.user.email)
                logger.info('RTR mail object ...' + str(mail))
                sendRTRMail(request, mail)
                logger.info('Mail Send Successfully' + str(mail))
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        logger.error('RTR Serializer Error: ' + str(serializeObj.errors))
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
        logger.info('Candidate RTR Put Data: ' + str(request.data))
        serializeObj = RTRWriteSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            obj = serializeObj.save()
            print(obj.id)
            if '-' in str(obj.id):
                obj.id = str(obj.id).replace('-', '')
            s = generate_doc(obj.id)

            candidate_id = str(obj.candidate_name_id).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            cursor = connection.cursor()
            print(obj.candidate_name_id)
            print(obj)
            # print(serializeObj.validated_data)
            print(candidate_id)
            cursor.execute("SELECT first_name , last_name  FROM osms_candidates where id=%s",
                           [candidate_id])
            candidate = cursor.fetchone()
            print(candidate)
            filename = str(candidate[0]) + '_' + str(candidate[1]) + str(uuid.uuid4()) + ".docx"
            serializeObj.save(rtr_doc=File(name=filename, file=BytesIO(s)), updated_by_id=request.user.id)
            logger.info('Candidate RTR Saved Successfully: ' + str(serializeObj.data))
            if serializeObj.data['job_id']:
                logger.info('Sending RTR mail ...')
                jd_id = str(obj.job_id_id).replace('UUID', ''). \
                    replace('(\'', '').replace('\')', '').replace('-', '')
                cursor.execute("SELECT job_title, client_name_id FROM osms_job_description where id=%s",
                               [jd_id])
                jd = cursor.fetchone()
                cursor.execute("SELECT company_name FROM osms_clients where id=%s",
                               [jd[1]])
                client = cursor.fetchone()
                context_email = {'sender_name': request.user.first_name + ' ' + request.user.last_name,
                                 'candidate_name': candidate[0]}
                mail = Mails()
                mail.subject = "RTR Document: " + jd[0] + '-' + client[0]
                mail.from_email = request.user.email
                mail.email = serializeObj.data['email']
                mail.resume = None
                mail.jd = serializeObj.data['rtr_doc']
                mail.message = render_to_string('rtr_email.html', context_email)
                mail.condidate_email = None
                setattr(mail, 'cc_email', request.user.email)
                sendRTRMail(request, mail)
                logger.info('Mail Send Successfully' + str(mail))
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        logger.error('RTR Serializer Error: ' + str(serializeObj.errors))
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
    search_fields = ['template_name', 'created_at']
    ordering_fields = ['template_name', 'created_at']
    ordering = ['template_name', 'created_at']
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        # candidateObj = emailTemplateModel.objects.all()
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
            serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id)
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
            serializeObj.save(updated_by_id=request.user.id)
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
    filter_fields = ["candidate_template__template_name", 'vendor_template__template_name', "created_at"]
    search_fields = ['candidate_template__template_name', 'vendor_template__template_name', 'created_at']
    ordering_fields = ['candidate_template__template_name', 'vendor_template__template_name', 'created_at']
    ordering = ['candidate_template__template_name', 'vendor_template__template_name', 'created_at']
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        # candidateObj = mailModel.objects.all()
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
            serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id)
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
            serializeObj.save(updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        candObj = self.get_object(pk)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CandidatesJobStagesViewSet(viewsets.ModelViewSet):
    queryset = candidatesJobDescription.objects.all()
    serializer_class = CandidateJobsStagesSerializer
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ['candidate_name__first_name' 'created_at']
    search_fields = ['candidate_name__first_name' 'created_at']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    permission_classes = []

    def list(self, request):
        # candidateObj = emailTemplateModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CandidateJobsStagesSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = EmailTemplateSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        logger.info('New Candidate Job Stages request data: ' + str(request.data))
        logger.info('New Candidate Job Stages request submission_date: ' + str(utils.get_datetime_from_date(
            request.data['submission_date'])))
        request.data['submission_date'] = utils.get_datetime_from_date(request.data['submission_date'])
        if request.data['send_out_date'] is not None:
            logger.info('New Candidate Job Stages request send_out_date: ' + str(utils.get_datetime_from_date(
                request.data['send_out_date'])))
            request.data['send_out_date'] = utils.get_datetime_from_date(request.data['send_out_date'])

        serializeObj = CandidateJobsStagesWriteSerializer(data=request.data, context={'request': request})
        if serializeObj.is_valid():
            # submission_datetime = serializeObj.data['submission_date'] + ' ' + utils.getCurrentTime()
            serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id)
            logger.info('serializeObj data: ' + str(serializeObj.data))

            stage_id = str(serializeObj.data['stage']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            candidate_id = str(serializeObj.data['candidate_name']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            job_id = str(serializeObj.data['job_description']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            cursor = connection.cursor()
            cursor.execute("SELECT stage_name from candidates_stages WHERE id=%s", [stage_id])
            stage = cursor.fetchone()

            BookAuthor = Candidates.job_description.through
            if BookAuthor.objects.filter(candidates_id=candidate_id, jobmodel_id=job_id).count() == 0:
                BookAuthor.objects.create(candidates_id=candidate_id, jobmodel_id=job_id)

            activityStatusModel.objects.create(candidate_name_id=candidate_id, activity_status=stage[0].strip(),
                                               job_id_id=job_id, created_by_id=request.user.id,
                                               updated_by_id=request.user.id)

            if stage[0].strip() == "SendOut":
                sendClientMail(request, serializeObj.data['candidate_name'], serializeObj.data['job_description'])

            elif stage[0].strip() != "Candidate Added":
                sendBDMMail(request, serializeObj.data['candidate_name'], stage[0].strip(),
                            serializeObj.data['job_description'], serializeObj.data['submission_date'],
                            serializeObj.data['notes'])

            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        logger.error('Candidate Jobs Stages Serializer Error: ' + str(serializeObj.errors))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return candidatesJobDescription.objects.get(pk=pk)
        except candidatesJobDescription.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = CandidateJobsStagesWriteSerializer(candObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        logger.info('New Candidate Job Stages update request: ' + str(request.data))
        candObj = self.get_object(pk)
        logger.info('New Candidate Job Stages request submission_date: ' + str(utils.get_datetime_from_date(
            request.data['submission_date'])))
        request.data['submission_date'] = utils.get_datetime_from_date(request.data['submission_date'])
        if request.data['send_out_date'] is not None:
            logger.info('New Candidate Job Stages request send_out_date: ' + str(utils.get_datetime_from_date(
                request.data['send_out_date'])))
            request.data['send_out_date'] = utils.get_datetime_from_date(request.data['send_out_date'])

        serializeObj = CandidateJobsStagesWriteSerializer(candObj, data=request.data, context={'request': request})
        if serializeObj.is_valid():
            # logger.info('serializeObj data: ' + str(serializeObj.data))

            # obj = serializeObj.save(updated_by_id=request.user.id)
            # submission_datetime = serializeObj.data['submission_date'] + ' ' + utils.getCurrentTime()
            serializeObj.save(updated_by_id=request.user.id)

            stage_id = str(serializeObj.data['stage']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            candidate_id = str(serializeObj.data['candidate_name']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            job_id = str(serializeObj.data['job_description']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            cursor = connection.cursor()
            cursor.execute("SELECT stage_name from candidates_stages WHERE id=%s", [stage_id])
            stage = cursor.fetchone()

            activityStatusModel.objects.create(candidate_name_id=candidate_id, activity_status=stage[0].strip(),
                                               job_id_id=job_id, created_by_id=request.user.id,
                                               updated_by_id=request.user.id)

            if stage[0].strip() == "SendOut":
                sendClientMail(request, serializeObj.data['candidate_name'], serializeObj.data['job_description'])

            elif stage[0].strip() != "Candidate Added":
                sendBDMMail(request, serializeObj.data['candidate_name'], stage[0].strip(),
                            serializeObj.data['job_description'], serializeObj.data['submission_date'],
                            serializeObj.data['notes'])

            return Response(serializeObj.data, status=status.HTTP_200_OK)
        logger.error('Candidate Jobs Stages Serializer Error: ' + str(serializeObj.errors))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        BookAuthor = Candidates.job_description.through
        candObj = self.get_object(pk)
        candidate_id = str(candObj.candidate_name_id).replace("-", '')
        job_id = str(candObj.job_description_id).replace("-", '')
        candObj.delete()
        if BookAuthor.objects.filter(candidates_id=candidate_id, jobmodel_id=job_id).count() > 0:
            BookAuthor.objects.filter(candidates_id=candidate_id, jobmodel_id=job_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InternalCandidateJobsStages(viewsets.ModelViewSet):
    queryset = internalCandidatesJobDescription.objects.all()
    serializer_class = InternalCandidateJobsStagesSerializer
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ['candidate_name__first_name' 'created_at']
    search_fields = ['candidate_name__first_name' 'created_at']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    permission_classes = []

    def list(self, request):
        # candidateObj = emailTemplateModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = InternalCandidateJobsStagesSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = EmailTemplateSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        logger.info('New Internal Candidate Job Stages request data: ' + str(request.data))
        logger.info('New Internal Candidate Job Stages request submission_date: ' + str(utils.get_datetime_from_date(
            request.data['submission_date'])))
        request.data['submission_date'] = utils.get_datetime_from_date(request.data['submission_date'])
        if request.data['send_out_date'] is not None:
            logger.info('New Internal Candidate Job Stages request send_out_date: ' + str(utils.get_datetime_from_date(
                request.data['send_out_date'])))
            request.data['send_out_date'] = utils.get_datetime_from_date(request.data['send_out_date'])

        serializeObj = InternalCandidateJobsStagesWriteSerializer(data=request.data, context={'request': request})
        if serializeObj.is_valid():
            # submission_datetime = serializeObj.data['submission_date'] + ' ' + utils.getCurrentTime()
            serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id)
            logger.info('serializeObj data: ' + str(serializeObj.data))

            stage_id = str(serializeObj.data['stage']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            candidate_id = str(serializeObj.data['candidate_name']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            job_id = str(serializeObj.data['job_description']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            cursor = connection.cursor()
            cursor.execute("SELECT stage_name from candidates_stages WHERE id=%s", [stage_id])
            stage = cursor.fetchone()

            BookAuthor = Candidates.job_description.through
            if BookAuthor.objects.filter(candidates_id=candidate_id, jobmodel_id=job_id).count() == 0:
                BookAuthor.objects.create(candidates_id=candidate_id, jobmodel_id=job_id)

            activityStatusModel.objects.create(candidate_name_id=candidate_id, activity_status=stage[0].strip(),
                                               job_id_id=job_id, created_by_id=request.user.id,
                                               updated_by_id=request.user.id)

            if stage[0].strip() == "SendOut":
                sendClientMail(request, serializeObj.data['candidate_name'], serializeObj.data['job_description'])

            elif stage[0].strip() != "Candidate Added":
                sendBDMMail(request, serializeObj.data['candidate_name'], stage[0].strip(),
                            serializeObj.data['job_description'], serializeObj.data['submission_date'],
                            serializeObj.data['notes'])

            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        logger.error('Candidate Jobs Stages Serializer Error: ' + str(serializeObj.errors))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return internalCandidatesJobDescription.objects.get(pk=pk)
        except internalCandidatesJobDescription.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = InternalCandidateJobsStagesWriteSerializer(candObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        logger.info('New Candidate Job Stages update request: ' + str(request.data))
        candObj = self.get_object(pk)
        logger.info('New Candidate Job Stages request submission_date: ' + str(utils.get_datetime_from_date(
            request.data['submission_date'])))
        request.data['submission_date'] = utils.get_datetime_from_date(request.data['submission_date'])
        if request.data['send_out_date'] is not None:
            logger.info('New Candidate Job Stages request send_out_date: ' + str(utils.get_datetime_from_date(
                request.data['send_out_date'])))
            request.data['send_out_date'] = utils.get_datetime_from_date(request.data['send_out_date'])

        serializeObj = InternalCandidateJobsStagesWriteSerializer(candObj, data=request.data, context={'request': request})
        if serializeObj.is_valid():
            # logger.info('serializeObj data: ' + str(serializeObj.data))

            # obj = serializeObj.save(updated_by_id=request.user.id)
            # submission_datetime = serializeObj.data['submission_date'] + ' ' + utils.getCurrentTime()
            serializeObj.save(updated_by_id=request.user.id)

            stage_id = str(serializeObj.data['stage']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            candidate_id = str(serializeObj.data['candidate_name']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            job_id = str(serializeObj.data['job_description']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            cursor = connection.cursor()
            cursor.execute("SELECT stage_name from candidates_stages WHERE id=%s", [stage_id])
            stage = cursor.fetchone()

            activityStatusModel.objects.create(candidate_name_id=candidate_id, activity_status=stage[0].strip(),
                                               job_id_id=job_id, created_by_id=request.user.id,
                                               updated_by_id=request.user.id)

            if stage[0].strip() == "SendOut":
                sendClientMail(request, serializeObj.data['candidate_name'], serializeObj.data['job_description'])

            elif stage[0].strip() != "Candidate Added":
                sendBDMMail(request, serializeObj.data['candidate_name'], stage[0].strip(),
                            serializeObj.data['job_description'], serializeObj.data['submission_date'],
                            serializeObj.data['notes'])

            return Response(serializeObj.data, status=status.HTTP_200_OK)
        logger.error('Candidate Jobs Stages Serializer Error: ' + str(serializeObj.errors))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        BookAuthor = Candidates.job_description.through
        candObj = self.get_object(pk)
        candidate_id = str(candObj.candidate_name_id).replace("-", '')
        job_id = str(candObj.job_description_id).replace("-", '')
        candObj.delete()
        if BookAuthor.objects.filter(candidates_id=candidate_id, jobmodel_id=job_id).count() > 0:
            BookAuthor.objects.filter(candidates_id=candidate_id, jobmodel_id=job_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CandidateStageViewSet(viewsets.ModelViewSet):
    # permission_classes = [DjangoObjectPermissions]
    queryset = candidateStageModel.objects.all()
    serializer_class = CandidateStageSerializer

    def list(self, request):
        status_type = request.query_params.get('type')
        candObj = User.objects.get(pk=request.user.id)
        if status_type is None:
            status_type = 'External'
        serializeObj = UserSerializer(candObj)
        groups = dict(serializeObj.data)
        userGroupDict = None
        userGroup = None
        queryset = None
        if len(groups['groups']) > 0:
            userGroupDict = dict(groups['groups'][0])
        if userGroupDict is not None:
            userGroup = userGroupDict['name']
        print(userGroup)
        uid = str(request.user.id).replace("-", "")
        print(uid)

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            queryset = candidateStageModel.objects.filter(type=status_type)
        else:
            roles_list = [3, 2]
            queryset = candidateStageModel.objects.filter(role__in=roles_list, type=status_type)

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CandidateStageSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CandidateStageSerializer(self.queryset, many=True)
        return Response(serializer.data)


class CandidateStageReviewViewSet(viewsets.ModelViewSet):
    # permission_classes = [DjangoObjectPermissions]
    queryset = activityStatusModel.objects.none()
    serializer_class = ActivityStatusSerializer
    filter_backends = [SearchFilter, OrderingFilter]  # SearchFilter,
    filter_fields = ['candidate_name__first_name' 'job_id']
    search_fields = ['candidate_name__first_name' 'created_at']
    ordering_fields = ['created_at']
    ordering = ['created_at']

    def list(self, request):
        if request.query_params.get('candidate_id') is not None:
            logger.info('candidate_id: ' + str(request.query_params.get('candidate_id')))
        if request.query_params.get('recruiter_id') is not None:
            logger.info('recruiter_id: ' + str(request.query_params.get('recruiter_id')))
        logger.info('jobdescription_id: ' + str(request.query_params.get('jobdescription_id')))
        if request.query_params.get('candidate_id') and request.query_params.get('jobdescription_id'):
            queryset = activityStatusModel.objects.filter(activity_status="Candidate Review",
                                                          candidate_name=request.query_params.get('candidate_id'),
                                                          job_id=request.query_params.get('jobdescription_id'))

            logger.info('queryset: ' + str(queryset.query))
            queryset = self.filter_queryset(queryset)
            # queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = ActivityStatusSerializer(page, many=True)
                # serializer = self.serializer_class(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = ActivityStatusSerializer(self.queryset, many=True)
        elif request.query_params.get('recruiter_id') is not None and request.query_params.get('jobdescription_id') is not None:
            queryset = jobAssingmentModel.objects.filter(
                Q(primary_recruiter_name_id=request.query_params.get('recruiter_id')) | Q(secondary_recruiter_name_id=request.query_params.get('recruiter_id')),
                job_id_id=request.query_params.get('jobdescription_id'),
                created_at__gte=get_current_date()
            )

            logger.info('queryset: ' + str(queryset.query))
            queryset = self.filter_queryset(queryset)
            # queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = JobAssingmentSerializer(page, many=True)
                # serializer = self.serializer_class(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = JobAssingmentSerializer(self.queryset, many=True)
            
        else:
            # queryset = self.filter_queryset(self.queryset)
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = ActivityStatusSerializer(page, many=True)
                # serializer = self.serializer_class(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = ActivityStatusSerializer(self.queryset, many=True)
        
        return Response(serializer.data)


"""class ExportCandidateModel(generics.ListAPIView):

    def get(self, request, format=None):
        response = download_csv(Candidates, request, Candidates.objects.all())
        return response"""

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


def send_candidate_mail(request, obj):
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


def send_vendor_mail(request, obj):
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


def get_headers(field_names):
    logger.info(field_names)
    return field_names


def get_data(item, field_names):
    return [{field: getattr(item, field)} for field in field_names]


# StreamingHttpResponse requires a File-like class that has a 'write' method
class Echo(object):
    def write(self, value):
        return value


def iter_items(queryset, pseudo_buffer):
    opts = queryset.model._meta
    field_names = [field.name for field in opts.fields]
    writer = csv.DictWriter(pseudo_buffer, fieldnames=field_names)
    pseudo_buffer.write(field_names)

    for item in queryset:
        logger.info(str(item))
        writer.writerow([row for row in queryset])
        # writer.writerow(get_data(item, field_names))


def get_model_field_names(model, ignore_fields=['content_object']):
    model_fields = model._meta.get_fields()
    model_field_names = list(set([f.name for f in model_fields if f.name not in ignore_fields]))
    return model_field_names


def get_lookup_fields(model, fields=None):
    model_field_names = get_model_field_names(model)

    lookup_fields = []
    if fields is not None:
        for x in fields:
            if "__" in x:
                # the __ is for ForeignKey lookups
                lookup_fields.append(x)
            elif x in model_field_names:
                lookup_fields.append(x)
            else:
                lookup_fields = model_field_names

    return lookup_fields


def qs_to_dataset(qs, fields=None):
    lookup_fields = get_lookup_fields(qs.model, fields=fields)
    return list(qs.values(*lookup_fields))


class ExportCandidateModel(viewsets.ModelViewSet):
    queryset = Candidates.objects.none()
    serializer_class = CandidateExportSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, ]  # SearchFilter,
    ordering_fields = ['first_name', 'created_at']
    ordering = ['first_name', 'created_at']
    filter_fields = ["first_name", "company_name", "created_at", ]
    search_fields = ['first_name', 'last_name', 'skills_1', 'skills_2', 'job_description__job_title', 'primary_email',
                     'job_description__client_name__company_name', 'total_experience_in_usa']
    filter_class = CandidateFilter

    # permission_classes = [DjangoModelPermissions]

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
        # print(userGroup)
        logger.info('userGroup Data: %s' % userGroup)
        uid = str(request.user.id).replace("-", "")

        if userGroup is not None and userGroup == 'ADMIN':
            queryset = Candidates.objects.all()  # .values(fields)
        elif userGroup is not None and userGroup == 'BDM MANAGER':
            if request.query_params.get('action'):
                querysetJS = candidatesJobDescription.objects.values('candidate_name_id').exclude(
                    stage_id__stage_name='Candidate Added').filter(
                    job_description_id__in=jobModel.objects.filter(created_by_id=request.user.id))
                queryset = Candidates.objects.filter(id__in=querysetJS)
                # exclude(stage__stage_name='Candidate Added'). values('job_description_id').
            else:
                queryset = Candidates.objects.all()
        elif userGroup is not None and userGroup == 'RECRUITER MANAGER':
            if request.query_params.get('action'):
                queryset = Candidates.objects.filter(created_by_id=request.user.id)
            else:
                queryset = Candidates.objects.all()
        elif userGroup is not None and userGroup == 'RECRUITER':
            if request.query_params.get('action'):
                queryset = Candidates.objects.filter(
                    created_by_id=request.user.id)  # exclude(stage__stage_name='Candidate Added').
            else:
                queryset = Candidates.objects.all()
        else:
            queryset = Candidates.objects.none()

        queryset = self.filter_queryset(queryset)
        logger.info("Filter queries: " + str(queryset.query))

        # response = download_csv(Candidates, request, queryset)

        opts = queryset.model._meta
        field_names = [field.name for field in opts.fields]

        """csv_buffer = CSVBuffer()
        csv_writer = csv.writer(csv_buffer)
        rows = (csv_writer.writerow(row) for row in queryset)
        # (iter_items(rows, CSVBuffer(), field_names))
        response = StreamingHttpResponse(streaming_content=rows,
                                         content_type='text/csv', )
        file_name = 'export-candidate-data'
        response['Content-Disposition'] = 'attachment;filename=%s.csv' % (file_name)
        logger.info("File starting to download.......")

        return response"""
        file_name = 'export-candidate-data'

        """pseudo_buffer = Echo()

        writer = csv.DictWriter(pseudo_buffer, fieldnames=field_names)
        pseudo_buffer.write(field_names)

        for item in queryset:
            logger.info(str(item))
            # writer.writerow([row for row in queryset])
            [{field: getattr(item, field)} for field in field_names]

        # rows = (["Row {}".format(idx), str(idx)] for idx in range(65536))
        response = StreamingHttpResponse(
            streaming_content=(iter_items(queryset, Echo())),
            content_type='text/csv',
        )
        response['Content-Disposition'] = 'attachment;filename=%s.csv' % (file_name)
        return response"""

        model_name = slugify(queryset.model.__name__)
        filename = "{}.csv".format(model_name)
        fields = ['id', 'first_name', 'last_name', 'date_of_birth', 'primary_email', 'secondary_email',
                  'primary_phone_number', 'secondary_phone_number', 'company_name', 'designation_id', 'skills_1',
                  'skills_2', 'min_salary', 'max_salary', 'min_rate', 'max_rate', 'qualification', 'currency', 'visa',
                  'current_location', 'country', 'total_experience', 'reason_for_job_change', 'rtr_done',
                  'willing_to_work_on_our_w2', 'open_for_relocation', 'rank', 'total_experience_in_usa',
                  'employer_phone_number', 'employer_name', 'employer_email', 'engagement_type', 'any_offer_in_hand',
                  'resume', 'resume_raw_data', 'remarks', 'certification', 'additional_qualification', 'stage_id',
                  'recruiter_name', 'created_by_id', 'updated_by_id', 'created_at', 'updated_at',
                  'candidatesjobdescription', 'updated_by', 'created_by', 'jobsubmissionmodel', 'job_description',
                  'placementcardmodel', 'interviewsmodel', 'candidatessubmissionmodel', 'stage', 'designation',
                  'feedbackmodel', 'rtrmodel', 'activitystatusmodel', 'candidatesrepositerymodel']

        # fields = None
        path = os.path.join(os.path.dirname(BASE_DIR), 'media_csv')
        if not os.path.exists(path):
            os.mkdir(path)
        if filename is None:
            model_name = slugify(queryset.model.__name__)
        filename = "{}.csv".format(model_name)
        lookups = get_lookup_fields(queryset.model, fields=fields)
        dataset = qs_to_dataset(queryset, fields)

        pseudo_buffer = Echo()
        logger.info(lookups)
        logger.info(field_names)
        writer = csv.DictWriter(pseudo_buffer, fieldnames=fields)
        pseudo_buffer.write(fields)
        writer.writeheader()
        """        for data_item in dataset:
            logger.info(data_item)
            writer.writerow(data_item)"""
        header = (writer.writerow(row) for row in fields)

        rows = (writer.writerow(row) for row in dataset)

        fp = StringIO()
        stream_file = File(fp)
        response = StreamingHttpResponse(streaming_content=rows,
                                         content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

        return response

        """pseudo_buffer = CSVBuffer()
        writer = csv.writer(pseudo_buffer)
        rowsData = []
        for obj in queryset:
            rowsData.append(writer.writerow([getattr(obj, field) for field in field_names]))

        rows = (writer.writerow(row) for row in queryset)
        response = StreamingHttpResponse(
            rows,
            content_type="text/csv",
        )
        response['Content-Disposition'] = 'attachment;filename=%s.csv' % (file_name)
        #             headers={'Content-Disposition': 'attachment; filename="somefilename.csv"'},
        return response"""

        """serializer = CandidateExportSerializer(queryset)
        logger.info("Total number of record2: " + str(len(serializer.data)))
        logger.info("Total number of record2: " + str(serializer.data))
        response_csv = HttpResponse(content_type='text/csv')
        response_csv['Content-Disposition'] = 'attachment; filename="export-candidate-data.csv"'
        writer = csv.DictWriter(response_csv, fieldnames=[])
        writer.writeheader()
        writer.writerows(serializer.data)
        return response_csv"""
        # return Response(serializer.data)

    def create(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        logger.info('ExportCandidateModel filter queryset: ' + str(queryset.query))
        serializer = CandidateSerializer(queryset, many=True)
        response = download_csv(Candidates, request, queryset)
        """outputs = []
        for i in range(len(serializer.data)):
            logger.info('Name: ' + str(serializer.data[i]['first_name']))
            rows = {
                'first_name': serializer.data[i]['first_name'],
                'last_name': serializer.data[i]['last_name'],
                'date_of_birth': serializer.data[i]['date_of_birth'],
                'primary_email': serializer.data[i]['primary_email'],
                'secondary_email': serializer.data[i]['secondary_email'],
                'primary_phone_number': serializer.data[i]['primary_phone_number'],
                'secondary_phone_number': serializer.data[i]['secondary_phone_number'],
                'company_name': serializer.data[i]['company_name'],

                'created_at': serializer.data[i]['created_at']
            }
            outputs.append(rows)
        """
        """response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export-candidate-data.csv"'
        writer = csv.DictWriter(response, fieldnames=['first_name',
                                                      'last_name', 'date_of_birth', 'primary_email', 'secondary_email', 'primary_phone_number',
                                                      'secondary_phone_number', 'company_name','created_at'
                                                      ])

        writer.writeheader()

        writer.writerows(serializer.data)
        logger.info("CSV DOWNLOAD response: " + str(response))"""
        # return response

        return Response(serializer.data)


class ImportCandidates(generics.ListAPIView):
    queryset = importFileModel.objects.all()
    serializer_class = ImportFileSerializer
    permission_classes = []

    def post(self, request, format=None):
        fileObj = ImportFileSerializer(data=request.data)
        if fileObj.is_valid():
            fileObj.save(created_by_id=request.user.id, updated_by_id=request.user.id)
        queryset = Candidates.objects.all()
        opts = queryset.model._meta
        field_names = [field.name for field in opts.fields]
        gendf = pd.DataFrame(columns=field_names)
        print(fileObj.data['file'])
        file_path = '.' + str(fileObj.data['file'])
        df = pd.read_csv(file_path, delimiter=",")
        print(df.head())
        json = fileObj.data['data_fields']
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
            # created_at=record['created_at'],
            # updated_at=record['updated_at'],
        ) for record in df_records]

        Candidates.objects.bulk_create(model_instances)

        # print(field_names)
        return Response(fileObj.data)


class GetCandidatesList(generics.ListAPIView):
    queryset = Candidates.objects.none()

    def get(self, request, format=None):
        queryset = None
        if request.query_params.get('job_id'):
            job_id = str(request.query_params.get('job_id')).replace('-', '')
            logger.info("job_id: " + str(job_id))
            queryset = Candidates.objects.raw(
                "SELECT ca.id, ca.first_name , ca.last_name ,CONCAT(u.first_name , ' ' , u.last_name) as "
                "updated_by_name, CONCAT(u1.first_name , ' ' , u1.last_name) as created_by_name, s.stage_name as status "
                ", cjs.submission_date ,cjs.updated_at ,ca.max_rate , "
                "ca.min_rate ,ca.min_salary , ca.max_salary , ca.visa FROM candidates_jobs_stages as cjs , "
                "users_user as u, users_user as u1, osms_candidates as ca , candidates_stages as s "
                "WHERE u.id = cjs.updated_by_id AND u1.id = ca.created_by_id AND cjs.stage_id = s.id AND "
                "cjs.candidate_name_id = ca.id AND "
                "cjs.job_description_id = %s ORDER BY cjs.submission_date DESC",
                [job_id])

        serializer = CandidatesSubmissionForJobListSerializer(queryset, many=True)
        return Response(serializer.data)


class GetCandidatesJobsStageList(generics.ListAPIView):
    queryset = candidatesJobDescription.objects.none()

    def get(self, request, format=None):
        if request.query_params.get('status') is not None and request.query_params.get('status') == 'internal':
            candidate_id = str(request.query_params.get('candidate_id')).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            externalStatus = candidatesJobDescription.objects.filter(candidate_name_id=candidate_id)
            internalStatus = internalCandidatesJobDescription.objects.filter(candidate_name_id=candidate_id)
            combined_list = chain(externalStatus, internalStatus)
            serializer = CandidateJobsStagesSerializer(combined_list, many=True)
            return Response(serializer.data)
        else:
            candidate_id = str(request.query_params.get('candidate_id')).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            externalStatus = candidatesJobDescription.objects.filter(candidate_name_id=candidate_id)
            # internalStatus = internalCandidatesJobDescription.objects.filter(candidate_name_id=candidate_id)
            # combined_list = chain(externalStatus, internalStatus)
            serializer = CandidateJobsStagesSerializer(externalStatus, many=True)
            return Response(serializer.data)


class CandidatesForSubmissionJob(generics.ListAPIView):
    queryset = candidatesJobDescription.objects.none()

    def get(self, request, format=None):
        if request.query_params.get('candidate_id'):
            candidate_id = str(request.query_params.get('candidate_id')).replace('-', '')
            jobs = candidatesJobDescription.objects.raw(
                "SELECT j.id, j.job_title, cl.company_name, cjs.submission_date, "
                "CONCAT(u.first_name,' ',u.last_name) as recruiter_name, "
                "s.stage_name as status FROM `candidates_jobs_stages` as cjs, osms_job_description as j,"
                " osms_clients as cl, users_user as u, candidates_stages as s "
                "WHERE j.id = cjs.job_description_id AND j.client_name_id = cl.id "
                "AND cjs.stage_id = s.id AND cjs.created_by_id = u.id AND "
                "cjs.candidate_name_id = %s", [candidate_id])
            # jobs = candidatesJobDescription.objects.annotate(job_title=COUNT('job_description__job_title')).values('job_description__job_title', 'job_description__client_name__company_name').filter(candidate_name_id=candidate_id)
            logger.info(jobs.query)
            # Obj = candidatesJobDescription.objects.filter(candidate_name_id=candidate_id)
            serializer = CandidatesForSubmissionJobSerializer(jobs, many=True)
            return Response(serializer.data)


class GetCandidatesDropdownList(generics.ListAPIView):
    queryset = Candidates.objects.none()

    def get(self, request, format=None):
        sql = "SELECT id, first_name , last_name FROM osms_candidates ORDER BY created_at DESC"
        queryset = Candidates.objects.raw(sql)
        serializer = CandidatesDropdownListSerializer(queryset, many=True)
        return Response(serializer.data)

