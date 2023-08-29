"""staffingapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include, re_path
from rest_framework.renderers import CoreJSONRenderer
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from . import settings

from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

schema_view = get_schema_view(title='Staffing App API', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])

admin.site.site_header = "Opallios ATS Admin"
admin.site.site_title = "Opallios ATS Admin Portal"
admin.site.index_title = "Welcome to Opallios ATS Portal"


def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [
    path('', admin.site.urls),
    path('sentry-debug/', trigger_error),
    path('api/users/', include('users.urls')),
    path('docs', schema_view, name="docs"),
    path('apidocs/', include_docs_urls(title='Staffing API')),
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
    path('api/clients/', include('clients.urls')),
    path('api/candidates/', include('candidates.urls')),
    path('api/vendors/', include('vendors.urls')),
    path('api/interviewers/', include('interviewers.urls')),
    path('api/interviews/', include('interviews.urls')),
    path('api/jobdescriptions/', include('jobdescriptions.urls')),
    path('api/candidatesdocumentrepo/', include('candidatesdocumentrepositery.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/website/', include('website.urls')),
    path('api/schedulers/', include('schedulers.urls')),
    path('api/offerletters/', include('offerletters.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/campaigns/', include('campaigns.urls')),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
