from django.contrib import admin

from parsers.models import ParserModel


@admin.register(ParserModel)
class ParserModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'job_title', 'resume', 'created_at')
    # list_filter = ('job_title')
    list_per_page = 10
    search_fields = ['job_title']