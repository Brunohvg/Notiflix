# Dockerfile
FROM python:3.12.3
ENV PYTHONUNBUFFERED 1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Expor a porta 8000 para o Django
EXPOSE 8000

# Entrypoint para executar as migrações e iniciar o servidor
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
