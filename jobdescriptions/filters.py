import django_filters
from django_filters import rest_framework as filters, DateFilter, DateRangeFilter
from django.db.models import Q

from jobdescriptions.models import jobModel
import logging
logger = logging.getLogger(__name__)


class JDFilter(django_filters.FilterSet):
    job_title = filters.CharFilter(method='filter_by_job_title')
    visa_type = filters.CharFilter(field_name='visa_type')
    location = filters.CharFilter(field_name='location')
    default_assignee = filters.CharFilter(field_name='default_assignee')

    start_date = DateFilter(field_name='created_at', lookup_expr='gt', )
    end_date = DateFilter(field_name='created_at', lookup_expr='lt')
    date_range = DateRangeFilter(field_name='created_at')
    # client_name = filters.CharFilter(field_name='client_name__company_name')
    client_name = filters.CharFilter(method='filter_by_client_name')
    job_description = filters.CharFilter(method='filter_by_job_description')
    key_skills = filters.CharFilter(method='filter_by_key_skills')

    visa_type = filters.CharFilter(field_name='visa_type')
    # key_skills = filters.CharFilter(field_name='key_skills')
    education_qualificaion = filters.CharFilter(field_name='education_qualificaion')
    revenue_frequency = filters.CharFilter(field_name='revenue_frequency')
    contract_type = filters.CharFilter(field_name='contract_type')

    employment_type = filters.CharFilter(field_name='employment_type')
    country = filters.CharFilter(field_name='country')

    industry_experience = filters.CharFilter(field_name='industry_experience')
    min_years_of_experience = filters.NumberFilter(field_name='min_years_of_experience')
    max_years_of_experience = filters.NumberFilter(field_name='max_years_of_experience')
    priority = filters.BooleanFilter(field_name='priority')
    min_rate = filters.NumberFilter(method='filter_by_min_rate')
    max_rate = filters.NumberFilter(method='filter_by_max_rate')
    min_salary = filters.NumberFilter(method='filter_by_min_salary')
    max_salary = filters.NumberFilter(method='filter_by_max_salary')
    projected_revenue = filters.NumberFilter(field_name='projected_revenue')

    class Meta:
        model = jobModel
        fields = {
            'projected_revenue':['lt' ,'gt']
        }

    def filter_by_job_title(self, queryset, name, value):
        queryset = queryset.filter(job_title__contains=value)
        logger.info('filter_by_job_title: ' + str(queryset.query))
        return queryset

    def filter_by_client_name(self, queryset, name, value):
        queryset = queryset.filter(Q(client_name__company_name__isnull=False) & Q(client_name__company_name__startswith=value))
        logger.info('filter_by_client_name: ' + str(queryset.query))
        return queryset

    def filter_by_job_description(self, queryset, name, value):
        queryset = queryset.filter(job_description__contains=value)
        logger.info('filter_by_job_description: ' + str(queryset.query))
        return queryset

    def filter_by_key_skills(self, queryset, name, value):
        queryset = queryset.filter(key_skills__contains=value)
        logger.info('filter_by_key_skills: ' + str(queryset.query))
        return queryset

    def filter_by_min_rate(self, queryset, name, value):
        print(value)
        if value is not None and value !='':
            queryset = queryset.filter(min_rate__gte=value)
            return queryset

    def filter_by_max_rate(self, queryset, name, value):
        if value is not None and value != '':
            queryset = queryset.filter(max_rate__lte=value)
            return queryset
        
    def filter_by_min_salary(self, queryset, name, value):
        print(value)
        if value is not None and value != '':
            queryset = queryset.filter(min_salary__gte=value)
            return queryset

    def filter_by_max_salary(self, queryset, name, value):
        if value is not None and value != '':
            queryset = queryset.filter(max_salary__lte=value)
            return queryset

    def filter_by_min_experience(self, queryset, name, value):
        print(value)
        if value is not None and value != '':
            queryset = queryset.filter(min_years_of_experience__gte=value)
            return queryset

    def filter_by_max_experience(self, queryset, name, value):
        print(value)
        if value is not None and value != '':
            queryset = queryset.filter(max_years_of_experience__lte=value)
            return queryset
