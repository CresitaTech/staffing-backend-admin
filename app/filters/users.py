import django_filters
from django_filters import rest_framework as filters, DateFilter, DateRangeFilter

from candidates.models import Candidates


class CandidateFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name='created_at', lookup_expr='gt', )
    end_date = DateFilter(field_name='created_at', lookup_expr='lt')
    date_range = DateRangeFilter(field_name='created_at')
    # min_salary = filters.CharFilter(method='filter_by_min_salary')
    # max_salary = filters.CharFilter(method='filter_by_max_salary')
    skills_1 = filters.CharFilter(field_name='skills_1')
    job_description = filters.CharFilter(field_name='job_description')
    current_location = filters.CharFilter(field_name='current_location')
    company_name = filters.CharFilter(field_name='company_name')
    qualification = filters.CharFilter(field_name='qualification')
    visa = filters.CharFilter(field_name='qualification')

    # Industry = filters.CharFilter(field_name='qualification')
    # Job Type = filters.CharFilter(field_name='qualification')
    # Remote = filters.CharFilter(field_name='qualification')

    class Meta:
        model = Candidates
        fields = {
            'salary_or_rate': ['lt', 'gt'],
            'total_experience': ['lt', 'gt'],
        }

    def filter_by_min_salary(self, queryset, name, value):
        print(value)
        queryset = queryset.filter(salary_or_rate__gte=value)
        return queryset

    def filter_by_max_salary(self, queryset, name, value):
        queryset = queryset.filter(salary_or_rate__lte=value)
        return queryset
