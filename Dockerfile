FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg gcc g++ git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir setuptools && \
    PIP_NO_BUILD_ISOLATION=false pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p uploads

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]