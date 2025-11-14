# Fix Login Redirect Issue - Solution

## Problem Diagnosed

After logging in at `localhost:3000`, you're being redirected to a duplicate login instance. 

**Root Cause:** The standalone login app (`Campus_Resource_hub_login`) at port 4000 has a redirect that sends users to port 3000. If port 4000 is still running or being accessed, it causes the duplicate login issue.

## Solution

### Step 1: Stop the Standalone Login App (Port 4000)

The standalone login app is no longer needed since the main app at port 3000 has its own login pages.

```bash
# Kill any process on port 4000
lsof -ti:4000 | xargs kill -9 2>/dev/null
echo "Port 4000 cleared"
```

### Step 2: Run ONLY the Main App (Port 3000)

```bash
# Start the main dashboard app
cd Campus_Resource_hub
npm run dev
```

This will run at `http://localhost:3000`

### Step 3: Access the App

**✅ Correct:** Open `http://localhost:3000` in your browser

**❌ Wrong:** Don't open `http://localhost:4000` (standalone login - not needed)

## What's Fixed

### Main App (Port 3000) - KEEP THIS RUNNING

- **Location:** `Campus_Resource_hub/`
- **Has:** Login page, Signup page, AND Dashboard
- **Behavior:** Login → Dashboard (stays at port 3000)
- **Status:** ✅ This is what you want

### Standalone Login App (Port 4000) - DON'T RUN THIS

- **Location:** `Campus_Resource_hub_login/`  
- **Has:** Only login/signup pages
- **Behavior:** Login → Redirects to port 3000
- **Status:** ❌ Not needed, causes duplicate login issue

## Verification Steps

1. **Stop everything**
   ```bash
   # Kill both ports
   lsof -ti:3000,4000 | xargs kill -9 2>/dev/null
   ```

2. **Start ONLY the main app**
   ```bash
   cd Campus_Resource_hub
   npm run dev
   ```

3. **Test login flow**
   - Open: `http://localhost:3000`
   - Should show: Login page
   - Login with: `admin@iu.edu` / `admin123`
   - Result: Should go directly to Dashboard at `localhost:3000`
   - ✅ NO redirect to port 4000

## Why This Happened

Previously, you had two separate apps:
1. Standalone login app (port 4000) - for authentication only
2. Main dashboard app (port 3000) - for the app features

We consolidated everything into ONE app at port 3000, but the standalone login app was still running/accessible, causing confusion.

## Current App Structure (Port 3000 Only)

```
Campus_Resource_hub/  (Port 3000)
├── Login Page         ← /login
├── Signup Page        ← /signup  
└── Dashboard          ← /dashboard (after login)
    ├── Resources
    ├── Bookings
    ├── Messages
    ├── Admin
    └── etc.
```

The app automatically:
- Shows login page if not authenticated
- Shows dashboard if authenticated
- NO external redirects
- Everything at port 3000

## Commands Summary

```bash
# 1. Stop everything
lsof -ti:3000,4000 | xargs kill -9 2>/dev/null

# 2. Start main app only
cd Campus_Resource_hub && npm run dev

# 3. Open browser to http://localhost:3000

# 4. Login and verify it stays at localhost:3000/dashboard
```

## If Issue Persists

1. **Clear browser cache/cookies** - Old sessions might interfere
2. **Check browser URL** - Make sure it says `localhost:3000` not `localhost:4000`
3. **Verify only one Vite server is running** - Should only see one process on port 3000

---

**Status:** Issue identified and solution provided  
**Action Required:** Stop port 4000, use only port 3000  
**Expected Result:** Login at port 3000 → Dashboard at port 3000 (no redirects)
