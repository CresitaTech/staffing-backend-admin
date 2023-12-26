"""
Django settings for staffingapp project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os
import logging.config
import logging
from decouple import config


# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# Add these new lines
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'assets')
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ff%7t#-#_&=xmfhza44&%a(4n5(3m-qus$i_==#@$0&dj#!3&_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

"""ALLOWED_HOSTS = [
    'api.opallius.com',
    'https://api.opallius.com/',
    'localhost',
	'http://localhost:4200'
]"""

ALLOWED_HOSTS = ['*']

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/?verification=1'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/?verification=1'

SITE_ID = 1

ACCOUNT_USER_EMAIL_FIELD = 'email'
ACCOUNT_LOGOUT_ON_GET = True

AUTH_USER_MODEL = 'users.User'

FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760 # 10MB

REST_AUTH_SERIALIZERS = {
    "USER_DETAILS_SERIALIZER": "users.serializers.UserRegisterSerializer",
}
REST_AUTH_REGISTER_SERIALIZERS = {
    "REGISTER_SERIALIZER": "users.serializers.UserRegisterSerializer",
}

# Application definition
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    # 'DEFAULT_PAGINATION_CLASS': 'staffingapp.pagination.HeaderLimitOffsetPagination',
    'PAGE_SIZE': 1000000,
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S"
}

SWAGGER_SETTINGS = {
    'SHOW_REQUEST_HEADERS': True,
    "SUPPORTED_SUBMIT_METHOD": ['get', 'post', 'put', 'delete', ],
    'USE_SESSION_AUTH': False,
    "LOGIN_URL": "/",
    "LOGOUT_URL": "/",
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'basic',
            'description': 'Personal API Key authorization',
            'name': 'Authorization',
            'in': 'header',
        }
    },
    'APIS_SORTER': 'alpha',
    "SHOW_REQUEST_HEADERS": True,
    "VALIDATOR_URL": None,
    'api_key': 'cea4bd55bdcf8ab18cb4e9b19f7236acc241a5ac',  # An API key

}

CKEDITOR_UPLOAD_PATH = os.path.join(BASE_DIR, 'uploads')
CKEDITOR_RESTRICT_BY_USER = True

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Advanced',
        'width': 758,
        'height': 300,
        'autoParagraph': False
    },
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'candidates',
    'clients',
    'jobdescriptions',
    'interviewers',
    'interviews',
    'vendors',
    'users',
    'candidatesdocumentrepositery',
    'ckeditor',
    'ckeditor_uploader',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'corsheaders',
    'reports',
    'website',
    'schedulers',
    'django_filters',
    'celery',
    # 'django_celery_beat',
    'dbbackup',
    'drf_api_logger',
    'django_celery_results',
    'django_crontab',
    # 'elasticapm.contrib.django',
    'offerletters',
    'analytics',
    'django_rest_passwordreset',
    'campaigns',
]

"""ELASTIC_APM = {
    # Set the required service name. Allowed characters:
    # a-z, A-Z, 0-9, -, _, and space
    'SERVICE_NAME': '',
    # Use if APM Server requires a secret token
    'SECRET_TOKEN': '',
    # Set the custom APM Server URL (default: http://localhost:8200)
    'SERVER_URL': 'http://localhost:8200',
    # Set the service environment
    'ENVIRONMENT': 'production',
}"""

CRONJOBS = [
    # For test health check
    # ('*/1 * * * *', 'staffingapp.cron.heartbeat_check', ['India', True], {'delay': 4}, '>> /var/log/scheduled_job.log'),
    ('30 7 * * *', 'staffingapp.cron.database_daily_backup', '>> /var/log/scheduled_job.log'),
    # Daily report for India
    (
    '30 22 * * mon,tue,wed,thu,fri', 'staffingapp.cron.generate_daily_submission_report_for_recruiter', ['India', True],
    {'delay': 4}, '>> /var/log/scheduled_job.log'),
    ('31 22 * * mon,tue,wed,thu,fri', 'staffingapp.cron.generate_daily_job_report_for_bdm', ['India', True],
     {'delay': 4}, '>> /var/log/scheduled_job.log'),
    ('32 22 * * mon,tue,wed,thu,fri', 'staffingapp.cron.generate_daily__recruiter_summary_report', ['India', True],
     {'delay': 4}, '>> /var/log/scheduled_job.log'),

    ('30 9 * * mon,tue,wed,thu,fri,sat', 'staffingapp.cron.sendmail_last_48hours_bdm_jobs', ['India', True],
     {'delay': 4}, '>> /var/log/scheduled_job.log'),
    #('30 18 * * mon,tue,wed,thu,fri,sat', 'staffingapp.cron.generate_bdm_daily_submission_report', ['India', True],
    # {'delay': 4}, '>> /var/log/scheduled_job.log'),
    ('01 17 * * wed,fri', 'staffingapp.cron.generate_send_weekly_recruiter_submission_follow_up', ['India', True],
     {'delay': 4}, '>> /var/log/scheduled_job.log'),
    ('45 17 * * mon,tue,wed,thu,fri', 'staffingapp.cron.send_daily_bdm_jobs_summary_report', ['India', True],
     {'delay': 4}, '>> /var/log/scheduled_job.log'),

    # Daily report for US
    ('30 6 * * tue,wed,thu,fri,sat', 'staffingapp.cron.generate_daily_submission_report_for_recruiter', ['US', True],
     {'delay': 4},
     '>> /var/log/scheduled_job.log'),
    ('31 6 * * tue,wed,thu,fri,sat', 'staffingapp.cron.generate_daily_job_report_for_bdm', ['US', True], {'delay': 4},
     '>> /var/log/scheduled_job.log'),
    ('32 6 * * tue,wed,thu,fri,sat', 'staffingapp.cron.generate_daily__recruiter_summary_report', ['US', True], {'delay': 4},
     '>> /var/log/scheduled_job.log'),
    #('00 5 * * tue,wed,thu,fri,sat', 'staffingapp.cron.generate_bdm_daily_submission_report', ['US', True],
    # {'delay': 4}, '>> /var/log/scheduled_job.log'),
    ('05 17 * * wed,fri', 'staffingapp.cron.generate_send_weekly_recruiter_submission_follow_up', ['US', True],
     {'delay': 4}, '>> /var/log/scheduled_job.log'),
    ('01 3 * * mon,tue,wed,thu,fri', 'staffingapp.cron.send_daily_bdm_jobs_summary_report', ['US', True],
     {'delay': 4}, '>> /var/log/scheduled_job.log'),

    # Weekly report for India
    ('30 22 * * sat', 'staffingapp.cron.sendmail_for_weekly_recuiter_performance_report', ['India', True], {'delay': 4},
     '>> /var/log/scheduled_job.log'),
    ('31 22 * * sat', 'staffingapp.cron.sendmail_for_weekly_recruiter_submission', ['India', True], {'delay': 4},
     '>> /var/log/scheduled_job.log'),
    ('32 22 * * sat', 'staffingapp.cron.sendmail_for_weekly_bdm_jobs', ['India', True], {'delay': 4},
     '>> /var/log/scheduled_job.log'),
    ('33 22 * * sat', 'staffingapp.cron.send_weekly_bdm_jobs_summary_report', ['India', True], {'delay': 4},
     '>> /var/log/scheduled_job.log'),

    # weekly report for US
    ('30 6 * * sun', 'staffingapp.cron.sendmail_for_weekly_recuiter_performance_report', ['US', True], {'delay': 4},
     '>> /var/log/scheduled_job.log'),
    ('31 6 * * sun', 'staffingapp.cron.sendmail_for_weekly_recruiter_submission', ['US', True], {'delay': 4},
     '>> /var/log/scheduled_job.log'),
    ('31 6 * * sun', 'staffingapp.cron.sendmail_for_weekly_bdm_jobs', ['US', True], {'delay': 4},
     '>> /var/log/scheduled_job.log'),
    ('32 6 * * sun', 'staffingapp.cron.send_weekly_bdm_jobs_summary_report', ['US', True], {'delay': 4},
     '>> /var/log/scheduled_job.log'),
    # Parse call data
    ('30 9 * * mon,tue,wed,thu,fri,sat', 'staffingapp.cron.parse_recruiter_calls_data_jobs', ['India', True],
     {'delay': 4}, '>> /var/log/scheduled_job.log'),
]

CREDENTIALS_FILE = os.path.join(BASE_DIR, 'client_id.json')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'osms.opallios@gmail.com'
EMAIL_HOST_PASSWORD = 'mqxwdlgmuoganhvy'

"""EMAIL_HOST = 'smtpout.secureserver.net'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'osms@opallioslabs.com'
EMAIL_HOST_PASSWORD = 'Naresh@123$#'"""

"""EMAIL_HOST = 'express-relay.jangosmtp.net'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'nareshkhuriwal'
EMAIL_HOST_PASSWORD = 'Opallios@123$'"""

"""EMAIL_HOST = 'us1-mta1.sendclean.net'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'smtp89119064'
EMAIL_HOST_PASSWORD = 'TKQqp6ELOW'"""

SENDCLEAN_EMAIL_HOST = 'us1-mta1.sendclean.net'
SENDCLEAN_EMAIL_USE_TLS = True
SENDCLEAN_EMAIL_PORT = 465
SENDCLEAN_EMAIL_HOST_USER = 'smtp89119064'
SENDCLEAN_EMAIL_HOST_PASSWORD = 'TKQqp6ELOW'


PARSER_EMAIL = 'kuriwaln@opallios.com'
PARSER_PASSWORD = 'Oplab@4562'

EMAIL_FROM_USER = 'osms@opallios.cloud'


ZOOM_API_KEY = 'lWuC-FosTCa3njZ0oyfpNg'
ZOOM_API_SECRET = 'jns5o1B3Fjvzbb84RraYZbTgCZ0rLOFeVks0'
ZOOM_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOm51bGwsImlzcyI6ImxXdUMtRm9zVENhM25qWjBveWZwTmciLCJleHAiOjM4MDI1MDc1NjAsImlhdCI6MTU5MzUxMzUwMn0.Q-X8VKH3OZz3HlGPURQSiA8-MVtYL1hhJXpKQoVD-6E'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'drf_api_logger.middleware.api_logger_middleware.APILoggerMiddleware',
    # 'elasticapm.contrib.django.middleware.TracingMiddleware',
]

DRF_API_LOGGER_DATABASE = True  # Default to False
# DRF_LOGGER_QUEUE_MAX_SIZE = 50  # Default to 50 if not specified.
# DRF_LOGGER_INTERVAL = 10  # In Seconds, Default to 10 seconds if not specified.
DRF_API_LOGGER_EXCLUDE_KEYS = ['password', 'token', 'access', 'refresh']
DRF_API_LOGGER_SLOW_API_ABOVE = 200  # Default to None

ROOT_URLCONF = 'staffingapp.urls'
CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = [
     'http://localhost:4200',
     'https://staff.opallius.com',
     'http://164.68.100.175:4202',
     'https://staging.opallius.com',
 ]



TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'static', 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'staffingapp.wsgi.application'

DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {
    "location": os.path.join(BASE_DIR, 'backups')
}

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'OPTIONS': {'charset': 'utf8mb4',
                    "init_command": "SET foreign_key_checks = 0;"
                    },
        # 'OPTIONS': {
        #    'read_default_file': '../my.cnf',
        #    'init_command': 'SET default_storage_engine=INNODB',
        # },
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = False

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
LOGIN_URL = 'rest_framework:login'
LOGOUT_URL = 'rest_framework:logout'

GLOBAL_ROLE = {
    'ADMIN': 'ADMIN',
    'BDMMANAGER': 'BDM MANAGER',
    'RECRUITER': 'RECRUITER',
    'RECRUITERMANAGER': 'RECRUITER MANAGER',
}

ADMIN = 1
BDM_MANAGER = 9
RECRUITER_MANAGER = 2
RECRUITER = 3

ROLE_CHOICES = (
    (ADMIN, 'Admin'),
    (BDM_MANAGER, 'BDM MANAGER'),
    (RECRUITER_MANAGER, 'Recruiter Manager'),
    (RECRUITER , 'Recruiter')
)

SUBMISSION_MAIL = "recsub@opallios.com"

# Celery Configuration Options
# CELERY_TIMEZONE = "UTC"
# CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_TIMEZONE = 'America/Los_Angeles'

# CELERY_TASK_TRACK_STARTED = True
# CELERY_TASK_TIME_LIMIT = 10  # no task should run for more than 10 seconds. Heroku force kills kills after 10 seconds.
# CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379')
# CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379')
# CELERY_CACHE_BACKEND = env('REDIS_URL', default='redis://localhost:6379')

# CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
# CELERY_CACHE_BACKEND = 'redis://127.0.0.1:6379'

CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = 'django-cache'

BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ALWAYS_EAGER = False

DJANGO_EMAIL_ADMINS_BACKEND = os.environ.get(
    "DJANGO_EMAIL_ADMINS_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
LOGGING_CONFIG = None

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(name)-12s %(levelname)-8s %(message)s'
        },
        'file': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            # 'filename': '/var/log/nginx/staff.log'
             'filename': 'E:/py10-ats/staffing-app-back-end-development-latest/staff.log'
        },
        'mail_admins': {
            'level': 'ERROR',
            # 'filters': ['require_debug_false'],
            "class": "django.utils.log.AdminEmailHandler",
            "reporter_class": "django.views.debug.ExceptionReporter"
        }
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console', 'file', 'mail_admins']
        },
        'staffingapp': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            # required to avoid double logging with root logger
            'propagate': False,
        },
        'django.request': {
            'level': 'INFO',
            'handlers': ['console', 'file', 'mail_admins']
        }
    }
}

# logging.config.dictConfig(LOGGING)
