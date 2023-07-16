from os import environ
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS").split(" ")
ALLOWED_HOSTS += ['127.0.0.1', 'localhost']
INTERNAL_IPS = ['127.0.0.1', 'localhost']