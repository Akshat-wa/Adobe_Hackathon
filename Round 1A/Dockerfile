FROM --platform=linux/amd64 python:3.10-slim

WORKDIR /app

COPY process_pdfs.py .
COPY requirements.txt .
COPY schema/ schema/

RUN pip install --no-cache-dir -r requirements.txt

VOLUME ["/app/input", "/app/output"]

CMD ["python", "process_pdfs.py"]
