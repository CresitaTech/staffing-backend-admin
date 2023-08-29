import csv
from django.core.mail import EmailMessage
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection
import datetime
import pandas as pd
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from candidates.models import Candidates, candidatesJobDescription
from candidates.serializers import CandidateJobsStagesSerializer
from clients.models import clientModel
from jobdescriptions.serializers import JobDescriptionSerializer
from comman_utils import utils
from jobdescriptions.models import jobModel
from reports.filters import ReportFilter
from reports.serializers import RecruiterPerformanceSummarySerializer, WeekendEmailReportSerializer, \
    RecruiterPerformanceSummaryGraphSerializer, \
    BdmPerformanceSummarySerializer, BdmPerformanceSummaryGraphSerializer, JobSummarySerializer, \
    JobSummaryGraphSerializer, ClientSummarySerializer, TopFivePlacementSerializer, ClientDropdownListSerializer, \
    JobsDropdownListSerializer, ClientDashboardListSerializer, UserObjectSerializer, ActiveClientSerializer, \
    TotalRecordSerializer, BdmEmailReportSerializer, RecruiterEmailReportSerializer, \
    RecruitersPerformanceSummarySerializer, AssingedDashboardListSerializer, ClientRevenueSerializer, \
    JobSummaryTableSerializer, MyCandidateSerializer, UnassignedJobsSerializer, JobsByBDMTableSerializer, \
    JobsByBDMGraphSerializer, ActiveJobsAgingSerializer, AssingedDashboardSerializer

# SELECT COUNT(*) as total_count, s.stage_name FROM `osms_candidates` as c, `candidates_stages` as s WHERE c.stage_id = s.id GROUP BY c.stage_id
# SELECT COUNT(*) as total_count, s.stage_name, u.first_name FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u WHERE c.stage_id = s.id AND c.created_by_id = u.id GROUP BY c.stage_id, u.first_name
from staffingapp.settings import GLOBAL_ROLE
from users.models import User
from users.serializers import UserSerializer
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class RecruiterPerformanceSummaryTable(generics.ListAPIView):
    serializer_class = RecruiterPerformanceSummarySerializer
    queryset = Candidates.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]  # SearchFilter,
    filter_class = ReportFilter

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        logger.debug('Date Range: ' + str(date_range))
        logger.debug('Start Date: ' + str(start_date))
        logger.debug('End Date: ' + str(end_date))

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
        logger.debug('userGroup Data: %s' % userGroup)
        uid = str(request.user.id).replace("-", "")

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date > %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date > %s AND cjs.submission_date < %s",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date > %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date > %s AND cjs.submission_date < %s",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date > %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date > %s AND cjs.submission_date < %s",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date > %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date > %s AND cjs.submission_date < %s",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [start_date, end_date])

        if queryset is not None:
            logger.debug('Recruiter Perf Table QuerySet Query formed: ' + str(queryset.query))
            logger.debug('Query: %s' % str(queryset.query))

        # queryset = self.filter_queryset(queryset)
        serializer = RecruitersPerformanceSummarySerializer(queryset, many=True)
        # print(serializer.data['first_name'])
        array_length = len(serializer.data)
        outputs = []
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
                'recruiter_name': recruiter_name[0] + ' ' + recruiter_name[1],
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

        logger.debug('Date Range: ' + str(date_range))
        logger.debug('Start Date: ' + str(start_date))
        logger.debug('End Date: ' + str(end_date))

        today = utils.get_current_date()
        yesterday = utils.yesterday_datetime()

        week_start, week_end = utils.week_date_range()
        month_start, month_end = utils.month_date_range()

        candObj = User.objects.get(pk=request.user.id)
        serializeObj = UserSerializer(candObj)
        groups = dict(serializeObj.data)
        userGroupDict = None
        userGroup = None
        if len(groups['groups']) > 0:
            userGroupDict = dict(groups['groups'][0])
        if userGroupDict is not None:
            userGroup = userGroupDict['name']
        uid = str(request.user.id).replace("-", "")
        queryset = None
        logger.debug('userGroup Role: %s' % GLOBAL_ROLE.get('ADMIN'))

        # if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):

        if date_range == 'today':
            queryset = Candidates.objects.raw(
                "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name , c.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s,`candidates_jobs_stages` as cjs , `users_user` as u WHERE cjs.stage_id = s.id AND c.created_by_id = u.id AND cjs.submission_date > %s "
                " AND cjs.candidate_name_id = c.id AND s.stage_name != 'Candidate Added' GROUP BY cjs.stage_id, u.first_name",
                [today])
        elif date_range == 'yesterday':
            queryset = Candidates.objects.raw(
                "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name , c.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s,`candidates_jobs_stages` as cjs , `users_user` as u WHERE cjs.stage_id = s.id AND c.created_by_id = u.id AND cjs.submission_date > %s AND cjs.submission_date < %s "
                " AND cjs.candidate_name_id = c.id AND s.stage_name != 'Candidate Added' GROUP BY cjs.stage_id, u.first_name",
                [yesterday, today])
        elif date_range == 'week':
            queryset = Candidates.objects.raw(
                "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name , c.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s,`candidates_jobs_stages` as cjs , `users_user` as u WHERE cjs.stage_id = s.id AND c.created_by_id = u.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s "
                " AND cjs.candidate_name_id = c.id AND s.stage_name != 'Candidate Added' GROUP BY cjs.stage_id, u.first_name",
                [week_start, week_end])
        elif date_range == 'month':
            queryset = Candidates.objects.raw(
                "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name , c.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s,`candidates_jobs_stages` as cjs , `users_user` as u WHERE cjs.stage_id = s.id AND c.created_by_id = u.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s "
                " AND cjs.candidate_name_id = c.id AND s.stage_name != 'Candidate Added' GROUP BY cjs.stage_id, u.first_name",
                [month_start, month_end])
        elif start_date is not None and end_date is not None:
            queryset = Candidates.objects.raw(
                "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, u.first_name as first_name , c.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s,`candidates_jobs_stages` as cjs , `users_user` as u WHERE cjs.stage_id = s.id AND c.created_by_id = u.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s "
                " AND cjs.candidate_name_id = c.id AND s.stage_name != 'Candidate Added' GROUP BY cjs.stage_id, u.first_name",
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
            logger.debug('Recruiter Perf Graph QuerySet Query formed: ' + str(queryset.query))
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

        logger.debug('Date Range: ' + str(date_range))
        logger.debug('Start Date: ' + str(start_date))
        logger.debug('End Date: ' + str(end_date))

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
        uid = str(request.user.id).replace("-", "")

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date > %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date > %s AND cjs.submission_date < %s",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date > %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date > %s AND cjs.submission_date < %s",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date > %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date > %s AND cjs.submission_date < %s",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date > %s",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date > %s AND cjs.submission_date < %s",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate,ca.max_rate, ca.min_salary , ca.max_salary,"
                    " cl.company_name AS client_name, j.location, CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, ca.created_at FROM `osms_job_description` as j, "
                    "`users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s",
                    [start_date, end_date])

        if queryset is not None:
            logger.debug('Recruiter CSV QuerySet Query formed: ' + str(queryset.query))
        # queryset = self.filter_queryset(queryset)
        serializer = RecruitersPerformanceSummarySerializer(queryset, many=True)
        # print(serializer.data['first_name'])
        array_length = len(serializer.data)
        outputs = []

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
                'min_salary': serializer.data[i]['max_salary'],
                'client_name': serializer.data[i]['client_name'],
                'location': serializer.data[i]['location'],
                'visa': serializer.data[i]['visa'],
                'job_type': serializer.data[i]['job_type'],
                'bdm_name': serializer.data[i]['bdm_name'],
                'status': serializer.data[i]['status'],
                'recruiter_name': recruiter_name[0] + ' ' + recruiter_name[1],
                'submission_date': serializer.data[i]['submission_date'],
                'job_date': serializer.data[i]['job_date'],
                'created_at': serializer.data[i]['created_at']
            }

            outputs.append(rows)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="recruiter_performance_summary.csv"'
        writer = csv.DictWriter(response, fieldnames=["candidate_name", "primary_email", "primary_phone_number",
                                                      "company_name", "total_experience", "rank", "job_title",
                                                      "skills_1",
                                                      "min_rate", "max_rate", "min_salary", "max_salary", "client_name",
                                                      "location", "visa", "job_type", "bdm_name",
                                                      "status", "recruiter_name", "submission_date", "job_date",
                                                      "created_at"
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

        logger.debug('Date Range: ' + str(date_range))
        logger.debug('Start Date: ' + str(start_date))
        logger.debug('End Date: ' + str(end_date))

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
        uid = str(request.user.id).replace("-", "")

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,(SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date > %s ",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date > %s AND cjs.submission_date < %s ",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,(SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date > %s ",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date > %s AND cjs.submission_date < %s ",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,(SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date > %s ",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date > %s AND cjs.submission_date < %s ",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,(SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date > %s ",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date > %s AND cjs.submission_date < %s ",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type, (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [start_date, end_date])

        if queryset is not None:
            logger.debug('BDM Perf Table QuerySet Query formed: ' + str(queryset.query))
        # queryset = self.filter_queryset(queryset)
        serializer = BdmPerformanceSummarySerializer(queryset, many=True)
        # print(serializer.data['first_name'])
        array_length = len(serializer.data)
        outputs = []
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
                'recruiter_name': recruiter_name[0] + ' ' + recruiter_name[1],
                'submission_date': serializer.data[i]['submission_date'],
                'job_date': serializer.data[i]['job_date'],
                'first_assingment_date': serializer.data[i]['first_assingment_date']
            }

            outputs.append(rows)

        """uuids = list(uuids)
        if len(uuids) > 0:
            userqr = User.objects.filter(id__in=uuids)
            userSer = UserObjectSerializer(userqr)"""

        return Response(outputs)


class BdmPerformanceSummaryGraph(generics.ListAPIView):
    queryset = Candidates.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]  # SearchFilter,
    filter_class = ReportFilter

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        logger.debug('Date Range: ' + str(date_range))
        logger.debug('Start Date: ' + str(start_date))
        logger.debug('End Date: ' + str(end_date))

        today = utils.get_current_date()
        yesterday = utils.yesterday_datetime()

        week_start, week_end = utils.week_date_range()
        month_start, month_end = utils.month_date_range()

        candObj = User.objects.get(pk=request.user.id)
        serializeObj = UserSerializer(candObj)
        groups = dict(serializeObj.data)
        userGroupDict = None
        userGroup = None
        if len(groups['groups']) > 0:
            userGroupDict = dict(groups['groups'][0])
        if userGroupDict is not None:
            userGroup = userGroupDict['name']
        uid = str(request.user.id).replace("-", "")
        queryset = None
        logger.debug('userGroup Role: %s' % GLOBAL_ROLE.get('ADMIN'))
        if userGroup is not None and (userGroup == GLOBAL_ROLE.get('ADMIN') or userGroup == GLOBAL_ROLE.get(
                'BDMMANAGER') or userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER')):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, COUNT(s.stage_name = 'Submission') as submission , u.first_name as first_name, j.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, "
                    "`osms_job_description` as j , `candidates_jobs_stages` as cjs WHERE cjs.stage_id = s.id AND s.stage_name != 'Candidate Added' AND cjs.job_description_id = j.id AND j.created_by_id = u.id AND cjs.candidate_name_id = c.id AND cjs.submission_date > %s GROUP BY u.first_name , cjs.stage_id",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, COUNT(s.stage_name = 'Submission') as submission , u.first_name as first_name, j.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, "
                    "`osms_job_description` as j , `candidates_jobs_stages` as cjs WHERE cjs.stage_id = s.id AND s.stage_name != 'Candidate Added' AND cjs.job_description_id = j.id AND j.created_by_id = u.id AND cjs.candidate_name_id = c.id AND cjs.submission_date > %s AND cjs.submission_date < %s GROUP BY u.first_name , cjs.stage_id",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, COUNT(s.stage_name = 'Submission') as submission , u.first_name as first_name, j.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, "
                    "`osms_job_description` as j , `candidates_jobs_stages` as cjs WHERE cjs.stage_id = s.id AND s.stage_name != 'Candidate Added' AND cjs.job_description_id = j.id AND j.created_by_id = u.id AND cjs.candidate_name_id = c.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s  GROUP BY u.first_name , cjs.stage_id",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, COUNT(s.stage_name = 'Submission') as submission , u.first_name as first_name, j.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, "
                    "`osms_job_description` as j , `candidates_jobs_stages` as cjs WHERE cjs.stage_id = s.id AND s.stage_name != 'Candidate Added' AND cjs.job_description_id = j.id AND j.created_by_id = u.id AND cjs.candidate_name_id = c.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s  GROUP BY u.first_name , cjs.stage_id",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT c.id, COUNT(*) as total_count, s.stage_name as stage_name, COUNT(s.stage_name = 'Submission') as submission , u.first_name as first_name, j.created_by_id FROM `osms_candidates` as c, `candidates_stages` as s, `users_user` as u, "
                    "`osms_job_description` as j , `candidates_jobs_stages` as cjs WHERE cjs.stage_id = s.id AND s.stage_name != 'Candidate Added' AND cjs.job_description_id = j.id AND j.created_by_id = u.id AND cjs.candidate_name_id = c.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s GROUP BY u.first_name , cjs.stage_id",
                    [start_date, end_date])

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
            logger.debug('BDM Perf Graph QuerySet Query formed: ' + str(queryset.query))
        serializer = BdmPerformanceSummaryGraphSerializer(queryset, many=True)
        return Response(serializer.data)


class BdmPerformanceSummaryCSV(generics.ListAPIView):
    queryset = Candidates.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]  # SearchFilter,
    filter_class = ReportFilter

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        logger.debug('Date Range: ' + str(date_range))
        logger.debug('Start Date: ' + str(start_date))
        logger.debug('End Date: ' + str(end_date))

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
        uid = str(request.user.id).replace("-", "")

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at ,(SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date > %s ",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at , (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date > %s AND cjs.submission_date < %s ",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at , (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at , (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at , (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at ,(SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date > %s ",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at , (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date > %s AND cjs.submission_date < %s ",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at , (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at , (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at , (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at ,(SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date > %s ",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at , (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date > %s AND cjs.submission_date < %s ",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at , (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at , (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at , (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at ,(SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date > %s ",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at , (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date > %s AND cjs.submission_date < %s ",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at , (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at , (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, j.job_title as job_title, ca.skills_1, ca.min_rate , ca.max_rate, ca.min_salary , ca.max_salary, cl.company_name AS client_name, j.location, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, s.stage_name as status, ca.created_by_id as recruiter_name, cjs.submission_date AS submission_date, j.created_at AS job_date ,ca.visa as visa ,j.employment_type as job_type,ca.created_at , (SELECT ja.created_at as assingment_date FROM job_description_assingment ja WHERE ja.job_id_id = j.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date  FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca,"
                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND s.stage_name != 'Candidate Added' AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND cjs.submission_date >= %s AND cjs.submission_date <= %s ",
                    [start_date, end_date])

        if queryset is not None:
            logger.debug('BDM Perf csv QuerySet Query formed: ' + str(queryset.query))
        # queryset = self.filter_queryset(queryset)
        serializer = BdmPerformanceSummarySerializer(queryset, many=True)
        array_length = len(serializer.data)
        outputs = []
        uuids = set()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bdm_performance_summary.csv"'

        writer = csv.DictWriter(response, fieldnames=["candidate_name", "primary_email", "primary_phone_number",
                                                      "company_name", "total_experience", "rank", "job_title",
                                                      "skills_1",
                                                      "min_rate", "max_rate", "min_salary", "max_salary", "client_name",
                                                      "location", "visa", "job_type", "bdm_name",
                                                      "status", "recruiter_name", "submission_date", "job_date",
                                                      "first_assingment_date", "created_at"
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
                'min_rate': serializer.data[i]['min_rate'],
                'max_rate': serializer.data[i]['max_rate'],
                'min_salary': serializer.data[i]['min_salary'],
                'max_salary': serializer.data[i]['max_salary'],
                'client_name': serializer.data[i]['client_name'],
                'location': serializer.data[i]['location'],
                'visa': serializer.data[i]['visa'],
                'job_type': serializer.data[i]['job_type'],
                'bdm_name': serializer.data[i]['bdm_name'],
                'status': serializer.data[i]['status'],
                'recruiter_name': recruiter_name[0] + ' ' + recruiter_name[1],
                'submission_date': serializer.data[i]['submission_date'],
                'job_date': serializer.data[i]['job_date'],
                'first_assingment_date': serializer.data[i]['first_assingment_date'],
                'created_at': serializer.data[i]['created_at']
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

        logger.debug('Date Range: ' + str(date_range))
        logger.debug('Start Date: ' + str(start_date))
        logger.debug('End Date: ' + str(end_date))

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
        uid = str(request.user.id).replace("-", "")

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at > %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at > %s AND j.created_at < %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at > %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at > %s AND j.created_at < %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at > %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at > %s AND j.created_at < %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at > %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at > %s AND j.created_at < %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [start_date, end_date])

        if queryset is not None:
            logger.debug('Job Summary QuerySet Query formed: ' + str(queryset.query))
        # queryset = self.filter_queryset(queryset)
        serializer = JobSummaryTableSerializer(queryset, many=True)
        # print(serializer.data['first_name'])
        array_length = len(serializer.data)
        outputs = []
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

        logger.debug('Date Range: ' + str(date_range))
        logger.debug('Start Date: ' + str(start_date))
        logger.debug('End Date: ' + str(end_date))

        today = utils.get_current_date()
        yesterday = utils.yesterday_datetime()

        week_start, week_end = utils.week_date_range()
        month_start, month_end = utils.month_date_range()

        candObj = User.objects.get(pk=request.user.id)
        serializeObj = UserSerializer(candObj)
        groups = dict(serializeObj.data)
        userGroupDict = None
        userGroup = None
        if len(groups['groups']) > 0:
            userGroupDict = dict(groups['groups'][0])
        if userGroupDict is not None:
            userGroup = userGroupDict['name']
        uid = str(request.user.id).replace("-", "")
        queryset = None
        logger.debug('userGroup Role: %s' % GLOBAL_ROLE.get('ADMIN'))

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT c.id,COUNT(*) as total_count, s.stage_name as stage_name,CONCAT(u.first_name, ' ' , u.last_name) as bdm_name , j.job_title as job_title , j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j ,"
                    " `candidates_jobs_stages` as cjs, users_user as u WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND u.id = j.created_by_id AND cjs.candidate_name_id = c.id AND j.created_at > %s GROUP BY cjs.stage_id, j.job_title",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT c.id,COUNT(*) as total_count, s.stage_name as stage_name,CONCAT(u.first_name, ' ' , u.last_name) as bdm_name , j.job_title as job_title , j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j ,"
                    " `candidates_jobs_stages` as cjs, users_user as u WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND u.id = j.created_by_id AND cjs.candidate_name_id = c.id AND j.created_at > %s AND j.created_at < %s GROUP BY cjs.stage_id, j.job_title",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT c.id,COUNT(*) as total_count, s.stage_name as stage_name,CONCAT(u.first_name, ' ' , u.last_name) as bdm_name , j.job_title as job_title , j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j ,"
                    " `candidates_jobs_stages` as cjs, users_user as u WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND u.id = j.created_by_id AND cjs.candidate_name_id = c.id AND j.created_at >= %s AND j.created_at <= %s GROUP BY cjs.stage_id, j.job_title",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT c.id,COUNT(*) as total_count, s.stage_name as stage_name,CONCAT(u.first_name, ' ' , u.last_name) as bdm_name , j.job_title as job_title , j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j ,"
                    " `candidates_jobs_stages` as cjs, users_user as u WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND u.id = j.created_by_id AND cjs.candidate_name_id = c.id AND j.created_at >= %s AND j.created_at <= %s GROUP BY cjs.stage_id, j.job_title",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT c.id,COUNT(*) as total_count, s.stage_name as stage_name,CONCAT(u.first_name, ' ' , u.last_name) as bdm_name , j.job_title as job_title , j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j ,"
                    " `candidates_jobs_stages` as cjs, users_user as u WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND u.id = j.created_by_id AND cjs.candidate_name_id = c.id AND j.created_at >= %s AND j.created_at <= %s GROUP BY cjs.stage_id, j.job_title",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT c.id,COUNT(*) as total_count, s.stage_name as stage_name,CONCAT(u.first_name, ' ' , u.last_name) as bdm_name , j.job_title as job_title , j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j ,"
                    " `candidates_jobs_stages` as cjs, users_user as u WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND u.id = j.created_by_id AND cjs.candidate_name_id = c.id AND j.created_at > %s GROUP BY cjs.stage_id, j.job_title",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT c.id,COUNT(*) as total_count, s.stage_name as stage_name,CONCAT(u.first_name, ' ' , u.last_name) as bdm_name , j.job_title as job_title , j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j ,"
                    " `candidates_jobs_stages` as cjs, users_user as u WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND u.id = j.created_by_id AND cjs.candidate_name_id = c.id AND j.created_at > %s AND j.created_at < %s GROUP BY cjs.stage_id, j.job_title",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT c.id,COUNT(*) as total_count, s.stage_name as stage_name,CONCAT(u.first_name, ' ' , u.last_name) as bdm_name , j.job_title as job_title , j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j ,"
                    " `candidates_jobs_stages` as cjs, users_user as u WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND u.id = j.created_by_id AND cjs.candidate_name_id = c.id AND j.created_at >= %s AND j.created_at <= %s GROUP BY cjs.stage_id, j.job_title",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT c.id,COUNT(*) as total_count, s.stage_name as stage_name,CONCAT(u.first_name, ' ' , u.last_name) as bdm_name , j.job_title as job_title , j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j ,"
                    " `candidates_jobs_stages` as cjs, users_user as u WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND u.id = j.created_by_id AND cjs.candidate_name_id = c.id AND j.created_at >= %s AND j.created_at <= %s GROUP BY cjs.stage_id, j.job_title",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT c.id,COUNT(*) as total_count, s.stage_name as stage_name,CONCAT(u.first_name, ' ' , u.last_name) as bdm_name , j.job_title as job_title , j.id as job_id FROM `osms_candidates` as c, `candidates_stages` as s, `osms_job_description` as j ,"
                    " `candidates_jobs_stages` as cjs, users_user as u WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND u.id = j.created_by_id AND cjs.candidate_name_id = c.id AND j.created_at >= %s AND j.created_at <= %s GROUP BY cjs.stage_id, j.job_title",
                    [start_date, end_date])

        if queryset is not None:
            logger.debug('Job Summary Graph Query formed: ' + str(queryset.query))

        serializer = JobSummaryGraphSerializer(queryset, many=True)
        return Response(serializer.data)


class JobSummaryCSV(generics.ListAPIView):
    queryset = Candidates.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]  # SearchFilter,
    filter_class = ReportFilter

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        logger.debug('Date Range: ' + str(date_range))
        logger.debug('Start Date: ' + str(start_date))
        logger.debug('End Date: ' + str(end_date))

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
        uid = str(request.user.id).replace("-", "")

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at > %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at > %s AND j.created_at < %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at > %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at > %s AND j.created_at < %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at > %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at > %s AND j.created_at < %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [start_date, end_date])

            # print(str(queryset.query))
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at > %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [today])
            elif date_range == 'yesterday':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at > %s AND j.created_at < %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = Candidates.objects.raw(
                    "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
                    "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s )AS"
                    " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
                    " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
                    " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
                    "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
                    " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id",
                    [start_date, end_date])

        if queryset is not None:
            logger.debug('Job Summary CSV Query formed: ' + str(queryset.query))

        # queryset = self.filter_queryset(queryset)
        serializer = JobSummarySerializer(queryset, many=True)
        # print(serializer.data['first_name'])
        array_length = len(serializer.data)
        outputs = []
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
        writer = csv.DictWriter(response, fieldnames=['id', 'job_id',
                                                      'job_title', 'client_name', 'bdm_name', 'job_date', 'job_type',
                                                      'min_salary', 'max_salary', 'min_rate', 'max_rate',
                                                      'client_interview', 'offered', 'submission', 'rejected_by_team',
                                                      'sendout_reject', 'offer_rejected', 'shortlisted',
                                                      'internal_interview', 'awaiting_feedback',
                                                      'placed', 'rejected_by_client',
                                                      'submission_reject', 'send_out'
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

        logger.debug('userGroup Data: %s' % userGroup)

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            logger.debug('================ADMIN DATA==========')
            active_jobs = jobModel.objects.count()
            active_clients = clientModel.objects.count()
            revenue = jobModel.objects.all().aggregate(Sum('projected_revenue'))['projected_revenue__sum']
            placed = candidatesJobDescription.objects.filter(stage_id__stage_name="Placed").annotate(
                Count('stage')).count()

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            logger.debug('================BDM==========')
            active_jobs = jobModel.objects.filter(
                created_by_id=request.user.id).count()  # Q(created_by_id__created_by_id=request.user.id) |
            active_clients = clientModel.objects.filter(
                created_by_id=request.user.id).count()  # Q(created_by_id__created_by_id=request.user.id) |
            queryset = jobModel.objects.raw(
                "SELECT c.id, COUNT(*) as total_records FROM `osms_candidates` as c, `osms_job_description` as j, `candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE cjs.job_description_id = j.id AND cjs.stage_id = s.id AND cjs.candidate_name_id = c.id AND j.created_by_id = %s AND s.stage_name != 'Candidate Added' ",
                [uid])
            serializer = TotalRecordSerializer(queryset, many=True)
            if serializer.data[0] is not None and len(serializer.data[0]) > 0:
                submissions = str(serializer.data[0]['total_records'])
            queryset = jobModel.objects.raw(
                "SELECT c.id, COUNT(*) as total_records FROM `osms_candidates` as c, `osms_job_description` as j, `candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE cjs.job_description_id = j.id AND cjs.stage_id = s.id AND cjs.candidate_name_id = c.id AND j.created_by_id = %s AND s.stage_name = 'Placed'",
                [uid])
            serializer = TotalRecordSerializer(queryset, many=True)
            if serializer.data[0] is not None and len(serializer.data[0]) > 0:
                placed = str(serializer.data[0]['total_records'])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            logger.debug('================REC MANAGER==========')
            active_jobs = jobModel.objects.filter(
                Q(default_assignee_id=request.user.id)).count()  # Q(created_by_id__created_by_id=request.user.id) |
            queryset = clientModel.objects.raw(
                "SELECT c.id, COUNT(DISTINCT(c.company_name)) as active_clients FROM `osms_job_description` as j, `osms_clients` as c WHERE j.client_name_id = c.id AND j.default_assignee_id = %s",
                [uid])
            serializer = ActiveClientSerializer(queryset, many=True)
            if serializer.data[0] is not None and len(serializer.data[0]) > 0:
                active_clients = str(serializer.data[0]['active_clients'])
            submissions = candidatesJobDescription.objects.filter(
                (Q(candidate_name__created_by_id=request.user.id))).exclude(
                stage__stage_name="Candidate Added").annotate(Count('stage')).count()
            placed = candidatesJobDescription.objects.filter(
                (Q(created_by_id__created_by_id=request.user.id) | Q(created_by_id=request.user.id)),
                stage_id__stage_name="Placed").annotate(Count('stage')).count()

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            logger.debug('================RECRUITER==========')
            interviewed = candidatesJobDescription.objects.filter(candidate_name__created_by_id=request.user.id).count()
            sendOut = candidatesJobDescription.objects.filter(candidate_name__created_by_id=request.user.id,
                                                              stage_id__stage_name="SendOut").annotate(
                Count('stage')).count()
            submissions = candidatesJobDescription.objects.filter(
                candidate_name__created_by_id=request.user.id).exclude(stage__stage_name="Candidate Added").annotate(
                Count('stage')).count()
            placed = candidatesJobDescription.objects.filter(candidate_name__created_by_id=request.user.id,
                                                             stage_id__stage_name="Placed").annotate(
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
        logger.debug('Aggreagte Data: ' + str(response))
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

        logger.debug('userGroup Data: %s' % userGroup)

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            queryset = clientModel.objects.raw(
                "SELECT cl.id, cl.company_name as client_name, (Select COUNT(s.stage_name) from osms_candidates as c,"
                "candidates_stages as s, osms_job_description as j , candidates_jobs_stages as cjs WHERE cjs.stage_id = s.id AND s.stage_name != 'Candidate Added' AND s.stage_name != 'Placed' "
                "AND cjs.job_description_id = j.id and j.client_name_id = cl.id AND cjs.candidate_name_id = c.id ) as submissions, (Select COUNT(s.stage_name) "
                "from osms_candidates as c, candidates_stages as s, osms_job_description as j , candidates_jobs_stages as cjs WHERE cjs.stage_id = s.id AND s.stage_name = 'Placed' AND cjs.job_description_id = j.id and j.client_name_id = cl.id and cjs.candidate_name_id = c.id) as placed, (Select COUNT(j.job_title) from osms_job_description as j WHERE j.client_name_id = cl.id ) as job_title FROM `osms_clients` as cl")  # Q(created_by_id__created_by_id=request.user.id) |

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            queryset = clientModel.objects.raw(
                "SELECT cl.id, cl.company_name as client_name, (Select COUNT(s.stage_name) from osms_candidates as c, candidates_stages as s, osms_job_description as j , candidates_jobs_stages as cjs WHERE cjs.stage_id = s.id AND s.stage_name != 'Candidate Added' AND s.stage_name != 'Placed' AND cjs.job_description_id = j.id and cjs.candidate_name_id = c.id and j.created_by_id = %s AND j.client_name_id = cl.id ) as submissions, (Select COUNT(s.stage_name) from osms_candidates as c, candidates_stages as s, osms_job_description as j , candidates_jobs_stages as cjs WHERE cjs.stage_id = s.id AND s.stage_name = 'Placed' AND cjs.job_description_id = j.id and cjs.candidate_name_id = c.id and j.created_by_id = %s AND j.client_name_id = cl.id ) as placed, (Select COUNT(j.job_title) from osms_job_description as j WHERE j.created_by_id = %s AND j.client_name_id = cl.id ) as job_title FROM `osms_clients` as cl WHERE cl.created_by_id = %s",
                [uid, uid, uid, uid])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            queryset = clientModel.objects.raw(
                "SELECT cl.id, cl.company_name as client_name, (Select COUNT(s.stage_name) from osms_candidates as c, candidates_stages as s, osms_job_description as j , candidates_jobs_stages as cjs WHERE cjs.stage_id = s.id AND s.stage_name != 'Candidate Added' AND s.stage_name != 'Placed' AND cjs.job_description_id = j.id and j.client_name_id = cl.id and cjs.candidate_name_id = c.id ) as submissions, (Select COUNT(s.stage_name) from osms_candidates as c, candidates_stages as s, osms_job_description as j , candidates_jobs_stages as cjs WHERE cjs.stage_id = s.id AND s.stage_name = 'Placed' AND cjs.job_description_id = j.id and j.client_name_id = cl.id and cjs.candidate_name_id = c.id ) as placed, (Select COUNT(j.job_title) from osms_job_description as j WHERE j.client_name_id = cl.id ) as job_title FROM `osms_clients` as cl, `osms_job_description` as ja WHERE ja.client_name_id = cl.id AND ja.default_assignee_id = %s GROUP BY cl.company_name",
                [uid])

        serializer = ClientSummarySerializer(queryset, many=True)

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
        logger.debug('Top Clients Data: ' + str(serializer.data))
        return Response(serializer.data)


class TopFivePlacement(generics.ListAPIView):
    queryset = Candidates.objects.none()

    def get(self, request, format=None):
        sql = 'SELECT  ca.id as id, CONCAT(ca.first_name, " ", ca.last_name ) AS candidate_name, cl.company_name AS client_name, s.stage_name as status FROM `osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND s.stage_name = "Placed"'
        queryset = Candidates.objects.raw(sql)
        serializer = TopFivePlacementSerializer(queryset, many=True)
        # serializer = AggregateDataSerializer(total_client, many=True)
        logger.debug('Top Placements Data: ' + str(serializer.data))
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
        sql = "SELECT id, job_title ,client_name_id  FROM osms_job_description WHERE status = 'Active' ORDER BY created_at DESC"
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

        logger.debug('Role: ' + str(userGroup))

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            queryset = jobModel.objects.raw(
                "SELECT j.id, j.created_at, j.job_title as posted_date, cl.company_name, ja.assignee_name, CONCAT(u.first_name , ' ' , u.last_name) as bdm_name, ja.created_at as assinged_date FROM `osms_job_description` as j, `osms_clients` as cl, `users_user` as u, `job_description_assingment` as ja"
                " WHERE (j.client_name_id = cl.id AND ja.job_id_id = j.id AND ja.primary_recruiter_name_id = %s AND j.created_by_id = u.id) OR (j.client_name_id = cl.id AND ja.job_id_id = j.id AND ja.secondary_recruiter_name_id = %s AND j.created_by_id = u.id) ORDER BY assinged_date DESC",
                [uid, uid])
            logger.debug('RM Jobs dashboard query: ' + str(queryset.query))

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            queryset = jobModel.objects.raw(
                "SELECT j.id, j.created_at as posted_date , j.status, j.job_title, (SELECT COUNT(*) FROM candidates_stages as s , candidates_jobs_stages as cjs , osms_candidates as ca WHERE cjs.stage_id = s.id AND cjs.candidate_name_id = ca.id AND "
                "ca.created_by_id = %s AND cjs.job_description_id = j.id AND s.stage_name != 'Candidate Added') as total_submissions , (SELECT COUNT(*) FROM candidates_stages as s , candidates_jobs_stages as cjs , osms_candidates as ca WHERE cjs.stage_id = s.id AND "
                "cjs.candidate_name_id = ca.id AND ca.created_by_id = %s AND cjs.job_description_id = j.id AND s.stage_name = 'Placed') as placed , cl.company_name, CONCAT (u.first_name ,' ', u.last_name) as bdm_name,ja.assignee_name, ja.created_at as assinged_date "
                "FROM `osms_job_description` as j, `osms_clients` as cl, `users_user` as u, `job_description_assingment` as ja WHERE (j.client_name_id = cl.id AND u.id = j.created_by_id AND ja.job_id_id = j.id AND ja.primary_recruiter_name_id = %s) OR"
                "(j.client_name_id = cl.id AND u.id = j.created_by_id AND ja.job_id_id = j.id AND ja.secondary_recruiter_name_id = %s) ORDER BY assinged_date DESC",
                [uid, uid, uid, uid])
            logger.debug('Recr Jobs dashboard query: ' + str(queryset.query))

        serializer = ClientDashboardListSerializer(queryset, many=True)
        return Response(serializer.data)


class MyCandidatesList(generics.ListAPIView):
    queryset = Candidates.objects.none()

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

        logger.debug('group: ' + str(userGroup))

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            queryset = Candidates.objects.raw(
                "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name,"
                "j.job_title as job_title, cl.company_name AS client_name, CONCAT(u.first_name,' ',u.last_name) as bdm_name, "
                "s.stage_name as current_status, cjs.submission_date AS submission_date, cjs.updated_at as last_updated FROM"
                "`osms_job_description` as j, `users_user` as u, `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages`"
                "as s, `candidates_jobs_stages` as cjs WHERE j.created_by_id = u.id AND j.client_name_id = cl.id and j.id = cjs.job_description_id"
                " AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND ca.created_by_id = %s ORDER BY ca.created_at DESC",
                [uid])
        # sql = "SELECT j.id, j.created_at, j.job_title, cl.company_name, u.first_name as default_assignee_name FROM `osms_job_description` as j, `osms_clients` as cl, `users_user` as u WHERE j.client_name_id = cl.id AND u.id = j.default_assignee_id "
        serializer = MyCandidateSerializer(queryset, many=True)
        logger.debug('Query for My candidates: ' + str(queryset.query))
        return Response(serializer.data)


class AssingedJobsList(generics.ListAPIView):
    queryset = jobModel.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, ]
    serializer_class = AssingedDashboardListSerializer

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

        logger.debug('group: ' + str(userGroup))

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            queryset = jobModel.objects.raw(
                "SELECT * FROM (SELECT j.id , j.job_title ,j.created_at as posted_date, c.company_name FROM `osms_job_description` as j LEFT JOIN `osms_clients` as c ON c.id = j.client_name_id) AS A "
                "LEFT JOIN (SELECT o.job_id_id as id, o.created_at as assinged_date,o.assignee_name , CONCAT(op1.first_name,' ',op1.last_name) as primary_recruiter_name,"
                " CONCAT(op2.first_name,' ',op2.last_name) as secondary_recruiter_name FROM `job_description_assingment` o INNER JOIN `users_user` op1 on o.primary_recruiter_name_id = op1.id LEFT JOIN `users_user` op2 on o.secondary_recruiter_name_id = op2.id) AS B ON A.id = B.id ORDER BY B.assinged_date DESC")
            logger.debug('Query for ADMIN: ' + str(queryset.query))

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            queryset = jobModel.objects.raw(
                "SELECT * FROM (SELECT j.id , j.job_title ,j.created_at as posted_date, c.company_name FROM `osms_job_description` as j LEFT JOIN `osms_clients` as c ON c.id = j.client_name_id) AS A "
                "LEFT JOIN (SELECT o.job_id_id as id, o.created_at as assinged_date,o.assignee_name , CONCAT(op1.first_name,' ',op1.last_name) as primary_recruiter_name,"
                " CONCAT(op2.first_name,' ',op2.last_name) as secondary_recruiter_name FROM `job_description_assingment` o INNER JOIN `users_user` op1 on o.primary_recruiter_name_id = op1.id LEFT JOIN `users_user` op2 on o.secondary_recruiter_name_id = op2.id) AS B ON A.id = B.id ORDER BY B.assinged_date DESC")
            logger.debug('Query for BDM: ' + str(queryset.query))

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if request.query_params.get('action'):
                queryset = jobModel.objects.raw(
                    "SELECT j.* , IF(ja.primary_recruiter_name_id = %s, 'YES', 'NO') as primary_recruiter_name , IF(ja.secondary_recruiter_name_id = %s, 'YES', 'NO') as secondary_recruiter_name FROM `osms_job_description` as j, `osms_clients` as cl, `users_user` as u, `job_description_assingment` as ja WHERE (j.client_name_id = cl.id AND u.id = j.default_assignee_id AND ja.job_id_id = j.id AND ja.primary_recruiter_name_id = %s) OR"
                    "(j.client_name_id = cl.id AND u.id = j.default_assignee_id AND ja.job_id_id = j.id AND ja.secondary_recruiter_name_id = %s) ORDER BY j.created_at DESC",
                    [uid, uid, uid, uid])
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = AssingedDashboardListSerializer(queryset, many=True)
                    return self.get_paginated_response(serializer.data)
                logger.debug('Query for RM: ' + str(queryset.query))
            else:
                queryset = jobModel.objects.raw(
                    "SELECT * FROM (SELECT j.id , j.job_title ,j.created_at as posted_date, c.company_name FROM `osms_job_description` as j LEFT JOIN `osms_clients` as c ON c.id = j.client_name_id) AS A "
                    "LEFT JOIN (SELECT o.job_id_id as id, o.created_at as assinged_date,o.assignee_name , CONCAT(op1.first_name,' ',op1.last_name) as primary_recruiter_name,"
                    " CONCAT(op2.first_name,' ',op2.last_name) as secondary_recruiter_name FROM `job_description_assingment` o INNER JOIN `users_user` op1 on o.primary_recruiter_name_id = op1.id LEFT JOIN `users_user` op2 on o.secondary_recruiter_name_id = op2.id) AS B ON A.id = B.id ORDER BY B.assinged_date DESC")
                logger.debug('Query for RM: ' + str(queryset.query))

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if request.query_params.get('action'):
                queryset = jobModel.objects.raw(
                    "SELECT j.* FROM `osms_job_description` as j, `osms_clients` as cl, `users_user` as u, `job_description_assingment` as ja WHERE (j.client_name_id = cl.id AND u.id = j.default_assignee_id AND ja.job_id_id = j.id AND ja.primary_recruiter_name_id = %s) OR"
                    "(j.client_name_id = cl.id AND u.id = j.default_assignee_id AND ja.job_id_id = j.id AND ja.secondary_recruiter_name_id = %s) ORDER BY j.created_at DESC",
                    [uid, uid])
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = AssingedDashboardListSerializer(queryset, many=True)
                    return self.get_paginated_response(serializer.data)
                logger.debug('Query for Rec: ' + str(queryset.query))

            else:
                queryset = jobModel.objects.raw(
                    "SELECT * FROM (SELECT j.id , j.job_title ,j.created_at as posted_date, c.company_name FROM `osms_job_description` as j LEFT JOIN `osms_clients` as c ON c.id = j.client_name_id) AS A "
                    "LEFT JOIN (SELECT o.job_id_id as id, o.created_at as assinged_date,o.assignee_name , CONCAT(op1.first_name,' ',op1.last_name) as primary_recruiter_name,"
                    " CONCAT(op2.first_name,' ',op2.last_name) as secondary_recruiter_name FROM `job_description_assingment` o INNER JOIN `users_user` op1 on o.primary_recruiter_name_id = op1.id LEFT JOIN `users_user` op2 on o.secondary_recruiter_name_id = op2.id) AS B ON A.id = B.id ORDER BY B.assinged_date DESC")
                logger.debug('Query for Rec: ' + str(queryset.query))

        serializer = AssingedDashboardSerializer(queryset, many=True)
        logger.debug('ASSIGNED AND UNASSIGNED DATA: ' + str(serializer.data))
        return Response(serializer.data)


class GraphPointList(generics.ListAPIView):
    queryset = Candidates.objects.none()

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        logger.debug('Date Range: ' + str(date_range))
        logger.debug('Start Date: ' + str(start_date))
        logger.debug('End Date: ' + str(end_date))

        today = utils.get_current_date()
        yesterday = utils.yesterday_datetime()
        week_start, week_end = utils.week_date_range()
        month_start, month_end = utils.month_date_range()

        if request.query_params.get('bdm_id') and request.query_params.get('stage'):
            bdm_id = str(request.query_params.get('bdm_id')).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            # stage_id = str(request.query_params.get('stage_id')).replace('UUID', ''). \
            # replace('(\'', '').replace('\')', '').replace('-', '')
            if date_range == 'today':
                candObj = candidatesJobDescription.objects.filter(job_description__created_by_id=bdm_id,
                                                                  stage__stage_name=request.query_params.get('stage'),
                                                                  submission_date__gt=today)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)
                return Response(serializer.data)

            elif date_range == 'yesterday':
                candObj = candidatesJobDescription.objects.filter(job_description__created_by_id=bdm_id,
                                                                  stage__stage_name=request.query_params.get('stage'),
                                                                  submission_date__gt=yesterday,
                                                                  submission_date__lt=today)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)
                return Response(serializer.data)

            elif date_range == 'week':
                candObj = candidatesJobDescription.objects.filter(job_description__created_by_id=bdm_id,
                                                                  stage__stage_name=request.query_params.get('stage'),
                                                                  submission_date__gt=week_start,
                                                                  submission_date__lt=week_end)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)
                return Response(serializer.data)

            elif date_range == 'month':
                candObj = candidatesJobDescription.objects.filter(job_description__created_by_id=bdm_id,
                                                                  stage__stage_name=request.query_params.get('stage'),
                                                                  submission_date__gt=month_start,
                                                                  submission_date__lt=month_end)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)
                return Response(serializer.data)

            elif start_date is not None and end_date is not None:
                candObj = candidatesJobDescription.objects.filter(job_description__created_by_id=bdm_id,
                                                                  stage__stage_name=request.query_params.get('stage'),
                                                                  submission_date__gt=start_date,
                                                                  submission_date__lt=end_date)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)
                return Response(serializer.data)

        elif request.query_params.get('recruiter_id') and request.query_params.get('stage'):
            recruiter_id = str(request.query_params.get('recruiter_id')).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            if date_range == 'today':
                candObj = candidatesJobDescription.objects.filter(candidate_name__created_by_id=recruiter_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  submission_date__gt=today)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)
                return Response(serializer.data)

            elif date_range == 'yesterday':
                candObj = candidatesJobDescription.objects.filter(candidate_name__created_by_id=recruiter_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  submission_date__gt=yesterday,
                                                                  submission_date__lt=today)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)
                return Response(serializer.data)

            elif date_range == 'week':
                candObj = candidatesJobDescription.objects.filter(candidate_name__created_by_id=recruiter_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  submission_date__gt=week_start,
                                                                  submission_date__lt=week_end)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)
                return Response(serializer.data)

            elif date_range == 'month':
                candObj = candidatesJobDescription.objects.filter(candidate_name__created_by_id=recruiter_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  submission_date__gt=month_start,
                                                                  submission_date__lt=month_end)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)
                return Response(serializer.data)

            elif start_date is not None and end_date is not None:
                candObj = candidatesJobDescription.objects.filter(candidate_name__created_by_id=recruiter_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  submission_date__gt=start_date,
                                                                  submission_date__lt=end_date)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)
                return Response(serializer.data)

        elif request.query_params.get('job_id') and request.query_params.get('stage'):
            job_id = str(request.query_params.get('job_id')).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            if date_range == 'today':
                candObj = candidatesJobDescription.objects.filter(job_description_id=job_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  job_description__created_at__gt=today)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)
                return Response(serializer.data)

            elif date_range == 'yesterday':
                candObj = candidatesJobDescription.objects.filter(job_description_id=job_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  job_description__created_at__gt=yesterday,
                                                                  job_description__created_at__lt=today)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)
                return Response(serializer.data)

            elif date_range == 'week':
                candObj = candidatesJobDescription.objects.filter(job_description_id=job_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  job_description__created_at__gt=week_start,
                                                                  job_description__created_at__lt=week_end)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)
                return Response(serializer.data)

            elif date_range == 'month':
                candObj = candidatesJobDescription.objects.filter(job_description_id=job_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  job_description__created_at__gt=month_start,
                                                                  job_description__created_at__lt=month_end)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)
                return Response(serializer.data)

            elif start_date is not None and end_date is not None:
                candObj = candidatesJobDescription.objects.filter(job_description_id=job_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  job_description__created_at__gt=start_date,
                                                                  job_description__created_at__lt=end_date)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)
                return Response(serializer.data)

        elif request.query_params.get('job_creater_id'):
            job_creater_id = str(request.query_params.get('job_creater_id')).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            if date_range == 'today':
                candObj = jobModel.objects.filter(created_by_id=job_creater_id, created_at__gt=today)
                serializer = JobDescriptionSerializer(candObj, many=True)
                return Response(serializer.data)

            elif date_range == 'yesterday':
                candObj = jobModel.objects.filter(created_by_id=job_creater_id, created_at__gt=yesterday,
                                                  created_at__lt=today)
                serializer = JobDescriptionSerializer(candObj, many=True)
                return Response(serializer.data)

            elif date_range == 'week':
                candObj = jobModel.objects.filter(created_by_id=job_creater_id, created_at__gt=week_start,
                                                  created_at__lt=week_end)
                serializer = JobDescriptionSerializer(candObj, many=True)
                return Response(serializer.data)

            elif date_range == 'month':
                candObj = jobModel.objects.filter(created_by_id=job_creater_id, created_at__gt=month_start,
                                                  created_at__lt=month_end)
                serializer = JobDescriptionSerializer(candObj, many=True)
                return Response(serializer.data)

            elif request.query_params.get('month') and request.query_params.get('year'):
                month = request.query_params.get('month')
                year = request.query_params.get('year')
                candObj = jobModel.objects.filter(created_by_id=job_creater_id, created_at__month=month,
                                                  created_at__year=year)
                serializer = JobDescriptionSerializer(candObj, many=True)
                return Response(serializer.data)

            elif request.query_params.get('single_date'):
                candObj = jobModel.objects.filter(created_by_id=job_creater_id,
                                                  created_at__date=request.query_params.get('single_date'))
                serializer = JobDescriptionSerializer(candObj, many=True)
                return Response(serializer.data)


class JobsByBDMSummaryTable(generics.ListAPIView):
    queryset = Candidates.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]  # SearchFilter,
    filter_class = ReportFilter

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

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
        uid = str(request.user.id).replace("-", "")

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = jobModel.objects.filter(created_at__gt=today)
            elif date_range == 'yesterday':
                queryset = jobModel.objects.filter(created_at__gt=yesterday, created_at__lt=today)
            elif date_range == 'week':
                queryset = jobModel.objects.filter(created_at__gt=week_start, created_at__lt=week_end)
            elif date_range == 'month':
                queryset = jobModel.objects.filter(created_at__gt=month_start, created_at__lt=month_end)
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.filter(created_at__gt=start_date, created_at__lt=end_date)

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.filter(created_at__gt=today)
            elif date_range == 'yesterday':
                queryset = jobModel.objects.filter(created_at__gt=yesterday, created_at__lt=today)
            elif date_range == 'week':
                queryset = jobModel.objects.filter(created_at__gt=week_start, created_at__lt=week_end)
            elif date_range == 'month':
                queryset = jobModel.objects.filter(created_at__gt=month_start, created_at__lt=month_end)
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.filter(created_at__gt=start_date, created_at__lt=end_date)

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.filter(created_at__gt=today)
            elif date_range == 'yesterday':
                queryset = jobModel.objects.filter(created_at__gt=yesterday, created_at__lt=today)
            elif date_range == 'week':
                queryset = jobModel.objects.filter(created_at__gt=week_start, created_at__lt=week_end)
            elif date_range == 'month':
                queryset = jobModel.objects.filter(created_at__gt=month_start, created_at__lt=month_end)
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.filter(created_at__gt=start_date, created_at__lt=end_date)

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = jobModel.objects.filter(created_at__gt=today)
            elif date_range == 'yesterday':
                queryset = jobModel.objects.filter(created_at__gt=yesterday, created_at__lt=today)
            elif date_range == 'week':
                queryset = jobModel.objects.filter(created_at__gt=week_start, created_at__lt=week_end)
            elif date_range == 'month':
                queryset = jobModel.objects.filter(created_at__gt=month_start, created_at__lt=month_end)
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.filter(created_at__gt=start_date, created_at__lt=end_date)

        if queryset is not None:
            logger.debug('Queryset : %s' % str(queryset.query))

        # queryset = self.filter_queryset(queryset)
        serializer = JobsByBDMTableSerializer(queryset, many=True)
        return Response(serializer.data)


class JobsByBDMSummaryCSV(generics.ListAPIView):
    queryset = Candidates.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]  # SearchFilter,
    filter_class = ReportFilter

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

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
        uid = str(request.user.id).replace("-", "")

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = jobModel.objects.filter(created_at__gt=today)
            elif date_range == 'yesterday':
                queryset = jobModel.objects.filter(created_at__gt=yesterday, created_at__lt=today)
            elif date_range == 'week':
                queryset = jobModel.objects.filter(created_at__gt=week_start, created_at__lt=week_end)
            elif date_range == 'month':
                queryset = jobModel.objects.filter(created_at__gt=month_start, created_at__lt=month_end)
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.filter(created_at__gt=start_date, created_at__lt=end_date)

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.filter(created_at__gt=today)
            elif date_range == 'yesterday':
                queryset = jobModel.objects.filter(created_at__gt=yesterday, created_at__lt=today)
            elif date_range == 'week':
                queryset = jobModel.objects.filter(created_at__gt=week_start, created_at__lt=week_end)
            elif date_range == 'month':
                queryset = jobModel.objects.filter(created_at__gt=month_start, created_at__lt=month_end)
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.filter(created_at__gt=start_date, created_at__lt=end_date)

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.filter(created_at__gt=today)
            elif date_range == 'yesterday':
                queryset = jobModel.objects.filter(created_at__gt=yesterday, created_at__lt=today)
            elif date_range == 'week':
                queryset = jobModel.objects.filter(created_at__gt=week_start, created_at__lt=week_end)
            elif date_range == 'month':
                queryset = jobModel.objects.filter(created_at__gt=month_start, created_at__lt=month_end)
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.filter(created_at__gt=start_date, created_at__lt=end_date)

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if date_range == 'today':
                queryset = jobModel.objects.filter(created_at__gt=today)
            elif date_range == 'yesterday':
                queryset = jobModel.objects.filter(created_at__gt=yesterday, created_at__lt=today)
            elif date_range == 'week':
                queryset = jobModel.objects.filter(created_at__gt=week_start, created_at__lt=week_end)
            elif date_range == 'month':
                queryset = jobModel.objects.filter(created_at__gt=month_start, created_at__lt=month_end)
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.filter(created_at__gt=start_date, created_at__lt=end_date)

        if queryset is not None:
            logger.debug('Queryset : %s' % str(queryset.query))

        # queryset = self.filter_queryset(queryset)
        serializer = JobsByBDMTableSerializer(queryset, many=True)
        array_length = len(serializer.data)
        outputs = []
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
                'bdm_name': str(serializer.data[i]['created_by']['first_name']) + ' ' + str(
                    serializer.data[i]['created_by']['last_name']),
                'job_date': serializer.data[i]['created_at']
            }

            outputs.append(rows)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="job_by_bdm_summary.csv"'
        writer = csv.DictWriter(response, fieldnames=['job_id',
                                                      'job_title', 'min_rate', 'max_rate', 'min_salary', 'max_salary',
                                                      'job_type', 'client_name', 'bdm_name', 'job_date'
                                                      ])

        writer.writeheader()

        writer.writerows(outputs)

        return response


class JobsByBDMSummaryGraph(generics.ListAPIView):
    queryset = jobModel.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

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
        uid = str(request.user.id).replace("-", "")

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT a.id, a.created_at, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id , COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at > %s GROUP BY DATE(a.created_at), bdm_name",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT a.id, a.created_at, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id, COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at > %s AND a.created_at < %s GROUP BY DATE(a.created_at), bdm_name",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT a.id, a.created_at, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id, COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at >= %s AND a.created_at <= %s GROUP BY DATE(a.created_at), bdm_name",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT a.id, a.created_at, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id, COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at >= %s AND a.created_at <= %s GROUP BY DATE(a.created_at), bdm_name",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                if (datetime.datetime.strptime(end_date, '%Y-%m-%d').date() - datetime.datetime.strptime(start_date,
                                                                                                         '%Y-%m-%d').date()).days > 30:
                    queryset = jobModel.objects.raw(
                        "SELECT a.id, MONTHNAME(a.created_at) AS month, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id, COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at >= %s AND a.created_at <= %s GROUP BY MONTHNAME(a.created_at) , bdm_name",
                        [start_date, end_date])
                else:
                    queryset = jobModel.objects.raw(
                        "SELECT a.id, a.created_at, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id, COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at >= %s AND a.created_at <= %s GROUP BY DATE(a.created_at), bdm_name",
                        [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT a.id, a.created_at, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id , COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at > %s GROUP BY DATE(a.created_at), bdm_name",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT a.id, a.created_at, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id , COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at > %s AND a.created_at < %s GROUP BY DATE(a.created_at), bdm_name",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT a.id, a.created_at, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id , COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at >= %s AND a.created_at <= %s GROUP BY DATE(a.created_at), bdm_name",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT a.id, a.created_at, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id , COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at >= %s AND a.created_at <= %s GROUP BY DATE(a.created_at), bdm_name",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                if (datetime.datetime.strptime(end_date, '%Y-%m-%d').date() - datetime.datetime.strptime(start_date,
                                                                                                         '%Y-%m-%d').date()).days > 30:
                    queryset = jobModel.objects.raw(
                        "SELECT a.id, MONTHNAME(a.created_at) AS month, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id , COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at >= %s AND a.created_at <= %s GROUP BY MONTHNAME(a.created_at) , bdm_name",
                        [start_date, end_date])
                else:
                    queryset = jobModel.objects.raw(
                        "SELECT a.id, a.created_at, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id , COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at >= %s AND a.created_at <= %s GROUP BY DATE(a.created_at), bdm_name",
                        [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT a.id, a.created_at, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id , COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at > %s GROUP BY DATE(a.created_at), bdm_name",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT a.id, a.created_at, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id , COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at > %s AND a.created_at < %s GROUP BY DATE(a.created_at), bdm_name",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT a.id, a.created_at, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id , COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at >= %s AND a.created_at <= %s GROUP BY DATE(a.created_at), bdm_name",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT a.id, a.created_at, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id , COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at >= %s AND a.created_at <= %s GROUP BY DATE(a.created_at), bdm_name",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                if (datetime.datetime.strptime(end_date, '%Y-%m-%d').date() - datetime.datetime.strptime(start_date,
                                                                                                         '%Y-%m-%d').date()).days > 30:
                    queryset = jobModel.objects.raw(
                        "SELECT a.id, MONTHNAME(a.created_at) AS month, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id , COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at >= %s AND a.created_at <= %s GROUP BY MONTHNAME(a.created_at) , bdm_name",
                        [start_date, end_date])
                else:
                    queryset = jobModel.objects.raw(
                        "SELECT a.id, a.created_at, CONCAT(u.first_name, ' ' , u.last_name) AS bdm_name ,a.created_by_id as bdm_id , COUNT(a.id) AS total_count FROM osms_job_description as a , users_user as u WHERE u.id = a.created_by_id AND a.created_at >= %s AND a.created_at <= %s GROUP BY DATE(a.created_at), bdm_name",
                        [start_date, end_date])

        if queryset is not None:
            logger.debug('Queryset : %s' % str(queryset.query))
            # queryset = self.filter_queryset(queryset)
            serializer = JobsByBDMGraphSerializer(queryset, many=True)
            # print(serializer.data['first_name'])
            return Response(serializer.data)


class ExportGraphsPointList(generics.ListAPIView):
    queryset = Candidates.objects.none()

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        today = utils.get_current_date()
        yesterday = utils.yesterday_datetime()
        week_start, week_end = utils.week_date_range()
        month_start, month_end = utils.month_date_range()

        if request.query_params.get('bdm_id') and request.query_params.get('stage'):
            bdm_id = str(request.query_params.get('bdm_id')).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            # stage_id = str(request.query_params.get('stage_id')).replace('UUID', ''). \
            # replace('(\'', '').replace('\')', '').replace('-', '')
            if date_range == 'today':
                candObj = candidatesJobDescription.objects.filter(job_description__created_by_id=bdm_id,
                                                                  stage__stage_name=request.query_params.get('stage'),
                                                                  submission_date__gt=today)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)

            elif date_range == 'yesterday':
                candObj = candidatesJobDescription.objects.filter(job_description__created_by_id=bdm_id,
                                                                  stage__stage_name=request.query_params.get('stage'),
                                                                  submission_date__gt=yesterday,
                                                                  submission_date__lt=today)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)

            elif date_range == 'week':
                candObj = candidatesJobDescription.objects.filter(job_description__created_by_id=bdm_id,
                                                                  stage__stage_name=request.query_params.get('stage'),
                                                                  submission_date__gt=week_start,
                                                                  submission_date__lt=week_end)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)

            elif date_range == 'month':
                candObj = candidatesJobDescription.objects.filter(job_description__created_by_id=bdm_id,
                                                                  stage__stage_name=request.query_params.get('stage'),
                                                                  submission_date__gt=month_start,
                                                                  submission_date__lt=month_end)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)

            elif start_date is not None and end_date is not None:
                candObj = candidatesJobDescription.objects.filter(job_description__created_by_id=bdm_id,
                                                                  stage__stage_name=request.query_params.get('stage'),
                                                                  submission_date__gt=start_date,
                                                                  submission_date__lt=end_date)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)

            array_length = len(serializer.data)
            outputs = []
            print(array_length)
            for i in range(array_length):  # Use `xrange` for python 2.

                rows = {
                    'candidate_name': str(serializer.data[i]['candidate_name']['first_name']) + ' ' + str(
                        serializer.data[i]['candidate_name']['last_name']),
                    'email': serializer.data[i]['candidate_name']['primary_email'],
                    'phone_number': serializer.data[i]['candidate_name']['primary_phone_number'],
                    'job_title': serializer.data[i]['job_description']['job_title'],
                    'min_rate': serializer.data[i]['candidate_name']['min_rate'],
                    'max_rate': serializer.data[i]['candidate_name']['max_rate'],
                    'min_salary': serializer.data[i]['candidate_name']['min_salary'],
                    'max_salary': serializer.data[i]['candidate_name']['max_salary'],
                    'status': serializer.data[i]['stage']['stage_name'],
                    'skills_1': serializer.data[i]['candidate_name']['skills_1'],
                    'skills_2': serializer.data[i]['candidate_name']['skills_2'],
                    'created_at': serializer.data[i]['candidate_name']['created_at']
                }

                outputs.append(rows)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="bdm_performance.csv"'
            writer = csv.DictWriter(response, fieldnames=['candidate_name', 'email', 'phone_number', 'job_title',
                                                          'min_rate', 'max_rate', 'min_salary', 'max_salary',
                                                          'status', 'skills_1', 'skills_2', 'created_at'
                                                          ])

            writer.writeheader()
            writer.writerows(outputs)
            return response


        elif request.query_params.get('recruiter_id') and request.query_params.get('stage'):
            recruiter_id = str(request.query_params.get('recruiter_id')).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            if date_range == 'today':
                candObj = candidatesJobDescription.objects.filter(candidate_name__created_by_id=recruiter_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  submission_date__gt=today)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)

            elif date_range == 'yesterday':
                candObj = candidatesJobDescription.objects.filter(candidate_name__created_by_id=recruiter_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  submission_date__gt=yesterday,
                                                                  submission_date__lt=today)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)

            elif date_range == 'week':
                candObj = candidatesJobDescription.objects.filter(candidate_name__created_by_id=recruiter_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  submission_date__gt=week_start,
                                                                  submission_date__lt=week_end)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)

            elif date_range == 'month':
                candObj = candidatesJobDescription.objects.filter(candidate_name__created_by_id=recruiter_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  submission_date__gt=month_start,
                                                                  submission_date__lt=month_end)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)

            elif start_date is not None and end_date is not None:
                candObj = candidatesJobDescription.objects.filter(candidate_name__created_by_id=recruiter_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  submission_date__gt=start_date,
                                                                  submission_date__lt=end_date)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)

            array_length = len(serializer.data)
            outputs = []
            for i in range(array_length):  # Use `xrange` for python 2.

                rows = {
                    'candidate_name': str(serializer.data[i]['candidate_name']['first_name']) + ' ' + str(
                        serializer.data[i]['candidate_name']['last_name']),
                    'email': serializer.data[i]['candidate_name']['primary_email'],
                    'phone_number': serializer.data[i]['candidate_name']['primary_phone_number'],
                    'job_title': serializer.data[i]['job_description']['job_title'],
                    'min_rate': serializer.data[i]['candidate_name']['min_rate'],
                    'max_rate': serializer.data[i]['candidate_name']['max_rate'],
                    'min_salary': serializer.data[i]['candidate_name']['min_salary'],
                    'max_salary': serializer.data[i]['candidate_name']['max_salary'],
                    'status': serializer.data[i]['stage']['stage_name'],
                    'skills_1': serializer.data[i]['candidate_name']['skills_1'],
                    'skills_2': serializer.data[i]['candidate_name']['skills_2'],
                    'created_at': serializer.data[i]['candidate_name']['created_at']
                }

                outputs.append(rows)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="recuiter_performance.csv"'
            writer = csv.DictWriter(response, fieldnames=['candidate_name', 'email', 'phone_number', 'job_title',
                                                          'min_rate', 'max_rate', 'min_salary', 'max_salary',
                                                          'status', 'skills_1', 'skills_2', 'created_at'
                                                          ])
            writer.writeheader()
            writer.writerows(outputs)
            return response

        elif request.query_params.get('job_id') and request.query_params.get('stage'):
            job_id = str(request.query_params.get('job_id')).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            if date_range == 'today':
                candObj = candidatesJobDescription.objects.filter(job_description_id=job_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  job_description__created_at__gt=today)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)

            elif date_range == 'yesterday':
                candObj = candidatesJobDescription.objects.filter(job_description_id=job_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  job_description__created_at__gt=yesterday,
                                                                  job_description__created_at__lt=today)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)

            elif date_range == 'week':
                candObj = candidatesJobDescription.objects.filter(job_description_id=job_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  job_description__created_at__gt=week_start,
                                                                  job_description__created_at__lt=week_end)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)

            elif date_range == 'month':
                candObj = candidatesJobDescription.objects.filter(job_description_id=job_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  job_description__created_at__gt=month_start,
                                                                  job_description__created_at__lt=month_end)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)

            elif start_date is not None and end_date is not None:
                candObj = candidatesJobDescription.objects.filter(job_description_id=job_id,
                                                                  stage__stage_name=str(
                                                                      request.query_params.get('stage')),
                                                                  job_description__created_at__gt=start_date,
                                                                  job_description__created_at__lt=end_date)
                serializer = CandidateJobsStagesSerializer(candObj, many=True)

            array_length = len(serializer.data)
            outputs = []
            for i in range(array_length):  # Use `xrange` for python 2.

                rows = {
                    'candidate_name': str(serializer.data[i]['candidate_name']['first_name']) + ' ' + str(
                        serializer.data[i]['candidate_name']['last_name']),
                    'email': serializer.data[i]['candidate_name']['primary_email'],
                    'phone_number': serializer.data[i]['candidate_name']['primary_phone_number'],
                    'job_title': serializer.data[i]['job_description']['job_title'],
                    'min_rate': serializer.data[i]['candidate_name']['min_rate'],
                    'max_rate': serializer.data[i]['candidate_name']['max_rate'],
                    'min_salary': serializer.data[i]['candidate_name']['min_salary'],
                    'max_salary': serializer.data[i]['candidate_name']['max_salary'],
                    'status': serializer.data[i]['stage']['stage_name'],
                    'skills_1': serializer.data[i]['candidate_name']['skills_1'],
                    'skills_2': serializer.data[i]['candidate_name']['skills_2'],
                    'created_at': serializer.data[i]['candidate_name']['created_at']
                }

                outputs.append(rows)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="job_summary.csv"'
            writer = csv.DictWriter(response, fieldnames=['candidate_name', 'email', 'phone_number', 'job_title',
                                                          'min_rate', 'max_rate', 'min_salary', 'max_salary',
                                                          'status', 'skills_1', 'skills_2', 'created_at'
                                                          ])
            writer.writeheader()
            writer.writerows(outputs)
            return response

        elif request.query_params.get('job_creater_id'):
            job_creater_id = str(request.query_params.get('job_creater_id')).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            if date_range == 'today':
                candObj = jobModel.objects.filter(created_by_id=job_creater_id, created_at__gt=today)
                serializer = JobDescriptionSerializer(candObj, many=True)

            elif date_range == 'yesterday':
                candObj = jobModel.objects.filter(created_by_id=job_creater_id, created_at__gt=yesterday,
                                                  created_at__lt=today)
                serializer = JobDescriptionSerializer(candObj, many=True)

            elif date_range == 'week':
                candObj = jobModel.objects.filter(created_by_id=job_creater_id, created_at__gt=week_start,
                                                  created_at__lt=week_end)
                serializer = JobDescriptionSerializer(candObj, many=True)

            elif date_range == 'month':
                candObj = jobModel.objects.filter(created_by_id=job_creater_id, created_at__gt=month_start,
                                                  created_at__lt=month_end)
                serializer = JobDescriptionSerializer(candObj, many=True)

            elif request.query_params.get('month') and request.query_params.get('year'):
                month = request.query_params.get('month')
                year = request.query_params.get('year')
                candObj = jobModel.objects.filter(created_by_id=job_creater_id, created_at__month=month,
                                                  created_at__year=year)
                serializer = JobDescriptionSerializer(candObj, many=True)

            elif request.query_params.get('single_date'):
                candObj = jobModel.objects.filter(created_by_id=job_creater_id,
                                                  created_at__date=request.query_params.get('single_date'))
                serializer = JobDescriptionSerializer(candObj, many=True)

            array_length = len(serializer.data)
            outputs = []
            for i in range(array_length):  # Use `xrange` for python 2.

                rows = {
                    'job_posted_date': serializer.data[i]['created_at'],
                    'client': serializer.data[i]['client_name']['company_name'],
                    'job_title': serializer.data[i]['job_title'],
                    'min_rate': serializer.data[i]['min_rate'],
                    'max_rate': serializer.data[i]['max_rate'],
                    'min_salary': serializer.data[i]['min_salary'],
                    'max_salary': serializer.data[i]['max_salary'],
                    'job_id': serializer.data[i]['job_id']
                }

                outputs.append(rows)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="bdm_jobs_summary.csv"'
            writer = csv.DictWriter(response, fieldnames=['job_posted_date', 'client', 'job_title',
                                                          'min_rate', 'max_rate', 'min_salary', 'max_salary', 'job_id'
                                                          ])
            writer.writeheader()
            writer.writerows(outputs)
            return response


class ActiveJobsAgingSummaryGraph(generics.ListAPIView):
    queryset = jobModel.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

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
        uid = str(request.user.id).replace("-", "")

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT js.id,js.job_id as job_id ,js.job_title,js.status, cl.company_name, CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date "
                    ", (SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date, (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u "
                    "WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND js.status = 'Active' AND js.created_at > %s ORDER BY js.created_at DESC",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT js.id, js.job_id as job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date "
                    ", (SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date, (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u "
                    "WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND js.status = 'Active' AND js.created_at > %s AND js.created_at < %s ORDER BY js.created_at DESC",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT js.id,js.job_id as job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date "
                    ", (SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date, (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u "
                    "WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT js.id,js.job_id as job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date "
                    ", (SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date, (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u "
                    "WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.raw(
                    "SELECT js.id,js.job_id as job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date "
                    ", (SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date, (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u "
                    "WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT js.id,js.job_id as job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date "
                    ", (SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date, (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u "
                    "WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND js.status = 'Active' AND js.created_at > %s ORDER BY js.created_at DESC",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT js.id, js.job_id as job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date "
                    ", (SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date, (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u "
                    "WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND js.status = 'Active' AND js.created_at > %s AND js.created_at < %s ORDER BY js.created_at DESC",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT js.id,js.job_id as job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date "
                    ", (SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date, (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u "
                    "WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT js.id,js.job_id as job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date "
                    ", (SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date, (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u "
                    "WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.raw(
                    "SELECT js.id,js.job_id as job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date "
                    ", (SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date, (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u "
                    "WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT js.id,js.job_id as job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date "
                    ", (SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date, (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u "
                    "WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND js.status = 'Active' AND js.created_at > %s ORDER BY js.created_at DESC",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT js.id, js.job_id as job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date "
                    ", (SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date, (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u "
                    "WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND js.status = 'Active' AND js.created_at > %s AND js.created_at < %s ORDER BY js.created_at DESC",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT js.id,js.job_id as job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date "
                    ", (SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date, (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u "
                    "WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT js.id,js.job_id as job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date "
                    ", (SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date, (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u "
                    "WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.raw(
                    "SELECT js.id,js.job_id as job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date "
                    ", (SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date, (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u "
                    "WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [start_date, end_date])

        if queryset is not None:
            logger.debug('Queryset : %s' % str(queryset.query))
            # queryset = self.filter_queryset(queryset)
            serializer = ActiveJobsAgingSerializer(queryset, many=True)
            # print(serializer.data['first_name'])
            return Response(serializer.data)


class ActiveJobsAgingSummaryTable(generics.ListAPIView):
    queryset = jobModel.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

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
        uid = str(request.user.id).replace("-", "")

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.status = 'Active' AND js.created_at > %s ORDER BY js.created_at DESC",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.status = 'Active' AND js.created_at > %s AND js.created_at < %s ORDER BY js.created_at DESC",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.status = 'Active' AND js.created_at > %s ORDER BY js.created_at DESC",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.status = 'Active' AND js.created_at > %s AND js.created_at < %s ORDER BY js.created_at DESC",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.status = 'Active' AND js.created_at > %s ORDER BY js.created_at DESC",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.status = 'Active' AND js.created_at > %s AND js.created_at < %s ORDER BY js.created_at DESC",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.status = 'Active' AND js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [start_date, end_date])

        if queryset is not None:
            logger.debug('Queryset : %s' % str(queryset.query))
            serializer = ActiveJobsAgingSerializer(queryset, many=True)
            return Response(serializer.data)


class ActiveJobsAgingSummaryCSV(generics.ListAPIView):
    queryset = jobModel.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

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
        uid = str(request.user.id).replace("-", "")

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.created_at > %s ORDER BY js.created_at DESC",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.created_at > %s AND js.created_at < %s ORDER BY js.created_at DESC",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.created_at > %s ORDER BY js.created_at DESC",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.created_at > %s AND js.created_at < %s ORDER BY js.created_at DESC",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.created_at > %s ORDER BY js.created_at DESC",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.created_at > %s AND js.created_at < %s ORDER BY js.created_at DESC",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.raw(
                    "SELECT js.id ,js.job_id ,js.job_title,js.status, cl.company_name , CONCAT(u.first_name , ' ' ,u.last_name) as bdm_name, js.created_at as posted_date ,(SELECT cjs.submission_date as submission_date FROM candidates_jobs_stages cjs , osms_job_description as j WHERE cjs.job_description_id = js.id ORDER BY cjs.submission_date ASC LIMIT 1) as first_submission_date ,"
                    "(SELECT ja.created_at as assingment_date FROM job_description_assingment ja ,osms_job_description as j WHERE ja.job_id_id = js.id ORDER BY ja.created_at ASC LIMIT 1) as first_assingment_date,(SELECT CONCAT(u1.first_name, ' ' , u1.last_name) FROM job_description_assingment as ja , users_user as u1 WHERE ja.job_id_id = js.id AND ja.primary_recruiter_name_id = u1.id ORDER BY ja.created_at ASC LIMIT 1) as primary_recruiter_name"
                    ",(SELECT CONCAT(u2.first_name, ' ' , u2.last_name) FROM job_description_assingment as ja , users_user as u2 WHERE ja.job_id_id = js.id AND ja.secondary_recruiter_name_id = u2.id ORDER BY ja.created_at ASC LIMIT 1) as secondary_recruiter_name , (SELECT DATEDIFF(CURDATE(), posted_date)) as job_age FROM osms_job_description as js , osms_clients as cl , users_user as u WHERE cl.id = js.client_name_id AND js.created_by_id = u.id AND "
                    "js.created_at >= %s AND js.created_at <= %s ORDER BY js.created_at DESC",
                    [start_date, end_date])

        if queryset is not None:
            logger.debug('Queryset : %s' % str(queryset.query))
            serializer = ActiveJobsAgingSerializer(queryset, many=True)
            array_length = len(serializer.data)
            outputs = []
            for i in range(array_length):  # Use `xrange` for python 2.
                rows = {
                    'job_id': serializer.data[i]['job_id'],
                    'job_title': serializer.data[i]['job_title'],
                    'status': serializer.data[i]['status'],
                    'client_name': serializer.data[i]['company_name'],
                    'posted_date': serializer.data[i]['posted_date'],
                    'first_submission_date': serializer.data[i]['first_submission_date'],
                    'first_assingment_date': serializer.data[i]['first_assingment_date'],
                    'job_age': serializer.data[i]['job_age'],
                    'bdm_name': serializer.data[i]['bdm_name'],
                    'primary_recruiter_name': serializer.data[i]['primary_recruiter_name'],
                    'secondary_recruiter_name': serializer.data[i]['secondary_recruiter_name'],
                }

                outputs.append(rows)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="active_jobs_aging_summary.csv"'
            writer = csv.DictWriter(response, fieldnames=['job_id', 'job_title', 'status', 'client_name',
                                                          'posted_date', 'first_submission_date',
                                                          'first_assingment_date', 'job_age', 'bdm_name',
                                                          'primary_recruiter_name', 'secondary_recruiter_name'])

            writer.writeheader()

            writer.writerows(outputs)

            return response


class UnassignedJobsCSV(generics.ListAPIView):
    queryset = jobModel.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]

    def get(self, request, format=None):
        queryset = jobModel.objects.raw(
            "SELECT j.id , j.job_id , j.job_title , cl.company_name , j.created_at as posted_date, CONCAT(u.first_name , ' ', u.last_name) as bdm_name "
            "FROM osms_job_description as j LEFT JOIN osms_clients as cl ON j.client_name_id = cl.id LEFT JOIN users_user as u ON u.id = j.created_by_id LEFT JOIN job_description_assingment as ja "
            "ON ja.job_id_id = j.id WHERE ja.primary_recruiter_name_id IS NULL AND ja.secondary_recruiter_name_id IS NULL ORDER BY j.created_at DESC")

        if queryset is not None:
            logger.debug('Queryset : %s' % str(queryset.query))
            # queryset = self.filter_queryset(queryset)
            serializer = UnassignedJobsSerializer(queryset, many=True)
            array_length = len(serializer.data)
            outputs = []
            for i in range(array_length):  # Use `xrange` for python 2.

                rows = {
                    'job_id': serializer.data[i]['job_id'],
                    'job_title': serializer.data[i]['job_title'],
                    'client_name': serializer.data[i]['company_name'],
                    'posted_date': serializer.data[i]['posted_date'],
                    'bdm_name': serializer.data[i]['bdm_name'],
                }

                outputs.append(rows)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="unassigned_jobs_summary.csv"'
            writer = csv.DictWriter(response, fieldnames=['job_id', 'job_title', 'client_name',
                                                          'posted_date', 'bdm_name'])

            writer.writeheader()

            writer.writerows(outputs)

            return response


class ClientRevenueReport(generics.ListAPIView):
    queryset = jobModel.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

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
        uid = str(request.user.id).replace("-", "")

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id , cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id , cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id , cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [start_date, end_date])

        if queryset is not None:
            logger.debug('Queryset : %s' % str(queryset.query))
            serializer = ClientRevenueSerializer(queryset, many=True)
            return Response(serializer.data)


class ClientRevenueReportCSV(generics.ListAPIView):
    queryset = jobModel.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, ]

    def get(self, request, format=None):
        date_range = request.query_params.get('date_range')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

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
        uid = str(request.user.id).replace("-", "")

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id , cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id , cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [start_date, end_date])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if date_range == 'today':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id , cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [today])
            elif date_range == 'yesterday':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [yesterday, today])
            elif date_range == 'week':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [week_start, week_end])
            elif date_range == 'month':
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [month_start, month_end])
            elif start_date is not None and end_date is not None:
                queryset = jobModel.objects.raw(
                    "SELECT cl.id ,cl.company_name as client_name_value , SUM(j.projected_revenue) as expected_revenue, (SELECT SUM(js.projected_revenue) FROM osms_job_description as js ,candidates_jobs_stages as cjs, candidates_stages as s WHERE js.client_name_id = cl.id ANd cjs.job_description_id = js.id"
                    " AND s.stage_name = 'Placed' AND s.id = cjs.stage_id) as actual_revenue FROM osms_job_description as j , osms_clients as cl WHERE j.client_name_id = cl.id AND j.created_at > %s AND j.created_at < %s GROUP BY client_name_value ORDER BY j.created_at DESC ",
                    [start_date, end_date])

        if queryset is not None:
            logger.debug('Queryset : %s' % str(queryset.query))
            serializer = ClientRevenueSerializer(queryset, many=True)
            array_length = len(serializer.data)
            outputs = []
            for i in range(array_length):  # Use `xrange` for python 2.

                rows = {
                    'client_name': serializer.data[i]['client_name_value'],
                    'expected_revenue': serializer.data[i]['expected_revenue'],
                    'actual_revenue': serializer.data[i]['actual_revenue'],
                }

                outputs.append(rows)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="client_revenue_report.csv"'
            writer = csv.DictWriter(response, fieldnames=['client_name', 'expected_revenue', 'actual_revenue'])

            writer.writeheader()

            writer.writerows(outputs)

            return response


# daily mail sending method
def send_recruiter_email(country):
    today_date = utils.get_current_datetime()
    start_date = utils.get_current_date()
    both_country = []
    if country == 'US':
        both_country.append('venkat@opallios.com')
        # start_date = datetime.datetime.strptime(today_date, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=12, minutes=30, seconds=00)
        start_date = str(datetime.date.today() - datetime.timedelta(days=1)) + str(' 12:30:00')
    queryset = Candidates.objects.raw(
        "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, cl.company_name AS client_name ,"
        "CONCAT(u1.first_name,' ',u1.last_name) as bdm_name , CONCAT(u2.first_name,' ',u2.last_name) as recruiter_name , u2.country as location , j.job_title FROM"
        " `osms_job_description` as j,`users_user` as u1, users_user as u2 , `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, "
        "`candidates_jobs_stages` as cjs WHERE j.created_by_id = u1.id AND ca.created_by_id = u2.id AND s.stage_name != 'Candidate Added' AND "
        "j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s AND u2.country = %s AND cl.country = %s ORDER BY recruiter_name",
        [start_date, today_date, country, country])
    output = []
    logger.debug('Queryset : %s' % str(queryset.query))
    if queryset is not None:
        serializer = RecruiterEmailReportSerializer(queryset, many=True)
        userqueryset = User.objects.raw("SELECT id, email, country from users_user where role = '3' AND country = %s",
                                        [country])
        user_serializer = UserSerializer(userqueryset, many=True)
        recruiter_emails = []
        for i in range(len(user_serializer.data)):
            recruiter_emails.append(user_serializer.data[i]['email'])

        bdmqueryset = User.objects.raw(
            "SELECT id, email, country from users_user where role = '9' AND country = %s", [country])
        bdm_serializer = UserSerializer(bdmqueryset, many=True)
        bdm_emails = []
        for i in range(len(bdm_serializer.data)):
            bdm_emails.append(bdm_serializer.data[i]['email'])

        for i in range(len(serializer.data)):  # Use `xrange` for python 2.
            rows = {
                'candidate_name': serializer.data[i]['candidate_name'],
                'client_name': serializer.data[i]['client_name'],
                'bdm_name': serializer.data[i]['bdm_name'],
                'recruiter_name': serializer.data[i]['recruiter_name'],
                'location': serializer.data[i]['location'],
                'job_title': serializer.data[i]['job_title']
            }
            output.append(rows)
        message = render_to_string('recruiter_email_report.html', {'data': output})
        # test_email = ['pandeym@cresitatech.com' , 'kuriwaln@opallios.com' , 'agrawalv@cresitatech.com']
        email = EmailMessage(subject="Daily Subimissions for {0}".format(start_date), body=message,
                             from_email='osms.opallios@gmail.com', to=recruiter_emails)
        email.content_subtype = 'html'
        # om = 'paradkaro@opallios.com'
        email.cc = ['mathurp@opallios.com', 'girish@opallios.com', 'paradkaro@opallios.com', 'minglaniy@opallios.com',
                    'kuriwaln@opallios.com'] + bdm_emails + both_country
        email.send()
        logger.debug('Email Send Successfully !!!!!!!!')
        return str(queryset.query)


def send_bdm_email(country):
    today_date = utils.get_current_datetime()
    start_date = utils.get_current_date()
    both_country = []
    if country == 'US':
        both_country.append('venkat@opallios.com')
        start_date = str(datetime.date.today() - datetime.timedelta(days=1)) + str(' 12:30:00')
    queryset = Candidates.objects.raw(
        "SELECT j.id ,j.job_title , j.job_id , cl.company_name as client_name , CONCAT(u.first_name,' ' ,u.last_name)"
        "as bdm_name,u.country as bdm_location FROM osms_job_description as j, osms_clients as cl,users_user as u "
        "WHERE cl.id = j.client_name_id "
        "AND u.id = j.created_by_id AND j.job_posted_date >= %s AND j.job_posted_date <= %s AND u.country = %s AND "
        "cl.country = %s ORDER BY bdm_name",
        [start_date, today_date, country, country])

    if queryset is not None:
        logger.debug('Queryset : %s' % str(queryset.query))
        serializer = BdmEmailReportSerializer(queryset, many=True)
        userqueryset = User.objects.raw(
            "SELECT id, email, country from users_user where role = '9' AND country = %s", [country])
        user_serializer = UserSerializer(userqueryset, many=True)
        bdm_emails = []
        for i in range(len(user_serializer.data)):
            bdm_emails.append(user_serializer.data[i]['email'])
        output = []
        for i in range(len(serializer.data)):
            rows = {
                'job_title': serializer.data[i]['job_title'],
                'job_id': serializer.data[i]['job_id'],
                'client_name': serializer.data[i]['client_name'],
                'bdm_name': serializer.data[i]['bdm_name'],
                'bdm_location': serializer.data[i]['bdm_location']
            }
            output.append(rows)
        message = render_to_string('bdm_email_report.html', {'data': output})
        email = EmailMessage(subject="Daily Jobs for {0}".format(start_date), body=message,
                             from_email='osms.opallios@gmail.com', to=bdm_emails)
        email.content_subtype = 'html'
        email.cc = ['mathurp@opallios.com', 'girish@opallios.com', 'paradkaro@opallios.com', 'minglaniy@opallios.com',
                    'kuriwaln@opallios.com']
        email.send()
        # ,'paradkaro@opallios.com'
        return str(queryset.query)


# weekly mail sending method
def send_daily_recuiter_performance_report(country):
    today_date = utils.get_current_datetime()
    start_date = utils.get_current_date()
    both_country = []
    if country == 'US':
        both_country.append('venkat@opallios.com')
        start_date = str(datetime.date.today() - datetime.timedelta(days=1)) + str(' 12:30:00')

    queryset = Candidates.objects.raw(
        "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
        "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j RIGHT JOIN `users_user` as u on j.created_by_id = u.id AND u.country = %s LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s ORDER BY bdm_name ) AS "
        " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
        " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
        " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
        "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
        " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id  ) AS B ON A.id = B.job_id ",
        [country, start_date, today_date])

    if queryset is not None:
        logger.debug('Recruiter Perf Table QuerySet Query formed: ' + str(queryset.query))

    userqueryset = User.objects.raw("SELECT id, email, country from users_user where role = '3' AND country = %s",
                                    [country])
    user_serializer = UserSerializer(userqueryset, many=True)
    recruiter_emails = []
    for i in range(len(user_serializer.data)):
        recruiter_emails.append(user_serializer.data[i]['email'])

    bdmqueryset = User.objects.raw(
        "SELECT id, email, country from users_user where role = '9' AND country = %s", [country])
    bdm_serializer = UserSerializer(bdmqueryset, many=True)
    bdm_emails = []
    for i in range(len(bdm_serializer.data)):
        bdm_emails.append(bdm_serializer.data[i]['email'])

    # queryset = self.filter_queryset(queryset)
    serializer = JobSummaryTableSerializer(queryset, many=True)
    # print(serializer.data['first_name'])
    array_length = len(serializer.data)
    outputs = []
    for i in range(array_length):
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
            'job_date': serializer.data[i]['job_date'].split(' ')[0],
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

    message = render_to_string('recruiter_performance_daily_report.html', {'data': outputs})
    email = EmailMessage(subject="Daily Jobs by BDMs: {0}".format(str(start_date).split(' ')[0]),
                         body=message, from_email='osms.opallios@gmail.com',
                         to=['mathurp@opallios.com', 'girish@opallios.com', 'paradkaro@opallios.com',
                             'minglaniy@opallios.com', 'kuriwaln@opallios.com'] + bdm_emails
                         # to=['kuriwaln@opallios.com']
                         )
    email.content_subtype = 'html'
    email.cc = recruiter_emails
    email.send()

    return str(queryset.query)


def send_weekly_recruiter_submission(country):
    today_date = utils.get_current_datetime()
    # start_date = str(utils.get_last_saturday())
    start_date = str(datetime.date.today() - datetime.timedelta(days=7))
    both_country = []
    if country == 'US':
        both_country.append('venkat@opallios.com')
        start_date = str(datetime.date.today() - datetime.timedelta(days=8)) + str(' 12:30:00')

    queryset = Candidates.objects.raw(
        "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, cl.company_name AS client_name ,"
        "CONCAT(u1.first_name,' ',u1.last_name) as bdm_name , CONCAT(u2.first_name,' ',u2.last_name) as recruiter_name , u2.country as location , j.job_title, cjs.submission_date FROM"
        " `osms_job_description` as j,`users_user` as u1, users_user as u2 , `osms_clients` as cl, `osms_candidates` as ca, `candidates_stages` as s, "
        "`candidates_jobs_stages` as cjs WHERE j.created_by_id = u1.id AND ca.created_by_id = u2.id AND s.stage_name != 'Candidate Added' AND "
        "j.client_name_id = cl.id and j.id = cjs.job_description_id AND cjs.stage_id = s.id AND ca.id = cjs.candidate_name_id AND cjs.submission_date >= %s AND cjs.submission_date <= %s AND u2.country = %s AND cl.country = %s ORDER BY recruiter_name, cjs.submission_date",
        [start_date, today_date, country, country])
    output = []
    finalOutput = []
    if queryset is not None:
        logger.debug('Queryset : %s' % str(queryset.query))
        serializer = RecruiterEmailReportSerializer(queryset, many=True)
        userqueryset = User.objects.raw("SELECT id, email, country from users_user where role = '3' AND country = %s",
                                        [country])
        user_serializer = UserSerializer(userqueryset, many=True)
        recruiter_emails = []
        for i in range(len(user_serializer.data)):
            recruiter_emails.append(user_serializer.data[i]['email'])

        bdmqueryset = User.objects.raw(
            "SELECT id, email, country from users_user where role = '9' AND country = %s", [country])
        bdm_serializer = UserSerializer(bdmqueryset, many=True)
        bdm_emails = []
        for i in range(len(bdm_serializer.data)):
            bdm_emails.append(bdm_serializer.data[i]['email'])

        for i in range(len(serializer.data)):
            rows = {
                'submission_date': str(serializer.data[i]['submission_date']).split(' ')[0],
                'candidate_name': serializer.data[i]['candidate_name'],
                'client_name': serializer.data[i]['client_name'],
                'bdm_name': serializer.data[i]['bdm_name'],
                'recruiter_name': serializer.data[i]['recruiter_name'],
                'job_title': serializer.data[i]['job_title']
            }
            output.append(rows)

        df = pd.DataFrame(output)
        if not df.empty:
            grouped = df.groupby('recruiter_name')
            for name, group in grouped:
                group_data = []
                for row_index, row in group.iterrows():
                    group_row = {
                        'submission_date': str(row['submission_date']).split(' ')[0],
                        'candidate_name': row['candidate_name'],
                        'client_name': row['client_name'],
                        'bdm_name': row['bdm_name'],
                        'recruiter_name': row['recruiter_name'],
                        'job_title': row['job_title']
                    }
                    group_data.append(group_row)

                row = {
                    'name': name,
                    'user_data': group_data,
                    'total_bdm': group['bdm_name'].nunique(),
                    'total_client': group['candidate_name'].nunique()
                }
                finalOutput.append(row)

        message = render_to_string('recruiter_weekly_submission_report.html', {'data': finalOutput})
        email = EmailMessage(subject="Weekly Submission by Recruiter: {0} to {1}".format(str(start_date).split(' ')[0],
                                                                                         str(today_date).split(' ')[0]),
                             body=message,
                             from_email='osms.opallios@gmail.com', to=recruiter_emails)
        email.content_subtype = 'html'
        email.cc = ['mathurp@opallios.com', 'girish@opallios.com', 'paradkaro@opallios.com', 'minglaniy@opallios.com',
                    'kuriwaln@opallios.com'] + bdm_emails + both_country
        email.send()
        print('Email Send Successfully !!!!!!!!')
        # return response
        # return render(request, "recruiter_weekly_submission_report.html", {'data': finalOutput, 'df': str(queryset.query)})

        return str(queryset.query)


def send_weekly_bdm_jobs(request, country='US'):
    today_date = utils.get_current_datetime()
    start_date = str(datetime.date.today() - datetime.timedelta(days=7))
    both_country = []
    if country == 'US':
        both_country.append('venkat@opallios.com')
        start_date = str(datetime.date.today() - datetime.timedelta(days=30)) + str(' 12:30:00')
    queryset = Candidates.objects.raw(
        "SELECT j.id ,j.job_title , j.job_id , cl.company_name as client_name , CONCAT(u.first_name,' ' ,u.last_name)"
        "as bdm_name,u.country as bdm_location, j.job_posted_date FROM osms_job_description as j, osms_clients as cl,"
        "users_user as u WHERE cl.id = j.client_name_id "
        "AND u.id = j.created_by_id AND j.job_posted_date >= %s AND j.job_posted_date <= %s AND u.country = %s AND "
        "cl.country = %s ORDER BY bdm_name, j.job_posted_date",
        [start_date, today_date, country, country])

    if queryset is not None:
        logger.debug('Queryset : %s' % str(queryset.query))
        serializer = BdmEmailReportSerializer(queryset, many=True)
        userqueryset = User.objects.raw(
            "SELECT id, email, country from users_user where role = '9' AND country = %s", [country])
        user_serializer = UserSerializer(userqueryset, many=True)
        bdm_emails = []
        for i in range(len(user_serializer.data)):
            bdm_emails.append(user_serializer.data[i]['email'])
        output = []
        finalOutput = []
        for i in range(len(serializer.data)):
            rows = {
                'job_posted_date': serializer.data[i]['job_posted_date'],
                'job_title': serializer.data[i]['job_title'],
                'client_name': serializer.data[i]['client_name'],
                'bdm_name': serializer.data[i]['bdm_name']
            }
            output.append(rows)

        df = pd.DataFrame(output)
        if not df.empty:
            grouped = df.groupby('bdm_name')
            for name, group in grouped:
                group_data = []
                for row_index, row in group.iterrows():
                    group_row = {
                        'job_posted_date': str(row['job_posted_date']).split(' ')[0],
                        'job_title': row['job_title'],
                        'client_name': row['client_name'],
                        'bdm_name': row['bdm_name'],
                    }
                    group_data.append(group_row)

                row = {
                    'name': name,
                    'user_data': group_data,
                    'total_jobs': group['job_title'].nunique(),
                    'total_client': group['client_name'].nunique()
                }
                finalOutput.append(row)

        message = render_to_string('bdm_weekly_jobs_report.html', {'data': finalOutput})
        email = EmailMessage(subject="Weekly Jobs Posted by BDMs: {0} to {1}".format(str(start_date).split(' ')[0],
                                                                                     str(today_date).split(' ')[0]),
                             body=message,
                             from_email='osms.opallios@gmail.com', to=['kuriwaln@opallios.com'])
        email.content_subtype = 'html'
        # email.cc = ['mathurp@opallios.com', 'girish@opallios.com', 'paradkaro@opallios.com', 'minglaniy@opallios.com',
        #            'kuriwaln@opallios.com'] + bdm_emails + both_country
        # email.send()
        print('Email Send Successfully !!!!!!!!')
        # return response
        return render(request, "bdm_weekly_jobs_report.html", {'data': finalOutput, 'df': str(queryset.query)})

        # return str(queryset.query)


# Arcived method
def send_weekend_recruiter_email(request, country='India'):
    today = datetime.date.today()
    # start_date = today - datetime.timedelta(days=today.weekday())
    start_date = str(today - datetime.timedelta(days=10)) + str(' 12:30:00')
    today_date = start_date + datetime.timedelta(days=4)
    both_country = []
    if country == 'US':
        both_country.append('venkat@opallios.com')
        today_date = str(start_date + datetime.timedelta(days=5)) + str(' 12:30:00')
        start_date = str(start_date) + str(' 12:30:00')
    queryset = Candidates.objects.raw(
        "SELECT u.id , CONCAT (u.first_name,' ',u.last_name) as recruiter_name , COUNT(DISTINCT(cjs.candidate_name_id)) as total_candidates , COUNT(DISTINCT(cjs.job_description_id)) as total_jobs FROM candidates_jobs_stages as cjs ,users_user as u ,"
        " candidates_stages as s WHERE cjs.created_by_id = u.id AND cjs.submission_date > %s AND cjs.submission_date < %s AND s.stage_name != 'Candidate Added' AND s.id = cjs.stage_id AND u.country = %s GROUP BY recruiter_name",
        [start_date, today_date, country])
    output = []
    if queryset is not None:
        logger.debug('Queryset : %s' % str(queryset.query))
        serializer = WeekendEmailReportSerializer(queryset, many=True)
        userqueryset = User.objects.raw("SELECT id, email, country from users_user where role = '3' AND country = %s",
                                        [country])
        user_serializer = UserSerializer(userqueryset, many=True)
        recruiter_emails = []
        for i in range(len(user_serializer.data)):
            recruiter_emails.append(user_serializer.data[i]['email'])

        bdmqueryset = User.objects.raw(
            "SELECT id, email, country from users_user where role = '9' AND country = %s", [country])
        bdm_serializer = UserSerializer(bdmqueryset, many=True)
        bdm_emails = []
        for i in range(len(bdm_serializer.data)):
            bdm_emails.append(bdm_serializer.data[i]['email'])

        total_jobs_count = 0
        total_candidates_count = 0
        for i in range(len(serializer.data)):  # Use `xrange` for python 2.
            total_jobs_count += int(serializer.data[i]['total_jobs'])
            total_candidates_count += int(serializer.data[i]['total_candidates'])

            rows = {
                'recruiter_name': serializer.data[i]['recruiter_name'],
                'total_jobs': serializer.data[i]['total_jobs'],
                'total_candidates': serializer.data[i]['total_candidates']
            }
            output.append(rows)
        total = {
            'total_jobs_count': total_jobs_count,
            'total_candidates_count': total_candidates_count,
        }
        message = render_to_string('recruiter_weekend_email_report.html', {'data': output, 'total': total})
        # test_email = ['pandeym@cresitatech.com' , 'kuriwaln@opallios.com' , 'agrawalv@cresitatech.com']
        email = EmailMessage(
            subject="Weekly Submissions by Recruiters: {0} to {1}".format(str(start_date).split(' ')[0],
                                                                          str(today_date).split(' ')[0]), body=message,
            from_email='osms.opallios@gmail.com', to=['kuriwaln@opallios.com'])
        email.content_subtype = 'html'
        # om = 'paradkaro@opallios.com'
        # email.cc = ['mathurp@opallios.com','girish@opallios.com','paradkaro@opallios.com','minglaniy@opallios.com','kuriwaln@opallios.com' , 'agrawalv@cresitatech.com'] + bdm_emails + both_country
        email.send()
        print('Email Send Successfully !!!!!!!!')

        return str(queryset.query)


def send_weekend_bdm_email(country):
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=today.weekday())
    today_date = start_date + datetime.timedelta(days=4)
    both_country = []
    if country == 'US':
        both_country.append('venkat@opallios.com')
        today_date = str(start_date + datetime.timedelta(days=5)) + str(' 12:30:00')
        start_date = str(start_date) + str(' 12:30:00')
    queryset = Candidates.objects.raw(
        "SELECT u.id, CONCAT (u.first_name,' ',u.last_name) as bdm_name ,(SELECT COUNT(*) FROM osms_job_description as js WHERE js.created_by_id = u.id AND js.created_at > %s AND"
        " js.created_at < %s) as total_jobs, COUNT(DISTINCT(cjs.candidate_name_id)) as total_candidates, COUNT(DISTINCT(cjs.job_description_id)) as total_jobs_worked FROM candidates_jobs_stages as cjs"
        " ,users_user as u , candidates_stages as s , osms_job_description as j WHERE cjs.job_description_id = j.id AND j.created_by_id = u.id AND"
        " cjs.submission_date > %s AND cjs.submission_date < %s AND s.stage_name != 'Candidate Added' AND s.id = cjs.stage_id AND u.country = %s GROUP BY bdm_name",
        [start_date, today_date, start_date, today_date, country])

    if queryset is not None:
        logger.debug('Queryset : %s' % str(queryset.query))
        serializer = WeekendEmailReportSerializer(queryset, many=True)
        userqueryset = User.objects.raw(
            "SELECT id, email, country from users_user where role = '9' AND country = %s", [country])
        user_serializer = UserSerializer(userqueryset, many=True)
        bdm_emails = []
        for i in range(len(user_serializer.data)):
            bdm_emails.append(user_serializer.data[i]['email'])
        output = []
        total_jobs_count = 0
        total_candidates_count = 0
        total_jobs_worked_count = 0
        for i in range(len(serializer.data)):
            total_jobs_count += int(serializer.data[i]['total_jobs'])
            total_candidates_count += int(serializer.data[i]['total_candidates'])
            total_jobs_worked_count += int(serializer.data[i]['total_jobs_worked'])
            rows = {
                'bdm_name': serializer.data[i]['bdm_name'],
                'total_jobs': serializer.data[i]['total_jobs'],
                'total_candidates': serializer.data[i]['total_candidates'],
                'total_jobs_worked': serializer.data[i]['total_jobs_worked']
            }
            output.append(rows)
        total = {
            'total_jobs_count': total_jobs_count,
            'total_candidates_count': total_candidates_count,
            'total_jobs_worked_count': total_jobs_worked_count
        }
        message = render_to_string('bdm_weekend_email_report.html', {'data': output, 'total': total})
        email = EmailMessage(subject="Weekly Jobs by BDMs: {0} to {1}".format(str(start_date).split(' ')[0],
                                                                              str(today_date).split(' ')[0]),
                             body=message, from_email='osms.opallios@gmail.com',
                             to=bdm_emails)
        email.content_subtype = 'html'
        email.cc = ['mathurp@opallios.com', 'girish@opallios.com', 'paradkaro@opallios.com', 'minglaniy@opallios.com',
                    'kuriwaln@opallios.com']
        email.send()
        return str(queryset.query)


def send_weeklly_recuiter_performance_report(country):
    week_start, week_end = utils.week_date_range()

    queryset = Candidates.objects.raw(
        "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, "
        "CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date FROM `osms_job_description` as j RIGHT JOIN `users_user` as u on j.created_by_id = u.id AND u.country = %s LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE j.created_at >= %s AND j.created_at <= %s ORDER BY bdm_name ) AS "
        " A LEFT JOIN (select j.id as job_id , sum(case when s.stage_name = 'Client Interview' then 1 else 0 end) as Client_Interview, sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered , sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,"
        " sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as 'Rejected_By_Team' ,sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as 'Sendout_Reject' , sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as 'Offer_Rejected' ,sum(case when s.stage_name = 'Shortlisted'"
        " then 1 else 0 end) as 'Shortlisted' , sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as 'Internal_Interview' ,sum(case when s.stage_name = 'Awaiting Feedback' then 1 else 0 end) as 'Awaiting_Feedback' , sum(case when s.stage_name = 'Placed' then 1 else 0 end) as 'Placed' ,"
        "sum(case when s.stage_name = 'Rejected By Client' then 1 else 0 end) as 'Rejected_By_Client' ,sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as 'Submission_Reject' ,sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as 'SendOut' from `osms_job_description` as j ,"
        " `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs  WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id ",
        [country, week_start, week_end])

    if queryset is not None:
        logger.debug('Recruiter Perf Table QuerySet Query formed: ' + str(queryset.query))

    userqueryset = User.objects.raw("SELECT id, email, country from users_user where role = '3' AND country = %s",
                                    [country])
    user_serializer = UserSerializer(userqueryset, many=True)
    recruiter_emails = []
    for i in range(len(user_serializer.data)):
        recruiter_emails.append(user_serializer.data[i]['email'])

    bdmqueryset = User.objects.raw(
        "SELECT id, email, country from users_user where role = '9' AND country = %s", [country])
    bdm_serializer = UserSerializer(bdmqueryset, many=True)
    bdm_emails = []
    for i in range(len(bdm_serializer.data)):
        bdm_emails.append(bdm_serializer.data[i]['email'])

    # queryset = self.filter_queryset(queryset)
    serializer = JobSummaryTableSerializer(queryset, many=True)
    # print(serializer.data['first_name'])
    array_length = len(serializer.data)
    outputs = []
    for i in range(array_length):
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
            'job_date': serializer.data[i]['job_date'].split(' ')[0],
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

    message = render_to_string('recruiter_performance_weekly_report.html', {'data': outputs})
    email = EmailMessage(subject="Weekly Jobs by BDMs: {0} to {1}".format(str(week_start).split(' ')[0],
                                                                          str(week_end).split(' ')[0]),
                         body=message, from_email='osms.opallios@gmail.com',
                         to=['mathurp@opallios.com', 'girish@opallios.com', 'paradkaro@opallios.com',
                             'minglaniy@opallios.com',
                             'kuriwaln@opallios.com'] + bdm_emails)
    email.content_subtype = 'html'

    email.cc = recruiter_emails
    email.send()

    return str(queryset.query)
