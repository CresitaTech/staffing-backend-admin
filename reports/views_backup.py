import csv

from dateutil.relativedelta import relativedelta
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection
import datetime
# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_csv.renderers import CSVRenderer
from datetime import date

from candidates.models import Candidates
from candidates.serializers import CandidateSerializer, CandidateWriteSerializer
from clients.models import clientModel
from clients.serializers import ClientSerializer
from comman_utils import utils
from jobdescriptions.models import jobModel
from reports.filters import ReportFilter
from reports.serializers import RecruiterPerformanceSummarySerializer, RecruiterPerformanceSummaryGraphSerializer, \
    BdmPerformanceSummarySerializer, BdmPerformanceSummaryGraphSerializer, JobSummarySerializer, \
    JobSummaryGraphSerializer, ClientSummarySerializer, TopFivePlacementSerializer, ClientDropdownListSerializer, \
    JobsDropdownListSerializer, ClientDashboardListSerializer, UserObjectSerializer, ActiveClientSerializer, \
    TotalRecordSerializer , AssingedDashboardListSerializer , JobSummaryTableSerializer , JobsByBDMTableSerializer

# SELECT COUNT(*) as total_count, s.stage_name FROM `osms_candidates` as c, `candidates_stages` as s WHERE c.stage_id = s.id GROUP BY c.stage_id
# SELECT COUNT(*) as total_count, s.stage_name, u.first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id GROUP BY c.stage_id, u.first_name
from staffingapp.settings import GLOBAL_ROLE
from users.models import User
from users.serializers import UserSerializer


class RecruiterPerformanceSummaryTable(generics.ListAPIView):
    serializer_class = RecruiterPerformanceSummarySerializer
    queryset = Candidates.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]  # SearchFilter,
    filter_class = ReportFilter

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        print(start_date)
        print(end_date)

        today = utils.get_current_date()
        yesterday = utils.yesterday_datetime()
        week_start, week_end = utils.week_date_range()
        month_start, month_end = utils.month_date_range()

        candObj = User.objects.get(pk=request.user.id)
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

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at > %s", [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name)as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s", [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s", [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s", [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s", [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s", [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s", [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s", [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s", [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s", [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s", [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw("SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, start_date, end_date])

        if queryset is not None:
            print(str(queryset.query))

        # queryset = self.filter_queryset(queryset)
        serializer = BdmPerformanceSummarySerializer(queryset, many=True)
        # print(serializer.data['first_name'])
        array_length = len(serializer.data)
        outputs = []
        print(array_length)
        uuids = set()
        for i in range(array_length):  # Use `xrange` for python 2.
            cursor = connection.cursor()
            recruiter_id = serializer.data[i]['recruiter_name']
            cursor.execute("SELECT first_name, last_name FROM users_user WHERE id=%s", [recruiter_id])
            recruiter_name = cursor.fetchone()
            uuids.add(recruiter_id)

            rows = {
                'candidate_name': serializer.data[i]['candidate_name'],
                'primary_email': serializer.data[i]['primary_email'],
                'primary_phone_number': serializer.data[i]['primary_phone_number'],
                'company_name': serializer.data[i]['company_name'],
                'total_experience': serializer.data[i]['total_experience'],
                'rank': serializer.data[i]['rank'],
                'job_title': serializer.data[i]['job_title'],
                'skills_1': serializer.data[i]['skills_1'],
                'min_rate': serializer.data[i]['min_rate'],
                'max_rate': serializer.data[i]['max_rate'],
                'min_salary': serializer.data[i]['min_salary'],
                'max_salary': serializer.data[i]['max_salary'],
                'visa': serializer.data[i]['visa'],
                'job_type': serializer.data[i]['job_type'],
                'client_name': serializer.data[i]['client_name'],
                'location': serializer.data[i]['location'],
                'bdm_name': serializer.data[i]['bdm_name'],
                'status': serializer.data[i]['status'],
                'recruiter_name': recruiter_name[0]+' '+recruiter_name[1],
                'submission_date': serializer.data[i]['submission_date'],
                'job_date': serializer.data[i]['job_date']
            }

            outputs.append(rows)

        return Response(outputs)


class RecruiterPerformanceSummaryGraph(generics.ListAPIView):
    queryset = Candidates.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]  # SearchFilter,
    filter_class = ReportFilter

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        print(start_date)
        print(end_date)

        today = utils.get_current_date()
        print(today)
        yesterday = utils.yesterday_datetime()
        print(yesterday)

        week_start, week_end = utils.week_date_range()
        print(week_start)
        print(week_end)

        month_start, month_end = utils.month_date_range()
        print(month_start)
        print(month_end)

        candObj = User.objects.get(pk=request.user.id)
        serializeObj = UserSerializer(candObj)
        groups = dict(serializeObj.data)
        userGroupDict = None
        userGroup = None
        if len(groups['groups']) > 0:
            userGroupDict = dict(groups['groups'][0])
        if userGroupDict is not None:
            userGroup = userGroupDict['name']
        print(userGroup)
        uid = str(request.user.id).replace("-", "")
        queryset = None
        print(GLOBAL_ROLE.get('ADMIN'))

        # if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):

        if date_range == 'today':
            queryset = Candidates.objects.raw(
                "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name , c.created_by_id  FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_at > %s GROUP BY c.stage_id, u.first_name",
                [today])
        elif date_range == 'yesterday':
            queryset = Candidates.objects.raw(
                "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name, c.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_at > %s AND c.created_at < %s GROUP BY c.stage_id, u.first_name",
                [yesterday , today])
        elif date_range == 'week':
            queryset = Candidates.objects.raw(
                "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name, c.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_at >= %s AND c.created_at <= %s GROUP BY c.stage_id, u.first_name",
                [week_start, week_end])
        elif date_range == 'month':
            queryset = Candidates.objects.raw(
                "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name, c.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_at >= %s AND c.created_at <= %s GROUP BY c.stage_id, u.first_name",
                [month_start, month_end])
        elif start_date is not None and end_date is not None:
            queryset = Candidates.objects.raw(
                "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name, c.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_at >= %s AND c.created_at <= %s GROUP BY c.stage_id, u.first_name",
                [start_date, end_date])


        """        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_at = %s GROUP BY c.stage_id, u.first_name", [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_at = %s GROUP BY c.stage_id, u.first_name", [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_at >= %s AND c.created_at <= %s GROUP BY c.stage_id, u.first_name", [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_at >= %s AND c.created_at <= %s GROUP BY c.stage_id, u.first_name", [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_at >= %s AND c.created_at <= %s GROUP BY c.stage_id, u.first_name", [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_by_id = %s AND c.created_at = %s GROUP BY c.stage_id, u.first_name", [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_by_id = %s AND c.created_at = %s GROUP BY c.stage_id, u.first_name", [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_by_id = %s AND c.created_at >= %s AND c.created_at <= %s GROUP BY c.stage_id, u.first_name", [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_by_id = %s AND c.created_at >= %s AND c.created_at <= %s GROUP BY c.stage_id, u.first_name", [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_by_id = %s AND c.created_at >= %s AND c.created_at <= %s GROUP BY c.stage_id, u.first_name", [uid, start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_by_id = %s AND c.created_at = %s GROUP BY c.stage_id, u.first_name", [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_by_id = %s AND c.created_at = %s GROUP BY c.stage_id, u.first_name", [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_by_id = %s AND c.created_at >= %s AND c.created_at <= %s GROUP BY c.stage_id, u.first_name", [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_by_id = %s AND c.created_at >= %s AND c.created_at <= %s GROUP BY c.stage_id, u.first_name", [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_by_id = %s AND c.created_at >= %s AND c.created_at <= %s GROUP BY c.stage_id, u.first_name", [uid, start_date, end_date])
"""
        if queryset is not None:
            print(str(queryset.query))
        serializer = RecruiterPerformanceSummaryGraphSerializer(queryset, many=True)
        # print(serializer.data)
        return Response(serializer.data)


class RecruiterPerformanceSummaryCSV(generics.ListAPIView):
    queryset = Candidates.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]  # SearchFilter,
    filter_class = ReportFilter

    def get(self, request, format=None):

        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        print(start_date)
        print(end_date)

        today = utils.get_current_date()
        yesterday = utils.yesterday_datetime()
        week_start, week_end = utils.week_date_range()
        month_start, month_end = utils.month_date_range()

        candObj = User.objects.get(pk=request.user.id)
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

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

        if queryset is not None:
            print(str(queryset.query))

        # queryset = self.filter_queryset(queryset)
        serializer = BdmPerformanceSummarySerializer(queryset, many=True)
        # print(serializer.data['first_name'])
        array_length = len(serializer.data)
        outputs = []
        print(array_length)
        uuids = set()
        for i in range(array_length):  # Use `xrange` for python 2.
            cursor = connection.cursor()
            recruiter_id = serializer.data[i]['recruiter_name']
            cursor.execute("SELECT first_name, last_name FROM users_user WHERE id=%s", [recruiter_id])
            recruiter_name = cursor.fetchone()
            uuids.add(recruiter_id)

            rows = {
                'candidate_name': serializer.data[i]['candidate_name'],
                'primary_email': serializer.data[i]['primary_email'],
                'primary_phone_number': serializer.data[i]['primary_phone_number'],
                'company_name': serializer.data[i]['company_name'],
                'total_experience': serializer.data[i]['total_experience'],
                'rank': serializer.data[i]['rank'],
                'job_title': serializer.data[i]['job_title'],
                'skills_1': serializer.data[i]['skills_1'],
                'rate': str(serializer.data[i]['min_rate'])+ '-' +str(serializer.data[i]['max_rate']),
                'salary': str(serializer.data[i]['min_salary'])+ '-' +str(serializer.data[i]['min_salary']),
                'client_name': serializer.data[i]['client_name'],
                'location': serializer.data[i]['location'],
                'visa': serializer.data[i]['visa'],
                'job_type': serializer.data[i]['job_type'],
                'bdm_name': serializer.data[i]['bdm_name'],
                'status': serializer.data[i]['status'],
                'recruiter_name': recruiter_name[0]+' '+recruiter_name[1],
                'submission_date': serializer.data[i]['submission_date'],
                'job_date': serializer.data[i]['job_date']
            }

            outputs.append(rows)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="recruiter_performance_summary.csv"'
        writer = csv.DictWriter(response, fieldnames=["candidate_name", "primary_email", "primary_phone_number",
                  "company_name", "total_experience", "rank","job_title", "skills_1",
                  "rate", "salary", "client_name", "location","visa" , "job_type" , "bdm_name",
                  "status","recruiter_name", "submission_date", "job_date"
                  ])

        writer.writeheader()

        writer.writerows(outputs)

        return response

####################### BDM Performance Summary ######################


class BdmPerformanceSummaryTable(generics.ListAPIView):
    queryset = Candidates.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]  # SearchFilter,
    filter_class = ReportFilter

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        print(start_date)
        print(end_date)

        today = utils.get_current_date()
        yesterday = utils.yesterday_datetime()
        week_start, week_end = utils.week_date_range()
        month_start, month_end = utils.month_date_range()

        candObj = User.objects.get(pk=request.user.id)
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

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at > %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id  AND ca.created_at = %s",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

        if queryset is not None:
            print(str(queryset.query))
        # queryset = self.filter_queryset(queryset)
        serializer = BdmPerformanceSummarySerializer(queryset, many=True)
        # print(serializer.data['first_name'])
        array_length = len(serializer.data)
        outputs = []
        print(array_length)
        uuids = set()
        for i in range(array_length):  # Use `xrange` for python 2.
            cursor = connection.cursor()
            recruiter_id = serializer.data[i]['recruiter_name']
            cursor.execute("SELECT first_name, last_name FROM users_user WHERE id=%s", [recruiter_id])
            recruiter_name = cursor.fetchone()
            uuids.add(recruiter_id)

            rows = {
                'candidate_name': serializer.data[i]['candidate_name'],
                'primary_email': serializer.data[i]['primary_email'],
                'primary_phone_number': serializer.data[i]['primary_phone_number'],
                'company_name': serializer.data[i]['company_name'],
                'total_experience': serializer.data[i]['total_experience'],
                'rank': serializer.data[i]['rank'],
                'job_title': serializer.data[i]['job_title'],
                'skills_1': serializer.data[i]['skills_1'],
                'min_rate': serializer.data[i]['min_rate'],
                'max_rate': serializer.data[i]['max_rate'],
                'min_salary': serializer.data[i]['min_salary'],
                'max_salary': serializer.data[i]['max_salary'],
                'visa': serializer.data[i]['visa'],
                'job_type': serializer.data[i]['job_type'],
                'client_name': serializer.data[i]['client_name'],
                'location': serializer.data[i]['location'],
                'bdm_name': serializer.data[i]['bdm_name'],
                'status': serializer.data[i]['status'],
                'recruiter_name': recruiter_name[0]+' '+recruiter_name[1],
                'submission_date': serializer.data[i]['submission_date'],
                'job_date': serializer.data[i]['job_date']
            }

            outputs.append(rows)

        uuids = list(uuids)
        print(uuids)
        if len(uuids) > 0:
            userqr = User.objects.filter(id__in=uuids)
            print(str(userqr.query))
            userSer = UserObjectSerializer(userqr)

        return Response(outputs)


class BdmPerformanceSummaryGraph(generics.ListAPIView):
    queryset = Candidates.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]  # SearchFilter,
    filter_class = ReportFilter

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        print(start_date)
        print(end_date)

        today = utils.get_current_date()
        print("==============================today=========="+str(today))
        yesterday = utils.yesterday_datetime()
        print("==============================today=========="+str(yesterday))

        week_start, week_end = utils.week_date_range()
        print(week_start)
        print(week_end)

        month_start, month_end = utils.month_date_range()
        print(month_start)
        print(month_end)

        candObj = User.objects.get(pk=request.user.id)
        serializeObj = UserSerializer(candObj)
        groups = dict(serializeObj.data)
        userGroupDict = None
        userGroup = None
        if len(groups['groups']) > 0:
            userGroupDict = dict(groups['groups'][0])
        if userGroupDict is not None:
            userGroup = userGroupDict['name']
        print(userGroup)
        uid = str(request.user.id).replace("-", "")
        queryset = None
        print(GLOBAL_ROLE.get('ADMIN'))
        if userGroup is not None and (userGroup == GLOBAL_ROLE.get('ADMIN') or userGroup == GLOBAL_ROLE.get('BDMMANAGER') ):
            if date_range == 'today':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name, j.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id and j.created_by_id = u.id AND c.created_at > %s GROUP BY c.stage_id, u.first_name", [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name, j.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id and j.created_by_id = u.id AND c.created_at > %s AND c.created_at < %s GROUP BY c.stage_id, u.first_name", [yesterday , today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name, j.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id and j.created_by_id = u.id AND c.created_at >= %s  AND c.created_at <= %s GROUP BY c.stage_id, u.first_name", [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name ,j.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id and j.created_by_id = u.id AND c.created_at >= %s  AND c.created_at <= %s GROUP BY c.stage_id, u.first_name", [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name , j.created_by_id  FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id and j.created_by_id = u.id AND c.created_at >= %s  AND c.created_at <= %s GROUP BY c.stage_id, u.first_name", [start_date, end_date])

        """        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id and j.created_by_id = u.id AND j.created_by_id = %s AND j.created_at = %s  GROUP BY c.stage_id, u.first_name", [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id and j.created_by_id = u.id AND j.created_by_id = %s AND j.created_at = %s GROUP BY c.stage_id, u.first_name", [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id and j.created_by_id = u.id AND j.created_by_id = %s AND j.created_at >= %s  AND j.created_at <= %s GROUP BY c.stage_id, u.first_name", [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id and j.created_by_id = u.id AND j.created_by_id = %s AND j.created_at >= %s  AND j.created_at <= %s GROUP BY c.stage_id, u.first_name", [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id and j.created_by_id = u.id AND j.created_by_id = %s AND j.created_at >= %s  AND j.created_at <= %s GROUP BY c.stage_id, u.first_name", [uid, start_date, end_date])
"""
        if queryset is not None:
            print(str(queryset.query))

        serializer = BdmPerformanceSummaryGraphSerializer(queryset, many=True)
        # print(serializer.data)
        return Response(serializer.data)


class BdmPerformanceSummaryCSV(generics.ListAPIView):
    queryset = Candidates.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]  # SearchFilter,
    filter_class = ReportFilter

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        print(start_date)
        print(end_date)

        today = utils.get_current_date()
        yesterday = utils.yesterday_datetime()
        week_start, week_end = utils.week_date_range()
        month_start, month_end = utils.month_date_range()

        candObj = User.objects.get(pk=request.user.id)
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

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

        if queryset is not None:
            print(str(queryset.query))
        # queryset = self.filter_queryset(queryset)
        serializer = BdmPerformanceSummarySerializer(queryset, many=True)
        array_length = len(serializer.data)
        outputs = []
        print(array_length)
        uuids = set()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bdm_performance_summary.csv"'

        writer = csv.DictWriter(response, fieldnames=["candidate_name", "primary_email", "primary_phone_number",
                  "company_name", "total_experience", "rank","job_title", "skills_1",
                  "rate", "salary", "client_name", "location","visa" , "job_type", "bdm_name",
                  "status","recruiter_name", "submission_date", "job_date"
                  ])

        writer.writeheader()

        for i in range(array_length):  # Use `xrange` for python 2.
            cursor = connection.cursor()
            recruiter_id = serializer.data[i]['recruiter_name']
            cursor.execute("SELECT first_name, last_name FROM users_user WHERE id=%s", [recruiter_id])
            recruiter_name = cursor.fetchone()
            uuids.add(recruiter_id)
            rows = {
                'candidate_name': serializer.data[i]['candidate_name'],
                'primary_email': serializer.data[i]['primary_email'],
                'primary_phone_number': serializer.data[i]['primary_phone_number'],
                'company_name': serializer.data[i]['company_name'],
                'total_experience': serializer.data[i]['total_experience'],
                'rank': serializer.data[i]['rank'],
                'job_title': serializer.data[i]['job_title'],
                'skills_1': serializer.data[i]['skills_1'],
                'rate': str(serializer.data[i]['min_rate'])+ '-' +str(serializer.data[i]['max_rate']),
                'salary': str(serializer.data[i]['min_salary'])+ '-' +str(serializer.data[i]['max_salary']),
                'client_name': serializer.data[i]['client_name'],
                'location': serializer.data[i]['location'],
                'visa': serializer.data[i]['visa'],
                'job_type': serializer.data[i]['job_type'],
                'bdm_name': serializer.data[i]['bdm_name'],
                'status': serializer.data[i]['status'],
                'recruiter_name': recruiter_name[0]+' '+recruiter_name[1],
                'submission_date': serializer.data[i]['submission_date'],
                'job_date': serializer.data[i]['job_date']
            }

            outputs.append(rows)

        writer.writerows(outputs)

        return response

####################### Job Performance Summary ######################


class JobSummaryTable(generics.ListAPIView):
    queryset = Candidates.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]  # SearchFilter,
    filter_class = ReportFilter

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        print(start_date)
        print(end_date)

        today = utils.get_current_date()
        yesterday = utils.yesterday_datetime()
        week_start, week_end = utils.week_date_range()
        month_start, month_end = utils.month_date_range()

        candObj = User.objects.get(pk=request.user.id)
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

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at = %s) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at = %s) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at = %s) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at = %s) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at = %s) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at = %s) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at = %s) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at = %s) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [start_date, end_date])


        if queryset is not None:
            print(str(queryset.query))

        # queryset = self.filter_queryset(queryset)
        serializer = JobSummaryTableSerializer(queryset, many=True)
        # print(serializer.data['first_name'])
        array_length = len(serializer.data)
        outputs = []
        print(array_length)
        uuids = set()
        for i in range(array_length):  # Use `xrange` for python 2.

            rows = {
                'id': serializer.data[i]['id'],
                'job_title': serializer.data[i]['job_title'],
                'job_id': serializer.data[i]['Job_ID'],
                'client_name': serializer.data[i]['client_name'],
                'bdm_name': serializer.data[i]['bdm_name'],
                'job_type': serializer.data[i]['employment_type'],
                'min_salary': serializer.data[i]['min_salary'],
                'max_salary': serializer.data[i]['max_salary'],
                'min_rate': serializer.data[i]['min_rate'],
                'max_rate': serializer.data[i]['max_rate'],
                'job_date': serializer.data[i]['job_date'],
                'client_interview': serializer.data[i]['Client_Interview'],
                'offered': serializer.data[i]['Offered'],
                'submission': serializer.data[i]['Submission'],
                'rejected_by_team': serializer.data[i]['Rejected_By_Team'],
                'sendout_reject': serializer.data[i]['Sendout_Reject'],
                'offer_rejected': serializer.data[i]['Offer_Rejected'],
                'shortlisted': serializer.data[i]['Shortlisted'],
                'internal_interview': serializer.data[i]['Internal_Interview'],
                'awaiting_feedback': serializer.data[i]['Awaiting_Feedback'],
                'placed': serializer.data[i]['Placed'],
                'rejected_by_client': serializer.data[i]['Rejected_By_Client'],
                'submission_reject': serializer.data[i]['Submission_Reject'],
                'send_out': serializer.data[i]['SendOut'],
            }

            outputs.append(rows)

        return Response(outputs)


class JobSummaryGraph(generics.ListAPIView):
    queryset = Candidates.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]  # SearchFilter,
    filter_class = ReportFilter

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        print(start_date)
        print(end_date)

        today = utils.get_current_date()
        print(today)
        yesterday = utils.yesterday_datetime()
        print(yesterday)

        week_start, week_end = utils.week_date_range()
        print(week_start)
        print(week_end)

        month_start, month_end = utils.month_date_range()
        print(month_start)
        print(month_end)

        candObj = User.objects.get(pk=request.user.id)
        serializeObj = UserSerializer(candObj)
        groups = dict(serializeObj.data)
        userGroupDict = None
        userGroup = None
        if len(groups['groups']) > 0:
            userGroupDict = dict(groups['groups'][0])
        if userGroupDict is not None:
            userGroup = userGroupDict['name']
        print(userGroup)
        uid = str(request.user.id).replace("-", "")
        queryset = None
        print(GLOBAL_ROLE.get('ADMIN'))
        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT c.id,COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title , j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_at = %s GROUP BY c.stage_id, j.job_title",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title , j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_at = %s GROUP BY c.stage_id, j.job_title",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title , j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_at >= %s AND j.created_at <= %s GROUP BY c.stage_id, j.job_title",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title, j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_at >= %s AND j.created_at <= %s GROUP BY c.stage_id, j.job_title",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title , j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_at >= %s AND j.created_at <= %s GROUP BY c.stage_id, j.job_title",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title ,j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_by_id = %s AND j.created_at = %s GROUP BY c.stage_id, j.job_title",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title,j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_by_id = %s AND j.created_at = %s GROUP BY c.stage_id, j.job_title",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title,j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_by_id = %s AND j.created_at >= %s AND j.created_at <= %s GROUP BY c.stage_id, j.job_title",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title,j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_by_id = %s  AND j.created_at >= %s AND j.created_at <= %s GROUP BY c.stage_id, j.job_title",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title,j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_by_id = %s  AND j.created_at >= %s AND j.created_at <= %s GROUP BY c.stage_id, j.job_title",
                    [uid, start_date, end_date])

        if queryset is not None:
            print(str(queryset.query))

        serializer = JobSummaryGraphSerializer(queryset, many=True)
        # print(serializer.data)
        return Response(serializer.data)


class JobSummaryCSV(generics.ListAPIView):
    queryset = Candidates.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]  # SearchFilter,
    filter_class = ReportFilter

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        print(start_date)
        print(end_date)

        today = utils.get_current_date()
        yesterday = utils.yesterday_datetime()
        week_start, week_end = utils.week_date_range()
        month_start, month_end = utils.month_date_range()

        candObj = User.objects.get(pk=request.user.id)
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

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at = %s) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at = %s) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at = %s) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at = %s) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at = %s) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at = %s) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at = %s) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at = %s) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (j.created_at >=%s AND j.created_at <=%s)) "
                    "AS A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission , sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' , "
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' , "
                    "sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,"
                    "sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s WHERE ca.stage_id = s.id AND ca.job_description_id = j.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [start_date, end_date])

        if queryset is not None:
            print(str(queryset.query))

        # queryset = self.filter_queryset(queryset)
        serializer = JobSummarySerializer(queryset, many=True)
        # print(serializer.data['first_name'])
        array_length = len(serializer.data)
        outputs = []
        print(array_length)
        uuids = set()
        for i in range(array_length):  # Use `xrange` for python 2.
            
            rows = {
                'id': serializer.data[i]['id'],
                'job_title': serializer.data[i]['job_title'],
                'job_id': serializer.data[i]['Job_ID'],
                'client_name': serializer.data[i]['client_name'],
                'bdm_name': serializer.data[i]['bdm_name'],
                'job_type': serializer.data[i]['employment_type'],
                'min_salary': serializer.data[i]['min_salary'],
                'max_salary': serializer.data[i]['max_salary'],
                'min_rate': serializer.data[i]['min_rate'],
                'max_rate': serializer.data[i]['max_rate'],
                'job_date': serializer.data[i]['job_date'],
                'client_interview': serializer.data[i]['Client_Interview'],
                'offered': serializer.data[i]['Offered'],
                'submission': serializer.data[i]['Submission'],
                'rejected_by_team': serializer.data[i]['Rejected_By_Team'],
                'sendout_reject': serializer.data[i]['Sendout_Reject'],
                'offer_rejected': serializer.data[i]['Offer_Rejected'],
                'shortlisted': serializer.data[i]['Shortlisted'],
                'internal_interview': serializer.data[i]['Internal_Interview'],
                'awaiting_feedback': serializer.data[i]['Awaiting_Feedback'],
                'placed': serializer.data[i]['Placed'],
                'rejected_by_client': serializer.data[i]['Rejected_By_Client'],
                'submission_reject': serializer.data[i]['Submission_Reject'],
                'send_out': serializer.data[i]['SendOut'],
            }

            outputs.append(rows)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="job_summary.csv"'
        writer = csv.DictWriter(response, fieldnames=['id','job_id',
                                                      'job_title', 'client_name', 'bdm_name','job_date','job_type','min_salary','max_salary','min_rate','max_rate',
                                                      'client_interview', 'offered' ,'submission', 'rejected_by_team',
                                                      'sendout_reject', 'offer_rejected' , 'shortlisted','internal_interview','awaiting_feedback',
                                                      'placed','rejected_by_client',
                                                      'submission_reject' , 'send_out'
                                                      ])

        writer.writeheader()

        writer.writerows(outputs)

        return response


class AggregateData(generics.ListAPIView):
    queryset = clientModel.objects.all()

    def get(self, request, format=None):
        candObj = User.objects.get(pk=request.user.id)
        serializeObj = UserSerializer(candObj)
        groups = dict(serializeObj.data)
        userGroupDict = None
        userGroup = None
        active_clients = 0
        submissions = 0
        placed = 0
        active_jobs = 0
        revenue = 0
        sendOut = 0
        interviewed = 0
        queryset = None
        uid = str(request.user.id).replace("-", "")

        if len(groups['groups']) > 0:
            userGroupDict = dict(groups['groups'][0])
        if userGroupDict is not None:
            userGroup = userGroupDict['name']

        print("========User Role: ========")
        print(userGroup)

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            print("========Admin Data========")
            active_jobs = jobModel.objects.count()
            active_clients = clientModel.objects.count()
            revenue = jobModel.objects.all().aggregate(Sum('projected_revenue'))['projected_revenue__sum']
            placed = Candidates.objects.filter(stage_id__stage_name="Placed").annotate(Count('stage')).count()

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            active_jobs = jobModel.objects.filter(created_by_id=request.user.id).count() # Q(created_by_id__created_by_id=request.user.id) |
            active_clients = clientModel.objects.filter(created_by_id=request.user.id).count() # Q(created_by_id__created_by_id=request.user.id) |
            queryset = jobModel.objects.raw(
                "SELECT c.id, COUNT(*) as total_records FROM `osms_candidates` as c, `osms_job_description` as j, `candidates_stages` as s WHERE c.job_description_id = j.id AND c.stage_id = s.id AND j.created_by_id = %s AND s.stage_name != 'Candidate Added'",
                [uid])
            serializer = TotalRecordSerializer(queryset, many=True)
            if serializer.data[0] is not None and len(serializer.data[0]) > 0:
                submissions = str(serializer.data[0]['total_records'])
            queryset = jobModel.objects.raw(
                "SELECT c.id, COUNT(*) as total_records FROM `osms_candidates` as c, `osms_job_description` as j, `candidates_stages` as s WHERE c.job_description_id = j.id AND c.stage_id = s.id AND j.created_by_id = %s AND s.stage_name = 'Placed'",
                [uid])
            serializer = TotalRecordSerializer(queryset, many=True)
            if serializer.data[0] is not None and len(serializer.data[0]) > 0:
                placed = str(serializer.data[0]['total_records'])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            active_jobs = jobModel.objects.filter(Q(default_assignee_id=request.user.id)).count() # Q(created_by_id__created_by_id=request.user.id) |
            queryset = clientModel.objects.raw("SELECT c.id, COUNT(DISTINCT(c.company_name)) as active_clients FROM `osms_job_description` as j, `osms_clients` as c WHERE j.client_name_id = c.id AND j.default_assignee_id = %s", [uid])
            serializer = ActiveClientSerializer(queryset, many=True)
            if serializer.data[0] is not None and len(serializer.data[0]) > 0:
                active_clients = str(serializer.data[0]['active_clients'])
            submissions = Candidates.objects.filter((Q(created_by_id__created_by_id=request.user.id) | Q(created_by_id=request.user.id)), stage_id__stage_name="Submission").annotate(Count('stage')).count()
            placed = Candidates.objects.filter((Q(created_by_id__created_by_id=request.user.id) | Q(created_by_id=request.user.id)), stage_id__stage_name="Placed").annotate(Count('stage')).count()

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            interviewed = Candidates.objects.filter(created_by_id=request.user.id).count()
            sendOut = Candidates.objects.filter(created_by_id=request.user.id, stage_id__stage_name="SendOut").annotate(
                Count('stage')).count()
            submissions = Candidates.objects.filter(created_by_id=request.user.id,
                                                    stage_id__stage_name="Submission").annotate(Count('stage')).count()
            placed = Candidates.objects.filter(created_by_id=request.user.id, stage_id__stage_name="Placed").annotate(
                Count('stage')).count()

        # active_jobs = jobModel.objects.count()
        # submissions = Candidates.objects.filter(stage_id__stage_name="Subimission").annotate(Count('stage')).count()
        # placed = Candidates.objects.filter(stage_id__stage_name="Placed").annotate(Count('stage')).count()
        response = {
            "active_clients": active_clients,
            "active_jobs": active_jobs,
            "submissions": submissions,
            "placed": placed,
            "revenue": revenue,
            "interviewed": interviewed,
            "sendOut": sendOut
        }
        # serializer = AggregateDataSerializer(total_client, many=True)
        return Response(response)


class TopClients(generics.ListAPIView):
    queryset = clientModel.objects.all()

    def get(self, request, format=None):
        candObj = User.objects.get(pk=request.user.id)
        serializeObj = UserSerializer(candObj)
        groups = dict(serializeObj.data)
        userGroupDict = None
        userGroup = None
        queryset = None
        uid = str(request.user.id).replace("-", "")

        if len(groups['groups']) > 0:
            userGroupDict = dict(groups['groups'][0])
        if userGroupDict is not None:
            userGroup = userGroupDict['name']

        print("========User Role: ========")
        print(userGroup)

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            queryset = clientModel.objects.raw("SELECT cl.id, cl.company_name as client_name, (Select COUNT(s.stage_name) from osms_candidates as c, candidates_stages as s, osms_job_description as j WHERE c.stage_id = s.id AND s.stage_name = 'Submission' AND c.job_description_id = j.id and j.client_name_id = cl.id ) as submissions, (Select COUNT(s.stage_name) from osms_candidates as c, candidates_stages as s, osms_job_description as j WHERE c.stage_id = s.id AND s.stage_name = 'Placed' AND c.job_description_id = j.id and j.client_name_id = cl.id ) as placed, (Select COUNT(j.job_title) from osms_job_description as j WHERE j.client_name_id = cl.id ) as job_title FROM `osms_clients` as cl")  # Q(created_by_id__created_by_id=request.user.id) |

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            queryset = clientModel.objects.raw("SELECT cl.id, cl.company_name as client_name, (Select COUNT(s.stage_name) from osms_candidates as c, candidates_stages as s, osms_job_description as j WHERE c.stage_id = s.id AND s.stage_name = 'Submission' AND c.job_description_id = j.id and j.created_by_id = %s AND j.client_name_id = cl.id ) as submissions, (Select COUNT(s.stage_name) from osms_candidates as c, candidates_stages as s, osms_job_description as j WHERE c.stage_id = s.id AND s.stage_name = 'Placed' AND c.job_description_id = j.id and j.created_by_id = %s AND j.client_name_id = cl.id ) as placed, (Select COUNT(j.job_title) from osms_job_description as j WHERE j.created_by_id = %s AND j.client_name_id = cl.id ) as job_title FROM `osms_clients` as cl WHERE cl.created_by_id = %s", [uid, uid, uid, uid])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            queryset = clientModel.objects.raw("SELECT cl.id, cl.company_name as client_name, (Select COUNT(s.stage_name) from osms_candidates as c, candidates_stages as s, osms_job_description as j WHERE c.stage_id = s.id AND s.stage_name = 'Submission' AND c.job_description_id = j.id and j.client_name_id = cl.id ) as submissions, (Select COUNT(s.stage_name) from osms_candidates as c, candidates_stages as s, osms_job_description as j WHERE c.stage_id = s.id AND s.stage_name = 'Placed' AND c.job_description_id = j.id and j.client_name_id = cl.id ) as placed, (Select COUNT(j.job_title) from osms_job_description as j WHERE j.client_name_id = cl.id ) as job_title FROM `osms_clients` as cl, `osms_job_description` as ja WHERE ja.client_name_id = cl.id AND ja.default_assignee_id = %s GROUP BY cl.company_name", [uid])

        serializer = ClientSummarySerializer(queryset, many=True)
        array_length = len(serializer.data)
        clients = []

        """        for i in range(array_length):  # Use `xrange` for python 2.
            id = serializer.data[i]['id']
            company_name = serializer.data[i]['company_name']

            submissions = Candidates.objects.filter(stage_id__stage_name="Subimission", job_description_id=id).annotate(Count('stage')).count()
            placed = Candidates.objects.filter(stage_id__stage_name="Placed", job_description_id=id).annotate(Count('stage')).count()
            active_jobs = jobModel.objects.filter(client_name_id=id).count() # Q(created_by_id__created_by_id=request.user.id) |

            row = {
                "client_name": str(company_name),
                "job_title" : active_jobs,
                "submissions": submissions,
                "placed": placed
            }
            clients.append(row)"""

        return Response(serializer.data)


class TopFivePlacement(generics.ListAPIView):
    queryset = Candidates.objects.none()

    def get(self, request, format=None):
        sql = 'SELECT  ca.id as id, CONCAT(ca.first_name, " ", ca.last_name ) AS candidate_name, cl.company_name AS client_name, s.stage_name as status FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND s.stage_name = "Placed" '
        queryset = Candidates.objects.raw(sql)
        serializer = TopFivePlacementSerializer(queryset, many=True)
        # serializer = AggregateDataSerializer(total_client, many=True)

        return Response(serializer.data)


class ClinetDropdownList(generics.ListAPIView):
    queryset = clientModel.objects.none()

    def get(self, request, format=None):
        sql = "SELECT id, company_name FROM osms_clients "
        queryset = clientModel.objects.raw(sql)
        serializer = ClientDropdownListSerializer(queryset, many=True)
        return Response(serializer.data)


class JobsDropdownList(generics.ListAPIView):
    queryset = jobModel.objects.none()

    def get(self, request, format=None):
        sql = "SELECT id, job_title ,client_name_id  FROM osms_job_description"
        queryset = jobModel.objects.raw(sql)
        serializer = JobsDropdownListSerializer(queryset, many=True)
        return Response(serializer.data)


class JobsDashboardList(generics.ListAPIView):
    queryset = jobModel.objects.none()

    def get(self, request, format=None):
        userObj = User.objects.get(pk=request.user.id)
        serializeObj = UserSerializer(userObj)
        groups = dict(serializeObj.data)
        userGroupDict = None
        userGroup = None
        queryset = None
        uid = str(request.user.id).replace("-", "")

        if len(groups['groups']) > 0:
            userGroupDict = dict(groups['groups'][0])
        if userGroupDict is not None:
            userGroup = userGroupDict['name']

        print("========User Role: ========")
        print(userGroup)

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            queryset = jobModel.objects.raw(
                "SELECT j.id, j.created_at, j.job_title, cl.company_name, u.first_name as default_assignee_name, ja.created_at as assinged_date FROM `osms_job_description` as j, `osms_clients` as cl, `users_user` as u, `job_description_assingment` as ja"
                " WHERE (j.client_name_id = cl.id AND u.id = j.default_assignee_id AND ja.job_id_id = j.id AND ja.primary_recruiter_name_id = %s) OR (j.client_name_id = cl.id AND u.id = j.default_assignee_id AND ja.job_id_id = j.id AND ja.secondary_recruiter_name_id = %s) ORDER BY assinged_date DESC",
                [uid, uid])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            queryset = jobModel.objects.raw(
                "SELECT j.id, j.created_at, j.job_title, cl.company_name, u.first_name as default_assignee_name, ja.created_at as assinged_date FROM `osms_job_description` as j, `osms_clients` as cl, `users_user` as u, `job_description_assingment` as ja"
                " WHERE (j.client_name_id = cl.id AND u.id = j.default_assignee_id AND ja.job_id_id = j.id AND ja.primary_recruiter_name_id = %s) OR (j.client_name_id = cl.id AND u.id = j.default_assignee_id AND ja.job_id_id = j.id AND ja.secondary_recruiter_name_id = %s) ORDER BY assinged_date DESC",
                [uid, uid])
        # sql = "SELECT j.id, j.created_at, j.job_title, cl.company_name, u.first_name as default_assignee_name FROM `osms_job_description` as j, `osms_clients` as cl, `users_user` as u WHERE j.client_name_id = cl.id AND u.id = j.default_assignee_id "
        serializer = ClientDashboardListSerializer(queryset, many=True)

        return Response(serializer.data)


class AssingedJobsList(generics.ListAPIView):
    queryset = jobModel.objects.none()

    def get(self, request, format=None):
        userObj = User.objects.get(pk=request.user.id)
        serializeObj = UserSerializer(userObj)
        groups = dict(serializeObj.data)
        userGroupDict = None
        userGroup = None
        queryset = None
        uid = str(request.user.id).replace("-", "")

        if len(groups['groups']) > 0:
            userGroupDict = dict(groups['groups'][0])
        if userGroupDict is not None:
            userGroup = userGroupDict['name']

        print("========User Role: ========")
        print(userGroup)

        queryset = jobModel.objects.raw("SELECT * FROM (SELECT j.id , j.job_title ,j.created_at as posted_date, c.company_name FROM `osms_job_description` as j LEFT JOIN `osms_clients` as c ON c.id = j.client_name_id) AS A "
                "LEFT JOIN (SELECT o.job_id_id as id, o.created_at as assinged_date,o.assignee_name , CONCAT(op1.first_name,' ',op1.last_name) as primary_recruiter_name,"
                " CONCAT(op2.first_name,' ',op2.last_name) as secondary_recruiter_name FROM `job_description_assingment` o INNER JOIN `users_user` op1 on o.primary_recruiter_name_id = op1.id LEFT JOIN `users_user` op2 on o.secondary_recruiter_name_id = op2.id) AS B ON A.id = B.id ORDER BY B.assinged_date DESC")

        # sql = "SELECT j.id, j.created_at, j.job_title, cl.company_name, u.first_name as default_assignee_name FROM `osms_job_description` as j, `osms_clients` as cl, `users_user` as u WHERE j.client_name_id = cl.id AND u.id = j.default_assignee_id "
        serializer = AssingedDashboardListSerializer(queryset, many=True)
        return Response(serializer.data)
        
class GraphPointList(generics.ListAPIView):
    queryset = Candidates.objects.none()

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        print(start_date)
        print(end_date)

        today = utils.get_current_date()
        yesterday = utils.yesterday_datetime()
        week_start, week_end = utils.week_date_range()
        month_start, month_end = utils.month_date_range()
        
        if request.query_params.get('bdm_id') and request.query_params.get('stage'):
            bdm_id = str(request.query_params.get('bdm_id')).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            #stage_id = str(request.query_params.get('stage_id')).replace('UUID', ''). \
                #replace('(\'', '').replace('\')', '').replace('-', '')
            if date_range == 'today':
                candObj = Candidates.objects.filter(job_description__created_by_id = bdm_id ,
                                                    stage__stage_name = request.query_params.get('stage') , created_at__gt = today)
                serializer = CandidateSerializer(candObj, many=True)
                return Response(serializer.data)
                
            elif date_range == 'yesterday':
                candObj = Candidates.objects.filter(job_description__created_by_id = bdm_id ,
                                                    stage__stage_name = request.query_params.get('stage') , created_at__gt = yesterday , created_at__lt = today )
                serializer = CandidateSerializer(candObj, many=True)
                return Response(serializer.data)
                
            elif date_range == 'week':
                candObj = Candidates.objects.filter(job_description__created_by_id = bdm_id ,
                                                    stage__stage_name = request.query_params.get('stage') , created_at__gt = week_start , created_at__lt = week_end)
                serializer = CandidateSerializer(candObj, many=True)
                return Response(serializer.data)
                
            elif date_range == 'month':
                candObj = Candidates.objects.filter(job_description__created_by_id = bdm_id ,
                                                    stage__stage_name = request.query_params.get('stage') , created_at__gt = month_start , created_at__lt = month_end)
                serializer = CandidateSerializer(candObj, many=True)
                return Response(serializer.data)
                
            elif start_date is not None and end_date is not None:
                candObj = Candidates.objects.filter(job_description__created_by_id = bdm_id ,
                                                    stage__stage_name = request.query_params.get('stage') , created_at__gt = start_date , created_at__lt = end_date)
                serializer = CandidateSerializer(candObj, many=True)
                return Response(serializer.data)

        elif request.query_params.get('recruiter_id') and request.query_params.get('stage') :
            recruiter_id = str(request.query_params.get('recruiter_id')).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            if date_range == 'today':
                candObj = Candidates.objects.filter(created_by_id = recruiter_id ,
                                                stage__stage_name = str(request.query_params.get('stage')) , created_at__gt = today)
                serializer = CandidateSerializer(candObj, many=True)
                return Response(serializer.data)
                
            elif date_range == 'yesterday':
                candObj = Candidates.objects.filter(created_by_id = recruiter_id ,
                                                stage__stage_name = str(request.query_params.get('stage')) , created_at__gt = yesterday ,created_at__lt = today )
                serializer = CandidateSerializer(candObj, many=True)
                return Response(serializer.data)
                
            elif date_range == 'week':
                candObj = Candidates.objects.filter(created_by_id = recruiter_id ,
                                                stage__stage_name = str(request.query_params.get('stage')) , created_at__gt = week_start , created_at__lt = week_end)
                serializer = CandidateSerializer(candObj, many=True)
                return Response(serializer.data)
                
            elif date_range == 'month':
                candObj = Candidates.objects.filter(created_by_id = recruiter_id ,
                                                stage__stage_name = str(request.query_params.get('stage')) , created_at__gt = month_start , created_at__lt = month_end)
                serializer = CandidateSerializer(candObj, many=True)
                return Response(serializer.data)
                
            elif start_date is not None and end_date is not None:
                candObj = Candidates.objects.filter(created_by_id = recruiter_id ,
                                                stage__stage_name = str(request.query_params.get('stage')) , created_at__gt = start_date , created_at__lt = end_date)
                serializer = CandidateSerializer(candObj, many=True)
                return Response(serializer.data)
                
        elif request.query_params.get('job_id') and request.query_params.get('stage') :
            job_id = str(request.query_params.get('job_id')).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            if date_range == 'today':
                candObj = Candidates.objects.filter(job_description_id = job_id ,
                                                stage__stage_name = str(request.query_params.get('stage')) , created_at__gt = today)
                serializer = CandidateSerializer(candObj, many=True)
                return Response(serializer.data)
                
            elif date_range == 'yesterday':
                candObj = Candidates.objects.filter(job_description_id = job_id ,
                                                stage__stage_name = str(request.query_params.get('stage')) , created_at__gt = yesterday ,created_at__lt = today )
                serializer = CandidateSerializer(candObj, many=True)
                return Response(serializer.data)
                
            elif date_range == 'week':
                candObj = Candidates.objects.filter(job_description_id = job_id ,
                                                stage__stage_name = str(request.query_params.get('stage')) , created_at__gt = week_start , created_at__lt = week_end)
                serializer = CandidateSerializer(candObj, many=True)
                return Response(serializer.data)
                
            elif date_range == 'month':
                candObj = Candidates.objects.filter(job_description_id = job_id ,
                                                stage__stage_name = str(request.query_params.get('stage')) , created_at__gt = month_start , created_at__lt = month_end)
                serializer = CandidateSerializer(candObj, many=True)
                return Response(serializer.data)
                
            elif start_date is not None and end_date is not None:
                candObj = Candidates.objects.filter(job_description_id = job_id ,
                                                stage__stage_name = str(request.query_params.get('stage')) , created_at__gt = start_date , created_at__lt = end_date)
                serializer = CandidateSerializer(candObj, many=True)
                return Response(serializer.data)
                
class JobsByBDMSummaryTable(generics.ListAPIView):
    queryset = Candidates.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]  # SearchFilter,
    filter_class = ReportFilter

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        print(start_date)
        print(end_date)

        today = utils.get_current_date()
        yesterday = utils.yesterday_datetime()
        week_start, week_end = utils.week_date_range()
        month_start, month_end = utils.month_date_range()

        candObj = User.objects.get(pk=request.user.id)
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

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = jobModel.objects.filter(created_at__gt = today)
            elif date_range == 'yesterday':
                queryset = jobModel.objects.filter(created_at__gt = yesterday ,created_at__lt = today)
            elif date_range == 'week':
                queryset = jobModel.objects.filter(created_at__gt=week_start, created_at__lt=week_end)
            elif date_range == 'month':
                queryset = jobModel.objects.filter(created_at__gt=month_start, created_at__lt=month_end)
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.filter(created_at__gt=start_date, created_at__lt=end_date)

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.filter(created_at__gt = today)
            elif date_range == 'yesterday':
                queryset = jobModel.objects.filter(created_at__gt = yesterday ,created_at__lt = today)
            elif date_range == 'week':
                queryset = jobModel.objects.filter(created_at__gt=week_start, created_at__lt=week_end)
            elif date_range == 'month':
                queryset = jobModel.objects.filter(created_at__gt=month_start, created_at__lt=month_end)
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.filter(created_at__gt=start_date, created_at__lt=end_date)
                
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.filter(created_at__gt = today)
            elif date_range == 'yesterday':
                queryset = jobModel.objects.filter(created_at__gt = yesterday ,created_at__lt = today)
            elif date_range == 'week':
                queryset = jobModel.objects.filter(created_at__gt=week_start, created_at__lt=week_end)
            elif date_range == 'month':
                queryset = jobModel.objects.filter(created_at__gt=month_start, created_at__lt=month_end)
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.filter(created_at__gt=start_date, created_at__lt=end_date)

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = jobModel.objects.filter(created_at__gt = today)
            elif date_range == 'yesterday':
                queryset = jobModel.objects.filter(created_at__gt = yesterday ,created_at__lt = today)
            elif date_range == 'week':
                queryset = jobModel.objects.filter(created_at__gt=week_start, created_at__lt=week_end)
            elif date_range == 'month':
                queryset = jobModel.objects.filter(created_at__gt=month_start, created_at__lt=month_end)
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.filter(created_at__gt=start_date, created_at__lt=end_date)

        if queryset is not None:
            print(str(queryset.query))

        # queryset = self.filter_queryset(queryset)
        serializer = JobsByBDMTableSerializer(queryset, many=True)
        # print(serializer.data['first_name'])
        print(serializer.data)
        return Response(serializer.data)
        
class JobsByBDMSummaryCSV(generics.ListAPIView):
    queryset = Candidates.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]  # SearchFilter,
    filter_class = ReportFilter

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        print(start_date)
        print(end_date)

        today = utils.get_current_date()
        yesterday = utils.yesterday_datetime()
        week_start, week_end = utils.week_date_range()
        month_start, month_end = utils.month_date_range()

        candObj = User.objects.get(pk=request.user.id)
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

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = jobModel.objects.filter(created_at__gt = today)
            elif date_range == 'yesterday':
                queryset = jobModel.objects.filter(created_at__gt = yesterday ,created_at__lt = today)
            elif date_range == 'week':
                queryset = jobModel.objects.filter(created_at__gt=week_start, created_at__lt=week_end)
            elif date_range == 'month':
                queryset = jobModel.objects.filter(created_at__gt=month_start, created_at__lt=month_end)
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.filter(created_at__gt=start_date, created_at__lt=end_date)

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.filter(created_at__gt = today)
            elif date_range == 'yesterday':
                queryset = jobModel.objects.filter(created_at__gt = yesterday ,created_at__lt = today)
            elif date_range == 'week':
                queryset = jobModel.objects.filter(created_at__gt=week_start, created_at__lt=week_end)
            elif date_range == 'month':
                queryset = jobModel.objects.filter(created_at__gt=month_start, created_at__lt=month_end)
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.filter(created_at__gt=start_date, created_at__lt=end_date)
                
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.filter(created_at__gt = today)
            elif date_range == 'yesterday':
                queryset = jobModel.objects.filter(created_at__gt = yesterday ,created_at__lt = today)
            elif date_range == 'week':
                queryset = jobModel.objects.filter(created_at__gt=week_start, created_at__lt=week_end)
            elif date_range == 'month':
                queryset = jobModel.objects.filter(created_at__gt=month_start, created_at__lt=month_end)
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.filter(created_at__gt=start_date, created_at__lt=end_date)

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = jobModel.objects.filter(created_at__gt = today)
            elif date_range == 'yesterday':
                queryset = jobModel.objects.filter(created_at__gt = yesterday ,created_at__lt = today)
            elif date_range == 'week':
                queryset = jobModel.objects.filter(created_at__gt=week_start, created_at__lt=week_end)
            elif date_range == 'month':
                queryset = jobModel.objects.filter(created_at__gt=month_start, created_at__lt=month_end)
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.filter(created_at__gt=start_date, created_at__lt=end_date)

        if queryset is not None:
            print(str(queryset.query))

        # queryset = self.filter_queryset(queryset)
        serializer = JobsByBDMTableSerializer(queryset, many=True)
        array_length = len(serializer.data)
        outputs = []
        print(array_length)
        uuids = set()
        for i in range(array_length):  # Use `xrange` for python 2.

            rows = {
                'job_id': serializer.data[i]['job_id'],
                'job_title': serializer.data[i]['job_title'],
                'min_rate': serializer.data[i]['min_rate'],
                'max_rate': serializer.data[i]['max_rate'],
                'min_salary': serializer.data[i]['min_salary'],
                'max_salary': serializer.data[i]['max_salary'],
                'job_type': serializer.data[i]['employment_type'],
                'client_name': serializer.data[i]['client_name']['company_name'],
                'bdm_name': str(serializer.data[i]['created_by']['first_name']) + ' ' + str(serializer.data[i]['created_by']['last_name']),
                'job_date': serializer.data[i]['created_at']
            }

            outputs.append(rows)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="job_by_bdm_summary.csv"'
        writer = csv.DictWriter(response, fieldnames=['job_id',
                                                      'job_title','min_rate','max_rate','min_salary' , 'max_salary',
                                                      'job_type' , 'client_name' , 'bdm_name' , 'job_date'
                                                      ])

        writer.writeheader()

        writer.writerows(outputs)

        return response