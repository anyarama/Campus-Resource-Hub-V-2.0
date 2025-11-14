# Login CORS Fix - URGENT

## Problem Identified
The login is failing with CORS errors even though `backend/extensions.py` includes `'http://localhost:4000'` in the allowed origins.

## Root Cause
The **backend Flask server needs to be manually restarted** to pick up the CORS configuration changes in `extensions.py`. The auto-reload feature doesn't always trigger for configuration changes.

## Browser Console Errors
```
Access to fetch at 'http://localhost:5001/api/auth/csrf-token' from origin 'http://localhost:4000' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```

## Solution - Manual Backend Restart

### Step 1: Stop the Current Backend Process
In the terminal running the backend (port 5001):
1. Press `Ctrl+C` to stop the Flask server
2. Wait for the process to fully terminate

### Step 2: Restart the Backend
Run this command in the terminal:
```bash
cd /Users/aneeshyaramati/Documents/GitHub/Campus-Resource-Hub-V-2.0 && FLASK_RUN_PORT=5001 PYTHONPATH=. python -m backend.app
```

### Step 3: Verify Backend Started
You should see output like:
```
 * Running on http://127.0.0.1:5001
 * Restarting with stat
```

### Step 4: Test Login Again
1. Go to `http://localhost:4000` in your browser
2. Enter credentials:
   - Email: `admin@iu.edu`
   - Password: `admin123`
3. Click "Sign In"
4. You should see "Signing in..." then redirect to `http://localhost:3000`

## What's Already Fixed (No Changes Needed)
✅ `backend/extensions.py` - Port 4000 added to CORS origins  
✅ `Campus_Resource_hub_login/.env` - Set to port 5001  
✅ `Campus_Resource_hub_login/src/api/client.ts` - CSRF token handling  
✅ `Campus_Resource_hub_login/src/api/services/authService.ts` - Redirect code exists  
✅ `Campus_Resource_hub_login/src/components/auth/LoginCard.tsx` - Real API call  

## Expected Behavior After Restart
1. CORS headers will be present in backend responses
2. CSRF token fetch will succeed (no errors)
3. Login POST request will complete successfully  
4. User will be redirected to `http://localhost:3000` after 1 second
5. Session cookie will be set for authentication

## Verification
After restarting, check the browser console - you should see NO CORS errors.
