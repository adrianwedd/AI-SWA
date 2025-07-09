FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home appuser
COPY worker/main.py ./
COPY config.yaml ./
USER appuser
ENTRYPOINT ["python", "main.py"]
