FROM python:3.11-slim

WORKDIR /app

# Adiciona dependências de sistema
RUN apt-get update && \
    apt-get install -y gcc build-essential libpq-dev && \
    apt-get clean

COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]