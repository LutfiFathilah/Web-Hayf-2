"""
Django settings for hayf project - VERCEL PRODUCTION READY
Optimized for Vercel serverless deployment with Neon PostgreSQL
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# ENVIRONMENT DETECTION
# ==============================================================================

# Detect if running on Vercel
IS_VERCEL = os.environ.get('VERCEL') == '1' or os.environ.get('VERCEL_ENV') is not None

# ==============================================================================
# SECURITY SETTINGS
# ==============================================================================

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production-12345')

# DEBUG - Default False untuk production, True untuk development
DEBUG = os.environ.get('DEBUG', 'False' if IS_VERCEL else 'True') == 'True'

ALLOWED_HOSTS = [
    '.vercel.app',
    '.now.sh', 
    'localhost', 
    '127.0.0.1',
]

# Add specific domain if needed
if os.environ.get('ALLOWED_HOST'):
    ALLOWED_HOSTS.append(os.environ.get('ALLOWED_HOST'))

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

# # ==============================================================================
# # DATABASE CONFIGURATION - UPDATED FOR NEON POSTGRESQL
# # ==============================================================================

# # Check if DATABASE_URL is provided (for Neon PostgreSQL)
# DATABASE_URL = os.environ.get('DATABASE_URL')

# if DATABASE_URL:
#     # Production with PostgreSQL (Neon, Supabase, etc.)
#     import dj_database_url
    
#     DATABASES = {
#         'default': dj_database_url.config(
#             default=DATABASE_URL,
#             conn_max_age=600,
#             conn_health_checks=True,
#             ssl_require=True,  # Required for Neon
#         )
#     }
    
#     # Additional PostgreSQL optimizations for Vercel
#     DATABASES['default']['OPTIONS'] = {
#         'sslmode': 'require',
#         'connect_timeout': 10,
#     }
    
# elif IS_VERCEL and os.environ.get('DB_NAME'):
#     # Alternative: PostgreSQL with individual credentials
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.postgresql',
#             'NAME': os.environ.get('DB_NAME'),
#             'USER': os.environ.get('DB_USER'),
#             'PASSWORD': os.environ.get('DB_PASSWORD'),
#             'HOST': os.environ.get('DB_HOST'),
#             'PORT': os.environ.get('DB_PORT', '5432'),
#             'OPTIONS': {
#                 'sslmode': 'require',
#                 'connect_timeout': 10,
#             },
#             'CONN_MAX_AGE': 600,
#         }
#     }
    
# elif IS_VERCEL:
#     # WARNING: SQLite on Vercel - data will be lost on redeploy!
#     # This is a fallback and NOT recommended for production
#     import logging
#     logging.warning('Using SQLite on Vercel - data will be lost on redeploy!')
    
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': '/tmp/db.sqlite3',
#         }
#     }
    
# else:
#     # Local development - SQLite
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': BASE_DIR / 'db.sqlite3',
#         }
#     }

# ======================================================================
# DATABASE CONFIGURATION (PostgreSQL only)
# ======================================================================

# Add these at the top of your settings.py
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qsl

load_dotenv()

# Replace the DATABASES section of your settings.py with this
tmpPostgres = urlparse(os.getenv("DATABASE_URL"))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': tmpPostgres.path.replace('/', ''),
        'USER': tmpPostgres.username,
        'PASSWORD': tmpPostgres.password,
        'HOST': tmpPostgres.hostname,
        'PORT': 5432,
        'OPTIONS': dict(parse_qsl(tmpPostgres.query)),
    }
}

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
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Static files directories - only add if they exist
STATICFILES_DIRS = []
static_dir = BASE_DIR / 'static'
if static_dir.exists():
    STATICFILES_DIRS.append(static_dir)

dashboard_static = BASE_DIR / 'dashboard' / 'static'
if dashboard_static.exists():
    STATICFILES_DIRS.append(dashboard_static)

# Storage configuration for Django 4.2+
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ==============================================================================
# MEDIA FILES
# ==============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Create media directory if it doesn't exist
if not IS_VERCEL:
    MEDIA_ROOT.mkdir(exist_ok=True)

# WARNING: Vercel doesn't support persistent file storage
# For production, use cloud storage (AWS S3, Cloudinary, etc.)

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
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

if DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
        'rest_framework.renderers.BrowsableAPIRenderer'
    )

# ==============================================================================
# CORS CONFIGURATION
# ==============================================================================

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Add production frontend URL
if os.environ.get('FRONTEND_URL'):
    CORS_ALLOWED_ORIGINS.append(os.environ.get('FRONTEND_URL'))

# For development only
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = False  # Set to True only for testing
else:
    CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ==============================================================================
# SESSION & CSRF CONFIGURATION
# ==============================================================================

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000', 
    'http://127.0.0.1:8000',
    'https://*.vercel.app',
]

# Add specific production domain
if os.environ.get('PRODUCTION_URL'):
    CSRF_TRUSTED_ORIGINS.append(os.environ.get('PRODUCTION_URL'))

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
MIDTRANS_IS_PRODUCTION = os.environ.get('MIDTRANS_IS_PRODUCTION', 'False') == 'True'

# Midtrans URLs - adjust based on environment
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:8000')
MIDTRANS_FINISH_URL = f'{BASE_URL}/payment/finish/'
MIDTRANS_UNFINISH_URL = f'{BASE_URL}/payment/unfinish/'
MIDTRANS_ERROR_URL = f'{BASE_URL}/payment/error/'
MIDTRANS_NOTIFICATION_URL = f'{BASE_URL}/payment/notification/'

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
        'simple': {
            'format': '{levelname} {message}',
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
        'level': 'WARNING' if IS_VERCEL else 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'dashboard': {
            'handlers': ['console'],
            'level': 'INFO' if IS_VERCEL else 'DEBUG',
            'propagate': False,
        },
    },
}

# ==============================================================================
# SECURITY SETTINGS FOR PRODUCTION
# ==============================================================================

if not DEBUG and IS_VERCEL:
    # SSL/HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    
    # Cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Security Headers
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # HSTS (uncomment after testing)
    # SECURE_HSTS_SECONDS = 31536000
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True