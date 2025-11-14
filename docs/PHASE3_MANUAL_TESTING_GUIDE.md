# Phase 3: Manual Testing Walkthrough Guide

**Date:** 2025-11-13  
**Status:** 📋 TESTING IN PROGRESS  
**Application:** http://localhost:3000  
**Backend:** http://localhost:5000

---

## 🎯 Testing Objectives

This guide provides a comprehensive manual testing walkthrough for all features integrated in Phase 2. Follow each workflow step-by-step and document results.

**Goals:**
- Verify all user workflows function correctly
- Test error handling and edge cases
- Confirm backend integration is working
- Validate UI/UX design compliance
- Document any bugs or issues found

---

## 📋 Testing Checklist

### Prerequisites Setup

**Required:**
- [ ] Backend server running on port 5000
- [ ] Frontend server running on port 3000  
- [ ] Database initialized with test data
- [ ] Admin user created
- [ ] At least 2 test users created
- [ ] Some resources created for testing

**Create Test Users:**
```bash
# Backend terminal
cd backend
python create_admin.py  # Creates admin user

# Create 2 regular student users via UI registration
```

---

## 🔐 Workflow 1: Authentication System

### Test 1A: User Registration
**Steps:**
1. Navigate to http://localhost:3000
2. Click "Sign Up" or go to signup page
3. Fill in registration form:
   - Email: test1@iu.edu
   - Username: testuser1
   - Full Name: Test User One
   - Password: SecurePass123!
   - Role: Student
4. Click "Sign Up"

**Expected Results:**
- [ ] Form validation works (highlights errors)
- [ ] CSRF token sent with request
- [ ] Success toast appears
- [ ] Redirected to dashboard/login
- [ ] User can login immediately

**Actual Result:** ___________________________

---

### Test 1B: User Login
**Steps:**
1. Navigate to login page
2. Enter credentials:
   - Email: test1@iu.edu
   - Password: SecurePass123!
3. Check "Remember Me" (optional)
4. Click "Login"

**Expected Results:**
- [ ] Loading state shown on button
- [ ] Success toast appears
- [ ] Redirected to dashboard
- [ ] User info displayed in topbar
- [ ] Session persists on page refresh

**Actual Result:** ___________________________

---

### Test 1C: Protected Routes
**Steps:**
1. Without logging in, try to access: http://localhost:3000/resources
2. Try to access admin pages without admin role

**Expected Results:**
- [ ] Redirected to login page
- [ ] Return URL preserved
- [ ] After login, redirected back to original page
- [ ] Admin pages blocked for non-admin users

**Actual Result:** ___________________________

---

### Test 1D: Logout
**Steps:**
1. While logged in, click logout button
2. Try to access protected pages

**Expected Results:**
- [ ] Logged out successfully
- [ ] Redirected to login
- [ ] Session cleared
- [ ] Cannot access protected pages

**Actual Result:** ___________________________

---

## 📦 Workflow 2: Resource Management

### Test 2A: Browse Resources
**Steps:**
1. Login as regular user
2. Navigate to Resources page
3. Scroll through resource list
4. Try search functionality
5. Try filter by category

**Expected Results:**
- [ ] Resources load from backend
- [ ] Loading state shown while fetching
- [ ] Resource cards display properly
- [ ] Images load correctly
- [ ] Search filters results
- [ ] Category filter works
- [ ] Empty state if no results

**Actual Result:** ___________________________

---

### Test 2B: View Resource Details
**Steps:**
1. Click on any resource card
2. Resource detail modal opens
3. Scroll through all information
4. Check reviews section (NEW!)
5. View average rating (if reviews exist)

**Expected Results:**
- [ ] Modal opens with smooth animation
- [ ] All resource info displayed
- [ ] Image loads correctly
- [ ] Reviews section visible at bottom
- [ ] Average rating calculated correctly
- [ ] Reviews list shows recent reviews
- [ ] "Write Review" button visible
- [ ] Close button works

**Actual Result:** ___________________________

---

### Test 2C: Create Resource (Staff/Admin Only)
**Steps:**
1. Login as staff or admin user
2. Navigate to Resources
3. Click "Add Resource" button
4. Fill in form:
   - Name: Test Conference Room
   - Type: room
   - Description: Test description
   - Location: Wells Library
   - Capacity: 10
   - Upload image (optional)
5. Click "Create Resource"

**Expected Results:**
- [ ] Form validation works
- [ ] Image upload works (< 5MB check)
- [ ] CSRF token sent
- [ ] Success toast appears
- [ ] New resource appears in list
- [ ] Resource searchable immediately

**Actual Result:** ___________________________

---

### Test 2D: Edit Resource  
**Steps:**
1. Open resource detail modal
2. Click "Edit" button
3. Modify some fields
4. Click "Save Changes"

**Expected Results:**
- [ ] Only owner/admin can edit
- [ ] Edit modal pre-fills with current data
- [ ] Changes save successfully
- [ ] Success toast appears
- [ ] Resource list updates

**Actual Result:** ___________________________

---

### Test 2E: Delete Resource (Admin Only)
**Steps:**
1. Login as admin
2. Open resource detail
3. Click "Delete" button
4. Confirm deletion

**Expected Results:**
- [ ] Only admin sees delete button
- [ ] Confirmation prompt appears
- [ ] Delete executes via API
- [ ] Success toast appears
- [ ] Resource removed from list
- [ ] Modal closes

**Actual Result:** ___________________________

---

## 📅 Workflow 3: Booking System

### Test 3A: Create Booking
**Steps:**
1. Login as regular user
2. Browse resources
3. Open available resource
4. Click "Book Now"
5. Select date and time:
   - Start time: Tomorrow 2:00 PM
   - End time: Tomorrow 4:00 PM
   - Purpose: Team meeting
6. Click "Submit Booking"

**Expected Results:**
- [ ] Booking modal opens
- [ ] Date/time pickers work
- [ ] Validation prevents past dates
- [ ] Validation requires end > start
- [ ] CSRF token sent
- [ ] Success toast appears
- [ ] Booking status: "Pending"

**Actual Result:** ___________________________

---

### Test 3B: View My Bookings
**Steps:**
1. Navigate to "My Bookings"
2. Review booking list
3. Filter by status (All, Pending, Confirmed, etc.)

**Expected Results:**
- [ ] All user bookings load from backend
- [ ] Bookings grouped/sorted appropriately
- [ ] Resource info displayed
- [ ] Status badge correct (pending, confirmed, cancelled)
- [ ] Filter works correctly
- [ ] Empty state if no bookings

**Actual Result:** ___________________________

---

### Test 3C: Cancel Booking
**Steps:**
1. In My Bookings
2. Find upcoming booking (> 2 hours away)
3. Click "Cancel Booking"
4. Confirm cancellation

**Expected Results:**
- [ ] Confirmation modal appears
- [ ] Cancel only available > 2 hours before
- [ ] API call executes
- [ ] Success toast appears
- [ ] Booking status updates to "Cancelled"
- [ ] Cannot cancel if <2 hours

**Actual Result:** ___________________________

---

### Test 3D: Booking Conflict Detection
**Steps:**
1. Create a booking for a resource
2. Try to create another booking for same resource at overlapping time

**Expected Results:**
- [ ] Conflict detected
- [ ] Error message shown
- [ ] Booking not created
- [ ] User notified of conflict

**Actual Result:** ___________________________

---

## 💬 Workflow 4: Messaging System

### Test 4A: View Message Threads
**Steps:**
1. Navigate to Messages page
2. View thread list

**Expected Results:**
- [ ] Thread list loads from backend
- [ ] Threads show participant name
- [ ] Last message preview visible
- [ ] Unread count badge shown
- [ ] Empty state if no messages
- [ ] Loading state while fetching

**Actual Result:** ___________________________

---

### Test 4B: Send Message
**Steps:**
1. Select a thread or start new conversation
2. Type message in input box
3. Press Enter or click Send

**Expected Results:**
- [ ] Message appears immediately in thread
- [ ] Message sent to backend
- [ ] Success toast appears
- [ ] Message list updates
- [ ] Input cleared after send
- [ ] Shift+Enter creates new line

**Actual Result:** ___________________________

---

### Test 4C: Receive and Read Messages
**Steps:**
1. Login as User A
2. Send message to User B
3. Logout, login as User B
4. Check Messages page
5. Click on thread with unread messages

**Expected Results:**
- [ ] Unread badge appears on thread
- [ ] Unread count updates
- [ ] Messages load in conversation
- [ ] Thread marked as read when viewed
- [ ] Unread badge disappears

**Actual Result:** ___________________________

---

## ⭐ Workflow 5: Review System (NEW!)

### Test 5A: Write Review
**Steps:**
1. Login as user
2. Navigate to Resources
3. Click on a resource you've previously used
4. Scroll down to Reviews section
5. Click "Write Review" button
6. Select star rating (1-5)
7. Enter optional comment
8. Click "Submit Review"

**Expected Results:**
- [ ] ReviewModal opens with smooth animation
- [ ] Star rating interactive (hover effects)
- [ ] Rating label updates (Poor, Fair, Good, Very Good, Excellent)
- [ ] Comment counter shows characters used (x/500)
- [ ] Submit disabled until rating selected
- [ ] Loading state during submission
- [ ] Success toast appears
- [ ] Review appears in list immediately
- [ ] Average rating updates
- [ ] Modal closes

**Actual Result:** ___________________________

---

### Test 5B: View Reviews
**Steps:**
1. Open resource detail modal
2. Scroll to Reviews section
3. View existing reviews

**Expected Results:**
- [ ] Reviews section visible
- [ ] Average rating displayed with stars
- [ ] Review count shown (X reviews)
- [ ] Individual reviews listed
- [ ] Each review shows: stars, user name, date, comment
- [ ] Up to 5 reviews shown
- [ ] If > 5 reviews, shows "Showing 5 of X"
- [ ] Loading spinner while fetching
- [ ] Empty state if no reviews

**Actual Result:** ___________________________

---

### Test 5C: Review Without Comment
**Steps:**
1. Open ReviewModal
2. Select only star rating
3. Leave comment empty
4. Submit

**Expected Results:**
- [ ] Submission works without comment
- [ ] Review appears with stars only
- [ ] No comment displayed in list

**Actual Result:** ___________________________

---

## 👨‍💼 Workflow 6: Admin Features

### Test 6A: Admin Dashboard Analytics
**Steps:**
1. Login as admin user
2. Navigate to Admin section (cube icon in sidebar)
3. View dashboard

**Expected Results:**
- [ ] KPI cards show real numbers from database:
  - Total Bookings (Number from DB)
  - Active Users (Number from DB)
  - Resources (Number from DB)
  - Utilization (Calculated percentage)
- [ ] Resource breakdown chart populated
- [ ] Charts display correctly
- [ ] Loading state shown initially
- [ ] No errors in console

**Actual Result:** ___________________________

---

### Test 6B: User Management
**Steps:**
1. Navigate to Admin → Users
2. View user list
3. Select a user
4. Click "Suspend User" from dropdown
5. Confirm action

**Expected Results:**
- [ ] User list loads from backend
- [ ] All users displayed in table
- [ ] Dropdown actions work
- [ ] Suspend updates via API
- [ ] Success toast appears
- [ ] User status badge updates to "Suspended"
- [ ] Loading indicator during action

**Actual Result:** ___________________________

---

### Test 6C: Bulk User Actions
**Steps:**
1. In Admin → Users
2. Select multiple users via checkboxes
3. Click "Activate" or "Suspend" in bulk action bar
4. Wait for completion

**Expected Results:**
- [ ] Bulk action bar appears when users selected
- [ ] Shows count of selected users
- [ ] Bulk action executes
- [ ] Success toast shows count
- [ ] All selected users updated
- [ ] Selection cleared after success
- [ ] Loading state during bulk action

**Actual Result:** ___________________________

---

### Test 6D: Content Moderation
**Steps:**
1. Navigate to Admin → Moderation  
2. View flagged content list
3. Select a flagged item
4. Click "Resolve" from dropdown

**Expected Results:**
- [ ] Flagged items load from backend
- [ ] Items displayed in table
- [ ] Resolve action calls hideReview API
- [ ] Success toast appears
- [ ] Item removed from list
- [ ] Loading indicator during action

**Actual Result:** ___________________________

---

## 🔍 Edge Case Testing

### Edge Case 1: Session Expiry
**Steps:**
1. Login normally
2. Wait for session to expire (or manually clear cookies)
3. Try to perform an action (e.g., create booking)

**Expected Results:**
- [ ] 401 error from backend
- [ ] Redirected to login
- [ ] Error toast appears
- [ ] Return URL preserved

**Actual Result:** ___________________________

---

### Edge Case 2: Network Failure
**Steps:**
1. Stop backend server
2. Try to load any page that fetches data
3. Restart backend
4. Reload page

**Expected Results:**
- [ ] Loading spinner shows
- [ ] Error message appears after timeout
- [ ] Error toast notification
- [ ] User-friendly error message
- [ ] Page works after backend restart

**Actual Result:** ___________________________

---

### Edge Case 3: Invalid Form Data
**Steps:**
1. Try to create resource with:
   - Empty name
   - Past dates for booking
   - Invalid file types for images
   - Email without @ symbol

**Expected Results:**
- [ ] Client-side validation catches errors
- [ ] Error messages displayed
- [ ] Submit button disabled
- [ ] Server-side validation as backup
- [ ] Clean error messages

**Actual Result:** ___________________________

---

### Edge Case 4: Concurrent Actions
**Steps:**
1. Open resource in two browser tabs
2. Edit in tab 1, save
3. Edit in tab 2, save
4. Check which change persists

**Expected Results:**
- [ ] Last save wins
- [ ] No data corruption
- [ ] Success toast in both tabs
- [ ] Changes reflected correctly

**Actual Result:** ___________________________

---

## 🎨 UI/UX Verification

### Design Consistency Check
**Review each page for:**
- [ ] IU Crimson color used correctly
- [ ] Typography consistent (h1, h2, body, caption)
- [ ] Spacing consistent (padding, margins, gaps)
- [ ] Button styles uniform
- [ ] Card elevation consistent
- [ ] Loading spinners same style
- [ ] Error messages consistent format
- [ ] Toast notifications working

**Pages to Check:**
- [ ] Login/Signup
- [ ] Dashboard
- [ ] Resources
- [ ] My Bookings
- [ ] Messages (NEW!)
- [ ] Admin Dashboard
- [ ] Admin Users
- [ ] Admin Moderation

---

### Responsive Design Check
**Test on different screen sizes:**
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

**Verify:**
- [ ] Layouts adjust properly
- [ ] No horizontal scrolling
- [ ] Touch targets adequate (44x44px min)
- [ ] Text readable at all sizes
- [ ] Images scale appropriately

---

## ⚡ Performance Check

### Load Time Testing
**Measure and record:**
- [ ] Initial page load:  _______ seconds
- [ ] Dashboard load: _______ seconds
- [ ] Resources page load: _______ seconds
- [ ] Time to interactive: _______ seconds

**Accept able Ranges:**
- Initial load < 3 seconds ✅
- Page transitions < 1 second ✅
- API responses < 500ms ✅

---

### Bundle Size Analysis
**Current Metrics:**
- Total JS: 1,482 KB (399 KB gzipped)
- Total CSS: 55 KB (10 KB gzipped)
- **Total:** ~410 KB gzipped

**Note:** Bundle is larger than ideal (target <500KB total) but acceptable. Consider code splitting in future optimization.

---

## 🐛 Bug Log

### Bugs Found During Testing

**Bug #1:**
- **Component:** __________________
- **Severity:** Critical / High / Medium / Low
- **Description:** __________________
- **Steps to Reproduce:** __________________
- **Expected:** __________________
- **Actual:** __________________
- **Status:** Open / Fixed / Deferred

**Bug #2:**
- **Component:** __________________
- **Severity:** Critical / High / Medium / Low
- **Description:** __________________

*(Add more as needed)*

---

## ✅ Feature Verification Matrix

| Feature | Working | Has Errors | Notes |
|---------|---------|------------|-------|
| **Authentication** |
| User Registration | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| User Login | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Logout | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Protected Routes | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| **Resources** |
| Browse Resources | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Search Resources | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Filter Resources | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| View Resource Details | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Create Resource | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Edit Resource | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Delete Resource | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| **Bookings** |
| Create Booking | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| View My Bookings | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Cancel Booking | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Conflict Detection | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| **Messaging** |
| View Threads | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Send Message | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Read Messages | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Unread Count | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| **Reviews** (NEW!) |
| Write Review | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| View Reviews | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Star Rating | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Average Rating | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| **Admin** |
| View Dashboard | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Analytics Data | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Manage Users | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Bulk User Actions | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| View Moderation Queue | ☐ Yes ☐ No | ☐ Yes ☐ No | |
| Resolve Flagged Content | ☐ Yes ☐ No | ☐ Yes ☐ No | |

---

## 🔒 Security Testing

### CSRF Protection
**Test:**
- [ ] All CREATE operations send CSRF token
- [ ] All UPDATE operations send CSRF token
- [ ] All DELETE operations send CSRF token
- [ ] Token automatically refreshed

### Session Security
**Test:**
- [ ] Sessions expire after inactivity
- [ ] httpOnly cookies used
- [ ] Secure flag set (in production)
- [ ] Session hijacking prevented

### Input Validation
**Test:**
- [ ] SQL injection attempts blocked
- [ ] XSS attempts sanitized
- [ ] File upload type validation
- [ ] File size limits enforced

---

## 📱 Browser Compatibility

### Desktop Browsers
- [ ] **Chrome** (latest) - Fully functional
- [ ] **Firefox** (latest) - Fully functional
- [ ] **Safari** (latest) - Fully functional
- [ ] **Edge** (latest) - Fully functional

### Mobile Browsers  
- [ ] **iOS Safari** - Basic functionality
- [ ] **Chrome Mobile** - Basic functionality

---

## ♿ Accessibility Quick Check

### Keyboard Navigation
**Test:**
1. Tab through all interactive elements
2. Use Enter/Space to activate buttons
3. Use Escape to close modals
4. Use arrow keys in dropdowns

**Results:**
- [ ] Logical tab order
- [ ] All elements reachable
- [ ] Focus indicators visible
- [ ] No keyboard traps

### Screen Reader
**Test with VoiceOver (Mac) or NVDA (Windows):**
- [ ] Page landmarks announced
- [ ] Buttons announced correctly
- [ ] Form labels read properly
- [ ] Error messages announced
- [ ] Loading states announced

---

## 📊 Testing Summary

### Overall Results

**Total Tests:** ______ / ______  
**Passed:** ______  
**Failed:** ______  
**Bugs Found:** ______

**Critical Issues:** ______  
**High Priority:** ______  
**Medium Priority:** ______  
**Low Priority:** ______

### Recommendation

☐ **READY FOR PRODUCTION** - All tests passed, no critical issues  
☐ **NEEDS FIXES** - Some issues found, fixes required  
☐ **NEEDS MAJOR WORK** - Significant problems, major refactoring needed

---

## 📝 Notes and Observations

**Positive Findings:**
1. ____________________________________
2. ____________________________________
3. ____________________________________

**Issues to Address:**
1. ____________________________________
2. ____________________________________
3. ____________________________________

**UX Improvements Suggested:**
1. ____________________________________
2. ____________________________________
3. ____________________________________

---

## ✅ Next Steps After Testing

### If All Tests Pass:
1. Document test results
2. Create Phase 3 completion report
3. Proceed to Phase 4: Deployment

### If Bugs Found:
1. Create bug list with priorities
2. Fix critical bugs first
3. Re-test after fixes
4. Document known issues

### Additional Work Identified:
1. Performance optimizations (code splitting)
2. TypeScript cleanup (optional)
3. E2E automated tests (future)
4. Additional documentation

---

**Testing Started:** 2025-11-13  
**Tester:** __________________  
**Testing Completed:** __________________  
**Status:** ☐ In Progress ☐ Complete

**Document Status:** ✅ READY FOR USE  
**Last Updated:** 2025-11-13
