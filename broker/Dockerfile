FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home appuser
COPY broker ./broker
COPY config.yaml ./
EXPOSE 8000
USER appuser
ENTRYPOINT ["uvicorn", "broker.main:app", "--host", "0.0.0.0", "--port", "8000"]
