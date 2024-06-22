import os
from celery import Celery
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notiflix.settings')

app = Celery('Notiflix')


app.config_from_object('django.conf.settings', namespace='CELERY')
app.autodiscover_tasks()


