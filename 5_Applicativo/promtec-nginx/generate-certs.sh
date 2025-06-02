#!/bin/bash
set -e

# Create certs directory if it doesn't exist
mkdir -p certs

# Generate a private key
openssl genrsa -out certs/nginx.key 2048

# Generate a Certificate Signing Request (CSR)
openssl req -new -key certs/nginx.key -out certs/nginx.csr -subj "/C=IT/ST=Italy/L=LocalCity/O=PromTec/CN=promtec.local"

# Generate a self-signed certificate (valid for 365 days)
openssl x509 -req -days 365 -in certs/nginx.csr -signkey certs/nginx.key -out certs/nginx.crt

# Set permissions
chmod 600 certs/nginx.key
chmod 644 certs/nginx.crt

echo "Self-signed SSL certificates generated successfully!"
echo "  - Private Key: certs/nginx.key"
echo "  - Certificate: certs/nginx.crt"
