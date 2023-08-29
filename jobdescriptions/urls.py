from jobdescriptions import views
from rest_framework import routers
from django.urls import path, include
from jobdescriptions.views import ExportJdModel, ImportJobDescription, GetJobAssingmentHistory, GetUserList, \
    GetUnassignedJobsStatus, ExportJobCandidateList, ExportAssignmentHistory, GetJobCurrentStatus

router = routers.DefaultRouter()
router.register(r'jobdescription', views.JobDescriptionViewSet)
router.register(r'jobassignment', views.JobAssingmentViewSet)
router.register(r'jobsubmission', views.JobSubmissionViewSet)
router.register(r'jobdescriptionnotes', views.JobDescriptionNotesViewSet)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('export_jd_model/', ExportJdModel.as_view(), name='Export JD Model'),
    path('import_jobdescription/', ImportJobDescription.as_view(), name='Import JD Model'),
    path('get_job_assingment_history/', GetJobAssingmentHistory.as_view(), name='Get Assingment History'),
    path('get_user_dropdown_list/', GetUserList.as_view(), name='Get User List'),
    path('export_job_candidate_list/', ExportJobCandidateList.as_view(), name='Get User List'),
    path('export_assignment_history/', ExportAssignmentHistory.as_view(), name='Get User List'),
    path('get_job_current_status/', GetJobCurrentStatus.as_view(), name='get_job_current_status'),
    path('get_unassigned_jobs_status/', GetUnassignedJobsStatus.as_view(), name='Get User List')
]