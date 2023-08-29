from django.conf.urls import url

from rest_framework import routers
from django.urls import path, include

from analytics import views

router = routers.DefaultRouter()
router.register(r'best_match_candidates', views.RecommendedCandidatesViewSet)
router.register(r'recommended_candidates', views.RecommendedCandidatesViewSet)
router.register(r'recommended_jobs', views.RecommendedJobsViewSet)

# router.register(r'candidates_summary_report', views.CandidateSummaryReportViewSet )
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
]