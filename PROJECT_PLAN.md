# Project Plan - Job & Scholarship Tracker Platform

## Executive Summary
A comprehensive web platform that automates job and scholarship application management by extracting questions from application URLs, generating AI-powered responses based on user documents, and monitoring application progress through email integration.

---

## 1. System Architecture

### 1.1 High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  (Django Templates + Bootstrap/HTMX for dynamic updates)    │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                     Application Layer                        │
│                    (Django Views & APIs)                     │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   Auth App   │ Tracker App  │Document App  │Notification App│
└──────────────┴──────────────┴──────────────┴────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                     Service Layer                            │
├──────────────┬──────────────┬──────────────┬────────────────┤
│Web Scraping  │Document Parse│  LLM Service │  Email Service │
└──────────────┴──────────────┴──────────────┴────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                     Data Layer                               │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  PostgreSQL  │    Redis     │  File Storage│   Task Queue   │
│  (Database)  │   (Cache)    │   (S3/Local) │   (Celery)     │
└──────────────┴──────────────┴──────────────┴────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                  External Services                           │
├──────────────┬──────────────┬──────────────────────────────┤
│  Gmail API   │  LLM API     │        Monitoring            │
│ (Email Data) │(Claude/GPT)  │    (Sentry/Logging)          │
└──────────────┴──────────────┴──────────────────────────────┘
```

### 1.2 Application Structure
```
job_and_scholarship_tracker/
├── config/                    # Main project configuration
│   ├── settings/
│   │   ├── base.py           # Base settings
│   │   ├── development.py    # Dev settings
│   │   └── production.py     # Production settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── accounts/             # User authentication & profiles
│   ├── tracker/              # Application tracking
│   ├── documents/            # Document management
│   ├── notifications/        # Notifications & reminders
│   └── core/                 # Shared utilities
├── services/                 # Business logic services
│   ├── scraper/             # Web scraping service
│   ├── parser/              # Document parsing service
│   ├── llm/                 # LLM integration service
│   └── email/               # Email integration service
├── static/                   # Static files (CSS, JS, images)
├── media/                    # User uploaded files
├── templates/                # HTML templates
├── tests/                    # Test suites
└── requirements/             # Dependencies
    ├── base.txt
    ├── development.txt
    └── production.txt
```

---

## 2. Technology Stack

### 2.1 Backend
- **Framework**: Django 4.2.19
- **API**: Django REST Framework (for future mobile apps)
- **Task Queue**: Celery 5.3+
- **Message Broker**: Redis 5.0+
- **Database**: PostgreSQL 15+ (production), SQLite (development)
- **Web Server**: Gunicorn + Nginx (production)

### 2.2 Frontend
- **Template Engine**: Django Templates
- **CSS Framework**: Bootstrap 5 or Tailwind CSS
- **JavaScript**: Vanilla JS + HTMX (for dynamic updates without complex framework)
- **Icons**: Font Awesome or Bootstrap Icons

### 2.3 Document Processing
- **PDF Parsing**: pdfplumber (better than PyPDF2 for complex layouts)
- **DOCX Parsing**: python-docx
- **OCR**: pytesseract + Pillow
- **Text Processing**: spaCy (for NLP)

### 2.4 Web Scraping
- **Primary**: Playwright (handles JavaScript-rendered content)
- **Fallback**: BeautifulSoup4 + requests (for simple static pages)
- **User Agent Rotation**: fake-useragent

### 2.5 LLM Integration
- **Primary**: Anthropic Claude API (Claude 3.5 Sonnet)
  - Reason: Better at following instructions, structured output
- **Alternative**: OpenAI GPT-4
- **Rate Limiting**: Custom implementation to stay within quotas

### 2.6 Email Integration
- **Gmail API**: google-api-python-client
- **Authentication**: OAuth2 (google-auth-oauthlib)
- **Email Parsing**: email library (built-in)

### 2.7 Production Tools
- **Caching**: Redis
- **Monitoring**: Sentry (error tracking)
- **Logging**: Python logging + file rotation
- **Environment Variables**: python-decouple
- **Static Files**: WhiteNoise
- **File Storage**: Django's FileSystemStorage (start), AWS S3 (scale)

---

## 3. Database Schema

### 3.1 Core Models

#### User (extends Django's AbstractUser)
```python
- id (PK)
- email (unique)
- first_name
- last_name
- date_joined
- is_active
- gmail_connected (boolean)
- gmail_refresh_token (encrypted)
- notification_preferences (JSON)
```

#### UserProfile
```python
- id (PK)
- user (FK to User, OneToOne)
- phone_number
- current_position
- linkedin_url
- github_url
- portfolio_url
- bio
- created_at
- updated_at
```

#### Document
```python
- id (PK)
- user (FK to User)
- document_type (resume/transcript/certificate/other)
- file (FileField)
- original_filename
- uploaded_at
- file_size
- is_processed (boolean)
- processed_at
```

#### ExtractedInformation
```python
- id (PK)
- document (FK to Document)
- data_type (name/email/education/experience/skills/certifications)
- content (JSON) # Structured extracted data
- confidence_score (float)
- extracted_at
```

#### Application
```python
- id (PK)
- user (FK to User)
- application_type (job/scholarship)
- title
- company_or_institution
- url (original application URL)
- description
- deadline
- status (draft/submitted/in_review/interview/offer/rejected/withdrawn)
- priority (high/medium/low)
- created_at
- updated_at
- submitted_at
- notes
```

#### Question
```python
- id (PK)
- application (FK to Application)
- question_text
- question_type (short_answer/essay/experience/education/skills/custom)
- is_required (boolean)
- is_extracted (boolean) # True if auto-extracted, False if manually added
- order
- created_at
```

#### Response
```python
- id (PK)
- question (FK to Question, OneToOne)
- generated_response (text)
- edited_response (text, nullable)
- is_ai_generated (boolean)
- generation_prompt (text) # Store prompt used for debugging
- generated_at
- last_edited_at
- version (integer) # For version control
```

#### ApplicationStatus
```python
- id (PK)
- application (FK to Application)
- status (same choices as Application.status)
- changed_by (manual/email_detected/user_update)
- notes
- created_at
```

#### EmailMessage
```python
- id (PK)
- user (FK to User)
- application (FK to Application, nullable)
- gmail_message_id (unique)
- subject
- sender
- body
- received_at
- is_application_related (boolean)
- is_processed (boolean)
- detected_status_change
- fetched_at
```

#### Reminder
```python
- id (PK)
- user (FK to User)
- application (FK to Application)
- reminder_type (deadline/follow_up/interview/custom)
- message
- scheduled_for
- is_sent (boolean)
- sent_at
- created_at
```

#### Notification
```python
- id (PK)
- user (FK to User)
- notification_type (reminder/status_change/email_received/system)
- title
- message
- link (URL to relevant page)
- is_read (boolean)
- created_at
- read_at
```

### 3.2 Indexes
- User.email (unique)
- Application.user + Application.status (composite)
- Application.deadline
- EmailMessage.gmail_message_id (unique)
- EmailMessage.user + EmailMessage.received_at (composite)
- Notification.user + Notification.is_read (composite)

---

## 4. Core Workflows

### 4.1 User Registration & Authentication Flow
```
1. User visits signup page
2. User fills registration form (email, password, name)
3. System creates user account
4. System sends verification email
5. User clicks verification link
6. Account activated → redirect to dashboard
7. User can log in with email/password
```

### 4.2 Document Upload & Processing Flow
```
1. User uploads document (resume/transcript/certificate)
2. System validates file (type, size)
3. System saves file to storage
4. Background task (Celery) processes document:
   a. Extract text based on file type
   b. Parse structured information using NLP
   c. Store in ExtractedInformation model
   d. Mark document as processed
5. User can view extracted information
6. User can edit/correct extracted information
```

### 4.3 Application Creation Flow (Core Feature)
```
1. User submits application URL
2. System validates URL
3. Background task scrapes the page:
   a. Fetch page content (Playwright for dynamic, BS4 for static)
   b. Extract job/scholarship title, company, description
   c. Extract deadline if present
   d. Use NLP/LLM to identify questions
   e. Classify question types
   f. Store in Application and Question models
4. System retrieves user's extracted document information
5. For each question:
   a. Build context (question + user's info)
   b. Call LLM API with structured prompt
   c. Generate response
   d. Store in Response model
6. User sees dashboard with:
   - Application details
   - Extracted questions
   - Generated responses
7. User can:
   - Add more questions manually
   - Edit generated responses
   - Mark application as submitted
```

### 4.4 Gmail Integration Flow
```
1. User initiates Gmail connection from settings
2. System redirects to Google OAuth consent screen
3. User grants permissions (read Gmail)
4. System receives authorization code
5. System exchanges code for access/refresh tokens
6. System stores encrypted refresh token
7. Background task (every hour):
   a. Fetch new emails using Gmail API
   b. Parse email content
   c. Detect if email is application-related (keywords, sender matching)
   d. Link email to existing application if match found
   e. Extract status updates from email content
   f. Update ApplicationStatus if status change detected
   g. Create notification for user
8. User sees linked emails on application detail page
```

### 4.5 Status Tracking & Reminders Flow
```
1. User creates application with deadline
2. System creates automatic reminders:
   - 1 week before deadline
   - 1 day before deadline
3. Background task (Celery Beat - runs daily):
   a. Check for reminders due today
   b. Create Notification for each reminder
   c. Send email if user has email notifications enabled
   d. Mark reminder as sent
4. User receives notification
5. User can manually update application status
6. System records status change in ApplicationStatus
7. If status changed via email detection:
   - System creates notification
   - User sees update on dashboard
```

---

## 5. AI/LLM Integration Strategy

### 5.1 Response Generation Pipeline
```python
def generate_response(question, user_documents):
    # 1. Gather context
    extracted_info = get_all_extracted_info(user_documents)

    # 2. Build prompt
    prompt = f"""
    You are helping a user answer an application question.

    Question: {question.question_text}
    Question Type: {question.question_type}

    User's Information:
    {format_user_info(extracted_info)}

    Generate a professional, tailored response that:
    - Directly answers the question
    - Uses specific examples from the user's background
    - Is appropriate in length for the question type
    - Maintains a professional tone

    Response:
    """

    # 3. Call LLM API
    response = call_claude_api(prompt)

    # 4. Store response
    save_response(question, response, prompt)

    return response
```

### 5.2 Question Extraction from URLs
```python
def extract_questions_from_url(url):
    # 1. Scrape page
    page_content = scrape_page(url)

    # 2. Use LLM to identify questions
    prompt = f"""
    Analyze this job/scholarship application page and extract all questions
    that applicants need to answer.

    Page Content:
    {page_content}

    Return a JSON array of questions with this structure:
    [
        {{
            "question_text": "...",
            "question_type": "short_answer|essay|experience|education|skills",
            "is_required": true|false
        }}
    ]

    Only include actual questions, not general descriptions.
    """

    # 3. Parse LLM response
    questions = parse_json_response(call_claude_api(prompt))

    return questions
```

### 5.3 Email Analysis for Status Detection
```python
def analyze_email_for_status(email_body, application):
    prompt = f"""
    Analyze this email to determine if it contains a status update
    for a job/scholarship application.

    Application: {application.title} at {application.company_or_institution}

    Email Content:
    {email_body}

    Return JSON:
    {{
        "is_status_update": true|false,
        "detected_status": "in_review|interview|offer|rejected|null",
        "confidence": 0.0-1.0,
        "summary": "brief summary of email"
    }}
    """

    result = parse_json_response(call_claude_api(prompt))
    return result
```

### 5.4 Cost Management
- Cache LLM responses to avoid duplicate calls
- Implement rate limiting per user
- Use cheaper models for simple tasks (question extraction)
- Use premium models for response generation
- Allow users to regenerate responses (with daily limits)
- Monitor API usage and costs

---

## 6. Web Scraping Strategy

### 6.1 Scraping Approaches

#### Option 1: Static Content (BeautifulSoup)
```python
def scrape_static_page(url):
    response = requests.get(url, headers=get_random_user_agent())
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract content
    title = soup.find('h1').get_text()
    description = soup.find('div', class_='description').get_text()

    return {' title': title, 'description': description}
```

#### Option 2: Dynamic Content (Playwright)
```python
async def scrape_dynamic_page(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)

        # Wait for content to load
        await page.wait_for_selector('.job-description')

        # Extract content
        content = await page.content()

        await browser.close()

    return content
```

### 6.2 Handling Different Platforms
- **LinkedIn**: Special handling, may require authentication
- **Indeed**: Static scraping works
- **Company Career Pages**: Varies, try static first, fallback to Playwright
- **Scholarship Portals**: Usually static
- **Generic URLs**: Auto-detect, try both methods

### 6.3 Rate Limiting & Politeness
- Implement delays between requests
- Respect robots.txt
- Use user agent rotation
- Cache scraped content (don't re-scrape same URL within 24 hours)

---

## 7. Security Considerations

### 7.1 Authentication & Authorization
- Use Django's built-in authentication
- Implement CSRF protection (Django default)
- Use HTTPS in production (enforce with middleware)
- Implement password strength requirements
- Add rate limiting on login attempts
- Use Django's permission system for authorization

### 7.2 Data Protection
- Encrypt sensitive data (Gmail tokens) using Django's crypto
- Hash passwords with Django's default (PBKDF2)
- Implement field-level encryption for sensitive user data
- Regular security audits
- GDPR compliance: Allow users to export/delete data

### 7.3 File Upload Security
- Validate file types (check magic bytes, not just extension)
- Limit file sizes (10MB for resumes, 50MB for transcripts)
- Scan uploads for malware (ClamAV integration)
- Store files outside web root
- Generate random filenames to prevent overwriting

### 7.4 API Security
- Store API keys in environment variables
- Never commit secrets to Git
- Use separate API keys for dev/prod
- Implement request signing for webhooks
- Rate limit API endpoints

### 7.5 Input Validation
- Sanitize all user inputs
- Validate URLs before scraping
- Escape HTML in templates (Django auto-escapes)
- Validate JSON responses from LLM
- SQL injection protection (use Django ORM)

---

## 8. Performance & Scalability

### 8.1 Caching Strategy
- **Redis Cache**:
  - User session data
  - Extracted document information (1 hour TTL)
  - Scraped page content (24 hours TTL)
  - LLM responses for identical questions (7 days TTL)
  - Database query results for dashboards

### 8.2 Database Optimization
- Add indexes on frequently queried fields
- Use select_related() and prefetch_related() to avoid N+1 queries
- Implement pagination for large datasets
- Use database connection pooling
- Regular VACUUM and ANALYZE (PostgreSQL)

### 8.3 Background Tasks
- **Celery Tasks**:
  - Document processing (immediate)
  - URL scraping (immediate)
  - LLM API calls (immediate with retry)
  - Gmail email fetching (every hour)
  - Reminder checking (daily at midnight)
  - Database cleanup (weekly)

### 8.4 Scalability Considerations
- **Horizontal Scaling**:
  - Use load balancer (Nginx) for multiple app servers
  - Redis cluster for distributed caching
  - Separate Celery workers for different task types
  - CDN for static files

- **Vertical Scaling**:
  - Start with modest server (2GB RAM, 1 CPU)
  - Scale up based on metrics

### 8.5 File Storage
- **Development**: Local filesystem
- **Production**: AWS S3 or DigitalOcean Spaces
- Implement lazy loading for file listings
- Compress PDFs if >5MB

---

## 9. Development Approach

### 9.1 Phase Implementation Order

#### Phase 1: MVP (Minimum Viable Product) - 4 weeks
- Django project setup
- User authentication (signup, login, profile)
- Document upload (no parsing yet)
- URL submission and basic scraping
- Manual question addition
- Simple text responses (no LLM)
- Basic dashboard

#### Phase 2: Core Features - 4 weeks
- Document parsing and extraction
- LLM integration for response generation
- Question extraction from URLs
- Application status tracking
- Basic notifications

#### Phase 3: Advanced Features - 3 weeks
- Gmail integration
- Email monitoring and status detection
- Automated reminders
- Enhanced UI/UX
- Search and filtering

#### Phase 4: Production Ready - 2 weeks
- Comprehensive testing
- Security hardening
- Performance optimization
- Production deployment
- Monitoring setup
- Documentation

### 9.2 Testing Strategy
- **Unit Tests**: 80% code coverage minimum
- **Integration Tests**: Test critical workflows
- **End-to-End Tests**: Test complete user journeys
- **Load Testing**: Simulate 100 concurrent users
- **Security Testing**: OWASP Top 10 checks

### 9.3 CI/CD Pipeline
```yaml
1. Code Push → GitHub
2. Run Tests (GitHub Actions)
3. Code Quality Checks (flake8, black)
4. Security Scan (bandit)
5. Build Docker Image (if tests pass)
6. Deploy to Staging
7. Run Smoke Tests
8. Manual Approval
9. Deploy to Production
10. Monitor Errors (Sentry)
```

---

## 10. Deployment Architecture

### 10.1 Production Stack
```
                    ┌─────────────┐
                    │   Domain    │
                    │  (DNS/SSL)  │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │    Nginx    │
                    │(Reverse Proxy)
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────┴────────┐ ┌───────┴────────┐ ┌──────┴──────┐
│  Gunicorn 1    │ │  Gunicorn 2    │ │   Static    │
│ (Django App)   │ │ (Django App)   │ │   Files     │
└───────┬────────┘ └───────┬────────┘ └─────────────┘
        │                  │
        └──────────┬───────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────┴────────┐   ┌────────┴────────┐
│  PostgreSQL    │   │     Redis       │
│   (Database)   │   │  (Cache/Queue)  │
└────────────────┘   └────────┬────────┘
                              │
                     ┌────────┴────────┐
                     │ Celery Workers  │
                     │  (Background)   │
                     └─────────────────┘
```

### 10.2 Server Requirements (Initial)
- **Application Server**: 2GB RAM, 2 CPU cores
- **Database Server**: 2GB RAM, 1 CPU core (can be same server initially)
- **Redis**: 512MB RAM (can be same server)
- **Storage**: 20GB SSD (will grow with user uploads)

### 10.3 Environment Variables
```bash
# Django
SECRET_KEY=
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# APIs
ANTHROPIC_API_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# AWS (if using S3)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=

# Monitoring
SENTRY_DSN=
```

### 10.4 Deployment Options

#### Option A: Traditional VPS (DigitalOcean, Linode)
- Pros: Full control, cost-effective
- Cons: Manual setup, maintenance
- Cost: ~$12-24/month

#### Option B: Platform as a Service (Heroku, Railway)
- Pros: Easy deployment, managed services
- Cons: Higher cost, less control
- Cost: ~$25-50/month

#### Option C: Containerized (Docker + DigitalOcean App Platform)
- Pros: Portable, scalable, modern
- Cons: More complex initial setup
- Cost: ~$20-40/month

**Recommendation**: Start with Option A (VPS), migrate to Option C when scaling.

---

## 11. Monitoring & Maintenance

### 11.1 Monitoring
- **Application Monitoring**: Sentry for error tracking
- **Server Monitoring**: UptimeRobot or Pingdom
- **Performance Monitoring**: Django Debug Toolbar (dev), New Relic (prod)
- **Log Aggregation**: Centralized logging with rotation

### 11.2 Backup Strategy
- **Database**: Daily automated backups, 7-day retention
- **User Files**: Daily backups to separate storage
- **Code**: Git repository (already backed up)

### 11.3 Maintenance Tasks
- Weekly: Review error logs, security updates
- Monthly: Database optimization, disk cleanup
- Quarterly: Dependency updates, security audit

---

## 12. Cost Estimation

### 12.1 Development Costs
- Developer time: 13 weeks (as outlined)
- Testing & QA: Included in timeline

### 12.2 Operational Costs (Monthly)
- **Server Hosting**: $20-40
- **Database**: Included in server or $10
- **Domain**: $1-2
- **SSL Certificate**: Free (Let's Encrypt)
- **LLM API** (Anthropic Claude):
  - Assume 1000 users, avg 5 applications/month, 10 questions each
  - 50,000 questions/month × $0.015 (estimate) = $750/month
  - **Major cost driver - implement caching and quotas**
- **Gmail API**: Free (within quotas)
- **Storage**: $5-20 (depends on user uploads)
- **Monitoring**: $0-25 (Sentry free tier to start)
- **Email Service**: $0-10 (SendGrid free tier)

**Total Estimated Monthly Cost**: $800-850 (with LLM being 90% of cost)

### 12.3 Cost Optimization Strategies
1. Implement aggressive caching for LLM responses
2. Allow users to reuse responses across similar questions
3. Offer tiered pricing (free: 3 apps/month, paid: unlimited)
4. Use smaller LLM models for simple tasks
5. Batch LLM API calls
6. Implement per-user quotas

---

## 13. Risk Assessment & Mitigation

### 13.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LLM API rate limits | High | Medium | Implement request queuing, caching |
| Web scraping blocked | High | High | Use multiple methods, provide manual fallback |
| Gmail API quota exceeded | Medium | Low | Monitor usage, implement polling intervals |
| Database performance issues | Medium | Medium | Proper indexing, connection pooling |
| File storage limits | Low | Low | Implement cleanup, file size limits |

### 13.2 Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| High LLM costs | High | High | Implement quotas, caching, consider self-hosted models |
| Privacy concerns | High | Low | GDPR compliance, clear privacy policy |
| User adoption | Medium | Medium | MVP first, gather feedback, iterate |
| Competition | Low | Medium | Focus on unique features (email integration) |

---

## 14. Success Metrics

### 14.1 Technical KPIs
- Page load time < 2 seconds
- API response time < 500ms
- 99.9% uptime
- Zero critical security vulnerabilities
- 80%+ code coverage

### 14.2 User KPIs (Post-Launch)
- User registration rate
- Application completion rate
- Response generation success rate
- User retention (30-day, 90-day)
- Gmail connection rate

---

## 15. Future Enhancements (Post-MVP)

### 15.1 Features
- Mobile app (React Native)
- Chrome extension for one-click application import
- Interview preparation based on application
- Application analytics and insights
- Team/organization accounts
- Integration with LinkedIn for profile import
- Calendar integration for deadline tracking
- Cover letter and resume builder

### 15.2 Technical Improvements
- GraphQL API
- Real-time notifications (WebSockets)
- Progressive Web App (PWA)
- Machine learning for status prediction
- Custom LLM fine-tuning on user's writing style
- Multi-language support

---

## 16. Implementation Plan with Agents

Given the scope, I'll create specialized agents for:

1. **Django Setup Agent**: Initialize project, apps, settings
2. **Database Design Agent**: Create all models and migrations
3. **Authentication Agent**: Implement auth system
4. **Document Processing Agent**: Build upload and parsing system
5. **Web Scraping Agent**: Implement URL processing
6. **LLM Integration Agent**: Build response generation
7. **Gmail Integration Agent**: Implement email monitoring
8. **Frontend Agent**: Create all templates and UI
9. **Testing Agent**: Write comprehensive tests
10. **Deployment Agent**: Configure production setup

Each agent will work on its specific domain with clear interfaces between components.

---

## Next Steps

1. Review and approve this plan
2. Update TODO.md with detailed technical tasks
3. Begin Phase 1: MVP Development
4. Launch agents in parallel for different components
5. Regular progress updates in TODO.md

---

**Document Version**: 1.0
**Last Updated**: 2025-10-31
**Status**: Awaiting Approval
