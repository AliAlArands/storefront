from .common import *

DEBUG = True

SECRET_KEY = 'django-insecure-^-mm2z9+md4r-sec10u0hk6wk1*-1@*hp*^#=)^4z$c(2!2byu'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'storefront',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': '321alidar'
    }
}