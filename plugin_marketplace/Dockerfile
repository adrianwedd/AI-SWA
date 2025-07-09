FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY services/plugin_marketplace ./services/plugin_marketplace
COPY core ./core
EXPOSE 8003
ENTRYPOINT ["uvicorn", "services.plugin_marketplace.service:app", "--host", "0.0.0.0", "--port", "8003"]
