#!/bin/bash

# Exit on any error
set -e

# Set variables
PROJECT_ID="meat-ry"
REGION="us-central1"
SERVICE_NAME="personalized-reading-support"

# Build the Docker image
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME .

# Push the image to Google Container Registry
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "PROJECT_ID=$PROJECT_ID,LOCATION=$REGION"

echo "Deployment complete. Your service URL is:"
gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)'