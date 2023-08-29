import django_filters
from django_filters import rest_framework as filters, DateFilter, DateRangeFilter

from jobdescriptions.models import jobModel


class JDFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name='created_at', lookup_expr='gt', )
    end_date = DateFilter(field_name='created_at', lookup_expr='lt')
    date_range = DateRangeFilter(field_name='created_at')
    client_name = filters.CharFilter(field_name='client_name__company_name')
    visa_type = filters.CharFilter(field_name='visa_type')
    key_skills = filters.CharFilter(field_name='key_skills')
    education_qualificaion = filters.CharFilter(field_name='education_qualificaion')
    revenue_frequency = filters.CharFilter(field_name='revenue_frequency')
    contract_type = filters.CharFilter(field_name='contract_type')
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
