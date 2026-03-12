FROM python:3.11-slim

WORKDIR /app

# instalar dependencias del sistema necesarias para reflex
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# copiar proyecto
COPY . .

# instalar dependencias python
RUN pip install --no-cache-dir -r requirements.txt

# inicializar reflex
RUN reflex init --name comandaspro || true

# compilar frontend
RUN reflex export

EXPOSE 8080

CMD ["reflex", "run", "--env", "prod", "--backend-only", "--host", "0.0.0.0", "--port", "8080"]
