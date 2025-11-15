"""
Django settings for hayf project - VERCEL PRODUCTION READY
FIXED: Windows compatibility untuk development
"""

import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# SECURITY SETTINGS
# ==============================================================================

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production-12345')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    '.vercel.app',
    '.now.sh', 
    'localhost', 
    '127.0.0.1',
    '*'
]

# ==============================================================================
# APPLICATION DEFINITION
# ==============================================================================

INSTALLED_APPS = [
    'daphne',
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'dashboard.apps.DashboardConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hayf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'dashboard' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'hayf.wsgi.application'
ASGI_APPLICATION = 'hayf.asgi.application'

# ==============================================================================
# DATABASE CONFIGURATION - AUTO DETECT ENVIRONMENT
# ==============================================================================

# Detect if running on Vercel
IS_VERCEL = os.environ.get('VERCEL', False)

if IS_VERCEL:
    # Production on Vercel - use /tmp/
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/db.sqlite3',
        }
    }
else:
    # Local development (Windows/Linux/Mac) - use project folder
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ==============================================================================
# POSTGRESQL CONFIGURATION (RECOMMENDED FOR PRODUCTION)
# Uncomment dan comment out SQLite di atas saat sudah setup PostgreSQL
# ==============================================================================

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME'),
#         'USER': os.environ.get('DB_USER'),
#         'PASSWORD': os.environ.get('DB_PASSWORD'),
#         'HOST': os.environ.get('DB_HOST'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#     }
# }

# ==============================================================================
# PASSWORD VALIDATION
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================

LANGUAGE_CODE = 'id'
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# ==============================================================================

STATIC_URL = '/static/'

# Static root untuk collectstatic
if IS_VERCEL:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Static files directories
STATICFILES_DIRS = []
if os.path.exists(os.path.join(BASE_DIR, 'static')):
    STATICFILES_DIRS.append(os.path.join(BASE_DIR, 'static'))
if os.path.exists(os.path.join(BASE_DIR, 'dashboard', 'static')):
    STATICFILES_DIRS.append(os.path.join(BASE_DIR, 'dashboard', 'static'))

# Whitenoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ==============================================================================
# MEDIA FILES
# ==============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
os.makedirs(MEDIA_ROOT, exist_ok=True)

# ==============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# REST FRAMEWORK
# ==============================================================================

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# ==============================================================================
# CORS CONFIGURATION
# ==============================================================================

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

if not DEBUG:
    CORS_ALLOWED_ORIGINS += ['https://*.vercel.app']

CORS_ALLOW_CREDENTIALS = True

# ==============================================================================
# SESSION & CSRF CONFIGURATION
# ==============================================================================

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']
if not DEBUG:
    CSRF_TRUSTED_ORIGINS += ['https://*.vercel.app']

# ==============================================================================
# MESSAGES FRAMEWORK
# ==============================================================================

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# ==============================================================================
# MIDTRANS PAYMENT GATEWAY
# ==============================================================================

MIDTRANS_CLIENT_KEY = os.environ.get('MIDTRANS_CLIENT_KEY', 'Mid-client-7IOSP8-yCqsvQrmc')
MIDTRANS_SERVER_KEY = os.environ.get('MIDTRANS_SERVER_KEY', 'Mid-server-d0YeZC33h0j943-0h5dqLKC5')
MIDTRANS_MERCHANT_ID = os.environ.get('MIDTRANS_MERCHANT_ID', 'G267798344')
MIDTRANS_IS_PRODUCTION = os.environ.get('MIDTRANS_IS_PRODUCTION', 'True') == 'True'

MIDTRANS_FINISH_URL = os.environ.get('MIDTRANS_FINISH_URL', 'http://localhost:8000/payment/finish/')
MIDTRANS_UNFINISH_URL = os.environ.get('MIDTRANS_UNFINISH_URL', 'http://localhost:8000/payment/unfinish/')
MIDTRANS_ERROR_URL = os.environ.get('MIDTRANS_ERROR_URL', 'http://localhost:8000/payment/error/')
MIDTRANS_NOTIFICATION_URL = os.environ.get('MIDTRANS_NOTIFICATION_URL', 'http://localhost:8000/payment/notification/')

DEFAULT_CURRENCY = 'IDR'

# ==============================================================================
# EMAIL CONFIGURATION
# ==============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'lutfifathila4@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'yijc kxhw tred cydh')

DEFAULT_FROM_EMAIL = f'Kopi Hayf <{EMAIL_HOST_USER}>'
SERVER_EMAIL = EMAIL_HOST_USER
CONTACT_EMAIL = EMAIL_HOST_USER

# ==============================================================================
# UNFOLD ADMIN
# ==============================================================================

UNFOLD = {
    "SITE_TITLE": "Kopi Hayf Admin",
    "SITE_HEADER": "Kopi Hayf Management",
    "SITE_URL": "/",
    "ENVIRONMENT": "development" if DEBUG else "production",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Dashboard",
                "separator": False,
                "items": [
                    {"title": "Dashboard", "icon": "dashboard", "link": "/admin/"},
                ],
            },
            {
                "title": "Produk",
                "separator": True,
                "items": [
                    {"title": "Produk", "icon": "shopping_bag", "link": "/admin/dashboard/product/"},
                    {"title": "Kategori", "icon": "category", "link": "/admin/dashboard/category/"},
                ],
            },
            {
                "title": "Pesanan",
                "separator": True,
                "items": [
                    {"title": "Pesanan", "icon": "receipt", "link": "/admin/dashboard/order/"},
                    {"title": "Pelanggan", "icon": "people", "link": "/admin/dashboard/customer/"},
                ],
            },
        ],
    },
}

# ==============================================================================
# AUTHENTICATION
# ==============================================================================

LOGIN_URL = '/masuk/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ==============================================================================
# LOGGING
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'dashboard': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# ==============================================================================
# SECURITY SETTINGS FOR PRODUCTION
# ==============================================================================

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ==============================================================================
# DEVELOPMENT vs PRODUCTION INFO
# ==============================================================================

print("=" * 60)
print(f"🚀 DJANGO SETTINGS LOADED")
print(f"📍 Environment: {'VERCEL (Production)' if IS_VERCEL else 'LOCAL (Development)'}")
print(f"🐛 DEBUG Mode: {DEBUG}")
print(f"💾 Database: {DATABASES['default']['NAME']}")
print(f"📁 Static Root: {STATIC_ROOT}")
print("=" * 60)