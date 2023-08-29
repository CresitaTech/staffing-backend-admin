from django.contrib import admin

from candidates.models import Candidates, candidateStageModel, candidateResumesModel


@admin.register(Candidates)
class CandidatesAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'company_name', 'primary_email', 'created_at')
    list_filter = ('first_name', 'created_at')
    list_per_page = 10
    search_fields = ['first_name']


@admin.register(candidateStageModel)
class candidateStageModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'stage_name', 'role', 'type', 'created_at')
    list_filter = ('stage_name', 'created_at')
    list_per_page = 10
    search_fields = ['stage_name']


@admin.register(candidateResumesModel)
class candidateResumesModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'job_title', 'candidate_resume_data', 'notes', 'created_at')
    list_filter = ('job_title', 'created_at')
    list_per_page = 10
    search_fields = ['job_title']

