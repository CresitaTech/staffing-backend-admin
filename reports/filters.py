import django_filters
from django_filters import rest_framework as filters, DateFilter, DateRangeFilter

from candidates.models import Candidates
from users.models import User


class ReportFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name='created_at', lookup_expr='gt', )
    end_date = DateFilter(field_name='created_at', lookup_expr='lt')
    date_range = DateRangeFilter(field_name='created_at')

    class Meta:
        model = Candidates
        fields = []


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(lookup_expr='icontains')
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    year_joined = django_filters.NumberFilter(field_name='date_joined', lookup_expr='year', label='Year Joined')
    year_joined__gt = django_filters.NumberFilter(field_name='date_joined', lookup_expr='year__gt',
                                                  label='Year Joined Greater Than')
    year_joined__lt = django_filters.NumberFilter(field_name='date_joined', lookup_expr='year__lt',
                                                  label='Year Joined Less Than')
    date_range = django_filters.DateRangeFilter(field_name='date_joined')
    start_date = django_filters.DateFilter(field_name='date_joined', lookup_expr='lt',
                                           label='Date joined is before (mm/dd/yyyy):')
    end_date = django_filters.DateFilter(field_name='date_joined', lookup_expr='gt',
                                         label='Date joined is after (mm/dd/yyyy):')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', ]
