# 🚀 AutoTest AI - Deployment Guide

This guide covers deploying AutoTest AI to production environments.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Platforms](#cloud-platforms)
5. [SSL/HTTPS Setup](#ssl-https-setup)
6. [Database Backup](#database-backup)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### Required Software

- **Docker** 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.0+ ([Install Compose](https://docs.docker.com/compose/install/))
- **Git** (for version control)

### Recommended Server Specs

**Minimum**:
- CPU: 2 cores
- RAM: 4 GB
- Storage: 20 GB
- OS: Ubuntu 20.04+, Debian 11+, or similar

**Recommended**:
- CPU: 4 cores
- RAM: 8 GB
- Storage: 50 GB SSD
- OS: Ubuntu 22.04 LTS

---

## ⚙️ Environment Configuration

### 1. Copy Environment Template

```bash
cp .env.example .env
```

### 2. Edit `.env` File

```bash
nano .env  # or use your preferred editor
```

### 3. Required Environment Variables

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_strong_password_here
POSTGRES_DB=autotest_prod

# Security
SECRET_KEY=your-secret-key-min-32-chars-random-string
JWT_SECRET_KEY=another-random-secret-key-for-jwt

# OpenAI API (for AI features)
OPENAI_API_KEY=sk-your-openai-api-key

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com

# GitHub Integration
GITHUB_TOKEN=ghp_your_github_personal_access_token

# Slack Integration (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Discord Integration (Optional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/WEBHOOK/URL

# Frontend URL
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### 4. Generate Strong Secrets

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🐳 Docker Deployment

### Quick Start (Development)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment

#### 1. **Run Deployment Script**

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```bash
deploy.bat
```

#### 2. **Manual Deployment**

```bash
# Create directories
mkdir -p backend/uploads backend/logs nginx/logs nginx/ssl backups

# Build images
docker-compose -f docker-compose.prod.yml build --no-cache

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

#### 3. **Verify Deployment**

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check API docs
curl http://localhost:8000/docs
```

---

## ☁️ Cloud Platforms

### AWS EC2

#### 1. **Launch EC2 Instance**
- AMI: Ubuntu 22.04 LTS
- Instance Type: t3.medium or larger
- Storage: 30 GB gp3
- Security Group: Allow ports 22, 80, 443, 8000, 3000

#### 2. **Connect and Setup**

```bash
# Connect via SSH
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/yourusername/autotest-ai.git
cd autotest-ai

# Configure environment
cp .env.example .env
nano .env

# Deploy
./deploy.sh
```

#### 3. **Configure Security Group**
- Inbound Rules:
  - HTTP (80) from 0.0.0.0/0
  - HTTPS (443) from 0.0.0.0/0
  - SSH (22) from your IP only

### DigitalOcean Droplet

#### 1. **Create Droplet**
- Image: Ubuntu 22.04 LTS
- Plan: Basic - $24/month (4 GB RAM, 2 vCPUs)
- Datacenter: Choose closest to users
- Enable: Monitoring, IPv6

#### 2. **Setup**

```bash
# Connect via SSH
ssh root@your-droplet-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Setup firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Clone and deploy
git clone https://github.com/yourusername/autotest-ai.git
cd autotest-ai
cp .env.example .env
nano .env
./deploy.sh
```

### Railway

#### 1. **Install Railway CLI**
```bash
npm i -g @railway/cli
railway login
```

#### 2. **Deploy**
```bash
railway init
railway up
```

#### 3. **Configure Environment Variables**
Go to Railway dashboard → Your Project → Variables and add all variables from `.env`

### Vercel (Frontend Only)

#### 1. **Install Vercel CLI**
```bash
npm i -g vercel
```

#### 2. **Deploy Frontend**
```bash
cd frontend
vercel
```

#### 3. **Configure Environment**
Add `NEXT_PUBLIC_API_URL` in Vercel dashboard

---

## 🔒 SSL/HTTPS Setup

### Using Let's Encrypt (Certbot)

#### 1. **Install Certbot**

```bash
sudo apt install certbot python3-certbot-nginx -y
```

#### 2. **Obtain Certificate**

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### 3. **Auto-Renewal**

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot automatically sets up cron job
```

#### 4. **Update nginx.conf**

Uncomment HTTPS server block in `nginx/nginx.conf` and update domain:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # ... rest of configuration
}
```

#### 5. **Restart Nginx**

```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

### Using Cloudflare (Easy SSL)

1. Add your domain to Cloudflare
2. Update DNS to point to your server IP
3. Enable SSL/TLS in Cloudflare (Full or Full Strict)
4. Cloudflare handles SSL automatically

---

## 💾 Database Backup

### Manual Backup

```bash
# Backup database
docker exec autotest_postgres_prod pg_dump -U postgres autotest_prod > backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Compress backup
gzip backups/backup_*.sql
```

### Automated Backups (Cron)

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/autotest-ai && docker exec autotest_postgres_prod pg_dump -U postgres autotest_prod | gzip > backups/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz

# Add weekly cleanup (keep last 30 days)
0 3 * * 0 find /path/to/autotest-ai/backups -name "backup_*.sql.gz" -mtime +30 -delete
```

### Restore from Backup

```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Restore database
gunzip < backups/backup_YYYYMMDD_HHMMSS.sql.gz | docker exec -i autotest_postgres_prod psql -U postgres autotest_prod

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📊 Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database connection
docker exec autotest_postgres_prod psql -U postgres -c "SELECT 1"

# Check all containers
docker-compose -f docker-compose.prod.yml ps
```

### Log Monitoring

```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service
docker-compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Clean up old images
docker system prune -a
```

### Recommended Monitoring Tools

1. **Uptime Robot** - Free uptime monitoring
2. **Grafana + Prometheus** - Metrics and dashboards
3. **Sentry** - Error tracking
4. **LogRocket** - Session replay and monitoring

---

## 🔧 Troubleshooting

### Common Issues

#### 1. **Port Already in Use**

```bash
# Find process using port
sudo lsof -i :8000
sudo lsof -i :3000

# Kill process
sudo kill -9 <PID>
```

#### 2. **Docker Build Fails**

```bash
# Clean Docker cache
docker system prune -a --volumes

# Rebuild without cache
docker-compose -f docker-compose.prod.yml build --no-cache
```

#### 3. **Database Connection Error**

```bash
# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres

# Restart database
docker-compose -f docker-compose.prod.yml restart postgres

# Check connection
docker exec -it autotest_postgres_prod psql -U postgres
```

#### 4. **Backend Not Starting**

```bash
# Check backend logs
docker-compose -f docker-compose.prod.yml logs backend

# Check environment variables
docker-compose -f docker-compose.prod.yml exec backend env

# Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

#### 5. **Frontend Build Error**

```bash
# Check Node version
docker-compose -f docker-compose.prod.yml exec frontend node --version

# Clear Next.js cache
docker-compose -f docker-compose.prod.yml exec frontend rm -rf .next

# Rebuild
docker-compose -f docker-compose.prod.yml up -d --build frontend
```

### Performance Optimization

#### 1. **Enable Caching**

Update `nginx.conf`:
```nginx
# Add caching
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;

location /api/ {
    proxy_cache my_cache;
    proxy_cache_valid 200 5m;
    # ... rest of config
}
```

#### 2. **Database Tuning**

Create `postgres.conf`:
```conf
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
```

Mount in docker-compose:
```yaml
volumes:
  - ./postgres.conf:/etc/postgresql/postgresql.conf
```

#### 3. **Scale Services**

```bash
# Scale backend workers
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

---

## 📝 Post-Deployment Checklist

- [ ] Environment variables configured
- [ ] SSL/HTTPS enabled
- [ ] Database backups scheduled
- [ ] Monitoring setup
- [ ] Firewall configured
- [ ] Domain DNS updated
- [ ] Health checks passing
- [ ] Logs accessible
- [ ] Admin user created
- [ ] Email notifications working
- [ ] GitHub integration tested
- [ ] Visual tests functional
- [ ] CI/CD pipelines configured

---

## 🆘 Support

### Resources

- **Documentation**: `/docs`
- **API Reference**: `http://localhost:8000/docs`
- **GitHub Issues**: Create an issue on GitHub
- **Email**: support@yourdomain.com

### Useful Commands

```bash
# View all containers
docker ps -a

# Restart all services
docker-compose -f docker-compose.prod.yml restart

# Stop all services
docker-compose -f docker-compose.prod.yml down

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# View resource usage
docker stats

# Clean up
docker system prune -a --volumes

# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🎉 Success!

If everything is running:

- ✅ Frontend: http://yourdomain.com
- ✅ Backend API: http://yourdomain.com/api
- ✅ API Docs: http://yourdomain.com/docs
- ✅ Database backups running
- ✅ SSL enabled
- ✅ Monitoring active

**Your AutoTest AI is now live!** 🚀

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Status**: Production Ready ✅
