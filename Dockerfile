FROM python:3.12-slim

WORKDIR /app
COPY . .
ENV PYTHONPATH=/app/src

CMD ["python", "-m", "concur_sae.cli", "--input", "fixtures/incoming/sample_sae.txt", "--output-dir", "out", "--db", "out/manifest.sqlite3"]
