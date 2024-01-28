"""
Django settings for wallet_api project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    '127.0.0.1',
    'posapi.bestpaygh.com'
]

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'wallet_api_app',
    'corsheaders'
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
}

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

CORS_ALLOWED_ORIGINS = [  # Replace with your allowed domain(s)
    'https://test.bestpaygh.com',
    'https://www.bestpaygh.com',
    'https://www.bestpaygh.com',
    'https://console.bestpaygh.com',
    'https://posapi.bestpaygh.com',
    'https://webhook-5n2u9.ondigitalocean.app',
    'https://webhook.bestpaygh.com',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://www.nobledatagh.com',
    'https://www.aunicetopupgh.com',
    'https://www.gh-bay.com',
    'https://www.dataforall.store',
    'https://www.bestpluggh.com',
    'https://www.ghdatahubs.com'
]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    'Accept',
    'accept-encoding',
    'Accept-Language',
    'Content-Type',
    'Authorization',
    'authorization'
    'Api-Key',
    'Api-Secret',
    'api-key',
    'api-secret',
    'x-api-key'
    'x-api-secret'
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'cache-control',
    'pragma',
]


ROOT_URLCONF = 'wallet_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'wallet_api.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': config("DATABASE_HOST"),
        'PORT': config("DATABASE_PORT"),
        'NAME': 'db',
        'USER': config("DATABASE_USERNAME"),
        'PASSWORD': config("DATABASE_PASSWORD"),
        'OPTIONS': {
            'sslmode': 'require'
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'assets/'
STATICFILES_DIRS = [BASE_DIR / 'static/']

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

FIREBASE_ADMIN_CERT = {
    "type": "service_account",
    "project_id": config('PROJECT_ID'),
    "private_key_id": config('PRIVATE_KEY_ID'),
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCYu2TBplvZSXL9\nSfcdZ90zP36rrBWDLOcUfbf2QHX08jN//QQ4Wwrzh9j3udUwoVyflUuo1oLNt0GL\nXqRaclcLt9OhvV4blz9+E1Hkd2pQ9d5agalGMvlUy1QUMmd8TvuemhglOD7oLkGx\n5eAuRytdTJtivzMQdS6yWpXpSA0EHpwcyLZjKDYfsGUe1s65mi/NNOczCg0DPZ44\nD30JgO8Ca9BPDrVbi43/v8gec/rt8YEomRq0Cza5v+UXSKHy2bk5UpkBMtXkVQe2\nHwZ67L122+wOi4IZe55npD3ZBJM/gUf3/a4oWkqC3lmDX0m2uJr6DjnSme8Jj4MY\nlpTnSGSzAgMBAAECggEAI5XJyHq/vLUpxw0EOAQ6nBWnqEz8aCc+od4Wzhe/w/Xo\nfOIRKSZBO3OD4FgabW2zPHVW/vwX1uFjMps29OHeGRtYAj+yXQBU6UWMF4yhJ0LZ\n70F1lKcMw65qJRiHVwW6B36EsKtVsNgSM2ZJYM7xMhhGve+pcKS04BZOBl/ktHgn\nIpYpBxG8kqp1ntGm2oYp849wLch4S5Yrzjq+Cc8NtBLGR4zr0YcY9pPxb2SqAs8f\ntsLLS8iQ409rBCgX9siaSZd7XJBCz76l0nhA9hkxPgKS1NXRa/ORRDX1secXDQlJ\nUjYxqQrMf+GaQVDuU7PrbLhKrvZ5z7WutdFh6od0sQKBgQDJ/WBngRlWlyvnE30H\n/4UzjdHta6ALWfuUg3CCm8DtM/XdunjHFvnE21drpwuuUuKEDxNdKLR+fIzWay7+\naVdPp6yUeOlWv328itCuexVrMHCfzTEFjetTkk6AOQqCrupcOOPBg0z96w43loLq\nWq/2s6apDy4VEdo0q0IUmCuogwKBgQDBkjh9vRX6tjHImp+m2lJWwq/kPXLfxNRN\nLgTQweCkCykQTvjfzNUBxeCT3t+ru7lIh4U4P9Iz5QqlqR9YbhR9EFt0Q9LGNEQR\nFVND++HCs2XLB1v5bS0r3OaWXvSkUQr3HzNXzBDaTu6RYh+mW+MaCqP28cq20NRK\nTYH5Oza8EQKBgD8/SHWAdheoBEY50vezKdlHugkWnymOxnjtY0hyTsm3cHA6WGE2\nr4TVjZ0W1FCEgYsKUWzlNwc4Jr1pGHDvOTim7yIabi4MjemAqfFIdx92Ln3LOWNc\n2ef0MwJxWfornRS9d4t7epszg+MiDOIm/VxJSpE7QJm2WlYNngZm05zTAoGBAL19\nQTW9kzWRg1yIGP+COxZZkUvR55EsIlPHV8lv8VNE5ZbkZ/bVkjMhHP5EMBryMqfQ\nmlX9C+3nKiwPSfMMF5xyFcTT3BJQ+czrXk5v1Yn+ighdFOkvugd1QHk1TTFJcH2H\nmoA48Mp0eE/ziV4WF1PX1LiZ68JY3Wg7RZ/QGn2xAoGATujlj05D0OrCOqoVuSun\nb7RshG/v/0YyHZdG8t1xPTYZ3ldK5BU44jogMrr0LyPqkAhGqsytGu/xpMAo1Hep\nTSE5GO/lkOHpqQGcsz7pK03o8949jj7OMVLZzV35ESuyLL1WpknfJwmnWkqE1Jxm\nKjuyaB7iUfLY21+6b6w4RN4=\n-----END PRIVATE KEY-----\n",
    "client_email": config('CLIENT_EMAIL'),
    "client_id": config('CLIENT_ID'),
    "auth_uri": config('AUTH_URI'),
    "token_uri": config('TOKEN_URI'),
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": config('client_x509_cert_url'),
    "universe_domain": "googleapis.com"
}
