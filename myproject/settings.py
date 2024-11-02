from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-ok%0087ccz^@ycm*f16&1-y8qlg5q(ly&bks&7kl8%hc50em*k'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required for django-allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
      'myapp',
]

AUTH_USER_MODEL = 'myapp.CustomUser'

# settings.py

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Add allauth middleware here
    'allauth.account.middleware.AccountMiddleware',
]

# Optionally, you may also need to add the SocialAccount adapter
SOCIALACCOUNT_ADAPTER = 'myapp.adapter.CustomSocialAccountAdapter'


ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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



WSGI_APPLICATION = 'myproject.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'myapp/static'),
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Google OAuth2 configuration for django-allauth
# settings.py

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': '66646889617-kvfp7pale03nr9rrsca8ttr9dng138lr.apps.googleusercontent.com',
            'secret': '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',
            'key': ''
        }
    }
}
SITE_ID = 1

# Redirect URLs after login and logout
LOGIN_REDIRECT_URL = 'http://127.0.0.1:8000/'
LOGOUT_REDIRECT_URL = '/'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
    }
}
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
PAYPAL_CLIENT_ID = 'Aej9PcLUiHnguBA-Y_TCOoLiVwuAEoxMBnF12UR4LXrpMwyK0dQRENJ-mPnXAYgmwuY6YqBbQz6kBZxu'
PAYPAL_CLIENT_SECRET = 'EJbrbMlxdVmrakRsiQJos203fomFZUR5UhZQgYITTGAFw9sTQFYzwT6vT688glny7oU_rSWzLXf9AJqt'
PAYPAL_MODE = 'sandbox'

RAZORPAY_KEY_ID = 'rzp_test_zBIsMuxyHLhyB1'
RAZORPAY_SECRET_KEY = 'kvkanMgfPxVmc4S3FyL1bOkO'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # For Gmail
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'aswathymj2002@gmail.com'
EMAIL_HOST_PASSWORD = 'pctn ytaf jybt tuar'
DEFAULT_FROM_EMAIL = 'aswathymj2002@gmail.com'
APPEND_SLASH = False
