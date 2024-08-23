#!/bin/bash

# Executar migrações
python manage.py migrate

# Iniciar o Gunicorn
exec gunicorn Notiflix.wsgi:application --bind 0.0.0.0:8000