from django.contrib import admin

# Register your models here.
from offerletters.models import OfferLettersModel


@admin.register(OfferLettersModel)
class OfferLettersModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'candidate_name', 'years_of_exp', 'contact_no', 'current_location', 'created_at')
    list_filter = ('candidate_name', 'created_at')
    list_per_page = 10
    search_fields = ['candidate_name']
