# Use an AMD64-compatible lightweight Python base
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy all source code and data files
COPY . /app

# Install dependencies and download the model once (during build)
RUN pip install --no-cache-dir -r requirements.txt && \
    python download_model.py

# Set offline flags to avoid runtime internet access
ENV TRANSFORMERS_OFFLINE=1
ENV HF_DATASETS_OFFLINE=1

# Default command to run your main script
CMD ["python", "main.py"]
