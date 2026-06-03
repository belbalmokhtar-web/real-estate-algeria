import os
from pathlib import Path

# بناء المسار الأساسي
BASE_DIR = Path(__file__).resolve().parent.parent

# ========== الأمان ==========
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-replace-in-production-xyz123')
DEBUG = False
ALLOWED_HOSTS = ['belbalmokhtar-web.pythonanywhere.com', 'www.belbalmokhtar-web.pythonanywhere.com']

# ========== التطبيقات المثبتة ==========
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # مكتبات خارجية
    'crispy_forms',
    'crispy_bootstrap5',
    # تطبيقات المشروع
    'accounts',
    'properties',
    'rewards',
    'reports',
]

# ========== الوسائط ==========
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ========== تكوين URL والقالب ==========
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                # Context processors الخاصة بالمشروع
                'properties.context_processors.site_context',
                # 'properties.context_processors.user_context',  # أضفها عند إنشائها
                # 'properties.context_processors.notification_context',  # أضفها عند إنشائها
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ========== قاعدة البيانات ==========
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/belbalmokhtar-web/real-estate-algeria/db.sqlite3',
    }
}

# للإنتاج: PostgreSQL (ملاحظ محذوف)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME', 'real_estate'),
#         'USER': os.environ.get('DB_USER', 'postgres'),
#         'PASSWORD': os.environ.get('DB_PASSWORD', ''),
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#     }
# }

# ========== التحقق من كلمات المرور ==========
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========== اللغة والوقت ==========
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Africa/Algiers'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / 'locale']

# ========== إعدادات المصادقة ==========
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ========== البريد الإلكتروني ==========
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# إعدادات البريد الإلكتروني للإنتاج (ملاحظة محذوفة)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# ========== الملفات الثابتة والوسائط ==========
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = '/home/belbalmokhtar-web/real-estate-algeria/staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/belbalmokhtar-web/real-estate-algeria/media'

# ========== الإعدادات الافتراضية ==========
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========== Crispy Forms ==========
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ========== إعدادات الجلسة ==========
SESSION_COOKIE_AGE = 86400 * 30  # 30 يوم
SESSION_SAVE_EVERY_REQUEST = True

# ========== حد رفع الملفات ==========
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# ========== إعدادات الأمان للإنتاج ==========
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000  # 1 سنة
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_PRELOAD = True

# ========== إعدادات التطبيق المخصصة ==========
SITE_NAME = 'عقاري'
SITE_NAME_FULL = 'عقاري — منصة العقارات الجزائرية'
PROPERTIES_PER_PAGE = 12
FEATURED_PROPERTIES_COUNT = 6

# الحد الأقصى للصور لكل عقار
MAX_PROPERTY_IMAGES = 10

# إعدادات المكافآت
REWARDS_POINTS_PER_REFERRAL = 50
REWARDS_MINIMUM_POINTS_REDEMPTION = 100

# ========== التسجيل والسجلات ==========
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
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
            'formatter': 'verbose' if DEBUG else 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG' if DEBUG else 'INFO',
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
    },
}

# إضافة تسجيل الملف في وضع الإنتاج
if not DEBUG:
    import os

    LOG_DIR = BASE_DIR / 'logs'
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    LOGGING['handlers']['file'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': LOG_DIR / 'django.log',
        'maxBytes': 1024 * 1024 * 5,  # 5 MB
        'backupCount': 5,
        'formatter': 'verbose',
    }
    LOGGING['loggers']['django']['handlers'].append('file')
    LOGGING['loggers']['django.request']['handlers'] = ['file']
