from django.contrib import admin

# Register your models here.
from clients.models import clientModel


@admin.register(clientModel)
class clientModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'company_name', 'primary_email', 'created_at')
    list_filter = ('first_name', 'created_at')
    list_per_page = 10
    search_fields = ['first_name']