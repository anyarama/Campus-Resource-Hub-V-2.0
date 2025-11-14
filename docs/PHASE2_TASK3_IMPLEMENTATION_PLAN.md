# Phase 2 - Task 3: Resource Management Integration
## Implementation Plan

**Status:** 🟢 READY TO IMPLEMENT  
**Date:** 2025-11-13  
**Estimated Time:** 2-2.5 hours

---

## 📊 Discovery Summary

### ✅ What Exists
1. **Resources.tsx** - Beautiful UI with filters, search, grid layout (uses sample data)
2. **resourcesService.ts** - Complete API client methods:
   - `getResources()` - with filters
   - `getResource(id)` - single resource
   - `createResource()` - create new
   - `updateResource()` - edit existing
   - `deleteResource()` - delete
   - `uploadResourceImage()` - image upload
   - `getAvailableSlots()` - availability
   - `searchResources()` - search
3. **api/types.ts** - Complete type definitions matching backend:
   - `Resource` interface
   - `ResourceFilters` interface
   - `ResourceFormData` interface
   - `PaginatedResponse<T>` interface
4. **ResourceCard component** - Exists but uses different type structure
5. **App.tsx** - State-based routing (activePage state)
6. **AuthContext** - Authentication working with backend

### 🔧 What Needs Implementation
1. Connect Resources page to real backend API
2. Create resource creation modal/form
3. Create resource detail view/modal
4. Add resource editing modal
5. Implement delete confirmation
6. Wire up search/filter to API
7. Add loading states
8. Add error handling
9. Update/align ResourceCard with backend types

---

## 🗺️ Implementation Steps

### Step 1: Update Resources.tsx to Use Real API Data
**Priority:** HIGH  
**Estimated Time:** 30 minutes

**Changes:**
- Replace sample data with `useState` for resources
- Add `useEffect` to fetch resources on mount
- Call `getResources()` from resourcesService
- Add loading state (`isLoading`)
- Add error state (`error`)
- Handle pagination
- Update filter logic to call API with filters
- Update search to call API

**Files:**
- `Campus_Resource_hub/src/components/pages/Resources.tsx`

**Key Points:**
- Use existing filter state structure
- Map backend Resource type to UI display
- Handle image_url (backend) vs image (current UI)
- Show loading skeleton during fetch
- Show error message if fetch fails

---

### Step 2: Create Resource Creation Modal
**Priority:** HIGH  
**Estimated Time:** 30 minutes

**Changes:**
- Create `ResourceFormModal.tsx` component
- Form fields:
  - Name (text input, required)
  - Type (select: room, equipment, facility, other, required)
  - Description (textarea, optional)
  - Location (text input, required)
  - Capacity (number input, optional)
  - Available (checkbox, default true)
  - Campus (text input, optional)
  - Building (text input, optional)
  - Floor (text input, optional)
  - Hourly Rate (number input, optional)
  - Contact Email (email input, optional)
  - Amenities (multi-input or comma-separated, optional)
- Image upload section (file input)
- Validation
- Submit calls `createResource()`
- Then calls `uploadResourceImage()` if image selected
- Show success toast
- Refresh resource list
- Handle errors

**Files to Create:**
- `Campus_Resource_hub/src/components/modals/ResourceFormModal.tsx`

**Files to Update:**
- `Campus_Resource_hub/src/components/pages/Resources.tsx` - Add modal state, wire up "Create Resource" button

---

### Step 3: Create Resource Detail View
**Priority:** MEDIUM  
**Estimated Time:** 20 minutes

**Changes:**
- Create `ResourceDetailModal.tsx` component
- Display all resource details
- Show image
- Show amenities as badges
- Show availability status
- Show average rating (if available)
- "Edit" button (for staff/admin)
- "Delete" button (for admin)
- "Book Now" button (for students)
- Close button

**Files to Create:**
- `Campus_Resource_hub/src/components/modals/ResourceDetailModal.tsx`

**Files to Update:**
- `Campus_Resource_hub/src/components/pages/Resources.tsx` - Add modal state, wire up card click

---

### Step 4: Add Resource Editing
**Priority:** HIGH  
**Estimated Time:** 20 minutes

**Changes:**
- Reuse `ResourceFormModal` component
- Pass existing resource data as props
- Pre-populate form fields
- Change title to "Edit Resource"
- Submit calls `updateResource(id, data)`
- Handle image upload separately if changed
- Show success toast
- Refresh resource list

**Files to Update:**
- `Campus_Resource_hub/src/components/modals/ResourceFormModal.tsx` - Support edit mode
- `Campus_Resource_hub/src/components/pages/Resources.tsx` - Add edit handlers

---

### Step 5: Implement Delete Confirmation
**Priority:** MEDIUM  
**Estimated Time:** 15 minutes

**Changes:**
- Create or reuse confirmation dialog
- "Are you sure you want to delete [Resource Name]?"
- Explain consequences
- Cancel/Delete buttons
- Call `deleteResource(id)`
- Show success toast
- Refresh resource list
- Handle errors

**Files to Update:**
- `Campus_Resource_hub/src/components/pages/Resources.tsx` - Add delete handler
- May reuse existing Modal component for confirmation

---

### Step 6: Wire Up Search and Filters to API
**Priority:** HIGH  
**Estimated Time:** 20 minutes

**Changes:**
- Debounce search input (500ms)
- On search change, call `searchResources(query)`
- On filter apply, call `getResources(filters)`
- Combine search + filters properly
- Update URL params (optional, for shareable links)
- Show "No results" when empty
- Clear filters reload all resources

**Files to Update:**
- `Campus_Resource_hub/src/components/pages/Resources.tsx`

**Key Mapping:**
- UI category filter → backend `type` field
- UI location filter → backend `location` field
- UI availability filter → backend `available` boolean
- UI rating filter → needs to be handled in backend (may need to adjust)

---

### Step 7: Add Comprehensive Loading States
**Priority:** MEDIUM  
**Estimated Time:** 15 minutes

**Changes:**
- Loading skeleton for resource grid
- Loading spinner in modals during submit
- Disable buttons during operations
- Loading state for image upload
- Optimistic UI updates (optional)

**Files to Update:**
- `Campus_Resource_hub/src/components/pages/Resources.tsx`
- `Campus_Resource_hub/src/components/modals/ResourceFormModal.tsx`

---

### Step 8: Add Error Handling
**Priority:** HIGH  
**Estimated Time:** 15 minutes

**Changes:**
- Display error messages from API
- Toast notifications for errors
- Form validation errors
- Network error handling
- 401 errors redirect to login
- 403 errors show "Permission Denied"
- Retry mechanism for failed requests

**Files to Update:**
- All resource-related components

---

### Step 9: Update/Align Components with Backend Types
**Priority:** MEDIUM  
**Estimated Time:** 15 minutes

**Changes:**
- Update ResourceCard to accept backend Resource type
- Map fields properly:
  - `image_url` (backend) vs `image` (UI)
  - `name` (backend) vs `title` (UI)
  - `type` (backend) vs `category` (UI)
  - `available` (backend) vs `status` (UI - available/unavailable)
- Remove local Resource interface from ResourceCard
- Import from api/types.ts

**Files to Update:**
- `Campus_Resource_hub/src/components/ResourceCard.tsx`
- Any other components using Resource type

---

## 📁 Files to Create

```
Campus_Resource_hub/src/components/modals/
├── ResourceFormModal.tsx       # Create/Edit resource form
├── ResourceDetailModal.tsx     # View resource details
└── ConfirmDialog.tsx           # Generic confirmation dialog (if doesn't exist)
```

---

## 📝 Files to Update

```
Campus_Resource_hub/src/
├── components/
│   ├── ResourceCard.tsx                # Update types
│   ├── pages/
│   │   └── Resources.tsx               # Main integration work
│   └── modals/
│       └── ResourceFormModal.tsx       # Create/update resource
└── api/
    └── services/
        └── resourcesService.ts          # Already complete ✅
```

---

## 🔐 Security Considerations

1. **CSRF Protection** - Already handled by apiClient
2. **Image Upload Validation**:
   - Client-side: File type (jpg, png, webp)
   - Client-side: File size (< 5MB)
   - Server handles the rest
3. **Authorization**:
   - Only staff/admin can create resources
   - Only staff/admin can edit resources
   - Only admin can delete resources
   - Check user role from AuthContext
4. **Input Sanitization**:
   - All done by backend
   - Client validates formats only

---

## 🧪 Testing Checklist

### Manual Testing
- [ ] List resources from backend
- [ ] Search resources
- [ ] Filter by type
- [ ] Filter by location
- [ ] Filter by availability
- [ ] Create new resource (staff/admin)
- [ ] Upload resource image
- [ ] View resource details
- [ ] Edit existing resource
- [ ] Delete resource (admin only)
- [ ] Handle permission denied errors
- [ ] Handle network errors
- [ ] Test loading states
- [ ] Test empty states
- [ ] Test with no results

### Integration Testing
- [ ] CSRF tokens working on mutations
- [ ] Session maintained across operations
- [ ] Pagination working
- [ ] Filters persist correctly
- [ ] Search clears when filters change
- [ ] Images display correctly
- [ ] Toasts show for success/error

---

## 📊 Type Mappings

### Backend → Frontend Display

```typescript
Backend Resource {
  id: number                      → Display as resource ID
  name: string                    → Display as title/card title
  type: 'room' | 'equipment'...   → Display as category badge
  description: string             → Display in detail view
  location: string                → Display as location with pin icon
  capacity: number                → Display in detail view
  available: boolean              → Display as "Available"/"Unavailable" badge
  image_url: string               → Display as card image
  amenities: string[]             → Display as badges in detail
  hourly_rate: number             → Display as "$XX/hour"
  campus: string                  → Display in detail
  building: string                → Part of location display
  floor: string                   → Part of location display
  contact_email: string           → Display in detail
  created_at: string              → Display in detail (formatted)
  updated_at: string              → Display in detail (formatted)
}
```

### Filter Mappings

```typescript
UI Filters → Backend API Params
{
  categories: ['lab', 'library']  → type: 'lab' (single value in backend)
  location: 'wells'               → location: 'wells'
  availability: true              → available: true
  minRating: 4.5                  → (needs backend support or client filter)
  search: 'query'                 → search: 'query'
}
```

---

## 🚀 Implementation Order

1. **Step 1** - Update Resources.tsx to use API ⭐ (Foundation)
2. **Step 6** - Wire up search/filters ⭐ (Core feature)
3. **Step 7** - Add loading states ⭐ (UX)
4. **Step 8** - Add error handling ⭐ (Robustness)
5. **Step 9** - Update ResourceCard types (Cleanup)
6. **Step 2** - Create resource form (Feature)
7. **Step 4** - Add edit functionality (Feature)
8. **Step 3** - Resource detail view (Feature)
9. **Step 5** - Delete confirmation (Feature)

---

## ✅ Success Criteria

1. Resources page displays real data from backend
2. Search works and filters results
3. Filters work independently and combined
4. Staff can create new resources
5. Staff can edit resources they own
6. Admin can delete any resource
7. Image upload works correctly
8. Loading states show during operations
9. Errors display with helpful messages
10. CSRF protection works on all mutations
11. Pagination works (if needed)
12. No console errors
13. Types match between frontend and backend

---

## 📚 References

- **Backend API Docs:** `backend/API_DOCUMENTATION.md`
- **OpenAPI Spec:** `docs/api_surface/OpenAPI.yaml`
- **Resource Routes:** `backend/routes/resources.py`
- **Resource Service:** `backend/services/resource_service.py`
- **Test Examples:** `backend/tests/api/test_resources_api.py`

---

## 🎯 Next Steps

1. Review this plan
2. Confirm approach with user
3. Start with Step 1 (API integration)
4. Proceed sequentially through steps
5. Test after each major step
6. Create completion documentation

**Ready to begin implementation!** 🚀
