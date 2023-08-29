from interviews import views , utils
from rest_framework import routers
from django.urls import path, include
from interviews.views import ExportInterviewsModel, CandidateInterviewsList

router = routers.DefaultRouter()
router.register(r'source', views.SourceViewSet)
router.register(r'feedback', views.FeedbackViewSet)
router.register(r'interview', views.InterviewViewSet)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('send_zoom_invite/', utils.zoom_users, name='send_zoom_invite'),
    path('zoom_users/', utils.zoom_users, name='zoom_users'),
    path('zoom_meetings/', utils.zoom_meetings, name='zoom_meetings'),
    path('zoom_meeting_create/', utils.zoom_meeting_create, name='zoom_meeting_create'),
    path('zoom_client/', utils.zoom_client, name='zoom_client'),
    path('list_zoom_meeting/', utils.list_zoom_meeting, name='list_zoom_meeting'),
    path('export_interviews_model/', ExportInterviewsModel.as_view(), name='Export Interviews Model'),
    path('candidate_interviews_list/', CandidateInterviewsList.as_view(), name='candidate_interviews_list'),
]