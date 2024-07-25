from celery import shared_task

# TODO Configuracao das tasks Celery

@shared_task
def teste(a, b):
    return a + b
