#!/bin/bash

# Executar migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Iniciar o Gunicorn
exec gunicorn Notiflix.wsgi:application --bind 0.0.0.0:8000
