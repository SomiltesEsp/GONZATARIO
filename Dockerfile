# Usar una imagen oficial de Python ligera
FROM python:3.12-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de requerimientos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código fuente al contenedor
COPY src/ ./src/

# Exponer el puerto por si Cloud Run necesita escuchar en HTTP (aunque Telegram hace polling, Cloud Run requiere un servidor o usar el workaround)
# NOTA: Para Cloud Run tradicional, el contenedor debe escuchar peticiones HTTP.
# Si usamos Webhooks, necesitaremos un pequeño servidor Flask/FastAPI. 
# Si usamos Polling, Cloud Run gen2 permite tareas en background (si la CPU siempre está asignada).
# Por ahora, dejaremos el comando que inicia el bot en modo polling.

CMD ["python", "src/main.py"]
