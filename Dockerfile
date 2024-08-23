FROM python:3.12.3
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Usar um script de entrada para inicializar a aplicação
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]