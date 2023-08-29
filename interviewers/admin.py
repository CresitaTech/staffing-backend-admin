from django.contrib import admin

# Register your models here.
from interviewers.models import designationModel, timeslotsModel


@admin.register(designationModel)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('name', 'remark', 'created_at')
    list_filter = ('name', 'created_at')
    list_per_page = 10
    search_fields = ['name']


@admin.register(timeslotsModel)
class TimeSlotsAdmin(admin.ModelAdmin):
    list_display = ('time_slot', 'remarks' , 'created_at')
    list_filter = ('time_slot', 'created_at')
    list_per_page = 10
    search_fields = ['time_slot']
