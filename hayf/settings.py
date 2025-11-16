"""
Django settings for hayf project - VERCEL PRODUCTION DEPLOYMENT
Optimized for Vercel serverless with Neon PostgreSQL & Midtrans Production
Version: Production Ready - FIXED with Hardcoded Midtrans Keys
"""

import os
from pathlib import Path
from urllib.parse import urlparse

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables (local development only)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ==============================================================================
# ENVIRONMENT DETECTION
# ==============================================================================

IS_VERCEL = os.environ.get('VERCEL') == '1' or os.environ.get('VERCEL_ENV') is not None

# ==============================================================================
# CORE SETTINGS
# ==============================================================================

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-dev-key-change-in-production')

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    '.vercel.app',
    '.now.sh',
    'localhost',
    '127.0.0.1',
]

# Add custom domain if provided
CUSTOM_DOMAIN = os.environ.get('CUSTOM_DOMAIN')
if CUSTOM_DOMAIN:
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)

# Allow all in development
if DEBUG:
    ALLOWED_HOSTS.append('*')

# ==============================================================================
# INSTALLED APPS
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

# ==============================================================================
# MIDDLEWARE
# ==============================================================================

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

# ==============================================================================
# TEMPLATES
# ==============================================================================

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
                'dashboard.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'hayf.wsgi.application'
ASGI_APPLICATION = 'hayf.asgi.application'

# ==============================================================================
# DATABASE - NEON POSTGRESQL
# ==============================================================================

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Parse connection string
    db_config = urlparse(DATABASE_URL)
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_config.path.replace('/', ''),
            'USER': db_config.username,
            'PASSWORD': db_config.password,
            'HOST': db_config.hostname,
            'PORT': db_config.port or 5432,
            'OPTIONS': {
                'sslmode': 'require',
                'connect_timeout': 10,
            },
            'CONN_MAX_AGE': 600,
            'CONN_HEALTH_CHECKS': True,
        }
    }
else:
    # Fallback to SQLite (development only)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    if IS_VERCEL:
        import logging
        logging.error('❌ DATABASE_URL not found! SQLite will lose data on redeploy!')

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
# STATIC FILES - WHITENOISE FOR VERCEL
# ==============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = []
if (BASE_DIR / 'static').exists():
    STATICFILES_DIRS.append(BASE_DIR / 'static')
if (BASE_DIR / 'dashboard' / 'static').exists():
    STATICFILES_DIRS.append(BASE_DIR / 'dashboard' / 'static')

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# WhiteNoise for production
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    WHITENOISE_MANIFEST_STRICT = False
    WHITENOISE_ALLOW_ALL_ORIGINS = True
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    WHITENOISE_AUTOREFRESH = True
    WHITENOISE_USE_FINDERS = True

# ==============================================================================
# MEDIA FILES
# ==============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

if not IS_VERCEL and not MEDIA_ROOT.exists():
    MEDIA_ROOT.mkdir(exist_ok=True)

# WARNING: Vercel has no persistent storage - use S3/Cloudinary for production

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

# Add production URLs
FRONTEND_URL = os.environ.get('FRONTEND_URL')
if FRONTEND_URL:
    CORS_ALLOWED_ORIGINS.append(FRONTEND_URL)

PRODUCTION_URL = os.environ.get('PRODUCTION_URL', 'https://web-hayf-2-f6l1.vercel.app')
if PRODUCTION_URL:
    CORS_ALLOWED_ORIGINS.append(PRODUCTION_URL)

CORS_ALLOW_ALL_ORIGINS = DEBUG
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
# SESSION & CSRF
# ==============================================================================

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://*.vercel.app',
    'https://web-hayf-2-f6l1.vercel.app',
]

if PRODUCTION_URL:
    CSRF_TRUSTED_ORIGINS.append(PRODUCTION_URL)
if CUSTOM_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f'https://{CUSTOM_DOMAIN}')

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
# MIDTRANS PAYMENT GATEWAY - 🔴 PRODUCTION CONFIGURATION 🔴
# ==============================================================================

# ⚠️ HARDCODED PRODUCTION CREDENTIALS - DO NOT CHANGE ⚠️
MIDTRANS_CLIENT_KEY = 'Mid-client-7IOSP8-yCqsvQrmc'
MIDTRANS_SERVER_KEY = 'Mid-server-d0YeZC33h0j943-0h5dqLKC5'
MIDTRANS_MERCHANT_ID = 'G267798344'
MIDTRANS_IS_PRODUCTION = True

# Production API URLs (NOT Sandbox)
MIDTRANS_API_URL = 'https://app.midtrans.com/snap/v1/transactions'
MIDTRANS_SNAP_URL = 'https://app.midtrans.com/snap/snap.js'

# Base URL for callbacks - CRITICAL FOR VERCEL
if IS_VERCEL:
    # Try to auto-detect Vercel URL
    VERCEL_URL = os.environ.get('VERCEL_URL')
    if VERCEL_URL:
        BASE_URL = f'https://{VERCEL_URL}'
    else:
        # Fallback to production URL
        BASE_URL = 'https://web-hayf-2-f6l1.vercel.app'
else:
    # Local development
    BASE_URL = 'http://localhost:8000'

# Callback URLs for Midtrans
MIDTRANS_FINISH_URL = f'{BASE_URL}/payment/finish/'
MIDTRANS_UNFINISH_URL = f'{BASE_URL}/payment/finish/'
MIDTRANS_ERROR_URL = f'{BASE_URL}/payment/finish/'
MIDTRANS_NOTIFICATION_URL = f'{BASE_URL}/payment/notification/'

# Site URL (for general use)
SITE_URL = BASE_URL

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

if EMAIL_HOST_USER:
    DEFAULT_FROM_EMAIL = f'Kopi Hayf <{EMAIL_HOST_USER}>'
    SERVER_EMAIL = EMAIL_HOST_USER
    CONTACT_EMAIL = EMAIL_HOST_USER
else:
    DEFAULT_FROM_EMAIL = 'noreply@example.com'
    SERVER_EMAIL = 'noreply@example.com'
    CONTACT_EMAIL = 'contact@example.com'

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

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'dashboard': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ==============================================================================
# SECURITY SETTINGS - PRODUCTION ONLY
# ==============================================================================

if not DEBUG:
    # HTTPS/SSL
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    
    # Cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Security headers
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # HSTS (uncomment after confirming everything works)
    # SECURE_HSTS_SECONDS = 31536000
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True

# ==============================================================================
# DEVELOPMENT INFO (local only)
# ==============================================================================

if not IS_VERCEL and DEBUG:
    db_type = DATABASES['default']['ENGINE'].split('.')[-1].upper()
    print("=" * 80)
    print("🚀 DJANGO HAYF PROJECT - DEVELOPMENT MODE")
    print("=" * 80)
    print(f"📍 Environment: LOCAL")
    print(f"🛠  DEBUG: {DEBUG}")
    print(f"💾 Database: {db_type}")
    if DATABASE_URL:
        print(f"🔗 DB Host: {urlparse(DATABASE_URL).hostname}")
    print(f"📁 Static Root: {STATIC_ROOT}")
    print("=" * 80)
    print("💳 MIDTRANS PAYMENT GATEWAY - 🔴 PRODUCTION MODE 🔴")
    print("=" * 80)
    print(f"   Client Key: {MIDTRANS_CLIENT_KEY[:15]}...{MIDTRANS_CLIENT_KEY[-4:]}")
    print(f"   Server Key: {MIDTRANS_SERVER_KEY[:15]}...{MIDTRANS_SERVER_KEY[-4:]}")
    print(f"   Merchant ID: {MIDTRANS_MERCHANT_ID}")
    print(f"   Mode: 🔴 PRODUCTION (REAL MONEY!)")
    print(f"   API URL: {MIDTRANS_API_URL}")
    print(f"   Snap URL: {MIDTRANS_SNAP_URL}")
    print("=" * 80)
    print("🌐 CALLBACK URLS")
    print("=" * 80)
    print(f"   Base URL: {BASE_URL}")
    print(f"   Finish URL: {MIDTRANS_FINISH_URL}")
    print(f"   Notification URL: {MIDTRANS_NOTIFICATION_URL}")
    print("=" * 80)
    print("⚠️  WARNING: PRODUCTION MODE ACTIVE!")
    print("⚠️  ALL TRANSACTIONS WILL BE REAL AND CHARGE ACTUAL MONEY!")
    print("=" * 80)