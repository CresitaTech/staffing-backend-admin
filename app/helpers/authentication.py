from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from users.models import User
from users.serializers import UserSerializer
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class CustomAuthToken(ObtainAuthToken):
    ADMIN = 1
    MANAGER = 2
    EMPLOYEE = 3

    ROLE_CHOICES = {
        ADMIN: 'Admin',
        MANAGER: 'Manager',
        EMPLOYEE: 'Employee'
    }

    def post(self, request, *args, **kwargs):
        logger.info('Loign Details: ' + str(request.data))
        serializer = self.serializer_class(data=request.data,

        context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        candObj = User.objects.get(pk=user.id)
        serializeObj = UserSerializer(candObj)
        groups = dict(serializeObj.data)
        userGroupDict = None
        userGroup = None
        if len(groups['groups']) > 0:
            userGroupDict = dict(groups['groups'][0])
        if userGroupDict is not None:
            userGroup = userGroupDict['name']
        print(userGroup)
        logger.info('userGroup Data: %s' % userGroup)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'roles': userGroup
        }, status.HTTP_200_OK)