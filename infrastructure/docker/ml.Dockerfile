# Packaging for the current honest model_unavailable boundary; not a trained predictor.
FROM python:3.12.14-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements-ml.txt ./
RUN python -m pip install --no-cache-dir -r requirements-ml.txt && useradd --uid 10001 app
COPY ml_contract.py ./
COPY ml_service/ ./ml_service/
USER 10001
EXPOSE 8001
CMD ["python", "-m", "uvicorn", "ml_service.app:app", "--host", "0.0.0.0", "--port", "8001"]
