"""
WSGI config for staffingapp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import sys

# Add the path to the DLL directory to the system's PATH variable
dll_path = r"D:\ATS-OSMS-BCK-python\staffing-app-back-end-development-latest\lib"
os.environ['PATH'] = f"{dll_path};{os.environ['PATH']}"

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffingapp.settings')

application = get_wsgi_application()
