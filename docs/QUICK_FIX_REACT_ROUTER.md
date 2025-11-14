# Quick Fix: Missing react-router-dom Dependency

## Error
```
Failed to resolve import "react-router-dom" from "src/components/pages/Signup.tsx"
```

## Solution

Run this command manually:

```bash
cd Campus_Resource_hub
npm install react-router-dom
```

## Why This Happened

The Login.tsx and Signup.tsx pages we just created use `useNavigate` from react-router-dom for navigation between pages, but the dependency wasn't installed yet.

## After Installing

The app should start successfully with `npm run dev`.

## Alternative: Remove Router Dependency Temporarily

If you want to test without react-router-dom, you can modify the pages to not use useNavigate:

**Login.tsx** - Replace:
```typescript
import { useNavigate } from 'react-router-dom';
const navigate = useNavigate();
const handleNavigateToSignUp = () => {
  navigate('/signup');
};
```

With:
```typescript
const handleNavigateToSignUp = () => {
  window.location.href = '/signup'; // Simple navigation
};
```

**Signup.tsx** - Same change.

But installing react-router-dom is the proper solution since the app will need routing anyway.

---

## All Required Dependencies

Make sure these are all installed in `Campus_Resource_hub/package.json`:

```json
{
  "dependencies": {
    "react": "^18.x",
    "react-dom": "^18.x",
    "react-router-dom": "^6.x"
  }
}
```

Install command:
```bash
cd Campus_Resource_hub
npm install react react-dom react-router-dom
```

---

**Once installed, `npm run dev` should work!**
