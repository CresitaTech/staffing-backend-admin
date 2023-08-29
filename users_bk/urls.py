"""staffingapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from users import views
from users.authentication import CustomAuthToken
from users.views import LoginView, LogoutView, PermissionViewSet, GroupPermissionViewSet, UserPermissionViewSet, \
    WordpressCandidateViewSet, WordpressJobsViewSet

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'user_countries', views.UserCountriesViewSet)
router.register(r'countries', views.CountriesViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    # path("login/", LoginView.as_view(), name="login"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('login/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('get_permission/', PermissionViewSet.as_view(), name='Permission List'),
    path('get_group_permission/', GroupPermissionViewSet.as_view(), name='Group Permission List'),
    path('get_user_permission/', UserPermissionViewSet.as_view(), name='User Permission List'),
    path('get_candidates/', WordpressCandidateViewSet.as_view(), name='Candidates List'),
    path('get_jobs/', WordpressJobsViewSet.as_view(), name='Jobs List'),
]