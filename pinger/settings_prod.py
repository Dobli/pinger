from .settings import *

ALLOWED_HOSTS = [os.environ.get('HOSTNAME', '*')]

DEBUG = os.environ.get('DEBUG', 'False') == "True"
AMQP_HOST = os.environ.get('AMQP_HOST', 'mq')
AMQP_USER = os.environ.get('AMQP_USER', 'pinger')
AMQP_PASS = os.environ.get('AMQP_PASS', 'pingerpass')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'pinger'),
        'USER': os.environ.get('DB_USER', 'pinger'),
        'PASSWORD': os.environ.get('DB_PASS', 'pinger'),
        'HOST': os.environ.get('DB_SERVICE', 'db'),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}
