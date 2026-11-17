# =============================================
# Python Configuration
# =============================================
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ==========================================
# Install system audio dependencies
# ==========================================
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    portaudio19-dev \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


# ==========================================
# Install environment dependencies
# ==========================================
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools==68.2.2 wheel && \
    pip install --no-cache-dir Cython "numpy==1.23.5" && \
    pip install --no-cache-dir --no-build-isolation madmom==0.16.1 && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]