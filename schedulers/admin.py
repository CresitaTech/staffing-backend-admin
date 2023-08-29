from django.contrib import admin

# Register your models here.
from django.utils.log import AdminEmailHandler

from schedulers.models import AgentCallsDataModel
from schedulers.tasks import report_error_task


@admin.register(AgentCallsDataModel)
class AgentCallsDataModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'call_to_number', 'caller_id_number', 'answer_agent_number', 'direction', 'start_stamp')
    list_filter = ('call_to_number', 'caller_id_number', 'answer_agent_number', 'direction')
    list_per_page = 10
    search_fields = ['call_to_number', 'caller_id_number', 'answer_agent_number', 'direction']
