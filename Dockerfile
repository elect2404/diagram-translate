# Usa una imagen base de Python oficial
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requerimientos
COPY backend/requirements.txt .

# Instala dependencias de Python (PyMuPDF viene con MuPDF incluido, no necesita librerías del sistema)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido del proyecto
COPY . .

# Establece el directorio de trabajo en la carpeta del backend
WORKDIR /app/backend

# Expone el puerto
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["python", "main.py"]
