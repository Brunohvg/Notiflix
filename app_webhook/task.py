from celery import shared_task

@shared_task
def minha_tarefa(parametro):
    print(f"Executando tarefa com o parâmetro: {parametro}")

# Chame a tarefa
minha_tarefa.delay("Isso é um teste")