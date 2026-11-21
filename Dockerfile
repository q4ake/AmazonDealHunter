FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY data ./data

# The container performs one check and exits. Use a scheduler (for example
# GitHub Actions cron) to run it periodically.
CMD ["python", "-m", "src.main", "--provider", "scavio", "--input", "data/products.scavio.example.json"]
