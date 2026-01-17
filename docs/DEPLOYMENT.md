# Deployment Guide

Complete guide to deploy Baity Telegram Bot to a VPS server.

---

## Prerequisites

- VPS with Ubuntu 22.04+ (or any Linux)
- Docker and Docker Compose installed
- Domain name (optional, for SSL)

---

## Quick Deployment

### 1. Connect to your VPS

```bash
ssh user@your-server-ip
```

### 2. Install Docker (if not installed)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Logout and login again for group changes
exit
```

### 3. Clone the project

```bash
# Clone repository
git clone https://github.com/your-repo/baity-telegram-bot.git
cd baity-telegram-bot

# Or upload files via SCP
scp -r ./baity-telegram-bot user@your-server-ip:/home/user/
```

### 4. Configure environment

```bash
# Copy example config
cp .env.example .env

# Edit with your values
nano .env
```

Update these values in `.env`:

```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

BOT_TOKEN=8139940477:AAG_q-ghGtDzvVePKZcSQZuDXYu2NDRRAu0
WEBHOOK_API_KEY=baity-webhook-secret-key-2024

CITY_CHANNELS={"1": "@mu_baghdad_baity"}
```

### 5. Deploy

```bash
# Make deploy script executable
chmod +x deploy.sh

# Build and start
./deploy.sh build
./deploy.sh start

# Check status
./deploy.sh status
```

---

## Deployment Commands

| Command | Description |
|---------|-------------|
| `./deploy.sh start` | Start the bot |
| `./deploy.sh stop` | Stop the bot |
| `./deploy.sh restart` | Restart the bot |
| `./deploy.sh logs` | View logs |
| `./deploy.sh status` | Check status |
| `./deploy.sh build` | Rebuild images |
| `./deploy.sh update` | Pull & redeploy |

---

## Manual Docker Commands

```bash
# Build
docker-compose -f docker-compose.prod.yml build

# Start
docker-compose -f docker-compose.prod.yml up -d

# Stop
docker-compose -f docker-compose.prod.yml down

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart
docker-compose -f docker-compose.prod.yml restart
```

---

## SSL Setup (HTTPS)

### Option 1: Using Certbot (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot -y

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/

# Update nginx.conf - uncomment SSL lines
nano nginx/nginx.conf

# Start with nginx
./deploy.sh nginx
```

### Option 2: Using Cloudflare (Recommended)

1. Add your domain to Cloudflare
2. Set SSL mode to "Full" or "Full (Strict)"
3. Point your domain to your VPS IP
4. Cloudflare handles SSL automatically

---

## Update ASP.NET Backend

After deployment, update your Baity backend with the production URL.

Edit `appsettings.json`:

```json
"TelegramWebhook": {
  "BaseUrl": "https://your-domain.com",
  "ApiKey": "baity-webhook-secret-key-2024"
}
```

Or for IP-based (no SSL):

```json
"TelegramWebhook": {
  "BaseUrl": "http://your-server-ip:8000",
  "ApiKey": "baity-webhook-secret-key-2024"
}
```

---

## Firewall Configuration

```bash
# Allow SSH
sudo ufw allow 22

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow bot port (if not using nginx)
sudo ufw allow 8000

# Enable firewall
sudo ufw enable
```

---

## Monitoring

### View logs

```bash
./deploy.sh logs
```

### Check health

```bash
curl http://localhost:8000/api/v1/health
```

### Monitor resources

```bash
docker stats baity-telegram-bot
```

---

## Troubleshooting

### Bot not starting

```bash
# Check logs
./deploy.sh logs

# Check container status
docker ps -a

# Rebuild
./deploy.sh build
./deploy.sh restart
```

### Port already in use

```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

### Permission denied

```bash
# Fix permissions
sudo chown -R $USER:$USER .
chmod +x deploy.sh
```

---

## Auto-restart on Server Reboot

Docker containers are set to `restart: always`, so they will automatically start when the server reboots.

To verify:

```bash
# Reboot server
sudo reboot

# After reboot, check status
./deploy.sh status
```

---

## Backup

### Backup configuration

```bash
# Backup .env file
cp .env .env.backup

# Backup to remote
scp .env user@backup-server:/backups/baity-bot/
```

---

## Production Checklist

- [ ] Environment set to `production`
- [ ] Debug mode disabled
- [ ] Strong API key configured
- [ ] Bot token is correct
- [ ] City channels configured
- [ ] Firewall configured
- [ ] SSL configured (recommended)
- [ ] ASP.NET backend URL updated
- [ ] Health endpoint accessible
- [ ] Test message sent successfully
