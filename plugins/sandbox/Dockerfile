FROM python:3.12-slim

# Create non-root user
RUN useradd -m sandbox

# Install project dependencies
COPY requirements.lock /tmp/requirements.lock
RUN pip install --no-cache-dir -r /tmp/requirements.lock && rm /tmp/requirements.lock

WORKDIR /app
USER sandbox
ENTRYPOINT ["pytest"]
