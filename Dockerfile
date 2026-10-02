FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
RUN mkdir -p /app/data /app/storage
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s CMD python -m app.healthcheck || exit 1

CMD ["python", "-m", "app.main"]
