# Migration Guide

> Step-by-step guide for upgrading to the latest version of Job & Scholarship Tracker

**From Version:** 1.0.x
**To Version:** 1.1.0
**Migration Date:** November 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [What's New](#whats-new)
3. [Pre-Migration Checklist](#pre-migration-checklist)
4. [Backup Your Data](#backup-your-data)
5. [Migration Steps](#migration-steps)
6. [Post-Migration Tasks](#post-migration-tasks)
7. [Troubleshooting](#troubleshooting)
8. [Rollback Instructions](#rollback-instructions)
9. [FAQ](#faq)

---

## 🎯 Overview

Version 1.1.0 introduces several powerful new features to help you better organize and track your applications. This migration guide will help you safely upgrade your existing installation without losing any data.

**Estimated Time:** 10-15 minutes
**Difficulty:** Easy
**Risk Level:** Low (with proper backup)

### Breaking Changes

**✅ Good News:** This update has **NO breaking changes**. All your existing data, applications, and documents will work exactly as before. The new features are **additive only**.

---

## ✨ What's New

### New Features in v1.1.0

1. **📝 Notes System** - Rich text notes with auto-save, pinning, and application linking
2. **🏷️ Tag System** - Custom color-coded tags for organizing applications
3. **📦 Archive** - Archive old applications without deleting them
4. **🎤 Interviews** - Full interview management with interviewer tracking
5. **👥 Referrals** - Track who referred you to each position
6. **📊 Analytics** - Sankey diagrams, timeline views, and success metrics
7. **🔍 Advanced Filters** - Multi-select filters with date ranges
8. **⚡ AJAX APIs** - Faster interactions without page reloads

### Database Changes

The following new tables will be created:
- `tracker_note` - For storing notes
- `tracker_tag` - For custom tags
- `tracker_interview` - For interview scheduling
- `tracker_interviewer` - For interviewer details
- `tracker_referral` - For referral tracking

The following fields will be added to existing tables:
- `tracker_application.is_archived` - Boolean for archive status
- `tracker_application.archived_at` - DateTime of archiving
- `tracker_application.notes` - Text field for quick notes
- `tracker_application_tags` - Many-to-many relationship table

**All existing data remains untouched.**

---

## ✅ Pre-Migration Checklist

Before starting the migration, ensure you have:

- [ ] **Access to your server** (SSH for production, terminal for local)
- [ ] **Admin/sudo access** (if needed for your setup)
- [ ] **At least 30 minutes** without users actively using the system
- [ ] **Backup storage space** (at least 2x your current database size)
- [ ] **Tested in development** (highly recommended for production systems)
- [ ] **Read this entire guide** (seriously, read it all first!)
- [ ] **Celery workers stopped** (if running in production)
- [ ] **Recent git commit** (if using version control)

### System Requirements

**Minimum Requirements:**
- Python 3.8+
- Django 4.2+
- PostgreSQL 12+ (production) or SQLite 3.8+ (development)
- Redis 6.0+ (for Celery)
- 100MB free disk space

**Check Your Current Version:**
```bash
python manage.py --version  # Should be Django 4.2.25 or higher
python --version            # Should be Python 3.8 or higher
```

---

## 💾 Backup Your Data

**⚠️ CRITICAL: Do NOT skip this step!**

Even though this is a safe migration, always backup before making changes.

### Option 1: Full Database Backup (Recommended)

**For PostgreSQL (Production):**
```bash
# Navigate to your project directory
cd /path/to/job_and_scholarship_tracker

# Create backup directory
mkdir -p backups

# Backup database
pg_dump -U your_username -d your_database_name > backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup was created
ls -lh backups/
```

**For SQLite (Development):**
```bash
# Navigate to your project directory
cd /path/to/job_and_scholarship_tracker

# Create backup directory
mkdir -p backups

# Copy SQLite database
cp db.sqlite3 backups/db_backup_$(date +%Y%m%d_%H%M%S).sqlite3

# Verify backup
ls -lh backups/
```

### Option 2: Django's dumpdata Command

**Backup all data to JSON:**
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create backup directory
mkdir -p backups

# Dump all data
python manage.py dumpdata --indent 2 > backups/full_backup_$(date +%Y%m%d_%H%M%S).json

# Verify backup
ls -lh backups/
```

**Backup specific apps:**
```bash
# Backup tracker app data
python manage.py dumpdata tracker --indent 2 > backups/tracker_backup.json

# Backup documents
python manage.py dumpdata documents --indent 2 > backups/documents_backup.json

# Backup accounts
python manage.py dumpdata accounts --indent 2 > backups/accounts_backup.json
```

### Option 3: Media Files Backup

**Backup uploaded documents:**
```bash
# Navigate to project directory
cd /path/to/job_and_scholarship_tracker

# Create backup of media files
tar -czf backups/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/

# Verify backup
ls -lh backups/
```

### Backup Checklist

After backing up, verify:
- [ ] Backup file exists and has a reasonable size (not 0 bytes)
- [ ] Backup file is readable (`head` or `cat` for JSON, `pg_restore --list` for SQL)
- [ ] Backup timestamp is correct (just created)
- [ ] Multiple backups if this is a production system

---

## 🚀 Migration Steps

### Step 1: Stop Running Services

**Stop Celery workers and beat scheduler:**
```bash
# Find and kill Celery processes
pkill -f "celery worker"
pkill -f "celery beat"

# Verify they're stopped
ps aux | grep celery
# Should show no results
```

**Stop Django development server (if running):**
```bash
# Press Ctrl+C in the terminal running runserver
```

**For production (systemd):**
```bash
sudo systemctl stop celery-worker
sudo systemctl stop celery-beat
sudo systemctl stop gunicorn  # Or your web server
```

### Step 2: Update Code

**If using Git (Recommended):**
```bash
# Navigate to project directory
cd /path/to/job_and_scholarship_tracker

# Stash any local changes (if needed)
git stash

# Pull latest changes
git pull origin main  # Or your branch name

# Check current version
git log --oneline -5
```

**If using manual download:**
1. Download the latest release from GitHub
2. Extract to a temporary directory
3. Copy files to your project directory (excluding db.sqlite3 and media/)
4. Overwrite when prompted

### Step 3: Update Dependencies

**Install new requirements:**
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Update pip
pip install --upgrade pip

# Install/update requirements
pip install -r requirements.txt

# Verify Quill.js and Plotly.js are available (they're CDN-based, no pip install needed)
```

**Check for any new system dependencies:**
```bash
# If you haven't installed Tesseract OCR yet (optional)
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# macOS:
brew install tesseract
```

### Step 4: Run Database Migrations

**This is the key step that creates new tables and fields.**

```bash
# Activate virtual environment (if not already)
source venv/bin/activate

# Check what migrations will run (dry run)
python manage.py migrate --plan

# You should see new migrations for tracker app, like:
# tracker.0002_note
# tracker.0003_tag
# tracker.0004_interview
# (etc.)

# Run migrations
python manage.py migrate

# Expected output:
# Operations to perform:
#   Apply all migrations: tracker, accounts, documents, notifications, admin, auth, contenttypes, sessions
# Running migrations:
#   Applying tracker.0002_note... OK
#   Applying tracker.0003_tag... OK
#   Applying tracker.0004_interview... OK
#   Applying tracker.0005_interviewer... OK
#   Applying tracker.0006_referral... OK
#   Applying tracker.0007_add_archive_fields... OK
```

**Verify migrations succeeded:**
```bash
# Check migration status
python manage.py showmigrations

# All migrations should have [X] checkmarks
```

### Step 5: Collect Static Files (Production Only)

**If running in production:**
```bash
# Collect static files
python manage.py collectstatic --noinput

# This collects new JavaScript and CSS files for the new features
```

### Step 6: Restart Services

**Development:**
```bash
# Terminal 1 - Django
python manage.py runserver

# Terminal 2 - Celery Worker
celery -A config worker -l info

# Terminal 3 - Celery Beat
celery -A config beat -l info
```

**Production (systemd):**
```bash
# Restart services
sudo systemctl start gunicorn     # Or your web server
sudo systemctl start celery-worker
sudo systemctl start celery-beat

# Check status
sudo systemctl status gunicorn
sudo systemctl status celery-worker
sudo systemctl status celery-beat
```

**Production (Railway/Heroku):**
```bash
# Railway auto-restarts on deploy
# Or manually restart:
railway restart

# Heroku:
heroku restart
```

### Step 7: Clear Cache (if using Redis cache)

```bash
# Connect to Redis
redis-cli

# Clear all cached data
FLUSHDB

# Exit
exit
```

### Step 8: Verify Installation

**Check the application:**
1. Open your browser
2. Navigate to your application (e.g., `http://localhost:8000`)
3. Log in with your account
4. You should see:
   - ✅ New "Notes" menu item
   - ✅ New "Interviews" menu item
   - ✅ New "Analytics" menu item
   - ✅ New "Archive" menu item
   - ✅ All existing data intact

**Test new features:**
1. Create a test note
2. Create a test tag
3. View analytics dashboard
4. Try filtering with new filters

---

## ✅ Post-Migration Tasks

### 1. Explore New Features

**Recommended First Steps:**
1. **Visit Analytics Dashboard** - See your application flow visualized
2. **Create Tags** - Set up your tagging system (Remote, High Priority, etc.)
3. **Create a Note** - Try the rich text editor
4. **Schedule an Interview** - Test interview management
5. **Try Advanced Filters** - Experience multi-select filtering

### 2. Data Housekeeping

**Clean up old data:**
```bash
# Archive old completed applications
# Use the UI to archive applications with status:
# - Offer (accepted or declined)
# - Rejected (more than 30 days ago)
# - Withdrawn

# This helps keep your dashboard focused on active applications
```

**Add tags to existing applications:**
1. Go through your existing applications
2. Add relevant tags to each
3. This makes filtering much more powerful

### 3. Update Your Workflow

**Incorporate new features:**
- 📝 **Take notes** after every interview or significant interaction
- 🏷️ **Tag applications** as you create them
- 🎤 **Add interviews** as soon as they're scheduled
- 👥 **Track referrals** when you receive them
- 📊 **Review analytics** weekly to track progress
- 📦 **Archive completed applications** monthly

### 4. Train Your Team (if applicable)

If multiple people use the system:
1. Share the NEW_FEATURES.md guide
2. Host a brief training session
3. Demonstrate key features
4. Answer questions
5. Gather feedback

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue: "No such table: tracker_note"

**Cause:** Migrations didn't run properly

**Solution:**
```bash
# Check migration status
python manage.py showmigrations tracker

# If migrations are unapplied [  ], run:
python manage.py migrate tracker

# If that fails, try:
python manage.py migrate --run-syncdb
```

#### Issue: "OperationalError: no such column: tracker_application.is_archived"

**Cause:** Migration for archive fields didn't apply

**Solution:**
```bash
# Run migrations again
python manage.py migrate tracker --fake-initial
python manage.py migrate

# Restart server
```

#### Issue: "Static files not loading" (CSS/JS)

**Cause:** Static files not collected in production

**Solution:**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Clear browser cache (Ctrl+Shift+Delete)
# Or hard refresh (Ctrl+Shift+R)
```

#### Issue: "ProgrammingError: relation 'tracker_tag' already exists"

**Cause:** Table exists but Django thinks it doesn't

**Solution:**
```bash
# Fake the migration
python manage.py migrate tracker --fake

# This tells Django the migration already ran
```

#### Issue: "Notes won't save" or "Auto-save not working"

**Cause:** JavaScript error or CSRF token issue

**Solution:**
1. Open browser console (F12)
2. Look for error messages
3. If CSRF error, clear cookies and log in again
4. If JavaScript error, hard refresh (Ctrl+Shift+R)

#### Issue: "Analytics charts not displaying"

**Cause:** Plotly.js not loading or ad blocker interference

**Solution:**
1. Disable ad blocker for your domain
2. Check browser console for errors
3. Ensure internet connection (Plotly is CDN-hosted)
4. Try different browser

#### Issue: "Celery workers not starting"

**Cause:** Multiple possible causes

**Solution:**
```bash
# Check Redis is running
redis-cli ping
# Should respond: PONG

# Check Celery logs
celery -A config worker -l debug

# Look for error messages
```

### Getting Help

If you encounter issues not listed here:

1. **Check application logs:**
   ```bash
   # Development
   tail -f /path/to/logfile

   # Production (systemd)
   sudo journalctl -u gunicorn -f
   sudo journalctl -u celery-worker -f
   ```

2. **Enable Django debug mode temporarily** (development only):
   ```python
   # In .env or settings
   DEBUG=True
   ```

3. **Check GitHub issues:**
   - Visit: https://github.com/NajibOladosu/job_and_scholarship_tracker/issues
   - Search for your error message
   - Create new issue if not found

4. **Provide details when asking for help:**
   - Django version: `python manage.py --version`
   - Python version: `python --version`
   - Database: PostgreSQL or SQLite
   - Environment: Development or Production
   - Error message (full traceback)
   - Steps to reproduce

---

## ⏪ Rollback Instructions

If something goes wrong and you need to revert to the previous version:

### Option 1: Restore from Backup

**For PostgreSQL:**
```bash
# Stop services
sudo systemctl stop gunicorn celery-worker celery-beat

# Drop current database (careful!)
psql -U your_username -c "DROP DATABASE your_database_name;"

# Recreate database
psql -U your_username -c "CREATE DATABASE your_database_name;"

# Restore from backup
psql -U your_username -d your_database_name < backups/backup_YYYYMMDD_HHMMSS.sql

# Restart services
sudo systemctl start gunicorn celery-worker celery-beat
```

**For SQLite:**
```bash
# Stop services
# Ctrl+C in terminal(s)

# Restore database
cp backups/db_backup_YYYYMMDD_HHMMSS.sqlite3 db.sqlite3

# Restart services
python manage.py runserver
# (and Celery in other terminals)
```

**For Django dumpdata backup:**
```bash
# Stop services

# Clear current database (optional)
python manage.py flush --no-input

# Load backup data
python manage.py loaddata backups/full_backup_YYYYMMDD_HHMMSS.json

# Restart services
```

### Option 2: Migrate Backwards

**Revert specific migrations:**
```bash
# Find the migration before the changes
python manage.py showmigrations tracker

# Migrate backwards to before new features
python manage.py migrate tracker 0001_initial

# Restart services
```

### Option 3: Git Rollback

**If using Git:**
```bash
# Find the commit before migration
git log --oneline

# Checkout the previous version
git checkout <commit_hash>

# Or revert to previous release
git checkout v1.0.0

# Reinstall requirements (might have changed)
pip install -r requirements.txt

# Migrate backwards
python manage.py migrate

# Restart services
```

---

## ❓ FAQ

### Q: Will I lose any data during migration?
**A:** No. This migration only adds new tables and fields. All existing data remains untouched.

### Q: Do I need to migrate if I'm using SQLite in development?
**A:** Yes. The migration process is the same for SQLite and PostgreSQL.

### Q: Can I migrate a live production system?
**A:** Yes, but schedule downtime. The migration typically takes 30-60 seconds, but include buffer time for testing.

### Q: What if I don't want to use the new features?
**A:** That's fine! The new features are optional. You can continue using the application exactly as before.

### Q: Will my custom modifications be affected?
**A:** If you've made custom code changes, review them carefully. The migration shouldn't affect most customizations, but test thoroughly.

### Q: Can I migrate without stopping Celery?
**A:** Not recommended. While Django migrations are usually safe with running workers, it's best practice to stop all services during migration.

### Q: How long does the migration take?
**A:** Typically 1-2 minutes for small databases, up to 5-10 minutes for large databases with thousands of applications.

### Q: What if migration fails halfway through?
**A:** Django migrations are atomic (all-or-nothing). If one fails, it rolls back automatically. Check logs for error details.

### Q: Do I need to update my Celery configuration?
**A:** No. Celery configuration remains the same.

### Q: Will this affect my Railway/Heroku deployment?
**A:** Migrations run automatically on Railway/Heroku deploy. Just push your code and migrations run during build.

### Q: Can I test the migration first?
**A:** Absolutely! Recommended workflow:
1. Clone your production database to a test environment
2. Run migration on test environment
3. Test all features
4. If successful, migrate production

### Q: What if I have thousands of applications?
**A:** The migration is optimized and should handle large datasets well. Budget extra time for very large databases (10,000+ applications).

### Q: Are there any performance impacts?
**A:** New indexes are added for optimal performance. The new features use caching to minimize database queries.

### Q: Can I migrate selectively (only some features)?
**A:** No. Migrations must run completely. However, you can choose not to use certain features after migration.

### Q: What Python/Django versions are supported?
**A:** Minimum: Python 3.8, Django 4.2. Recommended: Python 3.11+, Django 4.2.25+

---

## 📞 Support

### Getting Help

**Before asking for help:**
1. Read this entire guide
2. Check the [Troubleshooting](#troubleshooting) section
3. Search GitHub issues for similar problems
4. Review application logs for error details

**When asking for help, include:**
- Your environment (development/production, OS, etc.)
- Django and Python versions
- Full error message and traceback
- What you were trying to do
- What you've tried to fix it
- Relevant configuration details

**Support Channels:**
- **GitHub Issues**: https://github.com/NajibOladosu/job_and_scholarship_tracker/issues
- **Documentation**: NEW_FEATURES.md, CLAUDE.md, README.md
- **Deployment Guides**: RAILWAY_DEPLOYMENT.md, DEPLOYMENT.md

### Reporting Bugs

If you find a bug:
1. Verify it's reproducible
2. Check if it's already reported on GitHub
3. Create a new issue with:
   - Clear title describing the bug
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - System information
   - Screenshots/logs if applicable

---

## 🎉 Congratulations!

If you've made it this far, your migration is complete! 🚀

**Next Steps:**
1. Read NEW_FEATURES.md to learn about all new features
2. Explore the Analytics dashboard
3. Set up your tagging system
4. Start tracking interviews and referrals
5. Enjoy a more organized application process!

**Thank you for using Job & Scholarship Tracker!**

---

**Version History:**
- v1.1.0 - November 2025 - Added Notes, Tags, Archive, Interviews, Referrals, Analytics
- v1.0.0 - October 2025 - Initial production release

**Last Updated:** November 6, 2025
