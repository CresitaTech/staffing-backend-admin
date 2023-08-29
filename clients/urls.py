from clients import views
from rest_framework import routers
from django.urls import path, include

from clients.views import GenerateUUID , ExportClientModel ,ImportClientModel

router = routers.DefaultRouter()
router.register(r'client', views.ClientViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('generate_uuid/', GenerateUUID.as_view(), name='generate_uuid'),
    path('export_client_model/', ExportClientModel.as_view(), name='Export Clients Model'),
    path('import_clients/', ImportClientModel.as_view(), name='Import Clients Model'),
]