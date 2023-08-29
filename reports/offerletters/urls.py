from rest_framework import routers
from django.urls import path, include

from offerletters import views

router = routers.DefaultRouter()
router.register(r'offerletter', views.OfferLetters)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('show_offer_letter_email/', views.showOfferMail, name='SHow Offer Letter email'),

]