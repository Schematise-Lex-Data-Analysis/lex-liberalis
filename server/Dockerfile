FROM python:3.11-slim-bookworm

# -------- Environment --------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# -------- System dependencies --------
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -------- Working directory --------
WORKDIR /app

# -------- Upgrade pip tooling --------
RUN pip install --upgrade pip setuptools wheel

# -------- Install Python dependencies --------
COPY requirements.txt .
RUN pip install -r requirements.txt

# -------- Copy application code --------
COPY . .

# -------- Expose port --------
EXPOSE 8000

# -------- Run Flask app via Gunicorn --------
CMD ["gunicorn", "-b", "0.0.0.0:8000", "--timeout", "120", "server:app"]
