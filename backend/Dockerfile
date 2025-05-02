# Usa imagem base oficial do Python
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia tudo da pasta backend pro container
COPY backend/ .

# Instala dependências
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expõe a porta usada pelo Gunicorn
EXPOSE 8000

# Comando para rodar o servidor
CMD ["gunicorn", "wsgi:application", "--bind", "0.0.0.0:8000"]