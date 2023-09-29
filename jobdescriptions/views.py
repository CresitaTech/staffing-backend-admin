import datetime
import json
from collections import OrderedDict
import copy

from django.shortcuts import render

# Create your views here.
from clients.models import clientModel
from clients.serializers import ClientSerializer
from interviews.models import Mails
from jobdescriptions.models import jobModel, jobSubmissionModel, jobAssingmentModel, jobNotesModel,JobModelManager,JobModelBackup
from jobdescriptions.serializers import JobDescriptionSerializer, UserDropDownListSerializer, JobAssingmentSerializer, \
    JobSubmissionSerializer, JobDescriptionWriteSerializer, JobAssingmentWriteSerializer, JobSubmissionWriteSerializer, \
    JobDescriptionNotesSerializer, JobDescriptionNotesListSerializer, UnassignedJobsStatusSerializer, \
    ExportAssignmentHistoryModelSerializer, GetJobCurrentStatusSerializer
from rest_framework import viewsets, generics
from comman_utils.utils import handle_file_upload, download_csv
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from rest_framework import viewsets, filters
from io import BytesIO
import uuid
import time
from django.contrib import messages
from django.core.files import File
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from jobdescriptions.utils import render_to_pdf, sendAssingmentMail, sendJobNotesMail, sendJDMail, counvert_ist_to_pst
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from jobdescriptions.filters import JDFilter
from reports.utils import formulaFields
from users.models import User
from users.serializers import UserSerializer
from django.db.models import Q
from candidates.models import importFileModel, Candidates
from candidates.serializers import ImportFileSerializer, CandidatesSubmissionForJobListSerializer
import pandas as pd
from rest_framework.permissions import DjangoModelPermissions
from staffingapp.settings import GLOBAL_ROLE
import logging
from django.http import HttpResponse
import csv
from rest_framework.authtoken.models import Token

# Get an instance of a logger
logger = logging.getLogger(__name__)


class JobDescriptionViewSet(viewsets.ModelViewSet):
    queryset = jobModel.objects.all()
    serializer_class = JobDescriptionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, ]  # SearchFilter,
    ordering_fields = ['client_name__company_name', 'created_at']
    ordering = ['client_name__company_name', 'created_at']
    filter_fields = ["client_name__company_name", "job_title", "created_at", ]
    search_fields = ['client_name__company_name', 'priority', 'job_id', 'job_title', 'nice_to_have_skills',
                     'key_skills']
    filter_class = JDFilter
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
        logger.info('userGroup Data: %s' % userGroup)
        if userGroup is not None and userGroup == 'ADMIN':
            queryset = jobModel.objects.all()
        elif userGroup is not None and userGroup == 'BDM MANAGER':
            if request.query_params.get('action'):
                queryset = jobModel.objects.all()
            else:
                queryset = jobModel.objects.filter(created_by_id=request.user.id)
        elif userGroup is not None and userGroup == 'RECRUITER MANAGER':
            # queryset = jobModel.objects.filter(Q(created_by_id__created_by_id=request.user.id) | Q(created_by_id=request.user.id) | Q(default_assignee_id=request.user.id))
            queryset = jobModel.objects.all()
        elif userGroup is not None and userGroup == 'RECRUITER':
            sql = "SELECT j.id, j.job_title, CONCAT( u.first_name, " ", u.last_name ) as default_assignee, j.created_at FROM `osms_job_description` as j, `job_description_assingment` as a, `users_user` as u WHERE (j.id = a.job_id_id AND u.id = a.primary_recruiter_name_id AND a.primary_recruiter_name_id = %s) OR (j.id = a.job_id_id AND u.id = a.secondary_recruiter_name_id AND a.primary_recruiter_name_id = %s)"
            # queryset = jobModel.objects.raw(sql,[request.user.id, request.user.id])
            # queryset = jobModel.objects.filter( Q(created_by_id__created_by_id=request.user.id) | Q(default_assignee_id=request.user.id))
            queryset = jobModel.objects.all()
            # print(str(queryset.query))
        else:
            queryset = jobModel.objects.none()
            # queryset = jobModel.objects.filter(default_assignee_id = request.user.id)
        logger.info("JOb Query: " + str(queryset.query))
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = JobDescriptionSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = JobDescriptionSerializer(self.queryset, many=True)
        logger.info('Job List: ' + str(serializer.data))
        return Response(serializer.data)

    def create(self, request):
        logger.info('New job Create data: ' + str(request.data))
        serializeObj = JobDescriptionWriteSerializer(data=request.data)
        if serializeObj.is_valid():
            obj = serializeObj.save()

            cursor = connection.cursor()
            client_id = str(obj.client_name_id).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            cursor.execute("SELECT company_name FROM osms_clients WHERE id=%s", [client_id])
            client_name = cursor.fetchone()

            context = {'instance': serializeObj.validated_data}
            pdf = render_to_pdf('job_description.html', context)
         
         
            recuiter_context = {'instance': serializeObj.validated_data}
         
            recruiter_pdf = render_to_pdf('recruiter_job_description.html', recuiter_context)

            job_title = str(obj.job_title).replace('\\', '_').replace(r'/', '_')

            filename = str(client_name) + '-' + str(job_title) + ".pdf"
            recruiter_filename = str(client_name) + '-' + str(job_title) + ".pdf"
            serializeObj.save(job_pdf=File(name=filename, file=BytesIO(pdf.content)),
                              job_recruiter_pdf=File(name=recruiter_filename, file=BytesIO(recruiter_pdf.content)),
                              created_by_id=request.user.id, updated_by_id=request.user.id)
            logger.info('Job Pdf Saved Successfully: ' + str(serializeObj.data))
            print(serializeObj.data)
            job_title = serializeObj.data['job_title']
            assignee_id = str(serializeObj.data['default_assignee']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            client_id = str(serializeObj.data['client_name']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            cursor.execute("SELECT first_name ,email FROM users_user WHERE id=%s", [assignee_id])
            assignee = cursor.fetchone()
            cursor.execute("SELECT company_name FROM osms_clients WHERE id=%s", [client_id])
            client = cursor.fetchone()

            context_email = {'default_assignee_name': assignee[0],
                             'job_title': job_title,
                             'job_id': serializeObj.data['job_id'],
                             'location': serializeObj.data['location'],
                             'min_salary': serializeObj.data['min_salary'],
                             'max_salary': serializeObj.data['max_salary'],
                             'min_rate': serializeObj.data['min_rate'],
                             'max_rate': serializeObj.data['max_rate'],
                             'min_client_rate': serializeObj.data['min_client_rate'],
                             'max_client_rate': serializeObj.data['max_client_rate'],
                             'employment_type': serializeObj.data['employment_type'],
                             'client_name': client[0],
                             'sender_name': request.user.first_name,
                             'status': serializeObj.data['status']
                             }

            mail = Mails()
            mail.from_email = request.user.email
            mail.email = assignee[1]
            mail.subject = job_title + '-' + client[0]
            mail.resume = serializeObj.data['job_pdf']
            mail.jd = None
            mail.message = render_to_string('jd_email.html', context_email)
            mail.condidate_email = None
            setattr(mail, 'cc_email', request.user.email)
            print(mail.resume)
            logger.info('Sending JD Mail ......')
            mail_res = sendJDMail(request, mail)
            logger.info('Mail Send Successfully' + str(mail))
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        logger.error('Job Post Serialized Error: ' + str(serializeObj.errors))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return jobModel.objects.get(pk=pk)
        except jobModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        jobdescriptionObj = self.get_object(pk)
        serializeObj = JobDescriptionWriteSerializer(jobdescriptionObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        jobdescriptionObj = self.get_object(pk)
        serializeObj = JobDescriptionWriteSerializer(jobdescriptionObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        candObj = self.get_object(pk)
        print(candObj)
        logger.info('Job Put Data: ' + str(request.data))
        serializeObj = JobDescriptionWriteSerializer(candObj, data=request.data, partial=True)
        if serializeObj.is_valid():
            if request.query_params.get('action'):
                logger.info('In action Job: ' + str(request.data))
                serializeObj.save(updated_by_id=request.user.id)
            else:
                obj = serializeObj.save()
                cursor = connection.cursor()
                client_id = str(obj.client_name_id).replace('UUID', ''). \
                    replace('(\'', '').replace('\')', '').replace('-', '')
                cursor.execute("SELECT company_name FROM osms_clients WHERE id=%s", [client_id])
                client_name = cursor.fetchone()

                context = {'instance': obj}
                pdf = render_to_pdf('job_description.html', context)

                recuiter_context = {'instance': obj}
                
                recruiter_pdf = render_to_pdf('recruiter_job_description.html', recuiter_context)

                job_title = str(obj.job_title).replace('\\', '_').replace(r'/', '_')

                filename = str(client_name) + '-' + str(job_title) + ".pdf"
                recruiter_filename = str(client_name) + '-' + str(job_title) + ".pdf"
                serializeObj.save(job_pdf=File(name=filename, file=BytesIO(pdf.content)),
                                  job_recruiter_pdf=File(name=recruiter_filename, file=BytesIO(recruiter_pdf.content)),
                                  updated_by_id=request.user.id)
                print(serializeObj.data)
                logger.info('Job Pdf Updated Successfully: ' + str(serializeObj.data))
                job_title = serializeObj.data['job_title']
                assignee_id = str(serializeObj.data['default_assignee']).replace('UUID', ''). \
                    replace('(\'', '').replace('\')', '').replace('-', '')
                client_id = str(serializeObj.data['client_name']).replace('UUID', ''). \
                    replace('(\'', '').replace('\')', '').replace('-', '')
                cursor.execute("SELECT first_name ,email FROM users_user WHERE id=%s", [assignee_id])
                assignee = cursor.fetchone()
                cursor.execute("SELECT company_name FROM osms_clients WHERE id=%s", [client_id])
                client = cursor.fetchone()

                context_email = {'default_assignee_name': assignee[0],
                                 'job_title': job_title,
                                 'job_id': serializeObj.data['job_id'],
                                 'location': serializeObj.data['location'],
                                 'min_salary': serializeObj.data['min_salary'],
                                 'max_salary': serializeObj.data['max_salary'],
                                 'min_rate': serializeObj.data['min_rate'],
                                 'max_rate': serializeObj.data['max_rate'],
                                 'client_name': client[0],
                                 'sender_name': request.user.first_name,
                                 'status': serializeObj.data['status']
                                 }

                mail = Mails()
                mail.from_email = request.user.email
                mail.email = assignee[1]
                mail.subject = job_title + '-' + client[0]
                mail.resume = serializeObj.data['job_pdf']
                mail.jd = None
                mail.message = render_to_string('jd_email.html', context_email)
                mail.condidate_email = None
                setattr(mail, 'cc_email', request.user.email)
                print(mail.resume)
                logger.info('Sending JD mail ...')
                mail_res = sendJDMail(request, mail)
                logger.info('Mail Send Successfully' + str(mail))
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        logger.error('Job Update Serialized Error: ' + str(serializeObj.errors))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        candObj = self.get_object(pk)
        job_refer_id=candObj.id
        candObj1 = copy.copy(candObj)
        user_token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
        token = Token.objects.get(key=user_token)
        user = token.user
        utc_now = datetime.datetime.utcnow()

# Convert the UTC time to the Gunicorn server's timezone
        gunicorn_now = utc_now.astimezone(datetime.timezone(datetime.timedelta(hours=5.5)))
        jobModel.objects_custom.backup_jobs(candObj1,job_refer_id,gunicorn_now,user)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        


class JobSubmissionViewSet(viewsets.ModelViewSet):
    queryset = jobSubmissionModel.objects.all()
    serializer_class = JobSubmissionSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ("recruiter_name__first_name", "created_at")
    search_fields = ('recruiter_name__first_name', "created_at")
    permission_classes = [DjangoModelPermissions]
    ordering_fields = ['recruiter_name__first_name', 'created_at']
    ordering = ['recruiter_name__first_name', 'created_at']

    def list(self, request):
        # jobdescriptionObj = jobSubmissionModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = JobSubmissionSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = JobSubmissionSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = JobSubmissionWriteSerializer(data=request.data)
        if serializeObj.is_valid():
            candObj = User.objects.get(pk=request.user.id)
            userserializeObj = UserSerializer(candObj)
            groups = dict(userserializeObj.data)
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

            serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id)
            cursor = connection.cursor()
            candidate_id = str(serializeObj.data['candidate_name']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            cursor.execute(
                "SELECT resume , job_description_id ,first_name,last_name,primary_phone_number,primary_email,min_salary,min_rate,max_rate,"
                "current_location,visa,open_for_relocation,total_experience,qualification,total_experience_in_usa,any_offer_in_hand ,max_salary, created_by_id from osms_candidates WHERE id =%s",
                [candidate_id])
            candidate = cursor.fetchone()

            cursor.execute("SELECT job_title , created_by_id ,location  FROM osms_job_description WHERE id=%s",
                           [candidate[1]])
            jd = cursor.fetchone()

            cursor.execute("SELECT first_name , last_name , email FROM users_user WHERE id=%s",
                           [jd[1]])
            BDM = cursor.fetchone()

            cursor.execute("SELECT first_name , last_name , email , created_by_id FROM users_user WHERE id=%s",
                           [candidate[17]])
            recruiter = cursor.fetchone()

            cursor.execute("SELECT first_name , last_name , email , created_by_id FROM users_user WHERE id=%s",
                           [recruiter[3]])
            recruiter_manager = cursor.fetchone()

            context_email1 = {'assignee_name': serializeObj.data['assignee_name'],
                              'sender_name': request.user.first_name + ' ' + request.user.last_name,
                              'job_title': jd[0],
                              'candidate_info': {"first_name": candidate[2],
                                                 "last_name": candidate[3],
                                                 "primary_phone_number": candidate[4],
                                                 "primary_email": candidate[5],
                                                 "min_salary": candidate[6],
                                                 "max_salary": candidate[16],
                                                 "min_rate": candidate[7],
                                                 "max_rate": candidate[8],
                                                 "current_location": candidate[9],
                                                 "visa": candidate[10],
                                                 "open_for_relocation": candidate[11],
                                                 "total_experience": candidate[12],
                                                 "qualification": candidate[13],
                                                 "total_experience_in_usa": candidate[14],
                                                 "any_offer_in_hand": candidate[15]
                                                 }
                              }

            mail = Mails()
            mail.subject = 'Submission: ' + candidate[2] + ' ' + candidate[3] \
                           + ' for ' + jd[0] + ' ' + jd[2]
            mail.from_email = serializeObj.data['recruiter_email'].strip()
            mail.email = serializeObj.data['assignee_email'].strip()
            mail.jd = None
            mail.resume = None
            mail.message = render_to_string('jd_submission_email.html', context_email1)
            mail.condidate_email = None

            if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
                setattr(mail, 'cc_email',
                        [request.user.email.strip(), recruiter_manager[2].strip(), recruiter[2].strip(),
                         'pandeymohit307@gmail.com'])
            elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
                setattr(mail, 'cc_email', [recruiter_manager[2].strip(), recruiter[2].strip()])
            elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
                setattr(mail, 'cc_email', [request.user.email.strip(), recruiter[2].strip()])
            elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
                setattr(mail, 'cc_email', [request.user.email.strip(), recruiter_manager[2].strip()])
            elif userGroup is None or userGroup == '':
                setattr(mail, 'cc_email', [])

            print("+++++++++++++++++++++++++++++")
            sendAssingmentMail(request, mail)
            print("+++++++++++++++++++++++++++++")
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return jobSubmissionModel.objects.get(pk=pk)
        except jobModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        jobdescriptionObj = self.get_object(pk)
        serializeObj = JobSubmissionWriteSerializer(jobdescriptionObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        jobdescriptionObj = self.get_object(pk)
        serializeObj = JobSubmissionWriteSerializer(jobdescriptionObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        candObj = self.get_object(pk)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class JobAssingmentViewSet(viewsets.ModelViewSet):
    queryset = jobAssingmentModel.objects.all()
    serializer_class = JobAssingmentSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ("primary_recruiter_name__first_name", "secondary_recruiter_name__first_name", "created_at")
    search_fields = (
        'primary_recruiter_name__first_name', 'secondary_recruiter_name__first_name', 'assignee_name', "created_at")
    permission_classes = [DjangoModelPermissions]
    ordering_fields = ['primary_recruiter_name__first_name', 'secondary_recruiter_name__first_name', 'created_at']
    ordering = ['primary_recruiter_name__first_name', 'secondary_recruiter_name__first_name', 'created_at']

    def list(self, request):
        # jobdescriptionObj = jobAssingmentModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = JobAssingmentSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = JobAssingmentSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        logger.info('New job Assignment data: ' + str(request.data))
        user = User.objects.get(pk=request.user.id)
        recruiter = User.objects.get(pk=request.data['primary_recruiter_name'])
        userCountry = None
        recruiterCountry = None
        if user is not None:
            userCountry = user.country
        if recruiter is not None:
            recruiterCountry = recruiter.country
        request.data['assignment_date'] = datetime.datetime.now()
        logger.info('userCountry: ' + str(userCountry))
        logger.info('recruiterCountry: ' + str(recruiterCountry))
        if userCountry != "India":
            request.data['assignment_date'] = counvert_ist_to_pst(userCountry, recruiterCountry)

        logger.info('New job Assignment updated data: ' + str(request.data))
        serializeObj = JobAssingmentWriteSerializer(data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id) # , assignment_date=counvert_ist_to_pst(userCountry)
            print(serializeObj.data)
            job_id = str(serializeObj.data['job_id']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            # job_id = serializeObj.data['job_id']
            cursor = connection.cursor()
            cursor.execute(
                "SELECT job_pdf , job_id ,job_title ,location ,client_name_id ,min_salary ,max_salary,min_rate,max_rate,created_by_id  from osms_job_description WHERE id =%s",
                [job_id])
            jd = cursor.fetchone()

            cursor.execute("SELECT first_name , last_name , email FROM users_user WHERE id=%s",
                           [jd[9]])
            BDM = cursor.fetchone()

            cursor.execute("SELECT company_name  from osms_clients WHERE id =%s",
                           [jd[4]])
            client = cursor.fetchone()

            primary_id = str(serializeObj.data['primary_recruiter_name']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            cursor.execute("SELECT first_name , last_name FROM users_user WHERE id=%s", [primary_id])
            primary_recruiter_name = cursor.fetchone()

            if serializeObj.data['secondary_recruiter_email'] != '' and serializeObj.data[
                'secondary_recruiter_email'] != None:
                logger.info('Job assingning to twq recruiters: ')
                secondary_id = str(serializeObj.data['secondary_recruiter_name']).replace('UUID', ''). \
                    replace('(\'', '').replace('\')', '').replace('-', '')

                cursor.execute("SELECT first_name , last_name FROM users_user WHERE id=%s",
                               [secondary_id])
                secondary_recruiter_name = cursor.fetchone()

                context_email1 = {'sender_name': serializeObj.data['assignee_name'],
                                  'recruiter_name': primary_recruiter_name[0],
                                  'recruiter_title': 'Primary Recruiter',
                                  'job_id': jd[1],
                                  'job_title': jd[2],
                                  'location': jd[3],
                                  'min_salary': jd[5],
                                  'max_salary': jd[6],
                                  'min_rate': jd[7],
                                  'max_rate': jd[8],
                                  'client_name': client[0]}

                context_email2 = {'sender_name': serializeObj.data['assignee_name'],
                                  'recruiter_name': secondary_recruiter_name[0],
                                  'recruiter_title': 'Secondary Recruiter',
                                  'job_id': jd[1],
                                  'job_title': jd[2],
                                  'location': jd[3],
                                  'min_salary': jd[5],
                                  'max_salary': jd[6],
                                  'min_rate': jd[7],
                                  'max_rate': jd[8],
                                  'client_name': client[0]}

                mail_primary = Mails()
                mail_primary.subject = primary_recruiter_name[0] + ': New Assigned ' + jd[2] + '-' + client[0] + jd[3]
                mail_primary.from_email = serializeObj.data['assignee_email']
                mail_primary.email = serializeObj.data['primary_recruiter_email'].strip()
                mail_primary.resume = None
                mail_primary.jd = jd[0]
                mail_primary.message = render_to_string('jd_assingment_email.html', context_email1)
                mail_primary.condidate_email = None
                setattr(mail_primary, 'cc_email',
                        [serializeObj.data['assignee_email'].strip(), BDM[2].strip(), 'ats@opallios.com'])
                logger.info('Sending Mail to primary recruiter .....' + str(mail_primary))
                logger.info('Email From.....' + str(mail_primary.from_email))
                sendAssingmentMail(request, mail_primary)
                logger.info('Mail Successfully send ....' + str(mail_primary))
                print("===================" + mail_primary.jd)
                time.sleep(3)

                mail_secondary = Mails()
                mail_secondary.subject = secondary_recruiter_name[0] + ': New Assigned ' + jd[2] + '-' + client[0] + jd[
                    3]
                mail_secondary.from_email = serializeObj.data['assignee_email']
                mail_secondary.email = serializeObj.data['secondary_recruiter_email'].strip()
                mail_secondary.resume = None
                mail_secondary.jd = jd[0]
                mail_secondary.message = render_to_string('jd_assingment_email.html', context_email2)
                mail_secondary.condidate_email = None
                setattr(mail_secondary, 'cc_email',
                        [serializeObj.data['assignee_email'].strip(), BDM[2].strip(), 'ats@opallios.com'])
                print("+++++++++++++++++++++++++" + mail_secondary.jd)
                logger.info('Sending Mail to secondary recruiter .....' + str(mail_secondary))
                sendAssingmentMail(request, mail_secondary)
                logger.info('Mail Successfully send ....' + str(mail_secondary))

            else:
                logger.info('Job assingning to primary recruiter')
                context_email1 = {'sender_name': serializeObj.data['assignee_name'],
                                  'recruiter_name': primary_recruiter_name[0],
                                  'recruiter_title': 'Primary Recruiter',
                                  'job_id': jd[1],
                                  'job_title': jd[2],
                                  'location': jd[3],
                                  'min_salary': jd[5],
                                  'max_salary': jd[6],
                                  'min_rate': jd[7],
                                  'max_rate': jd[8],
                                  'client_name': client[0]}

                mail_primary = Mails()
                mail_primary.subject = primary_recruiter_name[0] + ': New Assigned ' + jd[2] + '-' + client[0] + jd[3]
                mail_primary.from_email = serializeObj.data['assignee_email']
                mail_primary.email = serializeObj.data['primary_recruiter_email'].strip()
                mail_primary.resume = None
                mail_primary.jd = jd[0]
                mail_primary.message = render_to_string('jd_assingment_email.html', context_email1)
                mail_primary.condidate_email = None
                setattr(mail_primary, 'cc_email',
                        [serializeObj.data['assignee_email'].strip(), BDM[2].strip(), 'ats@opallios.com'])
                logger.info('Sending Mail to primary recruiter .....' + str(mail_primary))
                sendAssingmentMail(request, mail_primary)
                logger.info('Mail Successfully send ....' + str(mail_primary))
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        logger.error('Job Assingment Post Serialized Error: ' + str(serializeObj.errors))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return jobAssingmentModel.objects.get(pk=pk)
        except jobModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        jobdescriptionObj = self.get_object(pk)
        serializeObj = JobAssingmentWriteSerializer(jobdescriptionObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        jobdescriptionObj = self.get_object(pk)
        serializeObj = JobAssingmentWriteSerializer(jobdescriptionObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        candObj = self.get_object(pk)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class JobDescriptionNotesViewSet(viewsets.ModelViewSet):
    queryset = jobNotesModel.objects.none()
    serializer_class = JobDescriptionNotesListSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ("job_title", "created_at")
    search_fields = ('job_title', "created_at")
    permission_classes = [DjangoModelPermissions]
    ordering_fields = ['job_title', 'created_at']
    ordering = ['job_title', 'created_at']

    def list(self, request):
        if request.query_params.get('job_id'):
            queryset = jobNotesModel.objects.filter(job_id=request.query_params.get('job_id'))

        if queryset is not None:
            logger.info('JobDescriptionNotesViewSet QuerySet Query formed: ' + str(queryset.query))

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = JobDescriptionNotesListSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = JobDescriptionNotesListSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = JobDescriptionNotesSerializer(data=request.data)
        if serializeObj.is_valid():
            candObj = User.objects.get(pk=request.user.id)
            userserializeObj = UserSerializer(candObj)
            groups = dict(userserializeObj.data)
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

            serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id)

            job_id = str(serializeObj.data['job_id']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            jdqueryset = jobModel.objects.get(pk=serializeObj.data['job_id'])
            jdSer = JobDescriptionWriteSerializer(jdqueryset)

            clientqueryset = clientModel.objects.get(pk=jdSer.data['client_name'])
            clientSer = ClientSerializer(clientqueryset)

            userqueryset = User.objects.raw(
                "SELECT u.id, u.email from users_user as u, job_description_assingment as jda where u.role = '3' AND "
                "u.is_active = '1' AND jda.job_id_id = %s GROUP BY u.email",
                [job_id])
            user_serializer = UserSerializer(userqueryset, many=True)
            recruiter_emails = []

            for i in range(len(user_serializer.data)):
                recruiter_emails.append(user_serializer.data[i]['email'])

            bdmqueryset = User.objects.raw(
                "SELECT u.id, u.email from users_user as u, osms_job_description as j where j.id = %s AND j.created_by_id = u.id",
                [job_id])
            bdm_serializer = UserSerializer(bdmqueryset, many=True)
            bdm_emails = []
            for i in range(len(bdm_serializer.data)):
                bdm_emails.append(bdm_serializer.data[i]['email'])

            context_email1 = {
                'sender_name': request.user.first_name + ' ' + request.user.last_name,
                'job_title': str(serializeObj.data['job_title']),
                'job_id': str(jdSer.data['job_id']),
                'client_name': str(clientSer.data['first_name']),
                'job_description_notes': str(serializeObj.data['job_description_notes'])
            }

            mail = Mails()
            mail.subject = 'Notes Added for ' + str(serializeObj.data['job_title']) + ' - ' + str(
                clientSer.data['first_name'])
            mail.from_email = request.user.email
            mail.email = str('kuriwaln@opallios.com')
            mail.jd = None
            mail.resume = None
            mail.message = render_to_string('jd_notes_email.html', context_email1)
            mail.condidate_email = None

            if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
                setattr(mail, 'cc_email', bdm_emails)
            elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
                setattr(mail, 'cc_email', recruiter_emails)
            elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
                setattr(mail, 'cc_email', bdm_emails)
            elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
                setattr(mail, 'cc_email', bdm_emails)
            elif userGroup is None or userGroup == '':
                setattr(mail, 'cc_email', [])

            print("+++++++++++++++++++++++++++++")
            sendJobNotesMail(request, mail)
            print("+++++++++++++++++++++++++++++")
            logger.info('Notes Email Send Successfully !!!!!!!!')
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return jobNotesModel.objects.get(pk=pk)
        except jobNotesModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        jobdescriptionObj = self.get_object(pk)
        serializeObj = JobDescriptionNotesSerializer(jobdescriptionObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        jobdescriptionObj = self.get_object(pk)
        serializeObj = JobDescriptionNotesSerializer(jobdescriptionObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        candObj = self.get_object(pk)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExportJdModel(generics.ListAPIView):

    def get(self, request, format=None):
        response = download_csv(jobModel, request, jobModel.objects.all())
        return response


class ImportJobDescription(generics.ListAPIView):
    queryset = importFileModel.objects.all()
    serializer_class = ImportFileSerializer
    permission_classes = []

    def post(self, request, format=None):
        fileObj = ImportFileSerializer(data=request.data)
        if fileObj.is_valid():
            fileObj.save(created_by_id=request.user.id, updated_by_id=request.user.id)
        queryset = jobModel.objects.all()
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

        model_instances = [jobModel(
            job_id=record['job_id'],
            client_name=fileObj.data['data_fields']['client_name'],
            end_client_name=record['end_client_name'],
            priority=record['priority'],
            industry_experience=record['industry_experience'],
            nice_to_have_skills=record['nice_to_have_skills'],
            job_title=record['job_title'],
            job_description=record['job_description'],
            visa_type=record['visa_type'],
            no_of_requests=record['no_of_requests'],
            roles_and_responsibilities=record['roles_and_responsibilities'],
            years_of_experience=record['years_of_experience'],
            key_skills=record['key_skills'],
            education_qualificaion=record['education_qualificaion'],
            start_date=record['start_date'],
            contract_type=record['contract_type'],
            contract_duration=record['contract_duration'],
            location=record['location'],
            Rate=record['Rate'],
            key_fields=record['key_fields'],
            status=record['status'],
            projected_revenue=record['projected_revenue'],
            default_assignee=fileObj.data['data_fields']['default_assignee'],
            revenue_frequqney=record['revenue_frequqney'],
            created_by=request.user.id,
            updated_by=request.user.id
            # created_at=record['created_at'],
            # updated_at=record['updated_at'],
        ) for record in df_records]

        jobModel.objects.bulk_create(model_instances)

        # print(field_names)
        return Response(fileObj.data)


class GetJobAssingmentHistory(generics.ListAPIView):
    queryset = jobAssingmentModel.objects.none()

    def get(self, request, format=None):
        if request.query_params.get('job_id'):
            job_id = str(request.query_params.get('job_id')).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            Obj = jobAssingmentModel.objects.filter(job_id_id=job_id)
            if Obj is not None:
                serializer = JobAssingmentSerializer(Obj, many=True)
                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class GetUserList(generics.ListAPIView):
    queryset = jobModel.objects.none()

    def get(self, request, format=None):
        queryset = jobModel.objects.raw("SELECT u.id , u.first_name , u.last_name ,u.email FROM users_user as u ,"
                                        "auth_group as ag , users_user_groups as g WHERE g.user_id = u.id AND u.is_deleted = False AND g.group_id = ag.id AND (ag.name = 'RECRUITER' OR ag.name = 'RECRUITER MANAGER') and u.is_active=1")
        print(queryset)
        serializer = UserDropDownListSerializer(queryset, many=True)
        return Response(serializer.data)


class GetJobCurrentStatus(generics.ListAPIView):
    queryset = jobModel.objects.none()

    def get(self, request, format=None):
        job_id = request.query_params.get('job_id')
        job_id = str(job_id).replace("-", "")
        query = "select j.id, j.job_title, " + formulaFields() + " from `osms_job_description` as j , `candidates_stages` " \
                      "as s, `candidates_jobs_stages` as cjs, users_user as u WHERE j.id = cjs.job_description_id AND cjs.stage_id = s.id AND j.id = '" + job_id + "' GROUP BY j.id "

        queryset = jobModel.objects.raw(query)
        logger.info(queryset.query)
        serializer = GetJobCurrentStatusSerializer(queryset, many=True)
        jobs = len(serializer.data)
        msg = None
        response = {'status': "success", 'message': str(msg), 'data': None}
        if jobs > 0:
            response = {'status': "success", 'message': str(msg), 'data': serializer.data}

            logger.info("Number of jobs: " + str(jobs))
            logger.info("Number of Submission: " + str(serializer.data[0]['Submission']))

            submission = int(serializer.data[0]['Submission'])
            SubmissionReject = int(serializer.data[0]['SubmissionReject'])
            SendOut = int(serializer.data[0]['SendOut'])
            SendoutReject = int(serializer.data[0]['SendoutReject'])
            SecondInterviewReject = int(serializer.data[0]['SecondInterviewReject'])
            RejectedByTeam = int(serializer.data[0]['RejectedByTeam'])
            RejectedByClient = int(serializer.data[0]['RejectedByClient'])
            Placed = int(serializer.data[0]['Placed'])
            Offered = int(serializer.data[0]['Offered'])
            OfferRejected = int(serializer.data[0]['OfferRejected'])
            OfferBackout = int(serializer.data[0]['OfferBackout'])
            InterviewSelect = int(serializer.data[0]['InterviewSelect'])
            InterviewReject = int(serializer.data[0]['InterviewReject'])
            InterviewBackout = int(serializer.data[0]['InterviewBackout'])
            InternalInterviewReject = int(serializer.data[0]['InternalInterviewReject'])
            InternalInterview = int(serializer.data[0]['InternalInterview'])
            HoldbyClient = int(serializer.data[0]['HoldbyClient'])
            HoldbyBDM = int(serializer.data[0]['HoldbyBDM'])
            FeedbackAwaited = int(serializer.data[0]['FeedbackAwaited'])
            ClientInterviewSecond = int(serializer.data[0]['ClientInterviewSecond'])
            ClientInterviewFirst = int(serializer.data[0]['ClientInterviewFirst'])
            ClientInterview = int(serializer.data[0]['ClientInterview'])
            CandidateReview = int(serializer.data[0]['CandidateReview'])
            CandidateAdded = int(serializer.data[0]['CandidateAdded'])

            # "sum(case when (s.stage_name = 'Submission' OR s.stage_name = 'Submission Reject' OR s.stage_name = 'Internal Interview' OR s.stage_name = 'Internal Interview Reject' OR s.stage_name = 'Candidate Review' OR s.stage_name = 'SendOut' OR s.stage_name = 'SendOut Reject' OR s.stage_name = 'Client Interview - First' OR s.stage_name = 'Interview Backout Interview Reject' OR s.stage_name = 'Interview Select' OR s.stage_name = 'Client Interview - Second' OR s.stage_name = 'Second Interview Reject' OR s.stage_name = 'Offerred' OR s.stage_name = 'Offer Reject' OR s.stage_name = 'Offer Backout' OR s.stage_name = 'Feedback Awaited' OR s.stage_name = 'Hold by BDM' OR s.stage_name = 'Hold by Client' OR s.stage_name = 'Placed' OR s.stage_name = 'Interview Reject') then 1 else 0 end) as Submission

            calOffered = OfferRejected + Placed
            calSendOut = SendoutReject + InterviewReject + OfferRejected + Placed
            calClientInterview = InterviewReject + OfferRejected + Placed
            logger.info("Number of calOffered: " + str(calOffered))
            logger.info("Number of calSendOut: " + str(calSendOut))

            if SendOut != calSendOut:
                msg = "You can't In active the jobs. Because some of sendout still pending."
                response = {'status': "error", 'message': str(msg), 'data': serializer.data}
            elif Offered != calOffered:
                msg = "You can't In active the jobs. Because some of offer still pending."
                response = {'status': "error", 'message': str(msg), 'data': serializer.data}
            elif ClientInterview != calClientInterview:
                msg = "You can't In active the jobs. Because some of ClientInterview still pending."
                response = {'status': "error", 'message': str(msg), 'data': serializer.data}

        return Response(response)


def qdict_to_dict(qdict):
    """Convert a Django QueryDict to a Python dict.

    Single-value fields are put in directly, and for multi-value fields, a list
    of all values is stored at the field's key.

    """
    return {k: v[0] if len(v) == 1 else v for k, v in qdict.lists()}


class GetUnassignedJobsStatus(generics.ListAPIView):
    queryset = jobModel.objects.all()
    serializer_class = JobDescriptionWriteSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, ]  # SearchFilter,
    ordering_fields = ['client_name__company_name', 'created_at']
    ordering = ['client_name__company_name', 'created_at']
    filter_fields = ["client_name__company_name", "job_title", "created_at", ]
    search_fields = ['client_name__company_name', 'priority', 'job_id', 'job_title', 'nice_to_have_skills',
                     'key_skills']
    filter_class = JDFilter

    def get(self, request, format=None):
        queryset = None
        responceData = {}
        if request.query_params.get('job_id'):
            job_id = str(request.query_params.get('job_id'))
            job = jobModel.objects.get(pk=job_id)
            assigned_jobs_ids = jobAssingmentModel.objects.values('job_id_id').filter(created_by_id=request.user.id,
                                                                                      job_id_id__job_title=job.job_title,
                                                                                      job_id_id__client_name=job.client_name).exclude(
                job_id_id__isnull=True)
            # logger.info(jobs_assigned) job_id_id=job_id,
            numberOfJobsBdms = jobModel.objects.filter(created_by_id=request.user.id, job_title=job.job_title).exclude(
                id__in=assigned_jobs_ids)
            # logger.info(numberOfJobs)
            assigned_jobs = jobAssingmentModel.objects.filter(job_id_id=job_id).order_by('-created_at')[:1]

            # full_queryset = JobDescriptionSerializer(numberOfJobsBdms, many=True)
            jda_serializer = JobAssingmentWriteSerializer(assigned_jobs, many=True)

            logger.info("Job Query: " + str(numberOfJobsBdms.query))
            logger.info('assigned_jobs query: ' + str(assigned_jobs.query))
            queryset = self.filter_queryset(numberOfJobsBdms)
            page = self.paginate_queryset(queryset)
            response = None

            if page is not None:
                logger.info('Page Found List: ' + str(len(page)))
                serializer = self.get_serializer(page, many=True)
                # serializer = self.serializer_class(page, many=True)
                logger.info(list(assigned_jobs.values()))
                response = self.get_paginated_response(serializer.data)
                response.data["last_assigned_recruiter"] = jda_serializer.data
                return response

            serializer = self.get_serializer(queryset, many=True)
            logger.info('Job List: ' + str(serializer.data))

            responceData = {
                "count": 0,
                "next": None,
                "previous": None,
                "results": serializer.data,
                "last_assigned_recruiter": jda_serializer.data
            }
            return Response(responceData)

            """queryset = jobModel.objects.raw("SELECT ja.id, ja.primary_recruiter_name_id as primary_recruiter_name, "
                                            "ja.secondary_recruiter_name_id as secondary_recruiter_name, "
                                            "( SELECT COUNT(*) FROM `osms_job_description` WHERE id NOT IN (SELECT "
                                            "job_id_id FROM job_description_assingment as ja, osms_job_description as "
                                            "j WHERE j.id = ja.job_id_id AND j.created_by_id = "
                                            "%s GROUP BY job_id_id ) AND "
                                            "created_by_id = %s ) as "
                                            "number_of_unassigned_jobs FROM `osms_job_description` as j, "
                                            "job_description_assingment as ja WHERE j.id = ja.job_id_id AND "
                                            "j.created_by_id = %s order by "
                                            "j.created_at desc limit 1", [job_id, str(request.user.id).replace("-", "")])

        logger.info(queryset.query)"""

        # serializer = UnassignedJobsStatusSerializer(responceData, many=True)
        # return Response(responceData)


class ExportJobCandidateList(generics.ListAPIView):
    queryset = Candidates.objects.none()

    def get(self, request, format=None):
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

        """        else:
            sql = "SELECT id, first_name , last_name FROM osms_candidates ORDER BY created_at DESC"
            queryset = Candidates.objects.raw(sql)"""

        serializer = CandidatesSubmissionForJobListSerializer(queryset, many=True)
        array_length = len(serializer.data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bdm_performance_summary.csv"'

        writer = csv.DictWriter(response, fieldnames=["id", "first_name", "last_name", "status",
                                                      "submission_date", "updated_at", "updated_by_name",
                                                      "created_by_name",
                                                      "visa",
                                                      "min_rate", "max_rate", "min_salary", "max_salary"
                                                      ])

        writer.writeheader()

        writer.writerows(serializer.data)

        return response


class ExportAssignmentHistory(generics.ListAPIView):
    queryset = jobAssingmentModel.objects.none()

    def get(self, request, format=None):
        if request.query_params.get('job_id'):
            job_id = str(request.query_params.get('job_id')).replace('-', '')
            logger.info("job_id: " + str(job_id))
            queryset = jobAssingmentModel.objects.raw(
                "SELECT jda.id, CONCAT(u.first_name , ' ' , u.last_name) as primary_recruiter, "
                "CONCAT(u1.first_name , ' ' , u1.last_name) as secondary_recruiter, jda.assignee_name, "
                "jda.created_at FROM job_description_assingment as jda, users_user as u, users_user as u1 "
                " WHERE u.id = jda.created_by_id AND u1.id = jda.updated_by_id AND "
                "jda.job_id_id = %s ORDER BY jda.created_at DESC",
                [job_id])

        serializer = ExportAssignmentHistoryModelSerializer(queryset, many=True)
        array_length = len(serializer.data)
        outputs = []
        for i in range(array_length):
            rows = {
                'primary_recruiter_name': serializer.data[i]['primary_recruiter'],
                'secondary_recruiter_name': serializer.data[i]['secondary_recruiter'],
                'assignee_name': serializer.data[i]['assignee_name'],
                'assignment_date': serializer.data[i]['created_at'],
            }

            outputs.append(rows)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bdm_performance_summary.csv"'

        writer = csv.DictWriter(response, fieldnames=[ "primary_recruiter_name", "secondary_recruiter_name",
                                                      "assignee_name", "assignment_date"
                                                      ])

        writer.writeheader()

        writer.writerows(outputs)

        return response
