from candidatesdocumentrepositery import views
from rest_framework import routers
from django.urls import path, include
from candidatesdocumentrepositery.views import GetRepoList

router = routers.DefaultRouter()
router.register(r'candidatesrepo', views.CandidatesDocumentRepoSet)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('get_repo/', GetRepoList.as_view(), name='Get Repo List'),
]