FROM eclipse-temurin:17-jre

WORKDIR /app

# Install Python + pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Backend deps
COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

# App files
COPY mars.jar /app/mars.jar
COPY src /app/src
COPY backend /app/backend
COPY frontend /app/frontend

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
