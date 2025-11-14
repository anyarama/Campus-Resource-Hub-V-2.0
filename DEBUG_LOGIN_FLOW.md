# Login Flow Debug Report

## Issue
User clicks "Sign In" → stuck at "Signing in..." → NO redirect to localhost:3000

## What's Working ✅
1. Login app connects to correct port (5001) - confirmed in logs
2. CSRF token fetched successfully (200 status)
3. CORS preflight passes (OPTIONS 200)
4. Redirect code EXISTS in authService.ts (line 15-19)

## What's NOT Working ❌
The POST request to `/auth/login` is NOT completing! 

Backend logs show:
```
127.0.0.1 - - [12/Nov/2025 16:18:04] "GET /api/auth/csrf-token HTTP/1.1" 200 -
127.0.0.1 - - [12/Nov/2025 16:18:04] "OPTIONS /api/auth/login HTTP/1.1" 200 -
```

Missing: `POST /api/auth/login HTTP/1.1` 

## Next Steps
1. Check browser console for JavaScript errors
2. Check if POST request is being sent at all
3. Check if credentials are correct (admin@iu.edu / admin123)
4. Check backend auth route for errors

## Hypothesis
The login POST is likely returning an error (400/401)  which means `response.data?.user` is null/undefined, so the redirect code never executes.
