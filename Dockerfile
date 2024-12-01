FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV SERVICE_TYPE=api
ENV SMTP_USER="parthibahazra@gmail.com"
ENV SMTP_PASSWORD=""

CMD if [ "$SERVICE_TYPE" = "api" ]; then uvicorn notification_service:app --host 0.0.0.0 --port 8000; \
    else python tasks.py; fi
