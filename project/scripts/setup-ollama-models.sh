#!/bin/bash
# Script to set up Ollama models in Docker container
#
# This script downloads and validates Ollama models in a Docker container.
# It checks if the container is running, downloads the model, and validates
# that the model is available.
#
# Usage:
#     ./setup-ollama-models.sh [model_name] [container_name]
#
# Examples:
#     ./setup-ollama-models.sh llama2:13b
#     ./setup-ollama-models.sh llama2:7b airflow-ollama

set -e

MODEL=${1:-"llama2:13b"}
CONTAINER=${2:-"airflow-ollama"}

echo "Setting up Ollama model: $MODEL in container: $CONTAINER"

# Check if container is running
if ! docker ps | grep -q "$CONTAINER"; then
    echo "Error: Container $CONTAINER is not running"
    echo "Please start the container first or specify a different container name"
    exit 1
fi

# Download model
echo "Downloading model: $MODEL"
if ! docker exec "$CONTAINER" ollama pull "$MODEL"; then
    echo "Error: Failed to download model $MODEL"
    exit 1
fi

# Validate model
echo "Validating model: $MODEL"
if ! docker exec "$CONTAINER" ollama list | grep -q "$MODEL"; then
    echo "Error: Model $MODEL not found after download"
    exit 1
fi

echo "Model $MODEL set up successfully"

