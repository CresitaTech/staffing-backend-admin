import logging

import django_filters
from django_filters import rest_framework as filters, DateFilter, DateRangeFilter

from candidates.models import Candidates, candidatesJobDescription
from django.db.models import Q

from candidates.serializers import CandidateJobsStagesSerializer
from jobdescriptions.models import jobModel

logger = logging.getLogger(__name__)


class CandidateFilter(django_filters.FilterSet):
    first_name = filters.CharFilter(method='filter_by_first_name')
    start_date = DateFilter(field_name='created_at', lookup_expr='gt' )
    end_date = DateFilter(field_name='created_at', lookup_expr='lt')
    date_range = DateRangeFilter(field_name='created_at')
    min_rate = filters.NumberFilter(method='filter_by_min_rate')
    max_rate = filters.NumberFilter(method='filter_by_max_rate')
    min_salary = filters.NumberFilter(method='filter_by_min_salary')
    max_salary = filters.NumberFilter(method='filter_by_max_salary')
    total_experience = filters.NumberFilter(field_name='total_experience')
    total_experience_in_usa = filters.NumberFilter(field_name='total_experience_in_usa')
    skills_1 = filters.CharFilter(method='filter_by_skills_1')
    skills_2 = filters.CharFilter(method='filter_by_skills_2')
    designation = filters.CharFilter(method='filter_by_designation')
    # job_description = filters.CharFilter(field_name='job_description__job_title')
    job_description = filters.CharFilter(method='filter_by_job_description')
    stage = filters.CharFilter(method='filter_by_stage')
    current_location = filters.CharFilter(field_name='current_location')
    country = filters.CharFilter(field_name='country')
    # client_name = filters.CharFilter(field_name='job_description__client_name__company_name')
    client_name = filters.CharFilter(method='filter_by_client_name')
    company_name = filters.CharFilter(field_name='company_name')
    qualification = filters.CharFilter(field_name='qualification')
    visa = filters.CharFilter(field_name='visa')

    class Meta:
        model = Candidates
        fields ={
            'total_experience': ['lt', 'gt'],
            'total_experience_in_usa':['lt' , 'gt']
        }

    def filter_by_min_rate(self, queryset, name, value):
        logger.info(value)
        queryset = queryset.filter(min_rate__gte=value)
        return queryset

    def filter_by_max_rate(self, queryset, name, value):
        queryset = queryset.filter(max_rate__lte=value)
        return queryset
        
    def filter_by_min_salary(self, queryset, name, value):
        print(value)
        queryset = queryset.filter(min_salary__gte=value)
        return queryset

    def filter_by_max_salary(self, queryset, name, value):
        queryset = queryset.filter(max_salary__lte=value)
        return queryset

    def filter_by_job_description(self, queryset, name, value):
        queryset = queryset.filter(job_description__job_title__contains=value)
        logger.info('filter_by_job_description: ' + str(queryset.query))
        return queryset

    def filter_by_client_name(self, queryset, name, value):
        queryset = queryset.filter(Q(job_description__client_name__company_name__isnull=False) & Q(job_description__client_name__company_name__startswith=value))
        logger.info('job_description__client_name__company_name: ' + str(queryset.query))
        return queryset

    def filter_by_skills_1(self, queryset, name, value):
        queryset = queryset.filter(skills_1__contains=value)
        logger.info('skills_1: ' + str(queryset.query))
        return queryset

    def filter_by_skills_2(self, queryset, name, value):
        queryset = queryset.filter(skills_2__contains=value)
        logger.info('skills_2: ' + str(queryset.query))
        return queryset

    def filter_by_designation(self, queryset, name, value):
        queryset = queryset.filter(designation__name__contains=value)
        logger.info('designation__name__contains: ' + str(queryset.query))
        return queryset

    def filter_by_first_name(self, queryset, name, value):
        queryset = queryset.filter(first_name__contains=value)
        logger.info('first_name: ' + str(queryset.query))
        return queryset

    def filter_by_stage(self, queryset, name, value):
        uid = str(value).replace("-", "")
        # logger.info('uid: ' + str(uid))
        querysetJS = candidatesJobDescription.objects.values('candidate_name_id').exclude(candidate_name_id__isnull=True).filter(
            stage_id=uid)
        """serializer = CandidateJobsStagesSerializer(querysetJS, many=True)
                array_length = len(serializer.data)
                candIds = []
                for i in range(array_length):
                    candIds.append(serializer.data[i]['candidate_name_id'])
                logger.info('candIds: ' + str(candIds))"""
        # queryset = Candidates.objects.filter(id__in=querysetJS)
        queryset = queryset.filter(id__in=querysetJS)
        logger.info('filter_by_stage: ' + str(queryset.query))
        return queryset
