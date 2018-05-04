import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pinger.settings')

amqp_host = settings.AMQP_HOST
amqp_user = settings.AMQP_USER
amqp_pass = settings.AMQP_PASS

app = Celery(
    'pinger',
    broker='amqp://' + amqp_user + ':' + amqp_pass + '@' + amqp_host + ':5672')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
