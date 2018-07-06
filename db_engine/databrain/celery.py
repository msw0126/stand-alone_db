from __future__ import absolute_import

import os

from celery import Celery
# set the default Django settings module for the 'celery' program.

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'db_engine.settings')
# from databrain.settings import CELERY_RESULT_BACKEND, BROKER_URL
from setting import CELERY_RESULT_BACKEND, BROKER_URL

celery_app = Celery('databrain',backend=CELERY_RESULT_BACKEND, broker=BROKER_URL,include=[
    "comm_model.tasks"
])

# Using a string here means the worker will not have to
# pickle the object when using Windows.
# celery_app.config_from_object('django.conf:settings')
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
