# Railway Deployment Guide - Job & Scholarship Tracker

This guide will help you deploy your Job & Scholarship Tracker application to Railway with automatic deployments from GitHub.

## 🚀 Quick Overview

Railway will automatically:
- ✅ Deploy when you push to GitHub
- ✅ Provide PostgreSQL database
- ✅ Provide Redis for Celery
- ✅ Give you a public URL with HTTPS
- ✅ Run your web server, Celery worker, and Celery beat

---

## 📋 Prerequisites

Before you start, make sure you have:

1. **GitHub Account** - Your code must be on GitHub
2. **Railway Account** - Sign up at https://railway.app (free, no credit card required for trial)
3. **Gemini API Key** - Get from https://makersuite.google.com/app/apikey

---

## 🎯 Step-by-Step Deployment

### Step 1: Sign Up for Railway

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Sign in with your GitHub account
4. Authorize Railway to access your repositories

### Step 2: Create a New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: `job_and_scholarship_tracker`
4. Railway will detect it's a Python app automatically

### Step 3: Add PostgreSQL Database

1. In your Railway project dashboard, click **"New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway will automatically create a PostgreSQL database
4. The `DATABASE_URL` environment variable will be auto-configured

### Step 4: Add Redis

1. Click **"New"** again
2. Select **"Database"** → **"Redis"**
3. Railway will create a Redis instance
4. The `REDIS_URL` environment variable will be auto-configured

### Step 5: Configure Environment Variables

1. Click on your **web service** (the main Python app)
2. Go to **"Variables"** tab
3. Click **"Raw Editor"** and paste the following:

```bash
# Django Settings
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
ALLOWED_HOSTS=.railway.app

# Security - Generate a new secret key
SECRET_KEY=your-super-secret-key-minimum-50-characters-long-generate-new-one

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key-here

# Email Configuration (Optional - for notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password

# Security Settings
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

**Important:**
- Generate a new `SECRET_KEY`: Run this locally:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- Add your actual `GEMINI_API_KEY`
- `DATABASE_URL` and `REDIS_URL` are automatically set by Railway

4. Click **"Update Variables"**

### Step 6: Deploy Additional Services (Celery Worker & Beat)

Railway's `Procfile` defines multiple processes, but we need to create separate services for worker and beat:

#### Create Celery Worker Service:

1. Click **"New"** → **"Empty Service"**
2. Name it: `celery-worker`
3. Go to **"Settings"** → **"Source"**
4. Connect to the same GitHub repository
5. Go to **"Deploy"** → **"Custom Start Command"**
6. Enter: `celery -A config worker --loglevel=info`
7. Go to **"Variables"** and copy ALL the same environment variables from your web service

#### Create Celery Beat Service:

1. Click **"New"** → **"Empty Service"**
2. Name it: `celery-beat`
3. Go to **"Settings"** → **"Source"**
4. Connect to the same GitHub repository
5. Go to **"Deploy"** → **"Custom Start Command"**
6. Enter: `celery -A config beat --loglevel=info`
7. Go to **"Variables"** and copy ALL the same environment variables from your web service

### Step 7: Configure Automatic Deployments from GitHub

Railway automatically sets this up! By default:

✅ **Automatic deployments are ENABLED**
- Every push to your **main branch** triggers a deployment
- You can change this to any branch in Settings

To configure which branch triggers deployments:

1. Go to your service → **"Settings"**
2. Scroll to **"Deploy Triggers"**
3. Select the branch you want (e.g., `main` or `claude/init-project-011CUfhxwN3CKr3oqPFxwycu`)
4. Save

**To deploy on merge to main:**
- Set the trigger branch to `main`
- When you merge your PR to main, Railway auto-deploys

### Step 8: Run Database Migrations

After the first deployment:

1. Go to your **web service**
2. Click **"Deployments"** tab
3. Click on the latest deployment
4. Click **"View Logs"**
5. Check if migrations ran automatically

If migrations didn't run, you can run them manually:

1. Go to your service
2. Click on **"Settings"** → **"Deploy"**
3. The migrations should run automatically on each deploy via the nixpacks.toml config

### Step 9: Create Superuser (Admin Account)

To create an admin account:

1. In your service, go to **"Settings"** → **"Networking"**
2. Note your public URL (e.g., `https://your-app.railway.app`)
3. You'll need to create a superuser via a one-time deployment command:

**Option A: Via Railway CLI (Recommended)**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run command
railway run python manage.py createsuperuser --settings=config.settings.production
```

**Option B: Via Django Admin Signal (Alternative)**
You can create a superuser through the application after deployment by using the signup page and then promoting the user via database.

### Step 10: Access Your Application

1. Go to **"Settings"** → **"Networking"**
2. Click **"Generate Domain"**
3. Railway will give you a URL like: `https://your-app.railway.app`
4. Visit your application!

---

## 🔄 Automatic Deployments in Action

Now that everything is set up:

1. **Make changes to your code locally**
2. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main  # or your branch name
   ```
3. **Railway automatically detects the push and deploys!**
4. **Watch the deployment in Railway dashboard**
5. **Your changes go live in ~2-5 minutes**

You can see deployment status:
- ✅ Building
- ✅ Deploying
- ✅ Active (live)

---

## 🏗️ Your Railway Project Structure

After setup, you'll have **4 services**:

1. **Web Service** - Django app (Gunicorn)
   - Runs your web application
   - Serves HTTP requests
   - Auto-runs migrations on deploy

2. **Celery Worker** - Background tasks
   - Processes document uploads
   - Runs AI question extraction
   - Generates AI responses

3. **Celery Beat** - Scheduler
   - Sends scheduled reminders
   - Checks for due deadlines

4. **PostgreSQL** - Database
   - Stores all application data

5. **Redis** - Message broker
   - Handles Celery task queue

---

## 📊 Monitoring Your Application

### View Logs:
1. Click on any service
2. Go to **"Deployments"** → Latest deployment
3. Click **"View Logs"**
4. See real-time logs for debugging

### Metrics:
1. Go to **"Metrics"** tab
2. See CPU, Memory, Network usage
3. Monitor application health

---

## 💰 Pricing Information

**Railway Free Trial:**
- $5 free credit per month
- No credit card required
- Enough for development and testing

**After free trial:**
- Pay-as-you-go pricing
- ~$5-20/month for a small app like this
- Only pay for what you use

**Estimated Monthly Cost:**
- Web service: ~$5-10
- Worker: ~$3-5
- Beat: ~$2-3
- PostgreSQL: Free or ~$5
- Redis: Free or ~$1
- **Total: ~$10-20/month**

---

## 🔧 Troubleshooting

### Issue: Deployment Fails

**Solution:**
1. Check logs in Railway dashboard
2. Verify all environment variables are set
3. Ensure `GEMINI_API_KEY` is valid
4. Check that `SECRET_KEY` is set

### Issue: Application Shows 500 Error

**Solution:**
1. Check web service logs
2. Verify `DEBUG=False` is set
3. Check `ALLOWED_HOSTS` includes `.railway.app`
4. Ensure database migrations ran

### Issue: Celery Tasks Not Running

**Solution:**
1. Check that Celery Worker service is running
2. Verify Redis is connected (check `REDIS_URL`)
3. Check worker logs for errors
4. Ensure all environment variables are copied to worker

### Issue: Static Files Not Loading

**Solution:**
1. Check that `collectstatic` ran during build
2. Verify `WhiteNoise` is in `MIDDLEWARE`
3. Check `STATIC_ROOT` and `STATIC_URL` settings

### Issue: Database Connection Error

**Solution:**
1. Verify PostgreSQL service is running
2. Check `DATABASE_URL` is set (should be automatic)
3. Check if migrations ran successfully

---

## 🚀 Post-Deployment Checklist

After successful deployment:

- [ ] Application is accessible via Railway URL
- [ ] Can create an account and login
- [ ] Can create applications
- [ ] Can upload documents
- [ ] Celery worker is processing tasks (check logs)
- [ ] Celery beat is running (check logs)
- [ ] Admin panel is accessible (`/admin/`)
- [ ] Static files are loading correctly
- [ ] No errors in logs

---

## 🔐 Security Best Practices

1. **Never commit sensitive keys to GitHub**
   - `.env` is in `.gitignore` ✅
   - Use Railway environment variables ✅

2. **Use strong SECRET_KEY**
   - Generate new one for production ✅
   - Minimum 50 characters ✅

3. **Keep DEBUG=False in production** ✅

4. **Use HTTPS only**
   - Railway provides free SSL ✅

5. **Regular updates**
   - Keep dependencies updated
   - Monitor security advisories

---

## 📚 Additional Resources

- **Railway Documentation**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Railway Status**: https://status.railway.app
- **Your Project Dashboard**: https://railway.app/dashboard

---

## 🎉 You're All Set!

Your Job & Scholarship Tracker is now:
- ✅ Deployed on Railway
- ✅ Automatically deploys on GitHub push
- ✅ Running with PostgreSQL and Redis
- ✅ Processing background tasks with Celery
- ✅ Accessible via public URL
- ✅ Secured with HTTPS

**Next time you make changes:**
1. Code locally
2. Push to GitHub
3. Railway auto-deploys
4. Changes go live automatically!

**Questions or issues?** Check the Railway docs or logs in the dashboard.

**Happy deploying! 🚀**
