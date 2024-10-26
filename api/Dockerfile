# Base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV DEBUG=true

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]