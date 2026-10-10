FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    AI_CODING_DATA_DIR=/app/data \
    AI_CODING_LOG_DIR=/app/data/logs \
    AI_WORKSPACE_ROOT=/app/workspace

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY agent ./agent

EXPOSE 2024
CMD ["uvicorn", "agent.app:app", "--host", "0.0.0.0", "--port", "2024"]
