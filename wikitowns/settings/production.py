from .base import *
#from whitenoise import WhiteNoise


#settings from heroku tutorial
import dj_database_url
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = ['*'] #this should change?

#STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
