from django.conf.urls import url

from rest_framework import routers
from django.urls import path, include

from schedulers import views
from schedulers.views import ImportCampaignData

router = routers.DefaultRouter()
router.register(r'import_campaign_data', views.ImportCampaignData)
router.register(r'send_clean_data', views.sendCleanWebhook)
router.register(r'recruiter_daily_calls', views.tataCallsWebhook)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('store_send_clean_data', views.sendCleanWebhookPost, name='store_send_clean_data'),
    path('jobs', views.jobs),
    # path('import_campaign_data/', ImportCampaignData.as_view(), name='Import Campaign Model'),
    path('jobs/(?P<pk>[0-9]+)$', views.jobs_detail),
    # path('send_weekend_bdm_email/', views.send_weekend_bdm_email, name='Send BDM Weekend email'),
    path('download_resume_by_candidate/', views.download_resume_by_candidate, name='download_resume_by_candidate'),
    path('parse_recruiter_calls_data/', views.parse_recruiter_calls_data, name='parse_recruiter_calls_data'),

]