#!/bin/bash
set -e

# set variables
ACR_NAME="privateregistry0719"
IMAGE_NAME="data-analysis-api"
TAG1="stable-1"
TAG2="stable-2"

# build docker image with both tags
echo "Building Docker image with tags $TAG1 and $TAG2..."
docker build -t "$ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG1" -t "$ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG2" .

# push both tags to Azure Container Registry
echo "Pushing Docker image with tag $TAG1..."
docker push "$ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG1"

echo "Pushing Docker image with tag $TAG2..."
docker push "$ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG2"

echo
echo "Deployment completed successfully for tags $TAG1 and $TAG2!" 