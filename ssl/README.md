This folder is optional and only used when running the Nginx reverse proxy (docker-compose profile: production).

Place your TLS certificate and key files here and update paths in nginx.conf:
- /etc/nginx/ssl/cert.pem
- /etc/nginx/ssl/key.pem

Example self-signed cert generation (PowerShell):

# NOTE: For local testing only; use a proper CA-issued certificate in production.
# New-SelfSignedCertificate commands require admin privileges.

