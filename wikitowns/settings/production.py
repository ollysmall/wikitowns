from .base import *
#from whitenoise import WhiteNoise

# settings from heroku tutorial
import dj_database_url
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# force use of SSL
SECURE_SSL_REDIRECT = True

EMAIL_USE_SSL = True

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True

ALLOWED_HOSTS = ['.noobhub.io']

ADMINS = [('Oliver', 'oliver@rotherfields.co.uk')]

# AWS S3 settings
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_S3_REGION = 'us-east-2'  # had to configure manually through aws cli
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

MEDIA_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
