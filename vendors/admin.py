from django.contrib import admin

# Register your models here.
from vendors.models import vendorModel


@admin.register(vendorModel)
class vendorModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact_person_first_name', 'designation', 'company_name', 'primary_email', 'created_at')
    list_filter = ('company_name', 'created_at')
    list_per_page = 10
    search_fields = ['contact_person_first_name']