# Backend API Integration - Complete Guide

## Overview

Successfully integrated Django REST Framework with JWT authentication into the Trackly project, providing a full REST API for the React frontend.

## 🔧 Backend Changes

### 1. Packages Installed
```bash
pip install djangorestframework djangorestframework-simplejwt django-cors-headers django-filter
```

### 2. Django Settings (`config/settings/base.py`)

**Added to INSTALLED_APPS:**
- `rest_framework`
- `rest_framework_simplejwt`
- `corsheaders`
- `django_filter`

**Added to MIDDLEWARE:**
- `corsheaders.middleware.CorsMiddleware` (before CommonMiddleware)

**REST Framework Configuration:**
```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

**JWT Configuration:**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}
```

**CORS Configuration:**
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Vite dev server
    'http://127.0.0.1:3000',
]
CORS_ALLOW_CREDENTIALS = True
```

### 3. API Serializers Created

**Tracker App (`tracker/serializers.py`):**
- `ApplicationListSerializer` - Lightweight for list views
- `ApplicationDetailSerializer` - Full details with nested relationships
- `ApplicationCreateUpdateSerializer` - For create/update operations
- `QuestionSerializer`
- `ResponseSerializer`
- `TagSerializer`
- `NoteSerializer`
- `InterviewSerializer`
- `ReferralSerializer`
- `ApplicationStatusSerializer`

**Documents App (`documents/serializers.py`):**
- `DocumentListSerializer`
- `DocumentDetailSerializer`
- `DocumentUploadSerializer` - With file validation
- `ExtractedInformationSerializer`

**Notifications App (`notifications/serializers.py`):**
- `NotificationSerializer`
- `ReminderSerializer`

**Accounts App (`accounts/serializers.py`):**
- `UserSerializer`
- `UserProfileSerializer`
- `UserRegistrationSerializer`
- `UserUpdateSerializer`
- `ChangePasswordSerializer`

### 4. API ViewSets Created

**Tracker App (`tracker/api_views.py`):**
- `ApplicationViewSet` - Full CRUD + custom actions
  - `stats()` - Get application statistics
  - `change_status()` - Change application status
- `QuestionViewSet`
- `ResponseViewSet`
- `TagViewSet`
- `NoteViewSet`
- `InterviewViewSet`
- `ReferralViewSet`

**Documents App (`documents/api_views.py`):**
- `DocumentViewSet` - Upload, view, delete documents
  - `upload()` - Custom upload action
  - `extracted_info()` - Get extracted document info

**Notifications App (`notifications/api_views.py`):**
- `NotificationViewSet`
  - `unread()` - Get unread notifications
  - `mark_read()` - Mark single notification as read
  - `mark_all_read()` - Mark all as read
- `ReminderViewSet`

**Accounts App (`accounts/api_views.py`):**
- `UserRegistrationView` - Register new users
- `UserProfileView` - View/update profile
- `ChangePasswordView` - Change password
- `current_user()` - Get current authenticated user

### 5. API URL Structure

All API endpoints are prefixed with `/api/`:

**Authentication:**
- `POST /api/auth/login/` - Login (get JWT tokens)
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/verify/` - Verify token
- `POST /api/auth/register/` - Register new user
- `GET /api/auth/me/` - Get current user
- `GET/PATCH /api/auth/profile/` - View/update profile
- `PUT /api/auth/change-password/` - Change password

**Applications:**
- `GET/POST /api/applications/` - List/create applications
- `GET/PATCH/DELETE /api/applications/{id}/` - Retrieve/update/delete
- `GET /api/applications/stats/` - Get statistics
- `POST /api/applications/{id}/change_status/` - Change status

**Questions & Responses:**
- `GET/POST /api/questions/`
- `GET/PATCH/DELETE /api/questions/{id}/`
- `GET/POST /api/responses/`
- `GET/PATCH/DELETE /api/responses/{id}/`

**Documents:**
- `GET /api/documents/` - List documents
- `POST /api/documents/upload/` - Upload document
- `GET /api/documents/{id}/` - Get document details
- `DELETE /api/documents/{id}/` - Delete document
- `GET /api/documents/{id}/extracted_info/` - Get extracted info

**Notifications:**
- `GET /api/notifications/` - List all notifications
- `GET /api/notifications/unread/` - Get unread only
- `POST /api/notifications/{id}/mark_read/` - Mark as read
- `POST /api/notifications/mark_all_read/` - Mark all as read
- `DELETE /api/notifications/{id}/` - Delete notification

**Reminders:**
- `GET/POST /api/reminders/`
- `GET/PATCH/DELETE /api/reminders/{id}/`

**Tags, Notes, Interviews, Referrals:**
- Similar CRUD endpoints for each resource

### 6. Django URL Configuration

Updated `config/urls.py` to:
1. Include API routes at `/api/`
2. Serve React app for all non-API routes (catch-all)
3. Keep legacy Django template routes for backward compatibility

### 7. Static Files Configuration

Updated to serve React build:
```python
TEMPLATES = [
    {
        "DIRS": [
            BASE_DIR / 'templates',
            BASE_DIR / 'frontend' / 'dist',  # React build
        ],
    },
]

STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'frontend' / 'dist' / 'assets',  # React assets
]
```

## 🎨 Frontend Changes

### 1. Dependencies Installed
```bash
npm install axios
```

### 2. API Client (`frontend/src/lib/api.ts`)

Created axios instance with:
- Base URL configuration
- JWT token injection via interceptors
- Automatic token refresh on 401 errors
- Request/response error handling

### 3. API Services

**Auth Service (`services/auth.ts`):**
- `login()` - Authenticate and store tokens
- `register()` - Register new user
- `logout()` - Clear tokens
- `getCurrentUser()` - Get user details
- `isAuthenticated()` - Check auth status
- `updateProfile()` - Update user profile
- `changePassword()` - Change password

**Applications Service (`services/applications.ts`):**
- `getAll()` - List applications with filters
- `getById()` - Get single application
- `create()` - Create new application
- `update()` - Update application
- `delete()` - Delete application
- `getStats()` - Get statistics
- `changeStatus()` - Update status

**Documents Service (`services/documents.ts`):**
- `getAll()` - List documents
- `getById()` - Get document details
- `upload()` - Upload new document
- `delete()` - Delete document
- `getExtractedInfo()` - Get extracted data

**Notifications Service (`services/notifications.ts`):**
- `getAll()` - List all notifications
- `getUnread()` - Get unread only
- `markRead()` - Mark single as read
- `markAllRead()` - Mark all as read
- `delete()` - Delete notification

### 4. Authentication Context

Created `AuthContext` with:
- Global auth state management
- User authentication functions
- Protected route logic
- Persistent auth across page reloads

### 5. Updated Components

**App.tsx:**
- Wrapped in `AuthProvider`
- Created `ProtectedRoute` component
- Real authentication checks
- Loading states

**Next Steps (To Complete):**
- Update Login page to use `authService.login()`
- Update Dashboard to fetch real data from `applicationsService.getStats()`
- Update Applications page to use `applicationsService.getAll()`
- Update Documents page to use `documentsService`
- Update Notifications page to use `notificationsService`
- Update Profile page to use `authService.updateProfile()`
- Add error handling and loading states to all pages

## 🚀 Running the Full Stack

### Development

**Terminal 1 - Django Backend:**
```bash
python manage.py runserver
# Runs on http://localhost:8000
```

**Terminal 2 - React Frontend:**
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

### Production Build

```bash
# Build React app
cd frontend
npm run build

# Collect static files
python manage.py collectstatic --noinput

# Run Django (serves both API and React app)
gunicorn config.wsgi:application
```

## 📝 API Response Formats

### Success Response
```json
{
  "id": 1,
  "field": "value"
}
```

### Error Response
```json
{
  "error": "Error message",
  "details": {}
}
```

### List Response (Paginated)
```json
{
  "count": 100,
  "next": "http://api/endpoint/?page=2",
  "previous": null,
  "results": []
}
```

## 🔒 Authentication Flow

1. **Login:**
   - POST credentials to `/api/auth/login/`
   - Receive `access` and `refresh` tokens
   - Store tokens in localStorage
   - Store user in localStorage

2. **Authenticated Requests:**
   - Include `Authorization: Bearer {access_token}` header
   - API interceptor adds this automatically

3. **Token Refresh:**
   - On 401 error, try to refresh using refresh token
   - POST refresh token to `/api/auth/refresh/`
   - Get new access token
   - Retry failed request

4. **Logout:**
   - Clear tokens from localStorage
   - Redirect to login page

## ✅ Completed

- ✅ Django REST Framework setup
- ✅ JWT authentication configuration
- ✅ CORS configuration
- ✅ All API serializers
- ✅ All API viewsets
- ✅ API URL routing
- ✅ Django serving React build
- ✅ React API client (axios)
- ✅ All API services
- ✅ Authentication context
- ✅ Protected routes

## ⏳ To Complete

- ⏳ Update Login page with real auth
- ⏳ Update all pages to use real API calls
- ⏳ Add error handling UI
- ⏳ Add loading states
- ⏳ Test full-stack integration
- ⏳ Update Sidebar logout functionality

## 🧪 Testing

**Test API Endpoints:**
```bash
# Get JWT token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Use token
curl http://localhost:8000/api/applications/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Test in Browser:**
1. Start Django: `python manage.py runserver`
2. Start React: `cd frontend && npm run dev`
3. Open http://localhost:3000
4. Login should connect to Django API

---

**Result**: Full REST API backend ready to power the React frontend! 🎉
