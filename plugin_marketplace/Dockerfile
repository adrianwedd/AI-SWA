FROM node:20-alpine AS frontend
WORKDIR /ui
COPY plugin_marketplace/web ./web
RUN cd web && npm ci && npm run build

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home appuser
COPY --from=frontend /ui/web/dist ./static
COPY services/plugin_marketplace ./services/plugin_marketplace
COPY core ./core
EXPOSE 8003
USER appuser
ENTRYPOINT ["uvicorn", "services.plugin_marketplace.service:app", "--host", "0.0.0.0", "--port", "8003"]
