# Deployment Guide

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Database Deployment](#database-deployment)
5. [Backend Deployment](#backend-deployment)
6. [Frontend Deployment](#frontend-deployment)
7. [Hardware Deployment](#hardware-deployment)
8. [Firebase Configuration](#firebase-configuration)
9. [Docker Deployment](#docker-deployment)
10. [Monitoring and Maintenance](#monitoring-and-maintenance)
11. [Troubleshooting](#troubleshooting)

## Deployment Overview

This guide provides step-by-step instructions for deploying AHON FloodWatch to production. The system consists of multiple components that can be deployed together or separately depending on your infrastructure requirements.

### Deployment Architecture

```
┌─────────────────┐
│   Frontend      │
│   (React/Vite)  │
└────────┬────────┘
         │
         │ HTTPS
         │
┌────────▼────────┐
│   Backend       │
│   (Django)      │
└────────┬────────┘
         │
         │
    ┌────┴────┬──────────┐
    │         │          │
┌───▼───┐ ┌──▼────┐ ┌──▼──────┐
│  DB   │ │Firebase│ │Hardware │
│(PostgreSQL)│ │ │ │ │
└───────┘ └───────┘ └─────────┘
```

### Deployment Options

1. **Traditional Deployment**: Manual deployment on VPS or dedicated server
2. **Docker Deployment**: Containerized deployment using Docker Compose
3. **Cloud Deployment**: Deploy to cloud platforms (AWS, GCP, Azure)
4. **Hybrid Deployment**: Mix of on-premises and cloud services

## Prerequisites

### System Requirements

- **Operating System**: Ubuntu 20.04 LTS or later (recommended)
- **CPU**: 2 cores minimum, 4 cores recommended
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 50 GB minimum, 100 GB recommended
- **Network**: Stable internet connection with static IP recommended

### Software Requirements

- **Python**: 3.9 or later
- **Node.js**: 16 or later
- **PostgreSQL**: 13 or later
- **Nginx**: 1.18 or later
- **Docker**: 20.10 or later (for Docker deployment)
- **Git**: Latest version
- **SSL Certificate**: Valid SSL certificate for HTTPS

### Domain Requirements

- **Domain Name**: Registered domain for the dashboard
- **DNS Configuration**: A records pointing to your server
- **SSL Certificate**: Valid SSL certificate (Let's Encrypt recommended)

## Environment Setup

### Server Preparation

1. **Update System**
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. **Install Basic Dependencies**
   ```bash
   sudo apt install -y python3 python3-pip python3-venv nodejs npm git nginx postgresql postgresql-contrib
   ```

3. **Create Application User**
   ```bash
   sudo adduser flood_detection
   sudo usermod -aG sudo flood_detection
   ```

4. **Configure Firewall**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

### Project Setup

1. **Clone Repository**
   ```bash
   sudo -u flood_detection -i
   cd /home/flood_detection
   git clone <repository-url>
   cd ai-flood-detection-system
   ```

2. **Create Directory Structure**
   ```bash
   mkdir -p logs
   mkdir -p uploads
   mkdir -p backups
   ```

## Database Deployment

### PostgreSQL Setup

1. **Create Database**
   ```bash
   sudo -u postgres psql
   ```
   ```sql
   CREATE DATABASE flood_detection;
   CREATE USER flood_detection_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE flood_detection TO flood_detection_user;
   \q
   ```

2. **Configure PostgreSQL**
   ```bash
   sudo nano /etc/postgresql/13/main/postgresql.conf
   ```
   Edit the following:
   ```ini
   listen_addresses = 'localhost'
   max_connections = 100
   shared_buffers = 256MB
   ```

3. **Restart PostgreSQL**
   ```bash
   sudo systemctl restart postgresql
   ```

### Database Migration

1. **Configure Environment**
   ```bash
   cd backend/Django
   cp .env.example .env
   nano .env
   ```
   Update database settings:
   ```ini
   DB_NAME=flood_detection
   DB_USER=flood_detection_user
   DB_PASSWORD=secure_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

2. **Run Migrations**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   ```

3. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

4. **Load Initial Data** (optional)
   ```bash
   python manage.py loaddata initial_data.json
   ```

## Backend Deployment

### Django Configuration

1. **Update Settings**
   ```bash
   nano flood_detection/settings.py
   ```
   Update production settings:
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
   CORS_ALLOWED_ORIGINS = ['https://your-domain.com']
   ```

2. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

### Gunicorn Setup

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Create Gunicorn Service**
   ```bash
   sudo nano /etc/systemd/system/flood_detection.service
   ```
   ```ini
   [Unit]
   Description=Flood Detection Django Service
   After=network.target postgresql.service

   [Service]
   User=flood_detection
   Group=flood_detection
   WorkingDirectory=/home/flood_detection/ai-flood-detection-system/backend/Django
   Environment="PATH=/home/flood_detection/ai-flood-detection-system/backend/Django/venv/bin"
   ExecStart=/home/flood_detection/ai-flood-detection-system/backend/Django/venv/bin/gunicorn \
             --workers 3 \
             --bind unix:/home/flood_detection/ai-flood-detection-system/backend/Django/gunicorn.sock \
             flood_detection.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

3. **Start Service**
   ```bash
   sudo systemctl start flood_detection
   sudo systemctl enable flood_detection
   sudo systemctl status flood_detection
   ```

## Frontend Deployment

### Build Configuration

1. **Install Dependencies**
   ```bash
   cd frontend/React
   npm install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   nano .env
   ```
   ```ini
   VITE_API_URL=https://your-domain.com/api
   ```

3. **Build for Production**
   ```bash
   npm run build
   ```

### Nginx Configuration

1. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/flood_detection
   ```
   ```nginx
   server {
       listen 80;
       server_name your-domain.com www.your-domain.com;

       # Redirect to HTTPS
       return 301 https://$server_name$request_uri;
   }

   server {
       listen 443 ssl http2;
       server_name your-domain.com www.your-domain.com;

       # SSL Configuration
       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers HIGH:!aNULL:!MD5;

       # Frontend
       location / {
           root /home/flood_detection/ai-flood-detection-system/frontend/React/dist;
           try_files $uri $uri/ /index.html;
       }

       # Backend API
       location /api/ {
           proxy_pass http://unix:/home/flood_detection/ai-flood-detection-system/backend/Django/gunicorn.sock;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       # Static Files
       location /static/ {
           alias /home/flood_detection/ai-flood-detection-system/backend/Django/static/;
       }

       # Media Files
       location /media/ {
           alias /home/flood_detection/ai-flood-detection-system/backend/Django/media/;
       }
   }
   ```

2. **Enable Site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/flood_detection /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### SSL Configuration

1. **Install Certbot**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Obtain SSL Certificate**
   ```bash
   sudo certbot --nginx -d your-domain.com -d www.your-domain.com
   ```

3. **Auto-renewal**
   ```bash
   sudo certbot renew --dry-run
   ```

## Hardware Deployment

### Arduino Deployment

1. **Upload Firmware**
   - Open Arduino IDE
   - Load `hardware/Arduino/flood_detection.ino`
   - Configure settings (Firebase, thresholds, etc.)
   - Upload to Arduino

2. **Install Hardware**
   - Follow Hardware Setup Guide
   - Install in protected location
   - Connect power system
   - Test all connections

3. **Configure Firebase**
   - Set up Firebase project
   - Enable Realtime Database
   - Configure security rules
   - Update firmware with credentials

### Hardware Monitoring

1. **Remote Monitoring**
   - Monitor via Firebase console
   - Check dashboard for sensor status
   - Review SMS logs for delivery issues

2. **Maintenance Schedule**
   - Weekly: Check physical connections
   - Monthly: Clean solar panel
   - Quarterly: Calibrate sensor
   - Annually: Replace battery if needed

## Firebase Configuration

### Firebase Setup

1. **Create Firebase Project**
   - Go to Firebase Console
   - Create new project
   - Enable Realtime Database
   - Set up security rules

2. **Generate Service Account Key**
   - Go to Project Settings
   - Service Accounts
   - Generate Private Key
   - Save securely

3. **Configure Django**
   ```bash
   nano backend/Django/.env
   ```
   ```ini
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_PRIVATE_KEY_PATH=/path/to/service-account-key.json
   FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com
   ```

4. **Security Rules**
   ```json
   {
     "rules": {
       ".read": "auth != null",
       ".write": "auth != null",
       "water_level": {
         ".read": true,
         ".write": "auth != null"
       }
     }
   }
   ```

## Docker Deployment

### Docker Compose Setup

1. **Create Docker Compose File**
   ```bash
   cd docker
   nano docker-compose.yml
   ```
   ```yaml
   version: '3.8'

   services:
     db:
       image: postgres:13
       environment:
         POSTGRES_DB: flood_detection
         POSTGRES_USER: flood_detection
         POSTGRES_PASSWORD: ${DB_PASSWORD}
       volumes:
         - postgres_data:/var/lib/postgresql/data
       ports:
         - "5432:5432"

     backend:
       build: ../backend/Django
       command: gunicorn flood_detection.wsgi:application --bind 0.0.0.0:8000
       volumes:
         - ../backend/Django:/app
       ports:
         - "8000:8000"
       depends_on:
         - db
       environment:
         - DB_HOST=db
         - DB_PORT=5432
         - DB_NAME=flood_detection
         - DB_USER=flood_detection
         - DB_PASSWORD=${DB_PASSWORD}

     frontend:
       build: ../frontend/React
       ports:
         - "3000:3000"
       depends_on:
         - backend

     nginx:
       image: nginx:latest
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
         - ../frontend/React/dist:/usr/share/nginx/html
       depends_on:
         - backend
         - frontend

   volumes:
     postgres_data:
   ```

2. **Build and Run**
   ```bash
   docker-compose up -d --build
   ```

3. **Run Migrations**
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   ```

## Monitoring and Maintenance

### System Monitoring

1. **Application Monitoring**
   ```bash
   # Check service status
   sudo systemctl status flood_detection
   sudo systemctl status nginx
   sudo systemctl status postgresql
   ```

2. **Log Monitoring**
   ```bash
   # View logs
   tail -f /home/flood_detection/ai-flood-detection-system/logs/django.log
   tail -f /var/log/nginx/access.log
   tail -f /var/log/nginx/error.log
   ```

3. **Resource Monitoring**
   ```bash
   # System resources
   htop
   df -h
   free -m
   ```

### Backup Strategy

1. **Database Backup**
   ```bash
   # Automated backup script
   sudo nano /usr/local/bin/backup_db.sh
   ```
   ```bash
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   pg_dump flood_detection | gzip > /home/flood_detection/backups/db_$DATE.sql.gz
   find /home/flood_detection/backups -name "db_*.sql.gz" -mtime +30 -delete
   ```
   ```bash
   sudo chmod +x /usr/local/bin/backup_db.sh
   ```

2. **Scheduled Backups**
   ```bash
   sudo crontab -e
   ```
   ```cron
   # Daily backup at 2 AM
   0 2 * * * /usr/local/bin/backup_db.sh
   ```

3. **Application Backup**
   ```bash
   # Backup application files
   tar -czf /home/flood_detection/backups/app_$(date +%Y%m%d).tar.gz /home/flood_detection/ai-flood-detection-system
   ```

### Update Strategy

1. **Code Updates**
   ```bash
   cd /home/flood_detection/ai-flood-detection-system
   git pull origin main
   ```

2. **Backend Updates**
   ```bash
   cd backend/Django
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   sudo systemctl restart flood_detection
   ```

3. **Frontend Updates**
   ```bash
   cd frontend/React
   npm install
   npm run build
   sudo systemctl reload nginx
   ```

## Troubleshooting

### Common Issues

#### Service Won't Start

**Check logs:**
```bash
sudo journalctl -u flood_detection -n 50
```

**Common causes:**
- Database connection issues
- Port conflicts
- Permission problems
- Configuration errors

#### Database Connection Failed

**Check PostgreSQL:**
```bash
sudo systemctl status postgresql
sudo -u postgres psql -l
```

**Verify credentials in .env file**

#### Nginx 502 Bad Gateway

**Check Gunicorn:**
```bash
sudo systemctl status flood_detection
```

**Check socket file:**
```bash
ls -la /home/flood_detection/ai-flood-detection-system/backend/Django/gunicorn.sock
```

#### SSL Certificate Issues

**Renew certificate:**
```bash
sudo certbot renew
sudo systemctl reload nginx
```

#### Hardware Not Connecting

**Check Firebase:**
- Verify Firebase credentials
- Check Firebase console for data
- Review hardware logs

**Check SIM800L:**
- Verify SIM card has data plan
- Check signal strength
- Review APN settings

### Performance Issues

#### Slow API Response

**Optimize database:**
```bash
sudo -u postgres psql flood_detection
```
```sql
VACUUM ANALYZE;
```

**Check database size:**
```sql
SELECT pg_size_pretty(pg_database_size('flood_detection'));
```

#### High Memory Usage

**Check Gunicorn workers:**
```bash
# Reduce workers in service file
--workers 2
```

**Restart service:**
```bash
sudo systemctl restart flood_detection
```

### Security Issues

#### Unauthorized Access

**Review logs:**
```bash
sudo tail -f /var/log/nginx/access.log
```

**Block suspicious IPs:**
```bash
sudo ufw deny from <IP_ADDRESS>
```

#### SSL Certificate Expired

**Renew certificate:**
```bash
sudo certbot renew --force-renewal
sudo systemctl reload nginx
```

## Appendix

### Environment Variables Reference

```ini
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DB_NAME=flood_detection
DB_USER=flood_detection_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_PATH=/path/to/service-account-key.json
FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com

# JWT
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=604800

# SMS
SMS_ENABLED=True
SMS_API_KEY=your-sms-api-key
MAX_SMS_PER_HOUR=100

# AI
AI_PREDICTION_ENABLED=True
AI_MODEL_PATH=/path/to/model.pkl

# Flood Thresholds
NORMAL_THRESHOLD=30
ALERT_THRESHOLD=45
WARNING_THRESHOLD=60
DANGER_THRESHOLD=75
```

### Service Commands

```bash
# Django
sudo systemctl start flood_detection
sudo systemctl stop flood_detection
sudo systemctl restart flood_detection
sudo systemctl status flood_detection

# Nginx
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl reload nginx
sudo systemctl status nginx

# PostgreSQL
sudo systemctl start postgresql
sudo systemctl stop postgresql
sudo systemctl restart postgresql
sudo systemctl status postgresql
```

### Useful Commands

```bash
# View logs
tail -f logs/django.log
tail -f logs/gunicorn.log

# Database operations
python manage.py dbshell
python manage.py showmigrations
python manage.py sqlmigrate app_name migration_name

# Django management
python manage.py collectstatic
python manage.py createsuperuser
python manage.py shell

# Git operations
git status
git pull origin main
git log --oneline
```

### Contact Information

- **Technical Support**: support@example.com
- **Emergency Contact**: +63-XXX-XXX-XXXX
- **Documentation**: docs/ directory

### Version History

- **v1.0.0** (2026-07-13): Initial deployment guide
