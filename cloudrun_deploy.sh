#!/bin/bash
# Script para desplegar el bot a Google Cloud Run

PROJECT_ID="gonzasaas" 
REGION="us-central1"
SERVICE_NAME="gonzasaas-bot"
REPO_NAME="gonzasaas-repo"
IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}"

# Cargar variables locales temporalmente si existe .env (solo para leer los tokens y GCS bucket)
if [ -f .env ]; then
  export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
fi

echo "🚀 Asegurando que el repositorio de Artifact Registry exista..."
gcloud artifacts repositories create $REPO_NAME --repository-format=docker --location=$REGION --description="Docker repository for GonzaSaaS Bot" || true

echo "🚀 Construyendo la imagen con Cloud Build..."
gcloud builds submit --tag $IMAGE_URL

echo "🚀 Desplegando fase 1 en Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_URL \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GCS_BUCKET_NAME=${GCS_BUCKET_NAME},SPREADSHEET_ID=${SPREADSHEET_ID},TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}

echo "🔗 Obteniendo la URL del servicio..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo "🚀 Configurando el Webhook y redesplegando (Fase 2)..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_URL \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GCS_BUCKET_NAME=${GCS_BUCKET_NAME},SPREADSHEET_ID=${SPREADSHEET_ID},TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN},WEBHOOK_URL=${SERVICE_URL}

echo "✅ Despliegue completado con éxito. URL: $SERVICE_URL"
