from django.conf.urls import url

from rest_framework import routers
from django.urls import path, include

from campaigns import views
from campaigns.views import SendCampaignListMail

router = routers.DefaultRouter()
router.register(r'campaign_list', views.CampaignListController)
router.register(r'campaign', views.CampaignController)
router.register(r'campaign_email_list_data', views.CampaignEmailListData)
router.register(r'campaign_email_list_mapping_data', views.CampaignEmailListMappingData)
router.register(r'custom_fields', views.CustomFieldsViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    # path('send_weekend_bdm_email/', views.send_weekend_bdm_email, name='Send BDM Weekend email'),
    path('send_campaign_list_email/', SendCampaignListMail.as_view(), name='Campaign Email List View'),
]