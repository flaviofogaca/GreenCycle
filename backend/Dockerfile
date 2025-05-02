# Usa imagem base oficial do Python
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala dependências
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expõe a porta que o app vai rodar
EXPOSE 8000

# Comando de execução
CMD ["gunicorn", "--chdir", "backend", "wsgi:application", "--bind", "0.0.0.0:8000"]
