from candidates import views
from rest_framework import routers
from django.urls import path, include

from candidates.views import ExportCandidateModel, ImportCandidates , GetCandidatesList

router = routers.DefaultRouter()
router.register(r'candidate', views.CandidateViewSet)
router.register(r'activity', views.ActivityStatusSet)
router.register(r'submission', views.SubmissionSet)
router.register(r'placement', views.PlacementCardSet)
router.register(r'rtr', views.RTRSet)
router.register(r'emailTemplate', views.EmailTemplateSet)
router.register(r'sendMail', views.CandidateMailSet)
router.register(r'candidateStages', views.CandidateStageViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('export_candidate_model/', ExportCandidateModel.as_view(), name='Export Candidates Model'),
    path('import_candidates/', ImportCandidates.as_view(), name='Import Candidates Model'),
     path('get_all/', GetCandidatesList.as_view(), name='Get All Candidates'),

]