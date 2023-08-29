import django_filters
from django_filters import rest_framework as filters, DateFilter, DateRangeFilter

from candidates.models import Candidates


class CandidateFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name='created_at', lookup_expr='gt' )
    end_date = DateFilter(field_name='created_at', lookup_expr='lt')
    date_range = DateRangeFilter(field_name='created_at')
    min_rate = filters.NumberFilter(method='filter_by_min_rate')
    max_rate = filters.NumberFilter(method='filter_by_max_rate')
    min_salary = filters.NumberFilter(method='filter_by_min_salary')
    max_salary = filters.NumberFilter(method='filter_by_max_salary')
    total_experience = filters.NumberFilter(field_name='total_experience')
    total_experience_in_usa = filters.NumberFilter(field_name='total_experience_in_usa')
    skills_1 = filters.CharFilter(field_name='skills_1')
    skills_2 = filters.CharFilter(field_name='skills_2')
    job_description = filters.CharFilter(field_name='job_description__job_title')
    current_location = filters.CharFilter(field_name='current_location')
    client_name = filters.CharFilter(field_name='job_description__client_name__company_name')
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
        print(value)
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
