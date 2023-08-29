import csv

from dateutil.relativedelta import relativedelta
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import render
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
    TotalRecordSerializer

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
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s", [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s", [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s", [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s", [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s", [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s", [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s", [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s", [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s", [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s", [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s", [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw("SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s", [uid, start_date, end_date])

        if queryset is not None:
            print(str(queryset.query))

        # queryset = self.filter_queryset(queryset)
        serializer = BdmPerformanceSummarySerializer(queryset, many=True)
        # print(serializer.data['first_name'])
        array_length = len(serializer.data)
        outputs = []
        recruiter_name = ""
        print(array_length)
        uuids = set()
        for i in range(array_length):  # Use `xrange` for python 2.
            recruiter_id = serializer.data[i]['recruiter_name']
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
                'rate': serializer.data[i]['rate'],
                'salary': serializer.data[i]['salary'],
                'client_name': serializer.data[i]['client_name'],
                'location': serializer.data[i]['location'],
                'bdm_name': serializer.data[i]['bdm_name'],
                'status': serializer.data[i]['status'],
                'recruiter_name': recruiter_id,
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
                "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_at = %s GROUP BY c.stage_id, u.first_name",
                [today])
        elif date_range == 'yesterday':
            queryset = Candidates.objects.raw(
                "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_at = %s GROUP BY c.stage_id, u.first_name",
                [yesterday])
        elif date_range == 'week':
            queryset = Candidates.objects.raw(
                "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_at >= %s AND c.created_at <= %s GROUP BY c.stage_id, u.first_name",
                [week_start, week_end])
        elif date_range == 'month':
            queryset = Candidates.objects.raw(
                "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_at >= %s AND c.created_at <= %s GROUP BY c.stage_id, u.first_name",
                [month_start, month_end])
        elif start_date is not None and end_date is not None:
            queryset = Candidates.objects.raw(
                "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id AND c.created_at >= %s AND c.created_at <= %s GROUP BY c.stage_id, u.first_name",
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
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

        if queryset is not None:
            print(str(queryset.query))

        # queryset = self.filter_queryset(queryset)
        serializer = BdmPerformanceSummarySerializer(queryset, many=True)
        # print(serializer.data['first_name'])
        array_length = len(serializer.data)
        outputs = []
        recruiter_name = ""
        print(array_length)
        uuids = set()
        for i in range(array_length):  # Use `xrange` for python 2.
            recruiter_id = serializer.data[i]['recruiter_name']
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
                'rate': serializer.data[i]['rate'],
                'salary': serializer.data[i]['salary'],
                'client_name': serializer.data[i]['client_name'],
                'location': serializer.data[i]['location'],
                'bdm_name': serializer.data[i]['bdm_name'],
                'status': serializer.data[i]['status'],
                # 'recruiter_name': recruiter_id,
                'submission_date': serializer.data[i]['submission_date'],
                'job_date': serializer.data[i]['job_date']
            }

            outputs.append(rows)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="recruiter_performance_summary.csv"'
        writer = csv.DictWriter(response, fieldnames=["candidate_name", "primary_email", "primary_phone_number",
                  "company_name", "total_experience", "rank","job_title", "skills_1",
                  "rate", "salary", "client_name", "location", "bdm_name",
                  "status", "submission_date", "job_date"
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
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
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
            recruiter_id = serializer.data[i]['recruiter_name']
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
                'rate': serializer.data[i]['rate'],
                'salary': serializer.data[i]['salary'],
                'client_name': serializer.data[i]['client_name'],
                'location': serializer.data[i]['location'],
                'bdm_name': serializer.data[i]['bdm_name'],
                'status': serializer.data[i]['status'],
                'recruiter_name': recruiter_id,
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
        if userGroup is not None and (userGroup == GLOBAL_ROLE.get('ADMIN') or userGroup == GLOBAL_ROLE.get('BDMMANAGER') ):
            if date_range == 'today':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id and j.created_by_id = u.id AND j.created_at = %s GROUP BY c.stage_id, u.first_name", [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id and j.created_by_id = u.id AND j.created_at = %s GROUP BY c.stage_id, u.first_name", [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id and j.created_by_id = u.id AND j.created_at >= %s  AND j.created_at <= %s GROUP BY c.stage_id, u.first_name", [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id and j.created_by_id = u.id AND j.created_at >= %s  AND j.created_at <= %s GROUP BY c.stage_id, u.first_name", [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw("SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id and j.created_by_id = u.id AND j.created_at >= %s  AND j.created_at <= %s GROUP BY c.stage_id, u.first_name", [start_date, end_date])

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
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
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
                  "rate", "salary", "client_name", "location", "bdm_name",
                  "status", "submission_date", "job_date"
                  ])

        writer.writeheader()

        for i in range(array_length):  # Use `xrange` for python 2.
            recruiter_id = serializer.data[i]['recruiter_name']
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
                'rate': serializer.data[i]['rate'],
                'salary': serializer.data[i]['salary'],
                'client_name': serializer.data[i]['client_name'],
                'location': serializer.data[i]['location'],
                'bdm_name': serializer.data[i]['bdm_name'],
                'status': serializer.data[i]['status'],
                # 'recruiter_name': userSer.data['first_name'],
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
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
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
            recruiter_id = serializer.data[i]['recruiter_name']
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
                'rate': serializer.data[i]['rate'],
                'salary': serializer.data[i]['salary'],
                'client_name': serializer.data[i]['client_name'],
                'location': serializer.data[i]['location'],
                'bdm_name': serializer.data[i]['bdm_name'],
                'status': serializer.data[i]['status'],
                'recruiter_name': recruiter_id,
                'submission_date': serializer.data[i]['submission_date'],
                'job_date': serializer.data[i]['job_date']
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
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_at = %s GROUP BY c.stage_id, j.job_title",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_at = %s GROUP BY c.stage_id, j.job_title",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_at >= %s AND j.created_at <= %s GROUP BY c.stage_id, j.job_title",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_at >= %s AND j.created_at <= %s GROUP BY c.stage_id, j.job_title",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_at >= %s AND j.created_at <= %s GROUP BY c.stage_id, j.job_title",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_by_id = %s AND j.created_at = %s GROUP BY c.stage_id, j.job_title",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_by_id = %s AND j.created_at = %s GROUP BY c.stage_id, j.job_title",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_by_id = %s AND j.created_at >= %s AND j.created_at <= %s GROUP BY c.stage_id, j.job_title",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_by_id = %s  AND j.created_at >= %s AND j.created_at <= %s GROUP BY c.stage_id, j.job_title",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, j.job_title as job_title FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j WHERE c.stage_id = s.id AND c.job_description_id = j.id AND j.created_by_id = %s  AND j.created_at >= %s AND j.created_at <= %s GROUP BY c.stage_id, j.job_title",
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
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at = %s",
                    [yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND j.default_assignee_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s",
                    [uid, today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at = %s",
                    [uid, yesterday])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
                    [uid, month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, ca.first_name as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.rate, ca.salary, cl.company_name AS client_name, j.location, u.first_name as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, ca.created_at AS submission_date, j.created_at AS job_date FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = ca.job_description_id AND ca.stage_id = s.id AND ca.created_by_id = %s AND ca.created_at >= %s  AND ca.created_at <= %s",
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
            recruiter_id = serializer.data[i]['recruiter_name']
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
                'rate': serializer.data[i]['rate'],
                'salary': serializer.data[i]['salary'],
                'client_name': serializer.data[i]['client_name'],
                'location': serializer.data[i]['location'],
                'bdm_name': serializer.data[i]['bdm_name'],
                'status': serializer.data[i]['status'],
                'recruiter_name': recruiter_id,
                'submission_date': serializer.data[i]['submission_date'],
                'job_date': serializer.data[i]['job_date']
            }

            outputs.append(rows)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bdm_performance_summary.csv"'
        writer = csv.DictWriter(response, fieldnames=['created_at', 'cadidate_name',
                                                      'candidate_stage', 'job_title', 'total_experience',
                                                      'visa', 'salary' ,'rate', 'client_name',
                                                      'bdm_name', 'recruiter_name'
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
                "SELECT c.id, COUNT(*) as total_records FROM `osms_candidates` as c, `osms_job_description` as j, `candidates_stages` as s WHERE c.job_description_id = j.id AND c.stage_id = s.id AND j.created_by_id = %s AND s.stage_name = 'Submission'",
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
        sql = "SELECT id, job_title FROM osms_job_description"
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
            queryset = jobModel.objects.raw("SELECT j.id, j.created_at, j.job_title, cl.company_name, u.first_name as default_assignee_name FROM `osms_job_description` as j, `osms_clients` as cl, `users_user` as u, `job_description_assingment` as ja WHERE j.client_name_id = cl.id AND u.id = j.default_assignee_id AND ja.job_id_id = j.id AND ja.primary_recruiter_name_id = %s", [uid])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            queryset = jobModel.objects.raw("SELECT j.id, j.created_at, j.job_title, cl.company_name, u.first_name as default_assignee_name FROM `osms_job_description` as j, `osms_clients` as cl, `users_user` as u, `job_description_assingment` as ja WHERE j.client_name_id = cl.id AND u.id = j.default_assignee_id AND ja.job_id_id = j.id AND ja.primary_recruiter_name_id = %s", [uid])

        # sql = "SELECT j.id, j.created_at, j.job_title, cl.company_name, u.first_name as default_assignee_name FROM `osms_job_description` as j, `osms_clients` as cl, `users_user` as u WHERE j.client_name_id = cl.id AND u.id = j.default_assignee_id "
        serializer = ClientDashboardListSerializer(queryset, many=True)

        return Response(serializer.data)