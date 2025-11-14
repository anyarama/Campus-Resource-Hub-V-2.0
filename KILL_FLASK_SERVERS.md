# How to Stop All Flask Instances

## Quick Method (Recommended)

### Option 1: Kill by Process Name
```bash
pkill -f "flask"
```

### Option 2: Kill Python Processes Running Flask
```bash
pkill -f "python -m backend.app"
```

### Option 3: Kill by Port (if Flask is running on port 5001)
```bash
lsof -ti:5001 | xargs kill -9
```

## Verify All Flask Processes Are Stopped
```bash
ps aux | grep flask
```
If nothing shows up (except the grep command itself), all Flask processes are stopped.

## Check What's Running on Port 5001
```bash
lsof -i :5001
```
Should return nothing if port is free.

## Complete Reset and Restart

### Step 1: Stop All Flask Instances
```bash
pkill -f "python -m backend.app"
```

### Step 2: Verify Port 5001 is Free
```bash
lsof -i :5001
```

### Step 3: Wait a moment
```bash
sleep 2
```

### Step 4: Start Fresh Backend
```bash
cd /Users/aneeshyaramati/Documents/GitHub/Campus-Resource-Hub-V-2.0 && FLASK_RUN_PORT=5001 PYTHONPATH=. python -m backend.app
```

## One-Line Command to Kill and Restart
```bash
pkill -f "python -m backend.app" && sleep 2 && cd /Users/aneeshyaramati/Documents/GitHub/Campus-Resource-Hub-V-2.0 && FLASK_RUN_PORT=5001 PYTHONPATH=. python -m backend.app
```

## If Everything Else Fails (Nuclear Option)
This will kill ALL Python processes (use with caution):
```bash
pkill -9 python
```

Then restart just the backend:
```bash
cd /Users/aneeshyaramati/Documents/GitHub/Campus-Resource-Hub-V-2.0 && FLASK_RUN_PORT=5001 PYTHONPATH=. python -m backend.app
```

## Expected Output After Restart
You should see:
```
 * Serving Flask app 'backend.app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5001
 * Restarting with stat
```

## Test the Backend is Running
```bash
curl http://localhost:5001/api/health
```

Should return: `{"status":"healthy"}`

## After Backend Restart - Test Login
1. Go to `http://localhost:4000`
2. Login with `admin@iu.edu` / `admin123`
3. Should redirect to `http://localhost:3000` (no CORS errors!)
