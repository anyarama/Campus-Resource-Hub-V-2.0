# Campus Resource Hub - Deployment Guide

This guide covers deploying the Campus Resource Hub application using Docker, including both development and production environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Development Deployment](#development-deployment)
- [Production Deployment](#production-deployment)
- [Docker Commands](#docker-commands)
- [Troubleshooting](#troubleshooting)
- [Monitoring](#monitoring)

## Prerequisites

### Required Software
- Docker (v20.10+)
- Docker Compose (v2.0+)
- Git
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### System Requirements
- **Minimum**: 2 CPU cores, 4GB RAM, 10GB disk space
- **Recommended**: 4 CPU cores, 8GB RAM, 20GB disk space

## Environment Setup

### Backend Environment Variables

Create `/backend/.env` file:

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False

# Database
DATABASE_URL=sqlite:///./instance/dev.db

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://yourdomain.com

# Upload Configuration
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216

# Session Configuration
SESSION_TYPE=filesystem
PERMANENT_SESSION_LIFETIME=3600
```

### Frontend Environment Variables

Create `/Campus_Resource_hub/.env`:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:5000/api

# Environment
VITE_NODE_ENV=production
```

### Production Environment Variables

For production, create `.env` in the project root:

```bash
# Secret Key (REQUIRED - Generate a strong random key)
SECRET_KEY=<generate-using-python-secrets-token-hex>

# Database URL (for production, consider PostgreSQL)
DATABASE_URL=postgresql://user:password@postgres:5432/campus_hub

# API URL (your production domain)
PROD_API_URL=https://api.yourdomain.com
PROD_FRONTEND_URL=https://yourdomain.com
```

## Development Deployment

### Quick Start with Docker Compose

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Campus-Resource-Hub-V-2.0
   ```

2. **Configure environment variables**
   ```bash
   cp backend/.env.example backend/.env
   cp Campus_Resource_hub/.env.example Campus_Resource_hub/.env
   ```

3. **Build and start services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - API Health: http://localhost:5000/health
   - API Docs: http://localhost:5000/api/docs (if implemented)

### Initialize Database

The database is automatically initialized on first run. To manually reset:

```bash
# Access backend container
docker-compose exec backend sh

# Run migrations
flask db upgrade

# (Optional) Seed database
flask seed-db
```

### Local Development Without Docker

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade
flask run
```

#### Frontend
```bash
cd Campus_Resource_hub
npm install
npm run dev
```

## Production Deployment

### Option 1: Docker Compose with Nginx

1. **Update environment variables** for production

2. **Build production images**
   ```bash
   docker-compose -f docker-compose.yml --profile production build
   ```

3. **Start services with nginx**
   ```bash
   docker-compose --profile production up -d
   ```

4. **Configure SSL (recommended)**
   ```bash
   # Place SSL certificates in nginx/ssl/
   cp your-cert.crt nginx/ssl/
   cp your-key.key nginx/ssl/
   ```

### Option 2: Separate Deployment

#### Deploy Backend

```bash
cd backend
docker build -t campus-hub-backend:latest .
docker run -d \
  -p 5000:5000 \
  --name campus-hub-backend \
  --env-file .env \
  -v $(pwd)/instance:/app/instance \
  -v $(pwd)/static/uploads:/app/static/uploads \
  campus-hub-backend:latest
```

#### Deploy Frontend

```bash
cd Campus_Resource_hub
docker build -t campus-hub-frontend:latest .
docker run -d \
  -p 3000:80 \
  --name campus-hub-frontend \
  campus-hub-frontend:latest
```

### Option 3: Cloud Deployment

#### AWS (EC2 + RDS)
1. Launch EC2 instance (t3.medium recommended)
2. Set up RDS PostgreSQL database
3. Configure security groups (ports 80, 443, 5000)
4. Deploy using Docker Compose
5. Set up Application Load Balancer
6. Configure Route 53 for DNS

#### DigitalOcean (Droplet + Managed Database)
1. Create Droplet (4GB RAM recommended)
2. Set up Managed PostgreSQL database
3. Install Docker and Docker Compose
4. Clone repository and deploy
5. Configure firewall rules
6. Set up domain and SSL with Let's Encrypt

#### Heroku
```bash
# Backend
cd backend
heroku create campus-hub-api
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main

# Frontend
cd Campus_Resource_hub
npm run build
# Deploy dist folder to Netlify or Vercel
```

## Docker Commands

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stopping Services
```bash
# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Rebuilding Services
```bash
# Rebuild all
docker-compose up --build

# Rebuild specific service
docker-compose up --build backend
```

### Accessing Containers
```bash
# Backend shell
docker-compose exec backend sh

# Frontend shell (builder)
docker-compose exec frontend sh
```

### Database Management
```bash
# Backup database
docker-compose exec backend sh -c "sqlite3 instance/dev.db .dump" > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T backend sh -c "sqlite3 instance/dev.db"
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find and kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or change port in docker-compose.yml
ports:
  - "5001:5000"
```

#### 2. Database Connection Error
```bash
# Check if database file exists
docker-compose exec backend ls -l instance/

# Reinitialize database
docker-compose exec backend flask db upgrade
```

#### 3. CORS Errors
- Verify `CORS_ORIGINS` in backend/.env includes your frontend URL
- Check browser console for exact error
- Ensure backend/extensions.py CORS configuration is correct

#### 4. Frontend Can't Reach Backend
- Verify `VITE_API_BASE_URL` in frontend .env
- Check network connectivity between containers
- Inspect browser Network tab for failed requests

#### 5. Permission Denied (File uploads)
```bash
# Fix permissions on upload directory
docker-compose exec backend chmod -R 777 static/uploads
```

### Health Checks

```bash
# Backend health
curl http://localhost:5000/health

# Frontend health
curl http://localhost:3000

# Check container status
docker-compose ps
```

### Viewing Container Resource Usage
```bash
docker stats
```

## Monitoring

### Application Logs

Backend logs are available via Flask's logging system:
```bash
docker-compose logs -f backend | grep ERROR
```

### Performance Monitoring

Consider integrating:
- **Sentry** for error tracking
- **New Relic** or **DataDog** for APM
- **Prometheus + Grafana** for metrics
- **ELK Stack** for log aggregation

### Database Monitoring

```bash
# Check database size
docker-compose exec backend sh -c "du -h instance/dev.db"

# Monitor active connections (if using PostgreSQL)
docker-compose exec postgres psql -U user -d campus_hub -c "SELECT count(*) FROM pg_stat_activity;"
```

## Security Considerations

### Production Checklist
- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False` in production
- [ ] Use HTTPS with valid SSL certificates
- [ ] Configure firewall rules (allow only 80, 443)
- [ ] Set up database backups
- [ ] Enable database connection pooling
- [ ] Implement rate limiting
- [ ] Configure Content Security Policy headers
- [ ] Regular security updates for base images
- [ ] Use environment-specific .env files
- [ ] Implement log rotation
- [ ] Set up monitoring and alerting

### SSL Configuration

For production with Let's Encrypt:
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (cron)
0 12 * * * /usr/bin/certbot renew --quiet
```

## Backup Strategy

### Automated Backups

Create `/scripts/backup.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T backend sh -c "sqlite3 instance/dev.db .dump" > backups/db_$DATE.sql
find backups/ -name "db_*.sql" -mtime +7 -delete
```

Add to crontab:
```bash
0 2 * * * /path/to/scripts/backup.sh
```

## Scaling

### Horizontal Scaling
- Deploy multiple backend instances behind a load balancer
- Use shared PostgreSQL database
- Implement Redis for session management
- Use object storage (S3) for file uploads

### Vertical Scaling
- Increase container resource limits in docker-compose.yml
- Optimize database queries and add indexes
- Implement caching (Redis, Memcached)

## Support

For issues and questions:
- Check logs: `docker-compose logs`
- Review API documentation: `/backend/API_DOCUMENTATION.md`
- Open GitHub issue

---

**Last Updated**: January 2025  
**Version**: 2.0
