FROM python:3.12.3
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Criar um usuário não root
RUN useradd -ms /bin/sh appuser
USER appuser

# Copiar e instalar dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código do projeto
COPY . .

# Expor a porta 8000 no contêiner
EXPOSE 8000

# Copiar o script de entrada e garantir permissões
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Usar o script de entrada para iniciar a aplicação
ENTRYPOINT ["/entrypoint.sh"]
