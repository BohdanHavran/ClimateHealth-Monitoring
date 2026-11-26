FROM python:3.12.14-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/matplotlib \
    HOME=/tmp
WORKDIR /app
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --no-create-home app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY --chown=10001:10001 climat.py ./
COPY --chown=10001:10001 ml_contract.py ./
COPY --chown=10001:10001 climate_health/ ./climate_health/
COPY --chown=10001:10001 infrastructure/certificates/ ./infrastructure/certificates/
COPY --chown=10001:10001 templates/ ./templates/
COPY --chown=10001:10001 static/ ./static/
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=3)" || exit 1
# A worker is single-threaded: matplotlib/fuzzy mutable state is not shared by threads.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "1", "--timeout", "30", "--access-logfile", "-", "--error-logfile", "-", "climat:app"]
