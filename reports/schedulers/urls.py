from django.conf.urls import url

from rest_framework import routers
from django.urls import path, include

from schedulers import views

router = routers.DefaultRouter()
# router.register(r'candidates_summary_report', views.CandidateSummaryReportViewSet )
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # path('', include(router.urls)),
    path('', views.index, name='View Name'),
    path('jobs', views.jobs),
    path('jobs/(?P<pk>[0-9]+)$', views.jobs_detail),
    # path('send_weekend_bdm_email/', views.send_weekend_bdm_email, name='Send BDM Weekend email'),
]