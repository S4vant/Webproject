from pathlib import Path
import os
import requests
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

def load_env(env_path = '.env'):
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=',1)
                os.environ[key] = value
                if key == 'SITE_URL':
                    print(f"Loaded SITE_URL from .env: {value}")

load_env()
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
def get_external_ip():
    try:
        ip = requests.get('https://api.ipify.org', timeout=2).text
        return ip
    except Exception as e:
        print(f"[ERROR] Не удалось получить внешний IP: {e}")
        return "127.0.0.1"  # безопасное значение по умолчанию

IP_ADDRESS = get_external_ip()
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

SERVER_URL= 'https://' + IP_ADDRESS + ':8000'
SITE_URL = os.getenv('SITE_URL')
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if DEBUG == 'TRUE':
    print("DEBUG = ", os.getenv("DEBUG"))
    print("Server_URL =", SERVER_URL)
print(f"Final SITE_URL value: {SITE_URL}")

ALLOWED_HOSTS = [
    'qlm.ddns.net',
    'www.qlm.ddns.net',
    'localhost',
    '127.0.0.1',
    '185.224.9.57',
]
#"localhost", "127.0.0.1", "0.0.0.0","127.0.0.1:8080","api.ipify.org", IP_ADDRESS,
CSRF_TRUSTED_ORIGINS = [ 'https://'+SITE_URL,"http://qlm.ddns.net"]
AUTH_USER_MODEL = 'application.CustomUser'
# Application definition
CORS_ALLOWED_ORIGINS = [ 'https://'+SITE_URL,"http://qlm.ddns.net"]
INSTALLED_APPS = [
    'corsheaders',
    'application',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'middleware.pols.RequestTimeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    

]

ROOT_URLCONF = 'qrcodesatsite.urls'
# 
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'application/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.static',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
            ],
        },
    },
]
WSGI_APPLICATION = 'qrcodesatsite.wsgi.application'
# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    # {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    # {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]



# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'


# Настройки для смены пароля
PASSWORD_CHANGE_REDIRECT_URL = 'password_change_done'
PASSWORD_RESET_REDIRECT_URL = 'password_reset_done'

# Static files (CSS, JavaScript, Images)


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'amedia'  



STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
