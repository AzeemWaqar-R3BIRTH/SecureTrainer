# 🌐 SecureTrainer Custom Domain Deployment Guide
## Deploy to securetrainer.com

This guide will walk you through purchasing a domain and deploying your SecureTrainer project to make it publicly accessible at **securetrainer.com**.

---

## 📋 Overview

**Total Cost Estimate**: $15-30/month
- Domain: $10-15/year (~$1/month)
- VPS Hosting: $5-20/month
- SSL Certificate: Free (Let's Encrypt)

**Timeline**: 2-4 hours for complete setup

---

## Step 1: Purchase Domain Name

### Option A: Namecheap (Recommended - Affordable)

**Steps**:
1. Go to https://www.namecheap.com
2. Search for "securetrainer.com"
3. Add to cart (~$10-13/year)
4. Create account and complete purchase
5. Enable "WhoisGuard" (free privacy protection)

**Pros**: Cheapest, easy DNS management, includes free privacy
**Cons**: None significant

### Option B: GoDaddy (Popular)

**Steps**:
1. Go to https://www.godaddy.com
2. Search for "securetrainer.com"
3. Add to cart (~$12-15/year)
4. Complete purchase

**Pros**: Well-known, good support
**Cons**: Slightly more expensive, upsells

### Option C: Google Domains

**Steps**:
1. Go to https://domains.google
2. Search for "securetrainer.com"
3. Purchase (~$12/year)

**Pros**: Clean interface, integrated with Google services
**Cons**: No significant disadvantages

**⭐ Recommendation**: Use **Namecheap** for best value

---

## Step 2: Choose Hosting Provider

### Option A: DigitalOcean (Recommended for VPS)

**Cost**: $6/month for basic droplet

**Why DigitalOcean**:
- Simple and developer-friendly
- Great documentation
- Easy scaling
- $200 free credit for new users (2 months free!)

**Steps to Get Started**:
1. Sign up at https://www.digitalocean.com
2. Use student pack or promo code for free credits
3. Verify account with credit card

### Option B: AWS EC2 (Enterprise-grade)

**Cost**: Free tier for 12 months, then ~$10/month

**Why AWS**:
- Industry standard
- Free tier available
- Powerful features
- Great for resume/portfolio

### Option C: Linode

**Cost**: $5/month for basic plan

**Why Linode**:
- Cheapest option
- Good performance
- Simple interface

### Option D: Heroku (Platform-as-a-Service)

**Cost**: Free tier available, $7/month for production

**Why Heroku**:
- Easiest deployment
- No server management
- Quick setup
- Limited resources on free tier

**⭐ Recommendation**: Use **DigitalOcean** for best balance of price, performance, and ease

---

## Step 3: Deploy to DigitalOcean (Detailed Guide)

### 3.1 Create Droplet (Virtual Server)

1. **Log into DigitalOcean**
2. **Click "Create" → "Droplets"**
3. **Choose Configuration**:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($6/month)
   - **CPU Options**: Regular (1 GB RAM, 1 vCPU)
   - **Datacenter**: Choose closest to your location
   - **Authentication**: SSH keys (recommended) or Password
   - **Hostname**: securetrainer-production

4. **Click "Create Droplet"**
5. **Note the IP address** (e.g., 123.456.789.012)

### 3.2 Connect to Your Server

**Windows (using PowerShell or WSL)**:
```bash
# SSH into your server
ssh root@YOUR_DROPLET_IP

# Enter password when prompted
```

**Alternative - Use PuTTY on Windows**:
1. Download PuTTY: https://www.putty.org/
2. Enter your droplet IP
3. Click "Open" and login as root

### 3.3 Initial Server Setup

```bash
# Update system packages
apt update && apt upgrade -y

# Install required software
apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install -y docker-compose

# Create non-root user for security
adduser securetrainer
usermod -aG sudo securetrainer
usermod -aG docker securetrainer

# Switch to new user
su - securetrainer
```

### 3.4 Clone and Setup Project

```bash
# Create project directory
mkdir -p /home/securetrainer/apps
cd /home/securetrainer/apps

# Clone your repository (if using Git)
git clone https://github.com/yourusername/securetrainer.git
cd securetrainer

# OR upload files using SCP from your Windows machine
# On your Windows machine (PowerShell):
# scp -r "C:\Users\Azeem's ASUS\Desktop\Antigravity Test 2\...\securetrainer" securetrainer@YOUR_IP:/home/securetrainer/apps/
```

### 3.5 Configure Environment Variables

```bash
# Create production environment file
nano .env

# Add the following (update with your actual values):
```

```bash
# Production Environment Configuration
FLASK_ENV=production
SECRET_KEY=GENERATE_RANDOM_64_CHAR_STRING_HERE

# Database Configuration
MONGO_URI=mongodb://localhost:27017/securetrainer
REDIS_URL=redis://localhost:6379/0

# Email Configuration (for QR codes)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_USE_TLS=True

# Security
ADMIN_TOKEN=GENERATE_RANDOM_ADMIN_TOKEN

# Performance
WORKER_PROCESSES=2
WORKER_CONNECTIONS=1000
```

**Save file**: Press `Ctrl+X`, then `Y`, then `Enter`

### 3.6 Install MongoDB

```bash
# Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Update package list
sudo apt update

# Install MongoDB
sudo apt install -y mongodb-org

# Start and enable MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify MongoDB is running
sudo systemctl status mongod
```

### 3.7 Setup Application

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Generate ML model with synthetic data
python generate_demo_training_data.py
python scripts/train_difficulty_model.py

# Create admin user
python create_admin.py
```

### 3.8 Configure Gunicorn (Production WSGI Server)

```bash
# Install Gunicorn
pip install gunicorn

# Create Gunicorn configuration
nano gunicorn_config.py
```

```python
# Gunicorn Configuration
bind = "127.0.0.1:8000"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "/home/securetrainer/apps/securetrainer/logs/gunicorn_access.log"
errorlog = "/home/securetrainer/apps/securetrainer/logs/gunicorn_error.log"
loglevel = "info"
```

**Save file**: `Ctrl+X`, `Y`, `Enter`

```bash
# Create logs directory
mkdir -p logs

# Test Gunicorn
gunicorn -c gunicorn_config.py securetrainer:app
```

Press `Ctrl+C` to stop after verifying it works

### 3.9 Create Systemd Service (Auto-start on Boot)

```bash
# Create service file
sudo nano /etc/systemd/system/securetrainer.service
```

```ini
[Unit]
Description=SecureTrainer Web Application
After=network.target mongod.service

[Service]
Type=notify
User=securetrainer
Group=securetrainer
WorkingDirectory=/home/securetrainer/apps/securetrainer
Environment="PATH=/home/securetrainer/apps/securetrainer/venv/bin"
ExecStart=/home/securetrainer/apps/securetrainer/venv/bin/gunicorn -c gunicorn_config.py securetrainer:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save file**: `Ctrl+X`, `Y`, `Enter`

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable securetrainer
sudo systemctl start securetrainer

# Check status
sudo systemctl status securetrainer
```

---

## Step 4: Configure Domain DNS

### 4.1 Point Domain to Server

**In Namecheap Dashboard**:
1. Go to **Domain List** → Click **Manage** next to securetrainer.com
2. Click **Advanced DNS**
3. Add these records:

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A Record | @ | YOUR_DROPLET_IP | Automatic |
| A Record | www | YOUR_DROPLET_IP | Automatic |

4. **Save changes**

**DNS Propagation**: Wait 5-30 minutes for DNS to propagate globally

### 4.2 Verify DNS

```bash
# On your local machine, check DNS
# Windows PowerShell:
nslookup securetrainer.com

# Should show your droplet IP
```

---

## Step 5: Configure Nginx (Web Server)

### 5.1 Create Nginx Configuration

```bash
# On your server
sudo nano /etc/nginx/sites-available/securetrainer
```

```nginx
# SecureTrainer Nginx Configuration

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name securetrainer.com www.securetrainer.com;
    
    # Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server (will be configured after SSL)
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name securetrainer.com www.securetrainer.com;

    # SSL certificates (will be added by certbot)
    # ssl_certificate /etc/letsencrypt/live/securetrainer.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/securetrainer.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/securetrainer_access.log;
    error_log /var/log/nginx/securetrainer_error.log;

    # File upload size limit
    client_max_body_size 10M;

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (if needed)
    location /static {
        alias /home/securetrainer/apps/securetrainer/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**Save file**: `Ctrl+X`, `Y`, `Enter`

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/securetrainer /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## Step 6: Install SSL Certificate (HTTPS)

```bash
# Install SSL certificate using Certbot
sudo certbot --nginx -d securetrainer.com -d www.securetrainer.com

# Follow prompts:
# 1. Enter email address
# 2. Agree to terms
# 3. Choose whether to redirect HTTP to HTTPS (select Yes)

# Certbot will automatically:
# - Obtain SSL certificate
# - Configure Nginx
# - Set up auto-renewal

# Test auto-renewal
sudo certbot renew --dry-run
```

---

## Step 7: Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Verify firewall status
sudo ufw status
```

---

## Step 8: Final Verification

### 8.1 Check All Services

```bash
# Check MongoDB
sudo systemctl status mongod

# Check Gunicorn/SecureTrainer
sudo systemctl status securetrainer

# Check Nginx
sudo systemctl status nginx

# View application logs
sudo journalctl -u securetrainer -f
```

### 8.2 Test Your Website

**Open browser and visit**:
- https://securetrainer.com
- https://www.securetrainer.com

**You should see**:
- ✅ Secure HTTPS connection
- ✅ SecureTrainer login page
- ✅ No SSL warnings

### 8.3 Test Key Features

1. **User Registration** → Create test account
2. **Login** → Verify authentication works
3. **Challenges** → Submit a challenge
4. **Admin Dashboard** → Access admin panel
5. **ML Model** → Check difficulty predictions

---

## Step 9: Ongoing Maintenance

### 9.1 Monitor Logs

```bash
# Application logs
sudo journalctl -u securetrainer -f

# Nginx access logs
sudo tail -f /var/log/nginx/securetrainer_access.log

# Nginx error logs
sudo tail -f /var/log/nginx/securetrainer_error.log
```

### 9.2 Update Application

```bash
# SSH into server
ssh securetrainer@YOUR_IP

# Navigate to project
cd /home/securetrainer/apps/securetrainer

# Pull latest changes (if using Git)
git pull

# Or upload new files via SCP

# Restart application
sudo systemctl restart securetrainer
```

### 9.3 Database Backup

```bash
# Create backup script
nano ~/backup.sh
```

```bash
#!/bin/bash
# MongoDB Backup Script
BACKUP_DIR="/home/securetrainer/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
mongodump --out $BACKUP_DIR/mongodb_$DATE

# Keep only last 7 backups
ls -t $BACKUP_DIR | tail -n +8 | xargs -I {} rm -rf $BACKUP_DIR/{}

echo "Backup completed: $BACKUP_DIR/mongodb_$DATE"
```

```bash
# Make executable
chmod +x ~/backup.sh

# Add to crontab (daily backup at 2 AM)
crontab -e

# Add this line:
0 2 * * * /home/securetrainer/backup.sh
```

### 9.4 Monitor Resources

```bash
# Install htop for monitoring
sudo apt install -y htop

# Run htop
htop

# Check disk usage
df -h

# Check memory usage
free -h
```

---

## 💰 Cost Breakdown

| Item | Provider | Cost | Billing |
|------|----------|------|---------|
| **Domain** | Namecheap | $10-13 | Yearly |
| **VPS Hosting** | DigitalOcean | $6 | Monthly |
| **SSL Certificate** | Let's Encrypt | FREE | - |
| **Email** | Gmail | FREE | - |
| **Total First Year** | - | **~$82** | - |
| **Monthly After** | - | **~$6** | - |

**Student Discounts**:
- GitHub Student Pack: Free DigitalOcean credits ($200)
- Namecheap Education: 30% off domains

---

## 🎓 For Your FYP

**Professional Domain Benefits**:
- ✅ Demonstrates deployment skills
- ✅ Portfolio-worthy project
- ✅ Accessible for evaluators
- ✅ Real-world production experience
- ✅ Resume enhancement

**FYP Presentation Points**:
- "Deployed to production at securetrainer.com"
- "Configured SSL/HTTPS for security"
- "Implemented CI/CD pipeline"
- "Set up monitoring and backups"
- "Managed cloud infrastructure"

---

## 🆘 Troubleshooting

### Website Not Loading

```bash
# Check if services are running
sudo systemctl status securetrainer nginx mongod

# Check Nginx error logs
sudo tail -100 /var/log/nginx/securetrainer_error.log

# Check application logs
sudo journalctl -u securetrainer -n 100
```

### SSL Certificate Issues

```bash
# Test certificate
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal
```

### Application Crashes

```bash
# Check logs
sudo journalctl -u securetrainer -n 200

# Restart service
sudo systemctl restart securetrainer

# Check if port 8000 is in use
sudo netstat -tulpn | grep 8000
```

### Database Connection Failed

```bash
# Check MongoDB status
sudo systemctl status mongod

# Restart MongoDB
sudo systemctl restart mongod

# Check connection
mongo --eval "db.adminCommand('ping')"
```

---

## 📞 Support Resources

- **DigitalOcean Docs**: https://docs.digitalocean.com/
- **Nginx Docs**: https://nginx.org/en/docs/
- **Certbot Docs**: https://certbot.eff.org/
- **MongoDB Docs**: https://docs.mongodb.com/

---

## ✅ Deployment Checklist

- [ ] Domain purchased (securetrainer.com)
- [ ] DigitalOcean droplet created
- [ ] SSH access configured
- [ ] Server packages installed
- [ ] MongoDB installed and running
- [ ] Application code deployed
- [ ] Environment variables configured
- [ ] ML model generated
- [ ] Gunicorn service running
- [ ] Nginx configured
- [ ] DNS records added
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Website accessible via HTTPS
- [ ] All features tested
- [ ] Backup system configured

---

**Estimated Total Time**: 2-4 hours
**Difficulty**: Intermediate
**Result**: Production-ready deployment at https://securetrainer.com

Good luck with your deployment! 🚀
