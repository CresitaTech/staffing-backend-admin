from django.contrib import admin

# Register your models here.
from jobdescriptions.models import jobModel


@admin.register(jobModel)
class jobModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'end_client_name', 'job_title', 'max_salary', 'country', 'created_at')
    list_filter = ('job_title', 'created_at')
    list_per_page = 10
    search_fields = ['job_title']