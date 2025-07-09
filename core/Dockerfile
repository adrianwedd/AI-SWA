FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home appuser
COPY core ./core
COPY config.yaml ./
COPY tasks.yml ./
USER appuser
ENTRYPOINT ["python", "-m", "core.cli", "run", "--memory", "state.json"]
