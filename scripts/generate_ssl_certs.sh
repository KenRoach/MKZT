#!/bin/bash
set -e

# Configuration
DOMAIN=${1:-"localhost"}
DAYS=${2:-365}
OUTPUT_DIR=${3:-"./certs"}
COUNTRY=${4:-"US"}
STATE=${5:-"California"}
LOCALITY=${6:-"San Francisco"}
ORGANIZATION=${7:-"Your Organization"}
ORGANIZATIONAL_UNIT=${8:-"IT Department"}
COMMON_NAME=${9:-"${DOMAIN}"}

# Create output directory if it doesn't exist
mkdir -p "${OUTPUT_DIR}"

# Generate private key
openssl genrsa -out "${OUTPUT_DIR}/server.key" 2048

# Generate CSR
openssl req -new -key "${OUTPUT_DIR}/server.key" -out "${OUTPUT_DIR}/server.csr" \
  -subj "/C=${COUNTRY}/ST=${STATE}/L=${LOCALITY}/O=${ORGANIZATION}/OU=${ORGANIZATIONAL_UNIT}/CN=${COMMON_NAME}"

# Generate self-signed certificate
openssl x509 -req -days "${DAYS}" \
  -in "${OUTPUT_DIR}/server.csr" \
  -signkey "${OUTPUT_DIR}/server.key" \
  -out "${OUTPUT_DIR}/server.crt"

# Set proper permissions
chmod 600 "${OUTPUT_DIR}/server.key"
chmod 644 "${OUTPUT_DIR}/server.crt"

# Clean up CSR
rm "${OUTPUT_DIR}/server.csr"

echo "SSL certificates generated successfully:"
echo "  Private key: ${OUTPUT_DIR}/server.key"
echo "  Certificate: ${OUTPUT_DIR}/server.crt"
echo "  Valid for: ${DAYS} days"
echo "  Domain: ${DOMAIN}"

# For production, you should use a proper CA-signed certificate
echo ""
echo "NOTE: For production environments, you should use a proper CA-signed certificate"
echo "      from a trusted certificate authority like Let's Encrypt." 