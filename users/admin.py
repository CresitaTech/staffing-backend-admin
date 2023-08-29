from django.contrib import admin

# Register your models here.
from users.models import User, UserCountries, Countries


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'email', 'role', 'is_active', 'created_at')
    list_filter = ('first_name', 'created_at')
    list_per_page = 10
    search_fields = ['first_name']


@admin.register(UserCountries)
class UserCountriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'country_name', 'user_name')
    list_per_page = 10
    search_fields = ['country_name']


@admin.register(Countries)
class CountriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'country_code', 'country_name', 'display_level')
    list_filter = ('country_code', 'country_name')
    list_per_page = 10
    search_fields = ['country_name']