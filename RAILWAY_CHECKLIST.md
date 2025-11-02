# Railway Deployment Checklist ✅

Use this checklist to ensure a smooth deployment to Railway.

## Before Deployment

- [ ] **Sign up for Railway** - https://railway.app
- [ ] **Get Gemini API Key** - https://makersuite.google.com/app/apikey
- [ ] **Push code to GitHub** - Make sure your latest code is on GitHub
- [ ] **Review environment variables** - Check `railway.env.example`

## Railway Setup (Do Once)

### 1. Create Project
- [ ] Login to Railway
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose `job_and_scholarship_tracker` repository

### 2. Add Databases
- [ ] Click "New" → "Database" → "PostgreSQL"
- [ ] Click "New" → "Database" → "Redis"
- [ ] Verify both services are running

### 3. Configure Web Service
- [ ] Click on main Python service
- [ ] Go to "Variables" tab
- [ ] Click "Raw Editor"
- [ ] Paste environment variables from `railway.env.example`
- [ ] **IMPORTANT: Replace placeholders:**
  - [ ] Generate new `SECRET_KEY`
  - [ ] Add your `GEMINI_API_KEY`
  - [ ] Add email credentials (optional)
- [ ] Click "Update Variables"
- [ ] Go to "Settings" → "Networking" → "Generate Domain"

### 4. Create Celery Worker Service
- [ ] Click "New" → "Empty Service"
- [ ] Name: `celery-worker`
- [ ] Settings → Source → Connect to same GitHub repo
- [ ] Settings → Deploy → Custom Start Command: `celery -A config worker --loglevel=info`
- [ ] Variables → Copy ALL variables from web service
- [ ] Deploy

### 5. Create Celery Beat Service
- [ ] Click "New" → "Empty Service"
- [ ] Name: `celery-beat`
- [ ] Settings → Source → Connect to same GitHub repo
- [ ] Settings → Deploy → Custom Start Command: `celery -A config beat --loglevel=info`
- [ ] Variables → Copy ALL variables from web service
- [ ] Deploy

### 6. Configure Auto-Deployment
- [ ] Go to web service → Settings → Deploy Triggers
- [ ] Select branch: `main` (or your preferred branch)
- [ ] Save
- [ ] Repeat for celery-worker and celery-beat services

## First Deployment

- [ ] Wait for all services to build and deploy (2-5 minutes)
- [ ] Check logs for each service (Deployments → View Logs)
- [ ] Verify no errors in logs
- [ ] Visit your Railway URL (from Settings → Networking)
- [ ] Verify application loads

## Create Admin Account

Choose one method:

**Method 1: Railway CLI (Recommended)**
```bash
npm i -g @railway/cli
railway login
railway link
railway run python manage.py createsuperuser --settings=config.settings.production
```

**Method 2: Via Application**
- [ ] Sign up through the web interface
- [ ] Manually promote to superuser via database or Django shell

## Post-Deployment Testing

- [ ] Visit application URL
- [ ] Create a test account
- [ ] Login successfully
- [ ] Create a test application
- [ ] Upload a test document
- [ ] Check Celery worker logs (document should be processed)
- [ ] Check Celery beat logs (scheduler running)
- [ ] Visit `/admin/` and login with superuser
- [ ] Verify static files load correctly

## Enable Automatic Deployments

- [ ] Verify Deploy Trigger is set to `main` branch
- [ ] Test by making a small change locally
- [ ] Commit and push to GitHub:
  ```bash
  git add .
  git commit -m "Test automatic deployment"
  git push origin main
  ```
- [ ] Watch Railway dashboard for automatic deployment
- [ ] Verify changes are live

## Ongoing Maintenance

After initial setup, your workflow is simple:

1. **Make changes locally**
2. **Commit and push to GitHub**
3. **Railway automatically deploys**
4. **Verify in Railway dashboard**

That's it! 🎉

## Service Status Check

Verify all services are running:

- [ ] **Web Service**: Status = "Active" ✅
- [ ] **Celery Worker**: Status = "Active" ✅
- [ ] **Celery Beat**: Status = "Active" ✅
- [ ] **PostgreSQL**: Status = "Active" ✅
- [ ] **Redis**: Status = "Active" ✅

## Troubleshooting

If something doesn't work:

1. **Check logs** - Each service has logs in Deployments tab
2. **Verify environment variables** - Make sure all are set correctly
3. **Check service status** - All should be "Active"
4. **Restart service** - Settings → click "Restart"
5. **Review RAILWAY_DEPLOYMENT.md** - Full troubleshooting guide

## Need Help?

- 📖 Full guide: `RAILWAY_DEPLOYMENT.md`
- 🌐 Railway docs: https://docs.railway.app
- 💬 Railway Discord: https://discord.gg/railway

---

**Once completed, you have:**
✅ Automatic deployments from GitHub
✅ Production-ready Django app
✅ Background task processing
✅ Secure HTTPS
✅ Scalable infrastructure

**Happy deploying! 🚀**
