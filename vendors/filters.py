import django_filters
from django_filters import rest_framework as filters, DateFilter, DateRangeFilter

from vendors.models import vendorModel


class VendorFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name='created_at', lookup_expr='gt')
    end_date = DateFilter(field_name='created_at', lookup_expr='lt')
    date_range = DateRangeFilter(field_name='created_at')
    specialised_in = filters.CharFilter(field_name='specialised_in')
    contact_person_first_name = filters.CharFilter(field_name='contact_person_first_name')
    contact_person_last_name = filters.CharFilter(field_name='contact_person_last_name')
    company_name = filters.CharFilter(field_name='company_name')

    class Meta:
        model = vendorModel
        fields = {
        }

    def filter_by_min_salary(self, queryset, name, value):
        print(value)
        queryset = queryset.filter(salary_or_rate__gte=value)
        return queryset

    def filter_by_max_salary(self, queryset, name, value):
        queryset = queryset.filter(salary_or_rate__lte=value)
        return queryset
