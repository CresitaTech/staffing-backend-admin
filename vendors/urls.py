from vendors import views
from rest_framework import routers
from django.urls import path, include
from vendors.views import ExportVendorModel, ImportVendorModel, GetEmailConfig, SendVendorListMail, GetVendorListData, \
    get_vendor_fields ,VendorBulkDeleteView

router = routers.DefaultRouter()
router.register(r'vendor', views.VendorViewSet)
router.register(r'emailTemplate', views.EmailTemplateViewSet)
router.register(r'emailConfiguration', views.EmailConfigurationSet)
router.register(r'list', views.VendorListSet)
router.register(r'list_data', views.GetVendorListData)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('export_vendors_model/', ExportVendorModel.as_view(), name='Export Vendors Model'),
    path('import_vendors/', ImportVendorModel.as_view(), name='Import Vendors Model'),
    path('get_config_obj/', GetEmailConfig.as_view(), name='Email Config model'),
    path('send_vendor_list_email/', SendVendorListMail.as_view(), name='Vendor Email List View'),
    path('add_mail_event/', views.add_mail_event, name='create Mail Events'),
    path('get_vendor_fields/', views.get_vendor_fields, name='Get Vendor Fields'),
    path('vendor_bulk_delete/' ,VendorBulkDeleteView.as_view() , name='Vendor Bulk Delete')
]