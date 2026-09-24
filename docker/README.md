# Docker Deployment

This directory contains Docker configuration files for deploying the AI-Assisted Flood Detection System using Docker and Docker Compose.

## Prerequisites

- Docker 20.10 or later
- Docker Compose 1.29 or later
- At least 4GB RAM available
- At least 10GB disk space available

## Quick Start

1. **Copy Environment File**
   ```bash
   cp .env.example .env
   ```

2. **Edit Environment Variables**
   ```bash
   nano .env
   ```
   Update the following variables:
   - Database credentials
   - Django secret key
   - Firebase credentials
   - SMS API key (if using SMS)

3. **Build and Start Services**
   ```bash
   docker-compose up -d --build
   ```

4. **Run Database Migrations**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

5. **Create Superuser**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

6. **Access the Application**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000/api
   - API Documentation: http://localhost:8000/swagger/

## Services

### PostgreSQL
- **Port**: 5432
- **Volume**: postgres_data
- **Environment Variables**: DB_NAME, DB_USER, DB_PASSWORD

### Backend (Django)
- **Port**: 8000
- **Workers**: 3
- **Volumes**: static_volume, media_volume
- **Depends On**: postgres

### Frontend (React)
- **Port**: 80
- **Depends On**: backend
- **Nginx**: Serves static files and proxies API requests

### Redis
- **Port**: 6379
- **Purpose**: Caching and task queue (optional)

## Management Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
```

### Rebuild Services
```bash
docker-compose up -d --build
```

### Run Django Commands
```bash
# Database migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec backend python manage.py collectstatic

# Django shell
docker-compose exec backend python manage.py shell
```

### Database Operations
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U flood_detection -d flood_detection

# Backup database
docker-compose exec postgres pg_dump -U flood_detection flood_detection > backup.sql

# Restore database
docker-compose exec -T postgres psql -U flood_detection flood_detection < backup.sql
```

## Volumes

### postgres_data
Persistent storage for PostgreSQL database.

### static_volume
Shared volume for Django static files.

### media_volume
Shared volume for Django media files (uploads).

## Networks

### flood_detection_network
Bridge network for inter-service communication.

## Troubleshooting

### Service Won't Start

Check service logs:
```bash
docker-compose logs <service_name>
```

### Database Connection Issues

1. Check if PostgreSQL is running:
```bash
docker-compose ps postgres
```

2. Check database logs:
```bash
docker-compose logs postgres
```

3. Verify environment variables in .env file

### Port Conflicts

If ports are already in use, modify the ports in docker-compose.yml:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Permission Issues

Ensure proper permissions for volumes:
```bash
docker-compose down
sudo chown -R $USER:$USER ../backend/Django
docker-compose up -d
```

### Rebuild After Code Changes

After making changes to the code:
```bash
docker-compose down
docker-compose up -d --build
```

## Production Deployment

For production deployment:

1. **Use Environment Variables**
   - Never commit .env file
   - Use strong passwords
   - Generate secure SECRET_KEY

2. **Configure SSL/TLS**
   - Use reverse proxy (nginx/caddy)
   - Obtain SSL certificate (Let's Encrypt)
   - Enable HTTPS only

3. **Database Security**
   - Change default passwords
   - Restrict database access
   - Enable database backups

4. **Resource Limits**
   - Set memory limits in docker-compose.yml
   - Configure log rotation
   - Monitor resource usage

5. **Monitoring**
   - Enable health checks
   - Set up log aggregation
   - Configure alerts

## Backup and Restore

### Backup

```bash
# Backup database
docker-compose exec postgres pg_dump -U flood_detection flood_detection > backup_$(date +%Y%m%d).sql

# Backup volumes
docker run --rm -v flood_detection_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup_$(date +%Y%m%d).tar.gz /data
```

### Restore

```bash
# Restore database
docker-compose exec -T postgres psql -U flood_detection flood_detection < backup_20260713.sql

# Restore volumes
docker run --rm -v flood_detection_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup_20260713.tar.gz -C /
```

## Scaling

### Scale Backend Workers

```bash
docker-compose up -d --scale backend=5
```

### Add Load Balancer

For high availability, add a load balancer (nginx, HAProxy) in front of multiple backend instances.

## Updating

### Update Code

```bash
git pull origin main
docker-compose down
docker-compose up -d --build
```

### Update Dependencies

```bash
# Backend
docker-compose exec backend pip install --upgrade -r requirements.txt

# Frontend
docker-compose exec frontend npm update
```

## Security

### Best Practices

1. **Never commit .env file**
2. **Use strong passwords**
3. **Keep images updated**
4. **Scan for vulnerabilities**
5. **Limit container privileges**
6. **Use non-root users in containers**
7. **Enable read-only filesystems where possible**

### Security Scanning

```bash
# Scan Docker images
docker scan flood_detection_backend
docker scan flood_detection_frontend
```

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Review documentation in ../docs/
- Contact technical support

## License

See project LICENSE file.
