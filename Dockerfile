# Usa una imagen base de Python oficial
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema necesarias para PyMuPDF
RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    mupdf \
    mupdf-tools \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos de requerimientos primero para aprovechar la caché de Docker
COPY backend/requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido del proyecto
COPY . .

# Establece el directorio de trabajo en la carpeta del backend
WORKDIR /app/backend

# Expone el puerto que usará FastAPI
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["python", "main.py"]
