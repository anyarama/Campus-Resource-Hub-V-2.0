# Phase 2 Task 5: API Gaps Analysis

## Messages API - Frontend vs Backend Comparison

### Frontend Service (messagesService.ts)
```typescript
GET /messages/threads           - Get user's message threads
GET /messages/threads/:threadId - Get messages in a thread
POST /messages                  - Send a new message
PUT /messages/:id/read          - Mark message as read
PUT /messages/threads/:threadId/read - Mark thread as read
GET /messages/unread-count      - Get unread message count
```

### Backend Routes (messages.py)
```python
GET  /api/messages              - List all message threads
GET  /api/messages/thread/:threadId - Get thread messages
POST /api/messages              - Send a new message
PUT  /api/messages/:id/read     - Mark message as read
GET  /api/messages/unread-count - Get unread message count
GET  /api/messages/search       - Search messages (EXTRA)
```

### Identified Gaps
1. ✅ **Path mismatch for threads**: Frontend uses `/messages/threads` but backend uses `/messages`
2. ❌ **Missing endpoint**: Frontend expects `PUT /messages/threads/:threadId/read` but backend doesn't have it
3. ✅ **Thread detail path mismatch**: Frontend uses `/messages/threads/:threadId` but backend uses `/messages/thread/:threadId`

---

## Reviews API - Frontend vs Backend Comparison

### Frontend Service (reviewsService.ts)
```typescript
GET  /reviews                   - Get paginated list with filters
GET  /reviews/:id               - Get review by ID
GET  /reviews/resource/:resourceId - Get reviews for a resource
POST /reviews                   - Create new review
PUT  /reviews/:id               - Update review
DELETE /reviews/:id             - Delete review
POST /reviews/:id/flag          - Flag review as inappropriate
```

### Backend Routes (reviews.py)
```python
GET    /api/reviews/resources/:resourceId/reviews - Get resource reviews
POST   /api/reviews             - Create review
PUT    /api/reviews/:id         - Update review
DELETE /api/reviews/:id         - Delete review
POST   /api/reviews/:id/flag    - Flag review
GET    /api/reviews/my-reviews  - Get user's reviews (EXTRA)
```

### Identified Gaps
1. ✅ **Resource reviews path mismatch**: Frontend uses `/reviews/resource/:resourceId` but backend uses `/reviews/resources/:resourceId/reviews`
2. ❌ **Missing endpoint**: Frontend expects `GET /reviews` (all reviews) - backend doesn't have it
3. ❌ **Missing endpoint**: Frontend expects `GET /reviews/:id` (single review) - backend doesn't have it

---

## Resolution Strategy

### Messages Service Fixes
1. ✅ **Update frontend paths** to match backend:
   - Change `/messages/threads` → `/messages`
   - Change `/messages/threads/:threadId` → `/messages/thread/:threadId`
2. ⚠️ **Handle missing endpoint**: Remove `markThreadAsRead()` or implement workaround

### Reviews Service Fixes
1. ✅ **Update frontend path**:
   - Change `/reviews/resource/:resourceId` → `/reviews/resources/:resourceId/reviews`
2. ⚠️ **Handle missing endpoints**:
   - `getReviews()` might not be needed (each resource shows its own reviews)
   - `getReview(id)` might not be needed (reviews shown inline)
   - Consider removing these methods from frontend service

### Next Steps
1. Update messagesService.ts with corrected paths
2. Update reviewsService.ts with corrected paths
3. Create Messages page component
4. Create Review modal component
5. Test complete integration

---

## Notes
- Backend uses `/api` prefix which is handled by `apiClient.ts` base URL
- Backend has extra endpoints (search, my-reviews) that frontend can leverage
- Some frontend methods may not be needed if UX doesn't require them
