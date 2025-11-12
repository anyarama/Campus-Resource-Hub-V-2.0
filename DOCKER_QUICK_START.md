# 🐳 Docker Quick Start Guide

## ✅ Docker Build In Progress

Your containers are currently building in the background! This process typically takes 3-5 minutes on first run.

## Check Build Progress

```bash
# See what's happening (in a new terminal)
docker-compose ps

# View build logs
docker-compose logs -f
```

## Once Build Completes

### 1. Check Container Status
```bash
docker-compose ps
```

You should see:
- `campus-hub-backend` - Status: Up
- `campus-hub-frontend` - Status: Up

### 2. Access Your Application

🌐 **Frontend**: http://localhost:3000  
🔧 **Backend API**: http://localhost:5000  
❤️ **Health Check**: http://localhost:5000/health

### 3. View Logs
```bash
# All services
docker-compose logs -f

# Just backend
docker-compose logs -f backend

# Just frontend
docker-compose logs -f frontend
```

## Common Commands

### Stop Containers
```bash
docker-compose down
```

### Restart
```bash
docker-compose restart
```

### Rebuild After Code Changes
```bash
docker-compose up --build
```

### See Resource Usage
```bash
docker stats
```

## Testing the API

Once running, test backend:
```bash
# Health check
curl http://localhost:5000/health

# Should return:
# {"message": "Campus Resource Hub API is running!", "status": "healthy"}
```

## Troubleshooting

### If Build Fails
```bash
# Clean everything and retry
docker-compose down -v
docker-compose up --build
```

### Port Already in Use
```bash
# Find what's using port 5000
lsof -ti:5000 | xargs kill -9

# Or edit docker-compose.yml to use different port
```

### View Container Details
```bash
# Inspect backend container
docker inspect campus-hub-backend

# Access backend shell
docker-compose exec backend sh
```

## What's Running

Your Docker setup includes:

1. **Backend Container**:
   - Flask API on port 5000
   - Auto-migrates database on startup
   - Health checks every 30s
   - Auto-restarts on failure

2. **Frontend Container**:
   - React app built with Vite
   - Nginx web server on port 3000
   - Serves production bun

dle
   - Gzip compression enabled

3. **Docker Network**:
   - Isolated network for containers
   - Backend and frontend can communicate
   - Secure by default

4. **Persistent Volumes**:
   - Database persists across restarts
   - Uploaded files persist  
- Only deleted with `docker-compose down -v`

## Next Steps

1. ✅ **Wait for build to complete** (shows in terminal)
2. ✅ **Check containers are running**: `docker-compose ps`
3. ✅ **Access frontend**: http://localhost:3000
4. ✅ **Test backend**: http://localhost:5000/health

---

**Note**: First build downloads Docker images and installs dependencies. This takes 3-5 minutes. Subsequent builds are much faster (cached).

## Current Build Status

Your bui ld is progressing through these stages:

- [x] Pulling base images (Python, Node, Nginx)
- [⏳] Installing backend dependencies
- [⏳] Installing frontend dependencies  
- [ ] Building frontend
- [ ] Starting services

**Watch the terminal for completion!**
