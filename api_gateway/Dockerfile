FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY services/api_gateway.py ./services/api_gateway.py
EXPOSE 8080
ENTRYPOINT ["uvicorn", "services.api_gateway:app", "--host", "0.0.0.0", "--port", "8080"]
