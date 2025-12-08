# 🚀 Quick Deployment Checklist

Use this checklist to deploy SecureTrainer to Render.com in under 30 minutes!

---

## ☁️ STEP 1: MongoDB Atlas (5 min)

- [ ] Create account at mongodb.com/atlas
- [ ] Create FREE cluster (M0)
- [ ] Create database user (save password!)
- [ ] Allow IP: 0.0.0.0/0 (Network Access)
- [ ] Copy connection string
- [ ] Replace `<password>` in connection string

**Connection String Format:**
```
mongodb+srv://username:password@cluster.xxxxx.mongodb.net/securetrainer?retryWrites=true&w=majority
```

---

## 🐙 STEP 2: Push to GitHub (10 min)

```powershell
# In securetrainer folder:
git init
git add .
git commit -m "Initial deployment"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/securetrainer.git
git branch -M main
git push -u origin main
```

---

## 🌐 STEP 3: Deploy on Render (10 min)

1. **Create Account**: render.com → Sign up with GitHub
2. **New Web Service**: Connect `securetrainer` repository
3. **Configure**:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn securetrainer:app`
   - Plan: **Free**

4. **Environment Variables** (click Advanced):
   ```
   PYTHON_VERSION = 3.11.0
   SECRET_KEY = <random 50+ chars>
   FLASK_ENV = production
   MONGO_URI = <your MongoDB Atlas string>
   MAIL_SERVER = smtp.gmail.com
   MAIL_PORT = 587
   MAIL_USE_TLS = True
   MAIL_USERNAME = your-email@gmail.com
   MAIL_PASSWORD = your-app-password
   ADMIN_TOKEN = <random token>
   ADMIN_REGISTRATION_TOKEN = <random token>
   ```

5. **Deploy!** → Wait 3-5 minutes

---

## 🔗 STEP 4: Custom Domain (5 min)

1. **Add in Render**:
   - Settings → Custom Domain
   - Add: `securetrainer.com`
   - Add: `www.securetrainer.com`

2. **Configure DNS** (at your registrar):
   ```
   Type: A
   Name: @
   Value: 216.24.57.1
   
   Type: CNAME
   Name: www
   Value: securetrainer.onrender.com
   ```

3. **Wait**: 10-60 min for DNS propagation

---

## ✅ VERIFICATION

- [ ] https://securetrainer.onrender.com loads
- [ ] https://securetrainer.com loads (after DNS)
- [ ] Registration works
- [ ] Login works
- [ ] Challenges load
- [ ] No errors in Render logs

---

## 🆘 TROUBLESHOOTING

**Build fails?**
- Check `requirements.txt` has all dependencies
- Verify `PYTHON_VERSION=3.11.0` in environment

**App crashes?**
- Check Render logs for errors
- Verify MongoDB connection string
- Test MongoDB user permissions

**Domain not working?**
- Wait 1-2 hours for DNS
- Check DNS at dnschecker.org
- Verify A record IP: 216.24.57.1

---

## 🎯 NEXT STEPS

After deployment:
1. Test all features thoroughly
2. Create admin account
3. Add sample challenges
4. Monitor logs for errors
5. Consider upgrading to paid ($7/mo) to remove sleep

---

**Total Time**: 30 minutes  
**Total Cost**: $0 (Free tier)  
**Result**: Live at securetrainer.com 🎉
