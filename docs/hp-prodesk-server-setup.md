# HP ProDesk 400 G3 — Parish Server Deployment Guide

> **Goal**: Set up the HP ProDesk 400 G3 as a self-hosted server at home, deploy the parish management app (SvelteKit + FastAPI + PostgreSQL + Nginx), expose it via Cloudflare Tunnel, enable remote SSH via Tailscale, then physically move the device to the office where it "just works" on plug-in.

---

## Phase 1: Install Ubuntu Server

### 1.1 Create bootable USB

```bash
# On your dev machine (WSL or Linux)
# Download Ubuntu Server 24.04 LTS ISO from https://ubuntu.com/download/server
# Flash to USB with:
sudo dd if=ubuntu-24.04-live-server-amd64.iso of=/dev/sdX bs=4M status=progress
# Or use Rufus/Balena Etcher on Windows
```

### 1.2 Install Ubuntu on the ProDesk

1. Plug USB into the ProDesk, power on, press **F9** for boot menu
2. Select the USB drive
3. Choose **Ubuntu Server (minimized)** install
4. During install:
   - Set hostname: `parish-server` (or whatever you prefer)
   - Create your user account (e.g. `tauriq`)
   - **Enable OpenSSH server** when prompted
   - Skip snaps — we'll install Docker manually
5. Remove USB, reboot

### 1.3 Post-install basics

```bash
# Login and update everything
sudo apt update && sudo apt upgrade -y

# Install essentials
sudo apt install -y curl git ufw htop net-tools

# Set timezone
sudo timedatectl set-timezone Pacific/Auckland
```

---

## Phase 2: Install Docker & Docker Compose

```bash
# Add Docker's official GPG key and repo
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to the docker group (log out/in after)
sudo usermod -aG docker $USER

# Verify
docker --version
docker compose version
```

---

## Phase 3: Deploy the Application

### 3.1 Clone the project

```bash
mkdir -p ~/apps
cd ~/apps

git clone https://github.com/Tauriqbarron/parish-database.git parish-app
cd parish-app
```

### 3.2 Create your environment file

```bash
cp .env.example .env
nano .env
```

Fill in all required values:

```bash
# Database (point to the Docker service name "db")
DATABASE_URL=postgresql://parish_user:STRONG_PASSWORD_HERE@db:5432/parish_db
POSTGRES_USER=parish_user
POSTGRES_PASSWORD=STRONG_PASSWORD_HERE
POSTGRES_DB=parish_db

# Security
SECRET_KEY=<generate with: openssl rand -base64 32>

# Google OAuth (create credentials at https://console.cloud.google.com)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Single-user authorization (only this email can access the app)
AUTHORIZED_EMAIL=your-email@gmail.com

# Auth.js secret (generate with: openssl rand -base64 32)
AUTH_SECRET=<generate with: openssl rand -base64 32>

# Production URLs (replace yourdomain.com with your actual domain)
AUTH_URL=https://yourdomain.com
ORIGIN=https://yourdomain.com
FRONTEND_URL=https://yourdomain.com
CORS_ORIGINS=["https://yourdomain.com"]

# Nginx/TLS
DOMAIN_NAME=yourdomain.com
EMAIL_FOR_LETS_ENCRYPT=your-email@example.com
```

### 3.3 Production `docker-compose.prod.yml`

The project already includes a production compose file with **5 services**:

| Service     | Image / Build        | Purpose                          |
|-------------|----------------------|----------------------------------|
| `db`        | `postgres:15-alpine` | PostgreSQL database              |
| `backend`   | `./backend`          | FastAPI API server (port 8000)   |
| `frontend`  | `./frontend`         | SvelteKit app (port 3000)        |
| `nginx`     | `nginx:1.25-alpine`  | Reverse proxy (ports 80 & 443)   |
| `certbot`   | `certbot/certbot`    | Let's Encrypt SSL auto-renewal   |

### 3.4 Run database migrations

```bash
# Start just the database first
docker compose -f docker-compose.prod.yml up -d db

# Run Alembic migrations
docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
```

### 3.5 Build and start all services

```bash
docker compose -f docker-compose.prod.yml up -d --build

# Check everything is running
docker compose -f docker-compose.prod.yml ps

# Check individual service logs
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend

# Test locally — backend health check
curl http://localhost:8000/api/health

# Test locally — frontend via nginx
curl http://localhost
```

### 3.6 SSL certificate (first time)

```bash
# Obtain initial Let's Encrypt certificate
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot --webroot-path=/var/www/certbot \
  -d yourdomain.com \
  --email your-email@example.com \
  --agree-tos --no-eff-email

# Reload nginx to pick up the certificate
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

> **Note**: The certbot container automatically renews certificates every 12 hours.

---

## Phase 4: Cloudflare Tunnel (Public Web Access)

This makes the app accessible at `https://yourdomain.com` without opening any ports on the office network. **Choose either this OR the Nginx/certbot approach in Phase 3** — Cloudflare Tunnel is simpler for office deployments where you can't control the network.

### 4.1 Prerequisites

- A domain name added to Cloudflare (free plan is fine) — update nameservers at your registrar

### 4.2 Install `cloudflared`

```bash
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb
rm cloudflared.deb

cloudflared --version
```

### 4.3 Authenticate

```bash
cloudflared tunnel login
# This opens a URL — copy it to a browser on your dev machine
# Select your domain and authorize
# Credentials are saved to ~/.cloudflared/cert.pem
```

### 4.4 Create the tunnel

```bash
cloudflared tunnel create parish-server

# Note the tunnel UUID printed (e.g. a1b2c3d4-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
# A credentials file is saved to ~/.cloudflared/<TUNNEL_UUID>.json
```

### 4.5 Configure the tunnel

```bash
nano ~/.cloudflared/config.yml
```

```yaml
tunnel: <TUNNEL_UUID>
credentials-file: /home/tauriq/.cloudflared/<TUNNEL_UUID>.json

ingress:
  # Route all traffic to nginx (which handles frontend + backend routing)
  - hostname: yourdomain.com
    service: http://localhost:80

  # Catch-all (required)
  - service: http_status:404
```

> **If using Cloudflare Tunnel instead of certbot**: Remove the `nginx` ports (80, 443) and `certbot` service from `docker-compose.prod.yml` since Cloudflare handles TLS termination. Nginx still runs internally as a reverse proxy but doesn't need to be exposed.

### 4.6 Create DNS record

```bash
cloudflared tunnel route dns parish-server yourdomain.com
# This creates a CNAME in Cloudflare pointing to your tunnel
```

### 4.7 Test the tunnel

```bash
# Run in foreground first to verify
cloudflared tunnel run parish-server

# Visit https://yourdomain.com in your browser — should see your app
# Ctrl+C to stop
```

### 4.8 Install as a systemd service (auto-start on boot)

```bash
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared

# Verify
sudo systemctl status cloudflared
```

> **Note**: The `service install` command copies your config to `/etc/cloudflared/` and creates the systemd unit. If it doesn't pick up your config, manually copy:
> ```bash
> sudo mkdir -p /etc/cloudflared
> sudo cp ~/.cloudflared/config.yml /etc/cloudflared/config.yml
> sudo cp ~/.cloudflared/<TUNNEL_UUID>.json /etc/cloudflared/<TUNNEL_UUID>.json
> ```

---

## Phase 5: Tailscale (Remote SSH Access)

Tailscale gives you a private mesh VPN so you can SSH into the ProDesk from anywhere, regardless of what network it's on.

### 5.1 Install Tailscale on the ProDesk

```bash
curl -fsSL https://tailscale.com/install.sh | sh

sudo tailscale up --ssh
# Follow the auth URL to link to your Tailscale account
# --ssh enables Tailscale SSH (no need for key management)
```

### 5.2 Install Tailscale on your dev machine

- **Windows**: Download from https://tailscale.com/download
- **WSL**: Same `curl` command as above
- Sign in with the same Tailscale account

### 5.3 Test SSH via Tailscale

```bash
# Find the ProDesk's Tailscale IP
tailscale status
# Look for parish-server — it'll have a 100.x.x.x IP

# SSH in using the Tailscale IP
ssh tauriq@100.x.x.x
# Or if you enabled Tailscale SSH:
ssh tauriq@parish-server
```

### 5.4 Ensure Tailscale starts on boot

```bash
sudo systemctl enable tailscaled
# It should already be enabled, but verify:
sudo systemctl status tailscaled
```

---

## Phase 6: Security Hardening

### 6.1 Firewall (UFW)

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (as a backup — Tailscale bypasses UFW)
sudo ufw allow 22/tcp

# No need to allow 80/443 — Cloudflare Tunnel is outbound only
# If NOT using Cloudflare Tunnel, also allow:
# sudo ufw allow 80/tcp
# sudo ufw allow 443/tcp

sudo ufw enable
sudo ufw status
```

### 6.2 Fail2ban

```bash
sudo apt install -y fail2ban

sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```

Find the `[sshd]` section and ensure:
```ini
[sshd]
enabled = true
port = ssh
maxretry = 5
bantime = 3600
```

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 6.3 Automatic security updates

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
# Select "Yes" to enable automatic security updates
```

### 6.4 SSH key-only auth (optional but recommended)

```bash
# On your dev machine, copy your key to the ProDesk
ssh-copy-id tauriq@<prodesk-local-ip>

# Then on the ProDesk, disable password auth
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd
```

---

## Phase 7: Automated Backups

### 7.1 Database backup script

```bash
mkdir -p ~/backups ~/scripts
nano ~/scripts/backup-db.sh
```

```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/tauriq/backups"
RETENTION_DAYS=30

# Dump the database from the Docker container
# Uses POSTGRES_USER and POSTGRES_DB from your .env
docker compose -f /home/tauriq/apps/parish-app/docker-compose.prod.yml \
  exec -T db pg_dump -U ${POSTGRES_USER:-parish_user} ${POSTGRES_DB:-parish_db} \
  | gzip > "$BACKUP_DIR/parish_db_$TIMESTAMP.sql.gz"

# Remove backups older than retention period
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: parish_db_$TIMESTAMP.sql.gz"
```

```bash
chmod +x ~/scripts/backup-db.sh
```

### 7.2 Schedule with cron

```bash
crontab -e
```

```cron
# Daily backup at 2am
0 2 * * * /home/tauriq/scripts/backup-db.sh >> /home/tauriq/backups/backup.log 2>&1
```

### 7.3 Offsite backup (optional)

Consider periodically copying backups offsite. Options:
- `rclone` to sync to Google Drive, OneDrive, or Backblaze B2
- `rsync` to another machine over Tailscale
- Manual `scp` pull from your dev machine periodically

---

## Phase 8: Auto-start Docker Compose on Boot

Docker's restart policy (`unless-stopped`) handles individual containers, but you need to ensure the compose project starts on boot.

```bash
sudo nano /etc/systemd/system/parish-app.service
```

```ini
[Unit]
Description=Parish Database Application
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
User=tauriq
WorkingDirectory=/home/tauriq/apps/parish-app
ExecStart=/usr/bin/docker compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.prod.yml down

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable parish-app
```

---

## Phase 9: The Move — Home to Office

### 9.1 Pre-move checklist

Run through this before unplugging:

```bash
# Verify all services auto-start
sudo reboot

# After reboot, wait 2 minutes, then check:
docker compose -f ~/apps/parish-app/docker-compose.prod.yml ps     # all 5 services running
curl http://localhost:8000/api/health                                # backend health check
sudo systemctl status cloudflared                                    # tunnel active
sudo systemctl status tailscaled                                     # tailscale connected
```

Visit `https://yourdomain.com` from your phone or another device to confirm everything is working end-to-end.

### 9.2 At the office

1. Plug in **power** and **Ethernet** (get an Ethernet cable and a spot from whoever manages the office network)
2. Power on
3. **That's it** — the ProDesk will:
   - Get a DHCP IP from the office network
   - Start Docker containers (frontend + backend + PostgreSQL + nginx)
   - Connect `cloudflared` tunnel outbound to Cloudflare → your domain goes live
   - Connect Tailscale → you can SSH in from your dev machine

### 9.3 Verify remotely

```bash
# From your dev machine (anywhere)
ssh tauriq@parish-server    # via Tailscale

# Check services
docker compose -f ~/apps/parish-app/docker-compose.prod.yml ps
sudo systemctl status cloudflared

# Visit your domain in a browser
# https://yourdomain.com
```

---

## Quick Reference

| What                  | How                                              |
|-----------------------|--------------------------------------------------|
| SSH into server       | `ssh tauriq@parish-server` (Tailscale)           |
| Check all services    | `docker compose -f ~/apps/parish-app/docker-compose.prod.yml ps` |
| Backend logs          | `docker compose -f ~/apps/parish-app/docker-compose.prod.yml logs -f backend` |
| Frontend logs         | `docker compose -f ~/apps/parish-app/docker-compose.prod.yml logs -f frontend` |
| Nginx logs            | `docker compose -f ~/apps/parish-app/docker-compose.prod.yml logs -f nginx` |
| Restart all           | `docker compose -f ~/apps/parish-app/docker-compose.prod.yml restart` |
| Backend health check  | `curl http://localhost:8000/api/health`           |
| Check tunnel status   | `sudo systemctl status cloudflared`              |
| Manual DB backup      | `~/scripts/backup-db.sh`                         |
| View Tailscale status | `tailscale status`                               |
| Run migrations        | `docker compose -f ~/apps/parish-app/docker-compose.prod.yml run --rm backend alembic upgrade head` |
| Update app            | `cd ~/apps/parish-app && git pull && docker compose -f docker-compose.prod.yml up -d --build` |
| View firewall rules   | `sudo ufw status`                                |

---

## Troubleshooting

### App not loading after move
1. SSH in via Tailscale — if this works, the server has internet
2. Check `sudo systemctl status cloudflared` — restart if needed
3. Check `docker compose -f docker-compose.prod.yml ps` — all 5 services should be up
4. Check backend health: `curl http://localhost:8000/api/health`

### Can't SSH via Tailscale
1. Tailscale needs outbound HTTPS — if the office blocks this, you'll need to talk to their IT
2. Check `sudo systemctl status tailscaled` (if you have console/monitor access)

### Cloudflare tunnel not connecting
1. The office network may require proxy settings — check with their IT
2. Verify: `cloudflared tunnel info parish-server`
3. Check logs: `sudo journalctl -u cloudflared -f`

### Database connection issues
1. Check if the DB container is healthy: `docker compose -f docker-compose.prod.yml ps`
2. View DB logs: `docker compose -f docker-compose.prod.yml logs db`
3. Restart just the DB: `docker compose -f docker-compose.prod.yml restart db`
4. Run pending migrations: `docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head`

### Google OAuth not working
1. Ensure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set in `.env`
2. In Google Cloud Console, add `https://yourdomain.com/auth/callback/google` as an authorized redirect URI
3. Ensure `AUTHORIZED_EMAIL` matches your Google account email
4. Check frontend logs: `docker compose -f docker-compose.prod.yml logs frontend`

### Nginx 502 Bad Gateway
1. Backend or frontend container may not be ready yet — wait and retry
2. Check backend is healthy: `docker compose -f docker-compose.prod.yml logs backend`
3. Verify nginx config: `docker compose -f docker-compose.prod.yml exec nginx nginx -t`

---

## Future Enhancements

- **Monitoring**: Add Uptime Kuma (Docker container) for health checks and alerts
- **CI/CD**: Set up a GitHub Actions workflow that SSHs in (via Tailscale) and runs `git pull && docker compose -f docker-compose.prod.yml up -d --build` on push to main
- **Offsite DB backups**: Automate with `rclone` to cloud storage
