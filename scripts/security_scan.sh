#!/bin/bash
set -e

IMAGE_NAME=$1
TAG=${2:-latest}

if [ -z "$IMAGE_NAME" ]; then
    echo "Usage: $0 <image_name> [tag]"
    exit 1
fi

# Check if required tools are installed
command -v trivy >/dev/null 2>&1 || { echo "Installing Trivy..."; 
    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin; }

echo "Running security scan on $IMAGE_NAME:$TAG"

# Scan for vulnerabilities
echo "Scanning for vulnerabilities..."
trivy image --severity HIGH,CRITICAL "$IMAGE_NAME:$TAG"

# Scan for secrets
echo "Scanning for secrets..."
trivy image --security-checks secret "$IMAGE_NAME:$TAG"

# Scan Dockerfile
if [ -f "Dockerfile.prod" ]; then
    echo "Scanning Dockerfile..."
    trivy config --severity HIGH,CRITICAL Dockerfile.prod
fi

# Check for outdated packages
echo "Checking for outdated packages..."
docker run --rm "$IMAGE_NAME:$TAG" pip list --outdated

echo "Security scan complete!" 