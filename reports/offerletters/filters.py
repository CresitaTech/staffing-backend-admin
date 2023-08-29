import django_filters
from django_filters import rest_framework as filters, DateFilter, DateRangeFilter

from offerletters.models import OfferLettersModel


class OfferLettersFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name='created_at', lookup_expr='gt' )
    end_date = DateFilter(field_name='created_at', lookup_expr='lt')
    date_range = DateRangeFilter(field_name='created_at')
    years_of_exp = filters.NumberFilter(field_name='years_of_exp')

    class Meta:
        model = OfferLettersModel
        fields = {
            'years_of_exp': ['lt', 'gt']
        }

