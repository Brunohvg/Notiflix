#!/bin/bash

# Esperar o banco de dados estar disponível (ajustar conforme necessário)
# Por exemplo, usando `wait-for-it` ou `dockerize` pode ser mais robusto
echo "Waiting for database to be ready..."
sleep 10

# Executar migrações
echo "Applying database migrations..."
python manage.py migrate

# Coletar arquivos estáticos
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Iniciar o Gunicorn
echo "Starting Gunicorn..."
exec gunicorn Notiflix.wsgi:application --bind 0.0.0.0:8000 --workers 3
