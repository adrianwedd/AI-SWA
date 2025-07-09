FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home appuser
COPY services/orchestrator_api.py ./services/orchestrator_api.py
COPY core ./core
COPY ai_swa ./ai_swa
COPY config.yaml ./
EXPOSE 8002
USER appuser
ENTRYPOINT ["uvicorn", "services.orchestrator_api:app", "--host", "0.0.0.0", "--port", "8002"]
