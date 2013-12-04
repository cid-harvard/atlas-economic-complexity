###############################################################################
# WARNING
###############################################################################
# Need to create a settings_local.py file adjacent to this one with the
# following variables:
# 
import os.path
import django

DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'betaharvard',
         'USER': 'root',
         'PASSWORD': 'root',
         'HOST': '172.16.3.142',
         'PORT': '3306',
     }
}

#Get the absolute path of the settings_local.py file's directory
SITE_ROOT = os.path.dirname(os.path.realpath('__file__'))

#Get  Root path of the settings_local.py file's directory
ROOT_PATH = os.path.dirname(__file__)


STATICFILES_DIRS = (
   os.path.join( SITE_ROOT,'..', 'media' ),
)
 
LOCALE_PATHS = (
      os.path.join(ROOT_PATH, 'locale'),
)
 
TEMPLATE_DIRS = (
   os.path.join( SITE_ROOT,'..', 'html' ),

)
 
SECRET_KEY = 'my_pets_name_is_eloise'

#Image cache folder 
DATA_FILES_PATH = os.path.join( SITE_ROOT,'..', 'media/data' )

#Set image mode Option are "SVG" and "PNG"
STATIC_IMAGE_MODE = "SVG"

# IF YOU ARE RUNNING THE SERVER LOCALLY (AND DO NOT WANT TO INSTALL REDIS): 
# Set the REDIS flag to false
# Define a django dummy cache framework
#
REDIS = False
#
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
    }, 
}
HTTP_HOST = '/'
DB_PREFIX = ''



