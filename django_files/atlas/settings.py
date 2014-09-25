###############################################################################
# WARNING
###############################################################################
# Need to create a settings_local.py file adjacent to this one with the
# following variables:
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': '[DATABASE NAME]',
#         'USER': 'user_name',
#         'PASSWORD': 'super_secret_pw',
#         'HOST': '',
#         'PORT': '',
#     }
# }
#
# STATICFILES_DIRS = (
#   "/Users/[USERNAME]/Sites/env/observatory/media/",
# )
#
# LOCALE_PATHS = (
#   '/Users/[USERNAME]/Sites/env/observatory/django_files/locale',
# )
#
# TEMPLATE_DIRS = (
#   '/Users/[USERNAME]/Sites/env/observatory/html',
# )
#
# SECRET_KEY = 'my_pets_name_is_eloise'
#
# IF YOU ARE RUNNING THE SERVER LOCALLY (AND DO NOT WANT TO INSTALL REDIS):
# Set the REDIS flag to false
# Define a django dummy cache framework
#
# REDIS = False
#
# CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
#    },
#}
# HTTP_HOST = '/'
# DB_PREFIX = ''
#
# FOR VERBOSE JS OUTPUT
# DEV = False

DEBUG = True
TEMPLATE_DEBUG = DEBUG
TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en'
SITE_ID = 1
USE_I18N = True
DEFAULT_CHARSET = "utf-8"
TEMPLATE_CONTEXT_PROCESSORS = (
  "django.contrib.auth.context_processors.auth",
  "django.core.context_processors.debug",
  "django.core.context_processors.i18n",
  "django.core.context_processors.media",
  "django.core.context_processors.static",
  "django.core.context_processors.request",
  "django.contrib.messages.context_processors.messages",
  "atlas.context_processors.supported_langs",
  "atlas.context_processors.settings_view",
)
USE_L10N = True
USE_TZ = True
MEDIA_ROOT = ''
MEDIA_URL = ''
STATIC_ROOT = ''
STATIC_URL = '/media/'
STATICFILES_FINDERS = (
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder',
  'compressor.finders.CompressorFinder',
)
TEMPLATE_LOADERS = (
  'django.template.loaders.filesystem.Loader',
  'django.template.loaders.app_directories.Loader',
)

# Uncomment lines for caching support
MIDDLEWARE_CLASSES = (
#  'django.middleware.cache.UpdateCacheMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
#  'django.middleware.cache.FetchFromCacheMiddleware',
  'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'atlas.urls'
WSGI_APPLICATION = 'atlas.wsgi.application'

INSTALLED_APPS = (
  'django.contrib.sessions',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  'django.contrib.humanize',
  'django.contrib.sitemaps',
  'observatory',
  'blog',
  'compressor'
)


CACHES = {
    'default': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '127.0.0.1:6379:0',
    },
}

VERSION = '1.0.7'

CACHE_VERY_SHORT = 60*10  # 10 minutes
CACHE_SHORT = 60*60  # 1 hour
CACHE_LONG = 60*60*24  # 1 day
CACHE_VERY_LONG = 60*60*24*7  # 1 week

COMPRESS_DEBUG_TOGGLE = "no_compress"

try:
  from settings_local import *
except ImportError:
  pass
