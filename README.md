# GONZATARIO - Bot de Inventario de Melaminas

Un bot interactivo de Telegram para gestionar el inventario de retazos de melamina de GonzaSaaS. Permite a los operarios registrar nuevas piezas (medidas, grosor, color, veta, foto) mediante un sistema de menú de botones fácil de usar, y darlas de baja cuando son usadas.

## Arquitectura

- **Frontend:** Bot de Telegram (`python-telegram-bot`)
- **Backend:** Python 3.12
- **Base de Datos:** Google Sheets (vía `gspread`)
- **Almacenamiento de Fotos:** Google Cloud Storage

## Instalación Local

1. Clonar el repositorio y crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/Scripts/activate # o venv/bin/activate en Linux
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configurar variables de entorno (`.env`):
   ```
   TELEGRAM_TOKEN=tu_token_de_telegram
   SPREADSHEET_ID=id_de_tu_google_sheet
   GCS_BUCKET_NAME=nombre_de_tu_bucket
   ```

4. Colocar el archivo `credentials.json` de Google Cloud en la raíz del proyecto.

5. Ejecutar:
   ```bash
   python src/main.py
   ```

## Pruebas (Tests)

El proyecto incluye tests unitarios para verificar el comportamiento sin afectar la producción.
```bash
pytest tests/ -v
```

## Despliegue en Google Cloud Run

El proyecto incluye soporte para ser empaquetado en Docker y desplegado en Google Cloud Run.

1. Asegúrate de tener instalado `gcloud` CLI y haber iniciado sesión (`gcloud auth login`).
2. Edita el script `cloudrun_deploy.sh` con tu `PROJECT_ID` y ejecuta:
   ```bash
   ./cloudrun_deploy.sh
   ```
*(Nota: Para Cloud Run en modo webhook, se necesitará un pequeño servidor HTTP. Actualmente corre en modo polling).*
