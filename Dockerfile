FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ ./src/

RUN pip install --no-cache-dir .

EXPOSE 8000

ENV DATABASE_PATH=/app/data/app.db

CMD ["uvicorn", "src.dashboard.main:app", "--host", "0.0.0.0", "--port", "8000"]
