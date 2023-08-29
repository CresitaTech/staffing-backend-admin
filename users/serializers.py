import logging

from django.contrib.auth.models import Group, Permission
from rest_framework import serializers

from users.models import User, Countries, UserCountries
logger = logging.getLogger(__name__)


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"
        depth = 3


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True, allow_null=True, )

    class Meta:
        model = Group
        fields = ("id", "name", "permissions")
        depth = 2


class UserCountriesSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    country_name = serializers.CharField(max_length=200)
    user_name = serializers.CharField(max_length=200)

    class Meta:
        model = UserCountries
        fields = ["id", "country_name", "user_name"]


class CountriesSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    country_code = serializers.CharField(max_length=200)
    country_name = serializers.CharField(max_length=200)

    class Meta:
        model = Countries
        fields = ["id", "country_code", "country_name"]


class UserByRoleSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    bdm_name = serializers.CharField(max_length=200)

    class Meta:
        model = User
        fields = ["id", "bdm_name"]

class UserSerializer(serializers.ModelSerializer):
    user_permissions = PermissionSerializer(many=True, read_only=True, allow_null=True, )
    groups = GroupSerializer(many=True, read_only=True, allow_null=True, )
    # Create a custom method field
    # user_countries = serializers.SerializerMethodField('_get_user_countries')
    # user_permissions = serializers.SerializerMethodField('_get_user_permissions')
    # groups = serializers.SerializerMethodField('_get_user_groups')

    # Use this method for the custom field
    """    def _get_user_countries(self, obj):
        request = self.context.get("request")
        pk = self.context.get("pk")
        if request:
            userCountriesq = UserCountries.objects.filter(user_name=pk)
            userCountries = UserCountriesSerializer(userCountriesq, many=True)
            return userCountries.data"""

    def _get_user_permissions(self, obj):
        request = self.context.get("request")
        if request:
            PermissionQuery = Permission.objects.filter(user=request.user)
            Permissions = PermissionSerializer(PermissionQuery, many=True)
            return Permissions.data

    def _get_user_groups(self, obj):
        request = self.context.get("request")
        if request:
            Groupq = Group.objects.filter(user=request.user)
            Groups = GroupSerializer(Groupq, many=True)
            return Groups.data

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'avatar', 'date_joined', 'role',
                  'is_active', 'is_deleted', 'user_permissions', 'groups', 'country', 'send_notification',
                  'created_by', 'updated_by', 'created_at', 'updated_at') # 'user_countries',
        extra_kwargs = {'password': {'write_only': True}}
        write_only_fields = "__all__"


class UserRestrictSerializer(serializers.ModelSerializer):
    user_permissions = PermissionSerializer(many=True, read_only=True, allow_null=True, )
    groups = GroupSerializer(many=True, read_only=True, allow_null=True, )
    # user_countries = UserCountriesSerializer(many=True, read_only=True, allow_null=True, )

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'avatar',
                  'date_joined', 'role', 'is_active', 'is_deleted',
                  'user_permissions', 'groups', 'country', 'send_notification', 'updated_by') #  'user_countries',
        extra_kwargs = {'email': {'write_only': True}}
        write_only_fields = "__all__"


class AllPermissionSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    codename = serializers.CharField(max_length=200)
    app_label = serializers.CharField(max_length=200)
    model = serializers.CharField(max_length=200)

    class Meta:
        model = Permission
        fields = ["id", "codename", "app_label", "model"]


class UserPermissionSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    codename = serializers.CharField(max_length=200)
    app_label = serializers.CharField(max_length=200)
    model = serializers.CharField(max_length=200)

    class Meta:
        model = Permission
        fields = ["id", "codename", "app_label", "model"]


class GroupPermissionSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=200)
    codename = serializers.CharField(max_length=200)
    app_label = serializers.CharField(max_length=200)
    model = serializers.CharField(max_length=200)

    class Meta:
        model = Group
        fields = ["id", "codename", "app_label", "model"]

