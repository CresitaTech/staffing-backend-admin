from .base import *

ALLOWED_HOSTS = ["*"]

BROWSERSTACK_URL = env('BROWSERSTACK_URL', default='')
