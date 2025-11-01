# Database Models Documentation

This document provides comprehensive documentation for all database models in the Job & Scholarship Tracker application.

## Table of Contents

1. [Accounts App](#accounts-app)
2. [Documents App](#documents-app)
3. [Tracker App](#tracker-app)
4. [Notifications App](#notifications-app)
5. [Model Relationships](#model-relationships)

---

## Accounts App

### User Model
**File**: `/home/user/job_and_scholarship_tracker/accounts/models.py`

Custom user model extending Django's `AbstractUser`. Uses email as the primary identifier instead of username.

**Fields**:
- `email` (EmailField, unique): Primary authentication identifier
- `first_name` (CharField): User's first name
- `last_name` (CharField): User's last name
- `is_staff` (BooleanField): Admin access flag
- `is_active` (BooleanField): Account activation status
- `date_joined` (DateTimeField): Account creation timestamp

**Custom Manager**: `CustomUserManager`
- `create_user(email, password, **extra_fields)`: Creates regular user
- `create_superuser(email, password, **extra_fields)`: Creates admin user

**Meta Options**:
- Ordering: `-date_joined` (newest first)
- Verbose names: 'user', 'users'

**Methods**:
- `__str__()`: Returns email
- `get_full_name()`: Returns full name or email if name is empty

**Settings Configuration**:
```python
AUTH_USER_MODEL = 'accounts.User'
```

---

### UserProfile Model
**File**: `/home/user/job_and_scholarship_tracker/accounts/models.py`

Extended profile with additional user information.

**Fields**:
- `user` (OneToOneField → User, primary_key): Associated user
- `phone_number` (CharField, max_length=20, optional): Contact number
- `current_position` (CharField, max_length=200, optional): Job title or student status
- `linkedin_url` (URLField, max_length=500, optional): LinkedIn profile
- `github_url` (URLField, max_length=500, optional): GitHub profile
- `portfolio_url` (URLField, max_length=500, optional): Personal website
- `bio` (TextField, optional): Professional biography
- `created_at` (DateTimeField, auto_now_add): Profile creation timestamp
- `updated_at` (DateTimeField, auto_now): Last update timestamp

**Meta Options**:
- Ordering: `-created_at`
- Verbose names: 'user profile', 'user profiles'

**Methods**:
- `__str__()`: Returns "Profile for {user's full name}"

**Relationship**: One-to-One with User (CASCADE delete)

---

## Documents App

### Document Model
**File**: `/home/user/job_and_scholarship_tracker/documents/models.py`

Stores user-uploaded documents (resumes, transcripts, certificates).

**Fields**:
- `user` (ForeignKey → User, CASCADE): Document owner
- `document_type` (CharField, choices): Type of document
  - `resume`: Resume
  - `transcript`: Transcript
  - `certificate`: Certificate
  - `other`: Other
- `file` (FileField): Uploaded file (stored in `documents/user_<id>/`)
- `original_filename` (CharField, max_length=255): Original filename
- `uploaded_at` (DateTimeField, auto_now_add): Upload timestamp
- `file_size` (PositiveIntegerField, optional): File size in bytes
- `is_processed` (BooleanField, default=False): Processing status
- `processed_at` (DateTimeField, optional): Processing timestamp

**Meta Options**:
- Ordering: `-uploaded_at`
- Indexes:
  - `(user, document_type)`
  - `(is_processed)`
  - `(user, is_processed)`

**Methods**:
- `__str__()`: Returns "{document type} - {filename}"
- `save()`: Auto-populates original_filename and file_size

**Properties**:
- `file_size_mb`: Returns file size in megabytes

**Relationship**: Many-to-One with User (CASCADE delete)

---

### ExtractedInformation Model
**File**: `/home/user/job_and_scholarship_tracker/documents/models.py`

Stores AI-extracted information from documents.

**Fields**:
- `document` (ForeignKey → Document, CASCADE): Source document
- `data_type` (CharField, choices): Type of extracted data
  - `name`: Name
  - `email`: Email
  - `education`: Education
  - `experience`: Work Experience
  - `skills`: Skills
  - `certifications`: Certifications
- `content` (JSONField): Extracted data in JSON format
- `confidence_score` (FloatField, default=0.0): Extraction confidence (0.0 to 1.0)
- `extracted_at` (DateTimeField, auto_now_add): Extraction timestamp

**Meta Options**:
- Ordering: `-extracted_at`
- Indexes:
  - `(document, data_type)`
  - `(data_type)`

**Methods**:
- `__str__()`: Returns "{data type} from {filename}"

**Properties**:
- `confidence_percentage`: Returns confidence as percentage

**Relationship**: Many-to-One with Document (CASCADE delete)

---

## Tracker App

### Application Model
**File**: `/home/user/job_and_scholarship_tracker/tracker/models.py`

Core model for tracking job and scholarship applications.

**Fields**:
- `user` (ForeignKey → User, CASCADE): Application owner
- `application_type` (CharField, choices): Application category
  - `job`: Job Application
  - `scholarship`: Scholarship Application
- `title` (CharField, max_length=200): Job title or scholarship name
- `company_or_institution` (CharField, max_length=200): Organization name
- `url` (URLField, max_length=500, optional): Application URL
- `description` (TextField, optional): Full description
- `deadline` (DateTimeField, optional): Application deadline
- `status` (CharField, choices, default='draft'): Current status
  - `draft`: Draft
  - `submitted`: Submitted
  - `in_review`: In Review
  - `interview`: Interview
  - `offer`: Offer
  - `rejected`: Rejected
  - `withdrawn`: Withdrawn
- `priority` (CharField, choices, default='medium'): Priority level
  - `high`: High
  - `medium`: Medium
  - `low`: Low
- `created_at` (DateTimeField, auto_now_add): Creation timestamp
- `updated_at` (DateTimeField, auto_now): Last update timestamp
- `submitted_at` (DateTimeField, optional): Submission timestamp
- `notes` (TextField, optional): Additional notes

**Meta Options**:
- Ordering: `-created_at`
- Indexes:
  - `(user, status)`
  - `(deadline)`
  - `(created_at)`
  - `(user, application_type)`

**Methods**:
- `__str__()`: Returns "{title} at {company/institution}"

**Properties**:
- `is_overdue`: Returns True if deadline passed and status is draft/in_review
- `days_until_deadline`: Returns days remaining until deadline

**Relationship**: Many-to-One with User (CASCADE delete)

---

### Question Model
**File**: `/home/user/job_and_scholarship_tracker/tracker/models.py`

Stores application questions and prompts.

**Fields**:
- `application` (ForeignKey → Application, CASCADE): Parent application
- `question_text` (TextField): Question content
- `question_type` (CharField, choices, default='custom'): Question category
  - `short_answer`: Short Answer
  - `essay`: Essay
  - `experience`: Work Experience
  - `education`: Education
  - `skills`: Skills
  - `custom`: Custom
- `is_required` (BooleanField, default=False): Required field flag
- `is_extracted` (BooleanField, default=False): Auto-extracted flag
- `order` (PositiveIntegerField, default=0): Display order
- `created_at` (DateTimeField, auto_now_add): Creation timestamp

**Meta Options**:
- Ordering: `['application', 'order', 'created_at']`
- Indexes:
  - `(application, order)`

**Methods**:
- `__str__()`: Returns "Q{order}: {first 50 chars}..."

**Relationship**: Many-to-One with Application (CASCADE delete)

---

### Response Model
**File**: `/home/user/job_and_scholarship_tracker/tracker/models.py`

Stores responses to application questions.

**Fields**:
- `question` (OneToOneField → Question, CASCADE): Associated question
- `generated_response` (TextField, optional): AI-generated response
- `edited_response` (TextField, optional, nullable): User-edited response
- `is_ai_generated` (BooleanField, default=False): AI generation flag
- `generation_prompt` (TextField, optional): Prompt used for AI generation
- `generated_at` (DateTimeField, optional): AI generation timestamp
- `last_edited_at` (DateTimeField, optional): Last edit timestamp
- `version` (PositiveIntegerField, default=1): Version number

**Meta Options**:
- Ordering: `['question']`

**Methods**:
- `__str__()`: Returns "Response to: {first 30 chars}..."
- `save()`: Auto-updates version and last_edited_at on edits

**Properties**:
- `final_response`: Returns edited_response if available, else generated_response

**Relationship**: One-to-One with Question (CASCADE delete)

---

### ApplicationStatus Model
**File**: `/home/user/job_and_scholarship_tracker/tracker/models.py`

Tracks application status changes over time (audit trail).

**Fields**:
- `application` (ForeignKey → Application, CASCADE): Parent application
- `status` (CharField, choices): New status value (same choices as Application.status)
- `changed_by` (CharField, choices, default='manual'): Change source
  - `manual`: Manual Update
  - `ai_detected`: AI Detected
  - `user_update`: User Update
- `notes` (TextField, optional): Change notes
- `created_at` (DateTimeField, auto_now_add): Change timestamp

**Meta Options**:
- Ordering: `-created_at`
- Indexes:
  - `(application, -created_at)`

**Methods**:
- `__str__()`: Returns "{title} - {status} ({date})"

**Relationship**: Many-to-One with Application (CASCADE delete)

---

## Notifications App

### Reminder Model
**File**: `/home/user/job_and_scholarship_tracker/notifications/models.py`

Scheduled reminders for applications.

**Fields**:
- `user` (ForeignKey → User, CASCADE): User to remind
- `application` (ForeignKey → Application, CASCADE): Related application
- `reminder_type` (CharField, choices, default='custom'): Reminder category
  - `deadline`: Deadline Reminder
  - `follow_up`: Follow-up Reminder
  - `interview`: Interview Reminder
  - `custom`: Custom Reminder
- `message` (TextField): Reminder message
- `scheduled_for` (DateTimeField): Scheduled send time
- `is_sent` (BooleanField, default=False): Send status
- `sent_at` (DateTimeField, optional): Actual send timestamp
- `created_at` (DateTimeField, auto_now_add): Creation timestamp

**Custom Manager**: `ReminderManager`
- `pending()`: Returns unsent reminders scheduled for now or earlier
- `upcoming(hours=24)`: Returns reminders scheduled within X hours

**Meta Options**:
- Ordering: `['scheduled_for']`
- Indexes:
  - `(user, is_sent)`
  - `(scheduled_for)`
  - `(is_sent, scheduled_for)`

**Methods**:
- `__str__()`: Returns "{reminder type} for {application title}"
- `mark_as_sent()`: Marks reminder as sent with timestamp

**Properties**:
- `is_overdue`: Returns True if scheduled time passed without being sent

**Relationships**:
- Many-to-One with User (CASCADE delete)
- Many-to-One with Application (CASCADE delete)

---

### Notification Model
**File**: `/home/user/job_and_scholarship_tracker/notifications/models.py`

User notifications for various system events.

**Fields**:
- `user` (ForeignKey → User, CASCADE): User to notify
- `notification_type` (CharField, choices): Notification category
  - `reminder`: Reminder
  - `status_change`: Status Change
  - `system`: System Notification
- `title` (CharField, max_length=200): Notification title
- `message` (TextField): Notification content
- `link` (URLField, max_length=500, optional, nullable): Related URL
- `is_read` (BooleanField, default=False): Read status
- `created_at` (DateTimeField, auto_now_add): Creation timestamp
- `read_at` (DateTimeField, optional): Read timestamp

**Custom Manager**: `NotificationManager`
- `unread()`: Returns unread notifications
- `recent(days=7)`: Returns notifications from last X days

**Meta Options**:
- Ordering: `-created_at`
- Indexes:
  - `(user, is_read)`
  - `(user, -created_at)`

**Methods**:
- `__str__()`: Returns "{title} for {user email}"
- `mark_as_read()`: Marks notification as read with timestamp

**Properties**:
- `time_since_created`: Returns human-readable time since creation

**Relationship**: Many-to-One with User (CASCADE delete)

---

## Model Relationships

### Entity Relationship Diagram

```
User (accounts.User)
├── 1:1 → UserProfile (accounts.UserProfile)
├── 1:N → Document (documents.Document)
├── 1:N → Application (tracker.Application)
├── 1:N → Reminder (notifications.Reminder)
└── 1:N → Notification (notifications.Notification)

Application (tracker.Application)
├── 1:N → Question (tracker.Question)
├── 1:N → ApplicationStatus (tracker.ApplicationStatus)
└── 1:N → Reminder (notifications.Reminder)

Document (documents.Document)
└── 1:N → ExtractedInformation (documents.ExtractedInformation)

Question (tracker.Question)
└── 1:1 → Response (tracker.Response)
```

### Relationship Summary

1. **User Relationships**:
   - One User has one UserProfile (OneToOne)
   - One User can have many Documents (ForeignKey)
   - One User can have many Applications (ForeignKey)
   - One User can have many Reminders (ForeignKey)
   - One User can have many Notifications (ForeignKey)

2. **Application Relationships**:
   - One Application belongs to one User (ForeignKey)
   - One Application can have many Questions (ForeignKey)
   - One Application can have many ApplicationStatus records (ForeignKey)
   - One Application can have many Reminders (ForeignKey)

3. **Document Relationships**:
   - One Document belongs to one User (ForeignKey)
   - One Document can have many ExtractedInformation records (ForeignKey)

4. **Question/Response Relationships**:
   - One Question belongs to one Application (ForeignKey)
   - One Question has one Response (OneToOneField)

### Database Indexes

All models include strategic indexes for optimal query performance:

- **User-based queries**: Most models have indexes on user foreign keys
- **Status filtering**: Application and notification models have status indexes
- **Time-based queries**: Timestamp fields are indexed where frequently queried
- **Compound indexes**: Multi-field indexes for common query patterns (e.g., user+status)

### Delete Behavior

All foreign key relationships use `CASCADE` delete behavior:
- Deleting a User deletes all associated records across all apps
- Deleting an Application deletes all questions, responses, statuses, and reminders
- Deleting a Document deletes all extracted information
- Deleting a Question deletes its response

This ensures referential integrity and prevents orphaned records.

---

## Usage Examples

### Creating a User and Profile

```python
from accounts.models import User, UserProfile

# Create user
user = User.objects.create_user(
    email='john@example.com',
    password='secure_password',
    first_name='John',
    last_name='Doe'
)

# Create profile
profile = UserProfile.objects.create(
    user=user,
    current_position='Software Engineer',
    linkedin_url='https://linkedin.com/in/johndoe',
    bio='Experienced developer seeking new opportunities'
)
```

### Creating an Application with Questions

```python
from tracker.models import Application, Question, Response

# Create application
app = Application.objects.create(
    user=user,
    application_type='job',
    title='Senior Python Developer',
    company_or_institution='Tech Corp',
    deadline='2025-12-31 23:59:59',
    status='draft',
    priority='high'
)

# Add question
question = Question.objects.create(
    application=app,
    question_text='Why do you want to work here?',
    question_type='essay',
    is_required=True,
    order=1
)

# Add response
response = Response.objects.create(
    question=question,
    generated_response='AI-generated answer here...',
    is_ai_generated=True
)
```

### Querying with Custom Managers

```python
from notifications.models import Notification, Reminder

# Get unread notifications
unread = Notification.objects.unread()

# Get recent notifications
recent = Notification.objects.recent(days=7)

# Get pending reminders
pending = Reminder.objects.pending()

# Get upcoming reminders
upcoming = Reminder.objects.upcoming(hours=48)
```

---

## Migration Status

All models have been migrated successfully:

- **accounts.0001_initial**: User and UserProfile models
- **documents.0001_initial**: Document and ExtractedInformation models
- **tracker.0001_initial**: Application, Question, Response, and ApplicationStatus models
- **notifications.0001_initial**: Reminder and Notification models

Database is ready for use with all models and indexes created.
