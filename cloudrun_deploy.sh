#!/bin/bash
# Script para desplegar el bot a Google Cloud Run

PROJECT_ID="gonzasaas" # CAMBIA ESTO por tu Project ID de GCP
REGION="us-central1"
SERVICE_NAME="gonzasaas-bot"
REPO_NAME="gonzasaas-repo"
IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}"

echo "🔨 Construyendo la imagen con Cloud Build..."
gcloud builds submit --tag $IMAGE_URL

echo "🚀 Desplegando en Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_URL \
  --region $REGION \
  --platform managed \
  --no-allow-unauthenticated \
  --set-env-vars GCS_BUCKET_NAME=${GCS_BUCKET_NAME},SPREADSHEET_ID=${SPREADSHEET_ID},TELEGRAM_TOKEN=${TELEGRAM_TOKEN}

echo "✅ Despliegue completado."
