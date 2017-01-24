from .base import *

#settings from heroku tutorial
import dj_database_url
DATABASES['default'] = dj_database_url.config()

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = ['*'] #this should change?


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
#STATICFILES_DIRS = (
#    os.path.join(PROJECT_ROOT, 'static'),
#)


STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
