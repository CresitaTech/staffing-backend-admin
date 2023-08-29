from django.contrib import admin

# Register your models here.
from candidatesdocumentrepositery.models import candidatesRepositeryModel


@admin.register(candidatesRepositeryModel)
class candidatesRepositeryModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'repo_name', 'resume', 'driving_license', 'offer_letter'
                    , 'passport', 'rtr', 'salary_slip', 'candidate_name_id', 'created_at')
    list_filter = ('repo_name', 'created_at')
    list_per_page = 10
    search_fields = ['repo_name']