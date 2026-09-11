# 🌐 Deploy AutoTest AI to Internet - Step by Step Guide

Your code is ready! Follow these simple steps to make your app live on the internet.

---

## ✅ STATUS: Code is on GitHub!

Your repository: https://github.com/MSNarayana35/1253

---

## 🚀 DEPLOY TO RAILWAY (5 Minutes)

### Step 1: Create Railway Account (1 minute)

1. Go to: **https://railway.app**
2. Click **"Start a New Project"**
3. Click **"Login with GitHub"**
4. Authorize Railway to access your GitHub

### Step 2: Deploy Your App (2 minutes)

1. After login, click **"+ New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and select: **"MSNarayana35/1253"**
4. Railway will start deploying automatically!

### Step 3: Add PostgreSQL Database (1 minute)

1. In your Railway project, click **"+ New"**
2. Select **"Database"**
3. Click **"PostgreSQL"**
4. Database will be created and DATABASE_URL auto-configured ✅

### Step 4: Configure Environment Variables (1 minute)

1. Click on your **backend service**
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. Add these (one by one):

```
SECRET_KEY=autotest-secret-key-production-2024-change-this-value
OPENAI_API_KEY=sk-your-api-key-here-optional
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tool.autotest.ai@gmail.com
SMTP_PASSWORD=fgaj mfod ybcl wvkj
SMTP_ENABLED=true
```

**Note**: Railway automatically adds `DATABASE_URL` when you create PostgreSQL

### Step 5: Get Your Live URL! (Done!)

1. Go to **"Settings"** tab
2. Under **"Domains"**, you'll see your URL
3. Example: `https://autotest-ai-production.up.railway.app`

**🎉 YOUR APP IS LIVE ON THE INTERNET!**

---

## 🌐 Alternative: Deploy to Render (Free)

### Step 1: Create Render Account

1. Go to: **https://render.com**
2. Sign up with GitHub
3. Authorize Render

### Step 2: Deploy Backend

1. Click **"New +"** → **"Web Service"**
2. Connect **"MSNarayana35/1253"** repository
3. Configure:
   - **Name**: `autotest-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

4. Click **"Create Web Service"**

### Step 3: Add PostgreSQL

1. Click **"New +"** → **"PostgreSQL"**
2. Name: `autotest-db`
3. Plan: `Free`
4. Click **"Create Database"**
5. Copy the **"Internal Database URL"**

### Step 4: Add Environment Variables to Backend

1. Go to your backend service
2. Click **"Environment"** tab
3. Add:

```
DATABASE_URL=[paste Internal Database URL]
SECRET_KEY=autotest-secret-key-production-2024
OPENAI_API_KEY=sk-optional
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tool.autotest.ai@gmail.com
SMTP_PASSWORD=fgaj mfod ybcl wvkj
SMTP_ENABLED=true
```

### Step 5: Deploy Frontend

1. Click **"New +"** → **"Web Service"**
2. Connect same repository
3. Configure:
   - **Name**: `autotest-frontend`
   - **Root Directory**: `frontend`
   - **Environment**: `Node`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`
   - **Instance Type**: `Free`

4. Add Environment Variable:
```
NEXT_PUBLIC_API_URL=https://autotest-backend.onrender.com
```
(Replace with your actual backend URL)

5. Click **"Create Web Service"**

**🎉 YOUR APP IS LIVE!**

Frontend: `https://autotest-frontend.onrender.com`

---

## 🎯 Easiest Option: Vercel (Frontend Only)

If you just want the frontend live quickly:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel login
vercel

# Follow prompts, select defaults
# Deploy to production
vercel --prod
```

**Done in 2 minutes!**

---

## 📋 What You Need

### Required (for AI features)
- [ ] OpenAI API Key (get from https://platform.openai.com/api-keys)

### Optional (for emails)
- [ ] Gmail account with App Password
- [ ] Or any SMTP server credentials

### Optional (for integrations)
- [ ] GitHub Personal Access Token
- [ ] Slack Webhook URL
- [ ] Discord Webhook URL

---

## 🔑 Generate Secure SECRET_KEY

Run this command to generate a strong secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Use this value for `SECRET_KEY` in production!

---

## ✅ Post-Deployment Checklist

After deployment:

1. **Visit your live URL**
   - Test if homepage loads
   - Create an account
   - Upload a requirement
   - Generate and run a test

2. **Check logs**
   - Railway: Click service → "Logs" tab
   - Render: Service → "Logs"
   - Look for any errors

3. **Test API**
   - Visit: `https://your-app-url.com/docs`
   - Try the /health endpoint
   - Verify it shows API documentation

4. **Share with team!**
   - Your app is now accessible worldwide
   - Share the URL with anyone

---

## 🆘 Troubleshooting

### Build Fails

**Error**: `Module not found`
- **Solution**: Check `requirements.txt` has all dependencies
- Run locally: `pip install -r backend/requirements.txt`

**Error**: `Port already in use`
- **Solution**: Use `$PORT` environment variable (Railway/Render auto-set this)

### Database Connection Fails

**Error**: `Connection refused`
- **Solution**: Verify `DATABASE_URL` is set correctly
- Check PostgreSQL service is running
- Use Internal Database URL (not external)

### Frontend Can't Reach Backend

**Error**: `Network error` or `CORS error`
- **Solution**: Update `NEXT_PUBLIC_API_URL` to your backend URL
- Verify CORS settings in backend allow your frontend domain

### App is Slow

**Free tiers sleep after inactivity**
- First request may take 30-60 seconds
- Subsequent requests are fast
- **Solution**: Upgrade to paid tier ($5-10/month) for always-on

---

## 💰 Costs

### Railway
- **Free Tier**: $5 credit/month (enough for hobby projects)
- **Paid**: ~$10-20/month for production

### Render
- **Free Tier**: Completely free (with limitations)
  - Sleeps after 15 min inactivity
  - 512 MB RAM
  - Good for demos
- **Paid**: $7/month for always-on

### Vercel
- **Free Tier**: Free forever for frontend
- **Paid**: Only if you need more

**Recommendation**: Start free, upgrade when needed!

---

## 🎉 Success Criteria

Your deployment is successful when:

- ✅ You can access your app URL from any device
- ✅ Homepage loads without errors
- ✅ You can create an account
- ✅ You can create a project
- ✅ API docs are accessible
- ✅ Health check returns healthy

---

## 📞 Quick Links

### Railway
- Dashboard: https://railway.app/dashboard
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

### Render
- Dashboard: https://dashboard.render.com
- Docs: https://render.com/docs
- Support: support@render.com

### Vercel
- Dashboard: https://vercel.com/dashboard
- Docs: https://vercel.com/docs

---

## 🚀 You're Ready!

**Choose your deployment platform and follow the steps above!**

**Recommended for beginners**: Railway (easiest)  
**Recommended for free**: Render (completely free tier)  
**Recommended for speed**: Vercel + Railway

---

## 🎊 After Deployment

Once live, you can:

1. **Share your URL** with team/clients
2. **Add custom domain** (optional)
3. **Setup monitoring** (free with UptimeRobot)
4. **Configure backups** (automatic on Railway/Render)
5. **Scale up** as traffic grows

---

**🌐 YOUR APP WILL BE LIVE IN 5-10 MINUTES!**

**Start here**: https://railway.app

**Questions?** Check `CLOUD_DEPLOYMENT.md` for detailed guides!

---

**Good luck with your deployment!** 🚀

Your AutoTest AI will soon be accessible from anywhere in the world! 🌍
