from interviewers import views
from rest_framework import routers
from django.urls import path, include


router = routers.DefaultRouter()
router.register(r'designation', views.DesignationViewSet)
router.register(r'timeslot', views.TimeSlotViewSet)
router.register(r'interviewer', views.InterviewerViewSet)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
]