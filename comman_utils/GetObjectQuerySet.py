from rest_framework.views import APIView
from users.models import User


class GetObjectQuerySet(APIView):
    queryset = User.objects.none()