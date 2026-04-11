FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg gcc g++ git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# Install CPU-only torch ecosystem FIRST before anything else
RUN pip install --no-cache-dir \
    torch==2.6.0 \
    torchaudio==2.6.0 \
    --index-url https://download.pytorch.org/whl/cpu

# Install rest but tell pip not to reinstall torch/torchaudio
RUN pip install --no-cache-dir --no-deps pyannote.audio==3.3.2
RUN pip install --no-cache-dir -r requirements.txt --no-deps

COPY . .
RUN mkdir -p uploads

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]