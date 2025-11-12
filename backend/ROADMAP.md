# Campus Resource Hub Backend - Development Roadmap

## ✅ COMPLETED PHASES

### Phase 1: Flask Backend Scaffold ✅
- Project structure
- Configuration management
- Extensions setup
- Health check endpoint
- Development environment

### Phase 2: Database Models & Migrations ✅
- User model with authentication
- Resource model
- Booking model with status workflow
- Message model with threading
- Review model with moderation
- Database migrations applied

### Phase 3: Authentication & Authorization ✅
- User registration and login
- Password hashing with bcrypt
- Session management with Flask-Login
- RBAC middleware (role-based access control)
- Profile management endpoints
- Password change functionality

---

## 📋 UPCOMING PHASES

### Phase 4: Resources Management (NEXT)
**Estimated Time: 3-4 hours**

**Files to Create:**
- `backend/data_access/resource_repository.py` - Resource CRUD operations
- `backend/services/resource_service.py` - Business logic for resources
- `backend/routes/resources.py` - Resource endpoints

**Endpoints to Implement:**
1. `GET /api/resources` - List all resources (with filters, pagination)
2. `GET /api/resources/:id` - Get resource details
3. `POST /api/resources` - Create new resource (authenticated, owner only)
4. `PUT /api/resources/:id` - Update resource (owner or admin)
5. `DELETE /api/resources/:id` - Delete resource (owner or admin)
6. `GET /api/resources/search` - Search resources
7. `GET /api/resources/categories` - List available categories

**Key Features:**
- Image upload handling
- Availability rules (JSON storage)
- Category filtering
- Location-based search
- Status management (draft → published → archived)
- Owner permissions enforcement

---

### Phase 5: Bookings System
**Estimated Time: 4-5 hours**

**Files to Create:**
- `backend/data_access/booking_repository.py`
- `backend/services/booking_service.py`
- `backend/routes/bookings.py`

**Endpoints to Implement:**
1. `GET /api/bookings` - List user's bookings
2. `GET /api/bookings/:id` - Get booking details
3. `POST /api/bookings` - Create new booking
4. `PUT /api/bookings/:id/approve` - Approve booking (staff/admin)
5. `PUT /api/bookings/:id/reject` - Reject booking (staff/admin)
6. `PUT /api/bookings/:id/cancel` - Cancel booking (requester)
7. `GET /api/bookings/conflicts` - Check for booking conflicts
8. `GET /api/resources/:id/availability` - Get resource availability calendar

**Key Features:**
- Conflict detection (no overlapping bookings)
- Approval workflow (pending → approved/rejected)
- Calendar integration
- Email notifications (optional)
- Booking history
- Cancellation with reasons

---

### Phase 6: Messaging System
**Estimated Time: 3-4 hours**

**Files to Create:**
- `backend/data_access/message_repository.py`
- `backend/services/message_service.py`
- `backend/routes/messages.py`

**Endpoints to Implement:**
1. `GET /api/messages` - List user's messages (threads)
2. `GET /api/messages/thread/:threadId` - Get thread messages
3. `POST /api/messages` - Send new message
4. `PUT /api/messages/:id/read` - Mark message as read
5. `GET /api/messages/unread-count` - Get unread message count
6. `GET /api/messages/search` - Search messages

**Key Features:**
- Thread-based conversations
- Read/unread status
- Association with bookings and resources
- Real-time updates (optional with WebSockets)
- Message search

---

### Phase 7: Reviews System
**Estimated Time: 2-3 hours**

**Files to Create:**
- `backend/data_access/review_repository.py`
- `backend/services/review_service.py`
- `backend/routes/reviews.py`

**Endpoints to Implement:**
1. `GET /api/resources/:id/reviews` - Get resource reviews
2. `POST /api/reviews` - Submit review (after booking completed)
3. `PUT /api/reviews/:id` - Update review (reviewer only)
4. `DELETE /api/reviews/:id` - Delete review (reviewer or admin)
5. `POST /api/reviews/:id/flag` - Flag inappropriate review
6. `GET /api/reviews/my-reviews` - Get user's reviews

**Key Features:**
- 1-5 star rating system
- Rating validation (CHECK constraint)
- Review moderation (flagging)
- Automatic average rating calculation
- One review per booking limit
- Review editing within timeframe

---

### Phase 8: Admin Dashboard Endpoints
**Estimated Time: 3-4 hours**

**Files to Create:**
- `backend/routes/admin.py`
- `backend/services/admin_service.py`

**Endpoints to Implement:**
1. `GET /api/admin/users` - List and manage users
2. `PUT /api/admin/users/:id/role` - Update user role
3. `PUT /api/admin/users/:id/status` - Suspend/activate user
4. `GET /api/admin/resources` - Moderate resources
5. `GET /api/admin/reviews/flagged` - View flagged reviews
6. `PUT /api/admin/reviews/:id/hide` - Hide inappropriate reviews
7. `GET /api/admin/analytics` - Get system analytics
8. `GET /api/admin/reports` - Generate reports

**Key Features:**
- User management (roles, status)
- Content moderation
- System analytics
- Usage statistics
- Activity logs

---

### Phase 9: Advanced Features (Optional)
**Estimated Time: 5-8 hours**

**Potential Features:**
1. **Email Notifications**
   - Booking confirmations
   - Approval/rejection notifications
   - Message notifications
   - Review notifications

2. **File Uploads**
   - Resource images
   - Profile pictures
   - Document attachments
   - File size and type validation

3. **Search & Filters**
   - Full-text search
   - Advanced filtering
   - Sorting options
   - Saved searches

4. **Calendar Integration**
   - iCal export
   - Google Calendar sync
   - Availability visualization

5. **AI Features** (Per project requirements)
   - Resource recommendations
   - Smart search
   - Automated categorization
   - Chatbot support

---

### Phase 10: Testing & Documentation
**Estimated Time: 4-6 hours**

**Tasks:**
1. **Unit Tests**
   - Test all service methods
   - Test repository methods
   - Mock database interactions

2. **Integration Tests**
   - Test full API endpoints
   - Test authentication flows
   - Test permission enforcement

3. **API Documentation**
   - OpenAPI/Swagger documentation
   - Postman collection
   - Example requests/responses

4. **Code Quality**
   - Run `ruff` linter
   - Run `black` formatter
   - Run `mypy` type checker
   - Code coverage report

---

### Phase 11: Deployment Preparation
**Estimated Time: 3-4 hours**

**Tasks:**
1. **Production Configuration**
   - Environment variable validation
   - Security hardening
   - HTTPS enforcement
   - Rate limiting

2. **Database Migration**
   - PostgreSQL setup
   - Migration scripts
   - Database backups

3. **Deployment**
   - Heroku/Railway/DigitalOcean setup
   - CI/CD pipeline
   - Docker containerization (optional)
   - Monitoring setup

---

## 🎯 Recommended Next Steps

**Immediate Priority (Phase 4):**
Start with Resources Management as it's the core functionality. Once users can create and browse resources, everything else builds on top of it.

**Command to Start Phase 4:**
```bash
# Create the necessary files
mkdir -p backend/data_access backend/services backend/routes

# Begin with resource repository
touch backend/data_access/resource_repository.py
touch backend/services/resource_service.py
touch backend/routes/resources.py
```

---

## 📊 Progress Tracker

- [x] Phase 1: Flask Backend Scaffold
- [x] Phase 2: Database Models & Migrations  
- [x] Phase 3: Authentication & Authorization
- [ ] Phase 4: Resources Management (NEXT)
- [ ] Phase 5: Bookings System
- [ ] Phase 6: Messaging System
- [ ] Phase 7: Reviews System
- [ ] Phase 8: Admin Dashboard
- [ ] Phase 9: Advanced Features (Optional)
- [ ] Phase 10: Testing & Documentation
- [ ] Phase 11: Deployment Preparation

---

## 🔗 Dependencies Between Phases

```
Phase 1 (Scaffold)
    ↓
Phase 2 (Models)
    ↓
Phase 3 (Auth) ← You are here
    ↓
Phase 4 (Resources) ← Start here next
    ↓
Phase 5 (Bookings) ← Depends on Resources
    ↓
Phase 6 (Messages) ← Can be parallel with Phase 7
Phase 7 (Reviews)  ← Depends on Bookings
    ↓
Phase 8 (Admin) ← Needs all previous phases
    ↓
Phase 9 (Advanced) ← Optional enhancements
    ↓
Phase 10 (Testing) ← Should be ongoing
Phase 11 (Deployment) ← Final step
```

---

## 💡 Tips for Success

1. **Test as you go** - Don't wait until the end to test endpoints
2. **Follow the pattern** - Use the same repository → service → routes pattern
3. **Keep security in mind** - Always use RBAC decorators appropriately
4. **Document AI usage** - Save prompts to `.prompt/` directory per project requirements
5. **Commit frequently** - Use git to track progress after each phase

---

## 🏁 Project Completion Checklist

- [ ] All CRUD operations implemented
- [ ] All relationships working correctly
- [ ] Authentication flows tested
- [ ] Authorization properly enforced
- [ ] Input validation comprehensive
- [ ] Error handling robust
- [ ] API documentation complete
- [ ] Unit tests written
- [ ] Integration tests passing
- [ ] Code quality checks passing (ruff, black, mypy)
- [ ] AI usage documented in `.prompt/`
- [ ] Ready for production deployment

---

**Total Estimated Time Remaining:** 25-35 hours (Phases 4-11)

**Ready to proceed with Phase 4: Resources Management?**
