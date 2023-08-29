import os
import uuid

import dj_database_url
import environ

import sentry_sdk
from django.utils.translation import gettext_lazy
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()
READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(os.path.join(BASE_DIR, 'settings', '.env'))

# GEOIP
GEOIP_PATH = os.path.join(BASE_DIR, 'data', 'GeoLite2-Country.mmdb')
SECRET_KEY = env('SECRET_KEY', default=str(uuid.uuid4()))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)
RUN_TESTS = env.bool('RUN_TESTS', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default="")

TRULOCAL_ENVIRONMENT = env('TRULOCAL_ENVIRONMENT', default='Local')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATIC_ROOT = os.path.join(BASE_DIR, '..', "staticfiles")

STATIC_URL = '/static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
    os.path.join(BASE_DIR, '..', 'databases', 'locale'),
)

# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'databases.clientDB',
    'databases.webDB',
    'website',
    'parler'
]

if RUN_TESTS:
    INSTALLED_APPS += [
        'behave_django',
    ]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

USE_ETAGS = True

if DEBUG:
    USE_DEBUG_TOOLBAR = env.bool('USE_DEBUG_TOOLBAR', default=True)
    if USE_DEBUG_TOOLBAR:
        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE.insert(1, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = [
        'localhost',
        'localhost:9000',
        '*',
        '127.0.0.1',
        '127.0.0.1:9000',
        '127.0.0.1:8001',
        '127.0.0.1:8002',
    ]

ENABLE_SSL = env('ENABLE_SSL', default=False)
if ENABLE_SSL:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SENTRY_ENABLED = env.bool('SENTRY_ENABLED', default=False)
if SENTRY_ENABLED:
    SENTRY_DSN_JS = env('SENTRY_DSN_JS', default='')
    SENTRY_KEY = env('SENTRY_KEY', default='')
    sentry_sdk.init(
        dsn=SENTRY_KEY,
        integrations=[DjangoIntegration()],
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )

ROOT_URLCONF = 'website.urls'

LANGUAGES = (
    ('en', gettext_lazy('English')),
    ('fr', gettext_lazy('French')),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, './templates')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'website.context_processors.ww_user',
                'website.context_processors.imgix',
                'website.context_processors.analytics',
                'website.context_processors.country_code',
                'website.context_processors.on_checkout',
                'website.context_processors.sentry_dsn_js',
                'website.context_processors.languages',
                'website.context_processors.gendered_region_label',
            ],
        },
    },
]

if not DEBUG:
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        (
            'django.template.loaders.cached.Loader',
            [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        )
    ]
else:
    TEMPLATES[0]['APP_DIRS'] = True

WSGI_APPLICATION = 'website.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

PARLER_DEFAULT_LANGUAGE_CODE = LANGUAGE_CODE
PARLER_LANGUAGES = {
    None: (
        {'code': 'en'},
        {'code': 'fr'},
    ),
    'default': {
        'fallback': PARLER_DEFAULT_LANGUAGE_CODE,
        'hide_untranslated': False,   # the default; let .active_translations() return fallbacks too.
    }
}

LANGUAGES = (
    ('en', "English"),
    ('fr', 'French'),
)

DATABASE_ROUTERS = ['databases.dbRouter.DBRouter']

APPEND_SLASH = True

DB_CONN_MAX_AGE = env.int('DB_CONN_MAX_AGE', 600)

DATABASES = {
    'default': dj_database_url.parse(env('DJANGO_DATABASE_URL', default=''), conn_max_age=DB_CONN_MAX_AGE),
    'client': dj_database_url.parse(env('CLIENT_DATABASE_URL', default=''), conn_max_age=DB_CONN_MAX_AGE),
    'web': dj_database_url.parse(env('WEB_DATABASE_URL', default=''), conn_max_age=DB_CONN_MAX_AGE),
    'connect': dj_database_url.parse(env('CONNECT_DATABASE_URL', default=''), conn_max_age=DB_CONN_MAX_AGE),
}

if RUN_TESTS:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': env('REDIS_URL', default='localhost:6379'),
        }
    }

MEDIA_URL_BASE = env('MEDIA_URL_BASE', default="https://trulocal.imgix.net")
IMGIX_COMPRESSION = '?auto=compress,format&fit=clip&h=450'
IMGIX_SQUARE_COMPRESSION = '?auto=compress,format&rect=center%2Ccenter%2C678%2C678&fit=crop&w=650&h=650'

ENDPOINTS_URL = env('ENDPOINTS_URL', default='http://127.0.0.1:8001/')
URL_PREFIX = ""

AUTH_TOKEN_SECRET = env('AUTH_TOKEN_SECRET', default='hello_world')
CLIENT_ID = env('CLIENT_ID', default='phoenix')
CLIENT_SECRET = env('CLIENT_SECRET', default='Its a secret')

SEGMENT_API_KEY = {
    "WRITE_KEY": env('SEGMENT_PYTHON_WRITE_KEY', default="RqrfU4aaysdAHyo7lPaLkzIFBx32HInv"),
    "JS_WRITE_KEY": env('SEGMENT_JS_WRITE_KEY', default="RqrfU4aaysdAHyo7lPaLkzIFBx32HInv"),
    "US_JS_WRITE_KEY": env('SEGMENT_US_JS_WRITE_KEY', default="RqrfU4aaysdAHyo7lPaLkzIFBx32HInv"),
    "DISABLE_SEGMENT": env.bool("SEGMENT_DISABLED", default=True),
}

STRIPE_PUBLISHABLE_KEY = {
    "ontario": env('STRIPE_PUBLISHABLE_ONTARIO', default="pk_test_XvVeYkSXWSR5ztznOjHXRHvt"),
    "quebec": env('STRIPE_PUBLISHABLE_QUEBEC', default="pk_test_XvVeYkSXWSR5ztznOjHXRHvt"),
    "alberta": env('STRIPE_PUBLISHABLE_ALBERTA', default="pk_test_XvVeYkSXWSR5ztznOjHXRHvt"),
    "nationwide": env('STRIPE_PUBLISHABLE_NATIONWIDE', default="pk_test_XvVeYkSXWSR5ztznOjHXRHvt"),
    "bc": env('STRIPE_PUBLISHABLE_BRITISH_COLUMBIA', default="pk_test_XvVeYkSXWSR5ztznOjHXRHvt"),
    "illinois": env('STRIPE_PUBLISHABLE_ILLINOIS', default="pk_test_XvVeYkSXWSR5ztznOjHXRHvt"),
    "invalid": env('STRIPE_PUBLISHABLE_INVALID', default="pk_test_xxxxxxxxxxxxxxxxxxxxx"),
    "connect": env('STRIPE_PUBLISHABLE_CONNECT', default="pk_test_XvVeYkSXWSR5ztznOjHXRHvt"),
}

STRIPE_API_KEY = {
    "ontario": env('STRIPE_API_KEY_ONTARIO', default="sk_test_BeGx4JTUNyvjWHUujDq74eN0"),
    "quebec": env('STRIPE_API_KEY_QUEBEC', default="sk_test_BeGx4JTUNyvjWHUujDq74eN0"),
    "alberta": env('STRIPE_API_KEY_ALBERTA', default="sk_test_BeGx4JTUNyvjWHUujDq74eN0"),
    "nationwide": env('STRIPE_API_KEY_NATIONWIDE', default="sk_test_BeGx4JTUNyvjWHUujDq74eN0"),
    "bc": env('STRIPE_API_KEY_BRITISH_COLUMBIA', default="sk_test_BeGx4JTUNyvjWHUujDq74eN0"),
    "illinois": env('STRIPE_API_KEY_ILLINOIS', default="sk_test_BeGx4JTUNyvjWHUujDq74eN0"),
    "invalid": env('STRIPE_API_KEY_INVALID', default="sk_test_xxxxxxxxxxxxxxxxxxxxx"),
    "connect": env('STRIPE_API_KEY_CONNECT', default="sk_test_BeGx4JTUNyvjWHUujDq74eN0"),
}

ANALYTICS = {
    'google': {
        'analytics': env('GOOGLE_ANALYTICS', default=""),  # UA-********-*
        'tag_manager': env('GOOGLE_TAG_MANAGER', default=""),  # GTM-*******
    },
    'facebook': {'pixel': env('FACEBOOK_PIXEL', default=""),},  # string of numbers
    'pinterest': env('PINTEREST', default=""),
}

LOG_LEVEL = env('LOG_LEVEL', default='INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{asctime} {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'trulocal': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'test': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

ITERABLE_API_URL = env('ITERABLE_API_URL', default='https://api.iterable.com')
ITERABLE_API_KEY_CA = env('ITERABLE_API_KEY_CA', default="41ff78ec95dd40458fb98f6ba26db613")
ITERABLE_API_KEY_US = env('ITERABLE_API_KEY_US', default="41ff78ec95dd40458fb98f6ba26db613")
ITERABLE_SIGNUP_LIST_CA = env('ITERABLE_SIGNUP_LIST_CA', default="648277")
ITERABLE_SIGNUP_LIST_US = env('ITERABLE_SIGNUP_LIST_US', default="648278")
