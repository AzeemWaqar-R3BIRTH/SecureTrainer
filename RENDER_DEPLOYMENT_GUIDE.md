# 🚀 SecureTrainer Deployment Guide - Render.com

Complete step-by-step guide to deploy SecureTrainer on Render.com with custom domain.

---

## 📋 PREREQUISITES

Before starting, make sure you have:

- [ ] GitHub account
- [ ] MongoDB Atlas account (free)
- [ ] Gmail account (for sending emails)
- [ ] Domain registered (securetrainer.com)

---

## STEP 1: SETUP MONGODB ATLAS (5 minutes)

### 1.1 Create Free MongoDB Cluster

1. Go to https://www.mongodb.com/cloud/atlas/register
2. Sign up for free account
3. Create a new project: "SecureTrainer"
4. Click "Build a Database"
5. Choose **FREE** tier (M0)
6. Select region closest to you
7. Cluster name: `securetrainer-cluster`
8. Click "Create"

### 1.2 Create Database User

1. Go to **Database Access** (left sidebar)
2. Click "Add New Database User"
3. Authentication Method: Password
4. Username: `securetrainer_admin`
5. Generate a secure password (save it!)
6. Database User Privileges: "Read and write to any database"
7. Click "Add User"

### 1.3 Whitelist IP Addresses

1. Go to **Network Access** (left sidebar)
2. Click "Add IP Address"
3. Click "Allow Access from Anywhere" (0.0.0.0/0)
4. Confirm

### 1.4 Get Connection String

1. Go to **Database** → **Connect**
2. Click "Connect your application"
3. Driver: Python, Version: 3.6 or later
4. Copy the connection string:
   ```
   mongodb+srv://securetrainer_admin:<password>@securetrainer-cluster.xxxxx.mongodb.net/securetrainer?retryWrites=true&w=majority
   ```
5. Replace `<password>` with your actual password
6. **Save this connection string** - you'll need it for Render!

---

## STEP 2: PUSH CODE TO GITHUB (10 minutes)

### 2.1 Initialize Git Repository

Open PowerShell in the securetrainer folder:

```powershell
# Navigate to project folder
cd "c:\Users\Azeem's ASUS\Desktop\Antigravity Test 2\Google Antigravity Test\Google Antigravity Test\Secure trainer backup after mid evaluation\qoder Secure Trainer FYP\Secure Trainer FYP\securetrainer"

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - SecureTrainer deployment"
```

### 2.2 Create GitHub Repository

1. Go to https://github.com
2. Click "New Repository"
3. Repository name: `securetrainer`
4. Description: "AI-Driven Cybersecurity Training Platform"
5. **Private** or Public (your choice)
6. **DO NOT** initialize with README
7. Click "Create Repository"

### 2.3 Push to GitHub

Copy the commands from GitHub and run:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/securetrainer.git
git branch -M main
git push -u origin main
```

---

## STEP 3: DEPLOY ON RENDER.COM (15 minutes)

### 3.1 Create Render Account

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (easiest)
4. Authorize Render to access your repositories

### 3.2 Create New Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Find and select `securetrainer` repository
4. Click "Connect"

### 3.3 Configure Service

Fill in the following:

**Basic Settings:**
- **Name**: `securetrainer` (this will be your-app URL)
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: Leave blank
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn securetrainer:app`

**Instance Type:**
- Select **Free** tier

### 3.4 Add Environment Variables

Click "Advanced" → "Add Environment Variable" and add these:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `SECRET_KEY` | `<generate random 50+ char string>` |
| `FLASK_ENV` | `production` |
| `MONGO_URI` | `<your MongoDB Atlas connection string>` |
| `MAIL_SERVER` | `smtp.gmail.com` |
| `MAIL_PORT` | `587` |
| `MAIL_USE_TLS` | `True` |
| `MAIL_USERNAME` | `azeemwaqar.work@gmail.com` |
| `MAIL_PASSWORD` | `wmwb ejkp sevx ipap` |
| `ADMIN_TOKEN` | `<generate random token>` |
| `ADMIN_REGISTRATION_TOKEN` | `<generate random token>` |

**Important Notes:**
- For `SECRET_KEY`, generate a random string (use: https://randomkeygen.com/)
- Use your actual MongoDB Atlas connection string from Step 1.4
- Keep your email credentials secure

### 3.5 Deploy!

1. Click "Create Web Service"
2. Wait 3-5 minutes for build and deployment
3. You'll see logs in real-time
4. Once deployed, you'll get a URL: `https://securetrainer.onrender.com`

---

## STEP 4: ADD CUSTOM DOMAIN (10 minutes)

### 4.1 Add Domain in Render

1. In your Render dashboard, go to your service
2. Click **Settings** → **Custom Domain**
3. Click "Add Custom Domain"
4. Enter: `securetrainer.com`
5. Click "Save"
6. Also add: `www.securetrainer.com`

### 4.2 Configure DNS

Render will show you DNS records. Go to your domain registrar (where you bought securetrainer.com) and add:

**For Root Domain (securetrainer.com):**
```
Type: A
Name: @
Value: 216.24.57.1
TTL: 3600
```

**For WWW Subdomain:**
```
Type: CNAME
Name: www
Value: securetrainer.onrender.com
TTL: 3600
```

### 4.3 Wait for DNS Propagation

- Typical time: 10-60 minutes
- Maximum: 24-48 hours
- Check status: https://dnschecker.org/

### 4.4 SSL Certificate

- Render automatically provisions SSL (HTTPS)
- Takes 1-5 minutes after DNS propagation
- Automatic renewal every 90 days

---

## STEP 5: VERIFY DEPLOYMENT

### 5.1 Test Your App

Visit your URLs:
- https://securetrainer.onrender.com
- https://securetrainer.com (after DNS propagation)
- https://www.securetrainer.com

### 5.2 Check Features

- [ ] Homepage loads
- [ ] Registration works
- [ ] Login works
- [ ] Challenges load
- [ ] Email sending works
- [ ] QR code generation works
- [ ] Admin panel accessible

---

## 🔧 TROUBLESHOOTING

### Build Fails

**Error**: `No module named 'X'`
- **Fix**: Add missing package to `requirements.txt`

**Error**: `Python version mismatch`
- **Fix**: Set `PYTHON_VERSION=3.11.0` in environment variables

### Application Crashes

**Check logs**:
1. Go to Render Dashboard → Your Service
2. Click "Logs" tab
3. Look for error messages

**Common issues**:
- MongoDB connection failed: Check `MONGO_URI` format
- Email errors: Verify Gmail credentials
- Import errors: Missing dependencies in `requirements.txt`

### Database Connection Issues

**Error**: `MongoServerSelectionTimeoutError`
- **Fix**: Check MongoDB Atlas network access (allow 0.0.0.0/0)
- **Fix**: Verify connection string has correct password
- **Fix**: Ensure database user has proper permissions

### Custom Domain Not Working

- Wait 1-2 hours for DNS propagation
- Check DNS records at registrar
- Verify A record points to correct IP
- Check https://dnschecker.org/

---

## 📊 MONITORING & MAINTENANCE

### View Logs

```bash
# In Render Dashboard
Go to your service → Logs tab
```

### Auto-Deploy on Git Push

By default, Render auto-deploys when you push to `main`:

```powershell
# Make changes
git add .
git commit -m "Update feature"
git push

# Render automatically rebuilds and deploys!
```

### Upgrade to Paid Plan

When ready to remove sleep (15 min inactivity):
1. Go to Settings → Instance Type
2. Select "Starter" ($7/month)
3. Confirm

---

## ✅ SUCCESS CHECKLIST

- [x] MongoDB Atlas cluster created
- [x] Database user and network access configured
- [x] Code pushed to GitHub
- [x] Render web service deployed
- [x] Environment variables configured
- [x] Custom domain added (securetrainer.com)
- [x] DNS records configured
- [x] SSL certificate active
- [x] Application tested and working

---

## 🎉 CONGRATULATIONS!

SecureTrainer is now live at:
- **https://securetrainer.com** 🚀

Your professional cybersecurity training platform is ready for users!

---

## 📞 SUPPORT

If you encounter issues:
1. Check Render logs for errors
2. Verify all environment variables
3. Test MongoDB connection separately
4. Review this guide step-by-step

---

**Deployment Date**: December 8, 2025  
**Platform**: Render.com (Free Tier)  
**Database**: MongoDB Atlas (Free Tier)  
**Domain**: securetrainer.com  
**Cost**: $0/month (Free tier with sleep) or $7/month (Always-on)
