###############################################################################
# WARNING
###############################################################################
# Need to create a settings_local.py file adjacent to this one with the
# following variables:
# 

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



STATICFILES_DIRS = (
   "/home/srinivas/HarvardRepo/observatory_economic_complexity/media",
)
 
LOCALE_PATHS = (
    '/home/srinivas/HarvardRepo/observatory_economic_complexity/django_files/locale',
)
 
TEMPLATE_DIRS = (
  '/home/srinivas/HarvardRepo/observatory_economic_complexity/html',

)
 
SECRET_KEY = 'my_pets_name_is_eloise'

#Image cache folder 
DATA_FILES_PATH ="/home/srinivas/HarvardRepo/observatory_economic_complexity/media/data/"

#Set image mode Option are "SVG" and "PNG"
STATIC_IMAGE_MODE = "PNG"

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



