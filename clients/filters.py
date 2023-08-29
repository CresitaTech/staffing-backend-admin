import django_filters
from django_filters import rest_framework as filters, DateFilter, DateRangeFilter
from clients.models import clientModel


class ClientFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name='created_at', lookup_expr='gt' )
    end_date = DateFilter(field_name='created_at', lookup_expr='lt')
    date_range = DateRangeFilter(field_name='created_at')
    primary_skills = filters.CharFilter(field_name='primary_skills')
    secondary_skills = filters.CharFilter(field_name='secondary_skills')
    company_name = filters.CharFilter(field_name='company_name')
    total_employee = filters.NumberFilter(field_name='total_employee')
    first_name = filters.CharFilter(field_name='first_name')
    last_name = filters.CharFilter(field_name='last_name')

    class Meta:
        model = clientModel
        fields = {
            'total_employee': ['lt', 'gt']
        }

    def filter_by_min_salary(self, queryset, name, value):
        print(value)
        queryset = queryset.filter(salary_or_rate__gte=value)
        return queryset

    def filter_by_max_salary(self, queryset, name, value):
        queryset = queryset.filter(salary_or_rate__lte=value)
        return queryset
