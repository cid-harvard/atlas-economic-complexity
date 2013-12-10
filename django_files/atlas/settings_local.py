DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'OBSERVATORY_DB',
         'USER': 'root',
         'PASSWORD': '',
         'HOST': '127.0.0.1',
         'PORT': '3306',
     }
 }
 
STATICFILES_DIRS = (
   "/Users/rvuillemot/Dev/observatory_economic_complexity/media/",
 )
 
LOCALE_PATHS = (
   '/Users/rvuillemot/Dev/observatory_economic_complexity/django_files/locale',
 )
 
TEMPLATE_DIRS = (
   '/Users/rvuillemot/Dev/observatory_economic_complexity/html',
 )

STATIC_IMAGE_MODE = "SVG"

#Image cache folder 
DATA_FILES_PATH ="/Users/rvuillemot/Dev/observatory_economic_complexity/media/data"

 
SECRET_KEY = 'my_pets_name_is_eloise'
#
# IF YOU ARE RUNNING THE SERVER LOCALLY (AND DO NOT WANT TO INSTALL REDIS): 
# Set the REDIS flag to false
# Define a django dummy cache framework

REDIS = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
    }, 
}

GOOGLE_ANALYTICS = {
  'default' : {
    'ACCOUNT': 'UA-22403682-3', 
  }
}

HTTP_HOST = '/'

DB_PREFIX = 'beta_'

DEV = False