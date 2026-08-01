# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/signalboxx/settings.py
# Compiled at: 2026-05-09 22:01:40
# Size of source mod 2**32: 9100 bytes
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config("SECRET_KEY", default="unsafe-dev-secret-key-change-in-prod")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=(Csv()))
INSTALLED_APPS = [
 'django.contrib.admin', 
 'django.contrib.auth', 
 'django.contrib.contenttypes', 
 'django.contrib.sessions', 
 'django.contrib.messages', 
 'django.contrib.staticfiles', 
 'rest_framework', 
 'rest_framework_simplejwt', 
 'channels', 
 'encrypted_model_fields', 
 'users', 
 'brokers', 
 'signals', 
 'execution', 
 'analytics']
MIDDLEWARE = [
 'django.middleware.security.SecurityMiddleware', 
 'django.contrib.sessions.middleware.SessionMiddleware', 
 'django.middleware.common.CommonMiddleware', 
 'django.middleware.csrf.CsrfViewMiddleware', 
 'django.contrib.auth.middleware.AuthenticationMiddleware', 
 'django.contrib.messages.middleware.MessageMiddleware', 
 'django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = "signalboxx.urls"
TEMPLATES = [
 {'BACKEND':"django.template.backends.django.DjangoTemplates", 
  'DIRS':[
   BASE_DIR / "templates"], 
  'APP_DIRS':True, 
  'OPTIONS':{"context_processors": [
                          "django.template.context_processors.debug",
                          "django.template.context_processors.request",
                          "django.contrib.auth.context_processors.auth",
                          "django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "signalboxx.wsgi.application"
ASGI_APPLICATION = "signalboxx.asgi.application"
DATABASE_URL = config("DATABASE_URL", default="")
if DATABASE_URL:
    if not DATABASE_URL.startswith("sqlite"):
        import re
        m = re.match("postgres(?:ql)?://(.+):(.+)@(.+):(\\d+)/(.+)", DATABASE_URL)
        if m:
            DATABASES = {"default": {'ENGINE':"django.db.backends.postgresql", 
                         'USER':(m.group)(1), 
                         'PASSWORD':(m.group)(2), 
                         'HOST':(m.group)(3), 
                         'PORT':(m.group)(4), 
                         'NAME':(m.group)(5)}}
    else:
        DATABASES = {"default": {'ENGINE':"django.db.backends.sqlite3",  'NAME':BASE_DIR / "db.sqlite3"}}
else:
    DATABASES = {"default": {'ENGINE':"django.db.backends.sqlite3", 
                 'NAME':BASE_DIR / "db.sqlite3"}}
AUTH_PASSWORD_VALIDATORS = [
 {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
 {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
 {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
 {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"}]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"
REST_FRAMEWORK = {'DEFAULT_AUTHENTICATION_CLASSES':('rest_framework_simplejwt.authentication.JWTAuthentication', ), 
 'DEFAULT_PERMISSION_CLASSES':('rest_framework.permissions.IsAuthenticated', )}
SIMPLE_JWT = {'ACCESS_TOKEN_LIFETIME':timedelta(hours=1), 
 'REFRESH_TOKEN_LIFETIME':timedelta(days=7), 
 'ROTATE_REFRESH_TOKENS':True, 
 'BLACKLIST_AFTER_ROTATION':False}
REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CHANNEL_LAYERS = {"default": {'BACKEND':"channels_redis.core.RedisChannelLayer", 
             'CONFIG':{"hosts": [REDIS_URL]}}}
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_BEAT_SCHEDULE = {'poll-order-fills':{'task':"execution.tasks.poll_order_fills", 
  'schedule':5.0}, 
 'sync-broker-balances':{'task':"execution.tasks.sync_broker_balances", 
  'schedule':300.0}}
SCHWAB_CLIENT_ID = config("SCHWAB_CLIENT_ID", default="")
SCHWAB_CLIENT_SECRET = config("SCHWAB_CLIENT_SECRET", default="")
SCHWAB_REDIRECT_URI = config("SCHWAB_REDIRECT_URI", default="http://localhost:8000/api/brokers/callback/schwab/")
WEBULL_DEVICE_ID = config("WEBULL_DEVICE_ID", default="")
SNAPTRADE_CLIENT_ID = config("SNAPTRADE_CLIENT_ID", default="")
SNAPTRADE_CONSUMER_KEY = config("SNAPTRADE_CONSUMER_KEY", default="")
SNAPTRADE_REDIRECT_URI = config("SNAPTRADE_REDIRECT_URI", default="http://localhost:8080/api/brokers/callback/snaptrade/")
FIELD_ENCRYPTION_KEY = config("FIELD_ENCRYPTION_KEY", default="")
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="SignalBoxx <noreply@signalboxx.io>")
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:8000")
import os as _os
_LOG_DIR = BASE_DIR / "logs"
_LOG_DIR.mkdir(exist_ok=True)
LOGGING = {'version':1, 
 'disable_existing_loggers':False, 
 'formatters':{'verbose':{'format':"{asctime} [{levelname}] {name} | {message}", 
   'style':"{", 
   'datefmt':"%Y-%m-%d %H:%M:%S"}, 
  'simple':{'format':"{asctime} [{levelname}] {message}", 
   'style':"{", 
   'datefmt':"%H:%M:%S"}}, 
 'handlers':{'console':{'class':"logging.StreamHandler", 
   'formatter':"simple"}, 
  'file_main':{'class':"logging.handlers.RotatingFileHandler", 
   'filename':str(_LOG_DIR / "signalboxx.log"), 
   'maxBytes':5242880, 
   'backupCount':5, 
   'formatter':"verbose"}, 
  'file_auth':{'class':"logging.handlers.RotatingFileHandler", 
   'filename':str(_LOG_DIR / "auth.log"), 
   'maxBytes':2097152, 
   'backupCount':3, 
   'formatter':"verbose"}, 
  'file_brokers':{'class':"logging.handlers.RotatingFileHandler", 
   'filename':str(_LOG_DIR / "brokers.log"), 
   'maxBytes':2097152, 
   'backupCount':3, 
   'formatter':"verbose"}, 
  'file_execution':{'class':"logging.handlers.RotatingFileHandler", 
   'filename':str(_LOG_DIR / "execution.log"), 
   'maxBytes':2097152, 
   'backupCount':3, 
   'formatter':"verbose"}}, 
 'loggers':{'users':{'handlers':[
    "console", "file_auth", "file_main"], 
   'level':"DEBUG", 
   'propagate':False}, 
  'signalboxx.auth':{'handlers':[
    "console", "file_auth", "file_main"], 
   'level':"DEBUG", 
   'propagate':False}, 
  'brokers':{'handlers':[
    "console", "file_brokers", "file_main"], 
   'level':"DEBUG", 
   'propagate':False}, 
  'signals':{'handlers':[
    "console", "file_main"], 
   'level':"INFO", 
   'propagate':False}, 
  'execution':{'handlers':[
    "console", "file_execution", "file_main"], 
   'level':"DEBUG", 
   'propagate':False}, 
  'analytics':{'handlers':[
    "console", "file_main"], 
   'level':"INFO", 
   'propagate':False}, 
  'django.request':{'handlers':[
    "console", "file_main"], 
   'level':"WARNING", 
   'propagate':False}}}

# okay decompiling ./signalboxx/__pycache__/settings.cpython-37.pyc
