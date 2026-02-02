# Production Deployment and TLS/SSL Configuration

This guide explains how to deploy the Parish Database in a production environment with TLS/SSL encryption using Nginx and Let's Encrypt.

## Prerequisites

1.  A server with Docker and Docker Compose installed.
2.  A domain name pointing to your server's IP address.
3.  Ports 80 and 443 open on your server's firewall.

## Step 1: Prepare Environment Variables

Create a `.env` file based on `.env.example` and ensure the following variables are set for production:

```bash
DOMAIN_NAME=yourdomain.com
ORIGIN=https://yourdomain.com
DATABASE_URL=postgresql://postgres:secure-password@db:5432/parish_db
SECRET_KEY=your-very-long-random-secret-key
AUTH_SECRET=your-auth-js-secret
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
AUTHORIZED_EMAIL=your-admin-email@gmail.com
CORS_ORIGINS=["https://yourdomain.com"]
```

## Step 2: Bootstrap SSL Certificates

Nginx will fail to start if the certificate files specified in the configuration do not exist. Follow these steps to bootstrap the certificates:

### 1. Create a dummy Nginx configuration
Temporarily modify `nginx/templates/parish.conf.template` or create a simple `nginx/conf.d/default.conf` that only listens on port 80:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
}
```

### 2. Start Nginx and Certbot
Run:
```bash
docker-compose -f docker-compose.prod.yml up -d nginx
```

### 3. Obtain the certificate
Run the following command, replacing `yourdomain.com` and `your-email@example.com`:

```bash
docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email your-email@example.com --agree-tos --no-eff-email -d yourdomain.com
```

### 4. Download Recommended SSL Parameters
Certbot usually provides these, but you may need to create them manually if they are missing:

```bash
mkdir -p nginx/conf.d
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > nginx/conf.d/options-ssl-nginx.conf
openssl dhparam -out nginx/conf.d/ssl-dhparams.pem 2048
```

## Step 3: Start the Full Stack

Once the certificates are in place, ensure your `nginx/templates/parish.conf.template` is correctly configured (as provided in the repository) and restart the services:

```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

## Step 4: Automated Renewal

The `certbot` service in `docker-compose.prod.yml` is configured to automatically check for renewals every 12 hours. Nginx will need to be reloaded to pick up new certificates. You can add a cron job to your host machine to reload Nginx periodically:

```bash
0 0 * * * docker-compose -f /path/to/your/project/docker-compose.prod.yml exec nginx nginx -s reload
```

## Security Considerations

*   **HSTS:** The configuration includes `Strict-Transport-Security` headers.
*   **CSP:** A restrictive Content Security Policy is included to mitigate XSS.
*   **Permissions:** Ensure the `nginx/` and certificate volumes have appropriate permissions.
```
