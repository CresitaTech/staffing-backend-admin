from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
from rest_framework import viewsets, generics
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions, DjangoModelPermissions, AllowAny
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import viewsets, filters
from django.db import connection

from candidates.models import Candidates
from candidates.serializers import CandidateSerializer
from clients.models import clientModel
from comman_utils.GetObjectQuerySet import GetObjectQuerySet
from jobdescriptions.models import jobModel
from jobdescriptions.serializers import JobDescriptionSerializer
from reports.filters import UserFilter
from users.models import User, UserCountries, Countries
from users.permissions import IsAdminUser, IsAdminOrAnonymousUser, IsLoggedInUserOrAdmin
from users.serializers import UserSerializer, GroupSerializer, UserRestrictSerializer, AllPermissionSerializer, \
    GroupPermissionSerializer, PermissionSerializer, UserCountriesSerializer, CountriesSerializer, UserByRoleSerializer
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
# logman = WriteLog()


class LoginView(GetObjectQuerySet):
    permission_classes = ()

    def post(self, request, ):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(username=email, password=password)
        if user:
            userObj = UserSerializer(request.user)
            return Response({"token": user.auth_token.key, 'user_info': userObj})
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(GetObjectQuerySet):
    def get(self, request, format=None):
        print(request)
        logger.info('Logout: ' + str(request.user))
        request.user.auth_token.delete()
        # Token.delete(self.request)
        return Response(status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.filter(is_deleted=False)
    serializer_class = UserSerializer
    permission_classes = [DjangoModelPermissions]
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ("date_joined", "is_active", "created_at")
    search_fields = ('date_joined', 'first_name')

    def retrieve(self, request, pk):
        candObj = User.objects.get(pk=pk)
        serializeObj = UserSerializer(candObj, context={'request': request, 'pk': pk})
        # logman.crud(serializeObj)
        return Response(serializeObj.data)

def list(self, request):
    queryset = self.filter_queryset(self.get_queryset())
    first_name = self.request.query_params.get('first_name', None)
    last_name = self.request.query_params.get('last_name', None)
    
    if first_name and not last_name:
        queryset = queryset.filter(first_name__icontains=first_name)
    elif last_name and not first_name:
        queryset = queryset.filter(last_name__icontains=last_name)
    elif first_name and last_name:
        queryset = queryset.filter(first_name__icontains=first_name, last_name__icontains=last_name)
    print(queryset)
    # Move the return statements outside the if-elif block
    page = self.paginate_queryset(queryset)
    if page is not None:
        serializer = UserSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    serializer = UserSerializer(queryset, many=True)
    return Response(serializer.data)


    def create(self, request, *args, **kwargs):
        permissions = request.data.get('user_permissions')
        groups = request.data.get('groups')
        user_countries = request.data.get('user_countries')

        serializeObj = UserSerializer(data=request.data)
        if serializeObj.is_valid():
            response = serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id , role=groups[0])
            user_obj = User.objects.get(id = response.id)
            user_obj.set_password(request.data['password'])
            user_obj.save()
            if permissions is not None and len(permissions) > 0:
                for permission in permissions:
                    logger.info('User permissions: ' + str(permissions))
                    perm = Permission.objects.get(pk=permission)
                    user = User.objects.get(pk=response.id)
                    user.created_at = timezone.now()
                    user.user_permissions.add(perm)
                    user.save()

            if groups is not None and len(groups) > 0:
                logger.info('User groups: ' + str(groups))
                user = User.objects.get(pk=response.id)
                user.created_at = timezone.now()
                user.groups.add(groups[0])
                user.save()

            """            if user_countries is not None and len(user_countries) > 0:
                logger.info('User user_countries: ' + str(user_countries))
                for item in user_countries:
                    userCountries = UserCountries(country_name=Countries.objects.get(pk=item.get('id')),
                                                  user_name=User.objects.get(pk=response.id),
                                                  created_by=request.user,
                                                  updated_by=request.user)
                    userCountries.save()
                    logger.info('Success Saved: ', str(userCountries))"""

            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        logger.info('User Serializer Error: ' + str(serializeObj.data))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        user = User.objects.get(pk=pk)
        user.is_deleted = True
        user.updated_by = request.user
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        candObj = User.objects.get(pk=pk)
        serializeObj = UserRestrictSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            logger.info('User Data Updated: ' + str(serializeObj.data))
            serializeObj.save(updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        logger.info('User Update serialized error: ' + str(serializeObj.data))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        permissions = request.data.get('user_permissions')
        groups = request.data.get('groups')
        user_countries = request.data.get('user_countries')
        candObj = User.objects.get(pk=pk)
        serializeObj = UserRestrictSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id=request.user.id)
            cursor = connection.cursor()
            try:
                uid = pk.replace("-", "")
                logger.info('User ID: ' + str(uid))
                cursor.execute("DELETE FROM users_user_user_permissions WHERE user_id=%s", uid)
                cursor.commit()

                print("Rows Deleted = ", cursor.rowcount)
            except Exception as my_error:
                logger.info('User permission delete error: ' + str(my_error))

            cursor.close()

            if permissions is not None and len(permissions) > 0:
                for permission in permissions:
                    logger.info('User groups: ' + str(permission))
                    perm = Permission.objects.get(pk=permission)
                    user = User.objects.get(pk=pk)
                    user.created_at = timezone.now()
                    user.user_permissions.add(perm)
                    user.save()

            if groups is not None and len(groups) > 0:
                logger.info('User groups: ' + str(groups))
                user = User.objects.get(pk=pk)
                user.created_at = timezone.now()
                user.groups.add(groups[0])
                user.save()

            """            if user_countries is not None and len(user_countries) > 0:
                logger.info('User user_countries: ' + str(user_countries))
                pk = pk.replace("-", "")
                UserCountries.objects.filter(user_name_id=pk).delete()
                for item in user_countries:
                    logger.info('Fetching user data: ' + str(item))
                    uid = item.get('id').replace("-", "")
                    logger.info('Fetching user Country ID: ' + str(uid) + ' UserID: ' + str(pk))
                    try:
                        userCountries = UserCountries(country_name=Countries.objects.get(pk=uid),
                                                      user_name=User.objects.get(pk=pk),
                                                      created_by=request.user,
                                                      updated_by=request.user)
                        userCountries.save()
                        logger.info('Success Saved: ', str(userCountries))

                        logger.info('query: ', str(userCountries))

                    except UserCountries.DoesNotExist:
                        logger.info('Object Not found: ', str(item))
                        pass"""

            return Response(serializeObj.data, status=status.HTTP_200_OK)
        logger.info('User Update serialized error: ' + str(serializeObj.data))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    # permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk):
        candObj = Group.objects.get(pk=pk)
        serializeObj = GroupSerializer(candObj)
        return Response(serializeObj.data)

    def list(self, request):
        candidateObj = Group.objects.all()
        candidateSerializeObj = GroupSerializer(candidateObj, many=True)
        return Response(candidateSerializeObj.data)

    def create(self, request, *args, **kwargs):
        permissions = request.data.get('permissions')
        serializeObj = GroupSerializer(data=request.data)
        if serializeObj.is_valid():
            logger.info('Group Data: ' + str(serializeObj.data))
            response = serializeObj.save()
            if permissions is not None and len(permissions) > 0:
                for permission in permissions:
                    # print(permission)
                    perm = Permission.objects.get(pk=permission)
                    group = Group.objects.get(pk=response.id)
                    group.permissions.add(perm)
                    group.save()

            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        logger.info('Group Serializer Error: ' + str(serializeObj.data))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        candObj = Group.objects.get(pk=pk)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        candObj = Group.objects.get(pk=pk)
        serializeObj = GroupSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        permissions = request.data.get('permissions')
        print(permissions)

        candObj = Group.objects.get(pk=pk)
        serializeObj = GroupSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save()
            cursor = connection.cursor()
            try:
                cursor.execute("DELETE FROM auth_group_permissions WHERE group_id=%s", pk)
                cursor.commit()
                print("Rows Deleted = ", cursor.rowcount)
            except Exception as my_error:
                print(my_error)
            cursor.close()

            if permissions is not None and len(permissions) > 0:
                for permission in permissions:
                    print(permission)
                    perm = Permission.objects.get(pk=permission)
                    group = Group.objects.get(pk=pk)
                    group.permissions.add(perm)
                    group.save()

            return Response(serializeObj.data, status=status.HTTP_200_OK)
        logger.info('Group Serializer Error: ' + str(serializeObj.data))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCountriesViewSet(viewsets.ModelViewSet):
    queryset = UserCountries.objects.all()
    serializer_class = UserCountriesSerializer
    # permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk):
        candObj = UserCountries.objects.get(pk=pk)
        serializeObj = UserCountriesSerializer(candObj)
        return Response(serializeObj.data)

    def list(self, request):
        candidateObj = UserCountries.objects.all()
        candidateSerializeObj = UserCountriesSerializer(candidateObj, many=True)
        return Response(candidateSerializeObj.data)

    def create(self, request, *args, **kwargs):
        serializeObj = UserCountriesSerializer(data=request.data)
        if serializeObj.is_valid():
            logger.info('UserCountries Data: ' + str(serializeObj.data))
            serializeObj.save()
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        logger.info('UserCountries Serializer Error: ' + str(serializeObj.data))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        candObj = UserCountries.objects.get(pk=pk)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        candObj = UserCountries.objects.get(pk=pk)
        serializeObj = UserCountriesSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        candObj = UserCountries.objects.get(pk=pk)
        serializeObj = UserCountriesSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save()
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        logger.info('UserCountries Serializer Error: ' + str(serializeObj.data))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)


class CountriesViewSet(viewsets.ModelViewSet):
    queryset = Countries.objects.all()
    serializer_class = CountriesSerializer
    # permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk):
        candObj = Countries.objects.get(pk=pk)
        serializeObj = CountriesSerializer(candObj)
        return Response(serializeObj.data)

    def list(self, request):
        candidateObj = Countries.objects.all().order_by('display_level')
        candidateSerializeObj = CountriesSerializer(candidateObj, many=True)
        return Response(candidateSerializeObj.data)

    def create(self, request, *args, **kwargs):
        serializeObj = CountriesSerializer(data=request.data)
        if serializeObj.is_valid():
            logger.info('Countries Data: ' + str(serializeObj.data))
            serializeObj.save()
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        logger.info('Countries Serializer Error: ' + str(serializeObj.data))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        candObj = Countries.objects.get(pk=pk)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        candObj = Countries.objects.get(pk=pk)
        serializeObj = CountriesSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        candObj = Countries.objects.get(pk=pk)
        serializeObj = CountriesSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save()
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        logger.info('Countries Serializer Error: ' + str(serializeObj.data))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)


class PermissionViewSet(generics.ListAPIView):
    # queryset = Group.objects.raw("SELECT p.id as id, p.codename as codename, c.app_label as app_label, c.model as model FROM `auth_permission` as p, `django_content_type` as c WHERE p.content_type_id = c.id")
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class GroupPermissionViewSet(generics.ListAPIView):
    queryset = Group.objects.all()

    def get(self, request, format=None):
        print(request.user.id)
        queryset = Group.objects.raw(
            "SELECT p.id as id, p.codename as codename, c.app_label as app_label, c.model as model FROM `auth_permission` as p, `django_content_type` as c, `auth_group_permissions` as gp, `auth_group` as g WHERE p.id = gp.permission_id AND p.content_type_id = c.id and g.id = gp.group_id")
        serializer = GroupPermissionSerializer(queryset, many=True)
        # print(serializer.data)
        return Response(serializer.data)


class UserPermissionViewSet(generics.ListAPIView):
    queryset = Group.objects.raw(
        "SELECT p.id as id, p.codename as codename, c.app_label as app_label, c.model as model FROM `auth_permission` as p, `django_content_type` as c, `users_user_user_permissions` as up, `users_user` as u WHERE p.id = up.permission_id AND p.content_type_id = c.id and u.id = up.user_id")

    def get(self, request, format=None):
        # queryset = Candidates.objects.all()
        serializer = GroupPermissionSerializer(self.queryset, many=True)
        # print(serializer.data)
        return Response(serializer.data)


class WordpressCandidateViewSet(generics.ListAPIView):
    queryset = Candidates.objects.all().order_by('-id')[:10]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        #queryset = jobModel.objects.raw("SELECT * FROM osms_candidates ORDER_BY id DESC LIMIT 10")
        queryset = Candidates.objects.all().order_by('-id')[:10]
        serializer = CandidateSerializer(queryset, many=True)
        return Response(serializer.data)


class WordpressJobsViewSet(generics.ListAPIView):
    queryset = jobModel.objects.all().order_by('-id')[:10]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        # queryset = jobModel.objects.raw("SELECT * FROM osms_job_description ORDER_BY id DESC LIMIT 10")
        queryset = jobModel.objects.all().order_by('-id')[:10]
        serializer = JobDescriptionSerializer(queryset, many=True)
        return Response(serializer.data)


class BdmUsersViewSet(generics.ListAPIView):
    queryset = User.objects.all().order_by('-id')[:10]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        user_role = request.query_params.get('user_role')
        roles = [2, user_role]
        if user_role == "client":
            queryset = clientModel.objects.raw(
                "SELECT id, company_name as bdm_name FROM `osms_clients`")
        else:
            queryset = User.objects.raw(
                "SELECT id, CONCAT(first_name, ' ' , last_name) as bdm_name FROM `users_user` WHERE role IN %s AND is_active = 1",
                [roles])




        serializer = UserByRoleSerializer(queryset, many=True)
        return Response(serializer.data)