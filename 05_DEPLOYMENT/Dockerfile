# ──────────────────────────────────────────────────────────
# Themis Court Path — Production Dockerfile
# Deploys Flask app to Google Cloud Run
# ──────────────────────────────────────────────────────────

FROM python:3.13-slim

# Install system dependencies required by PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmupdf-dev \
    libfreetype6 \
    libharfbuzz0b \
    libjpeg62-turbo \
    libopenjp2-7 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (Docker layer caching — only reinstalls if deps change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY static/ static/
COPY templates/ templates/

# Bundle the Navajo County PDF template into the image
# This file is the blank fillable court form
COPY Petition_to_Establish_Child_Support.pdf /app/templates_pdf/

# Set environment variables
ENV FLASK_ENV=production
ENV SOURCE_PDF=/app/templates_pdf/Petition_to_Establish_Child_Support.pdf
ENV PYTHONUNBUFFERED=1

# Cloud Run injects PORT — default to 8080
ENV PORT=8080

# Expose the port (documentation only — Cloud Run uses $PORT)
EXPOSE ${PORT}

# Run with gunicorn (production WSGI server)
# - 4 workers handles concurrent PDF generation
# - 300s timeout for large PDF operations
CMD exec gunicorn \
    --bind 0.0.0.0:${PORT} \
    --workers 4 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    app:app
