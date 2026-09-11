# 🌐 AutoTest AI - Cloud Deployment Guide

Deploy AutoTest AI to the internet in minutes!

---

## 🚀 Quick Deploy Options

### Option 1: Railway (Recommended - Easiest)
**Free tier available, deploys in 5 minutes**

### Option 2: Render  
**Free tier available, automatic deploys**

### Option 3: Vercel (Frontend) + Railway (Backend)
**Best performance, free tier**

### Option 4: AWS/DigitalOcean
**Full control, requires server management**

---

## 🎯 OPTION 1: Railway (Fastest & Easiest)

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Click "Start a New Project"
3. Sign up with GitHub (recommended)

### Step 2: Deploy Backend

#### A. From GitHub (Recommended)
1. **Push code to GitHub first**:
   ```bash
   # Initialize git if not already done
   git init
   git add .
   git commit -m "Initial commit"
   
   # Create repository on GitHub and push
   git remote add origin https://github.com/yourusername/autotest-ai.git
   git push -u origin main
   ```

2. **Deploy on Railway**:
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect and deploy

#### B. From CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

### Step 3: Configure Environment Variables

In Railway dashboard, add these variables:

```env
# Required
DATABASE_URL=postgresql://[will be auto-generated]
SECRET_KEY=your-secret-key-min-32-chars
OPENAI_API_KEY=sk-your-api-key

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_ENABLED=true

# Frontend URL (after deployment)
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

### Step 4: Add PostgreSQL Database
1. In Railway dashboard, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway automatically sets DATABASE_URL

### Step 5: Deploy Frontend
1. Click "New Service"
2. Select your repository
3. Set Root Directory: `frontend`
4. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```

### Step 6: Get Your URLs
Railway provides:
- Backend: `https://autotest-backend-production.up.railway.app`
- Frontend: `https://autotest-frontend-production.up.railway.app`

**Your app is now live!** 🎉

---

## 🎯 OPTION 2: Render

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub

### Step 2: Deploy Backend
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: autotest-backend
   - **Root Directory**: backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Add PostgreSQL
1. Click "New +" → "PostgreSQL"
2. Copy the Internal Database URL
3. Add to backend environment variables as `DATABASE_URL`

### Step 4: Deploy Frontend
1. Click "New +" → "Web Service"
2. Connect repository
3. Configure:
   - **Name**: autotest-frontend
   - **Root Directory**: frontend
   - **Environment**: Node
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`

### Step 5: Environment Variables
Add in Render dashboard:
```env
DATABASE_URL=[from PostgreSQL]
SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-your-key
NEXT_PUBLIC_API_URL=https://autotest-backend.onrender.com
```

**Live in 10 minutes!** 🚀

---

## 🎯 OPTION 3: Vercel (Frontend) + Railway (Backend)

### Step 1: Deploy Backend to Railway
Follow Railway steps above for backend only

### Step 2: Deploy Frontend to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy frontend
cd frontend
vercel

# Follow prompts:
# - Project name: autotest-ai
# - Framework: Next.js
# - Build command: npm run build
# - Output directory: .next
```

### Step 3: Set Environment Variable
```bash
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://your-backend.railway.app
```

### Step 4: Deploy
```bash
vercel --prod
```

**Result**: Lightning-fast frontend + Stable backend! ⚡

---

## 🎯 OPTION 4: DigitalOcean Droplet (Full Control)

### Step 1: Create Droplet
1. Go to https://digitalocean.com
2. Create account ($200 free credit)
3. Click "Create" → "Droplets"
4. Choose:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic - $12/month (2GB RAM)
   - **Location**: Closest to you
   - **Authentication**: SSH keys

### Step 2: Access Droplet
```bash
ssh root@your-droplet-ip
```

### Step 3: Install Dependencies
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Git
apt install git -y
```

### Step 4: Clone & Deploy
```bash
# Clone repository
git clone https://github.com/yourusername/autotest-ai.git
cd autotest-ai

# Configure environment
cp .env.example .env
nano .env  # Edit with your values

# Deploy with Docker
docker-compose -f docker-compose.prod.yml up -d
```

### Step 5: Configure Domain (Optional)
```bash
# Install nginx
apt install nginx -y

# Copy our nginx config
cp nginx/nginx.conf /etc/nginx/sites-available/autotest
ln -s /etc/nginx/sites-available/autotest /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

# Restart nginx
systemctl restart nginx
```

### Step 6: SSL Certificate
```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get certificate
certbot --nginx -d yourdomain.com
```

**Your app is live with custom domain!** 🌐

---

## 📋 Pre-Deployment Checklist

### Code Preparation
- [ ] Code pushed to GitHub
- [ ] `.gitignore` includes sensitive files
- [ ] `.env.example` is up to date
- [ ] All dependencies in `requirements.txt` and `package.json`

### Environment Variables Ready
- [ ] `SECRET_KEY` generated
- [ ] `OPENAI_API_KEY` available
- [ ] `SMTP` credentials ready (optional)
- [ ] `GITHUB_TOKEN` ready (optional)

### Database
- [ ] PostgreSQL for production (Railway/Render auto-provision)
- [ ] Or SQLite for testing

---

## 🎨 Custom Domain Setup

### After Deployment on Railway/Render

1. **Get your deployment URL**:
   - Railway: `https://your-app.up.railway.app`
   - Render: `https://your-app.onrender.com`

2. **Buy a domain** (optional):
   - Namecheap: $8-15/year
   - Google Domains: $12/year
   - Cloudflare: At cost

3. **Configure DNS**:
   Add CNAME record:
   ```
   Type: CNAME
   Name: autotest (or @)
   Value: your-app.up.railway.app
   ```

4. **Add custom domain** in platform:
   - Railway: Settings → Domains → Add Domain
   - Render: Settings → Custom Domain

5. **SSL automatically configured** ✅

---

## 🔒 Security Checklist

Before going live:

- [ ] Change `SECRET_KEY` to strong random value
- [ ] Set `DEBUG=false` in production
- [ ] Use strong database passwords
- [ ] Enable HTTPS (auto on most platforms)
- [ ] Set up CORS correctly
- [ ] Enable rate limiting
- [ ] Backup database regularly

---

## 💰 Cost Comparison

| Platform | Backend | Frontend | Database | Total/Month |
|----------|---------|----------|----------|-------------|
| **Railway** | $5 | $5 | $5 | **$15** or Free tier |
| **Render** | Free | Free | Free | **$0** (limited) |
| **Vercel + Railway** | $5 | Free | $5 | **$10** |
| **DigitalOcean** | - | - | - | **$12+** |
| **AWS** | Variable | Variable | Variable | **$20-50+** |

**Recommendation**: Start with Railway free tier, upgrade as needed.

---

## 🚀 Quick Deploy Script

Save this as `deploy-cloud.sh`:

```bash
#!/bin/bash

echo "🚀 AutoTest AI - Cloud Deployment"
echo "=================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git..."
    git init
fi

# Add all files
echo "📝 Adding files to git..."
git add .

# Commit
echo "💾 Committing..."
git commit -m "Deploy to cloud"

# Push to GitHub
echo "📤 Pushing to GitHub..."
echo "Make sure you've created a repository on GitHub first!"
read -p "Enter your GitHub repository URL: " repo_url
git remote add origin $repo_url || git remote set-url origin $repo_url
git push -u origin main

echo ""
echo "✅ Code pushed to GitHub!"
echo ""
echo "🌐 Next steps:"
echo "1. Go to https://railway.app"
echo "2. Click 'Deploy from GitHub repo'"
echo "3. Select your repository"
echo "4. Add environment variables"
echo "5. Deploy!"
echo ""
echo "🎉 Your app will be live in 5 minutes!"
```

Make executable:
```bash
chmod +x deploy-cloud.sh
./deploy-cloud.sh
```

---

## 📞 Need Help?

### Documentation
- Railway: https://docs.railway.app
- Render: https://render.com/docs
- Vercel: https://vercel.com/docs

### Common Issues

**Build fails**:
- Check `requirements.txt` includes all dependencies
- Verify Python version (3.11+)
- Check logs in platform dashboard

**Database connection fails**:
- Verify `DATABASE_URL` is set
- Check PostgreSQL service is running
- Review database logs

**Frontend can't reach backend**:
- Update `NEXT_PUBLIC_API_URL` to backend URL
- Check CORS settings in backend
- Verify backend is running

---

## 🎯 Recommended Deployment

**For quickest deployment:**

1. **Push to GitHub** (5 minutes)
2. **Deploy on Railway** (5 minutes)
3. **Configure environment** (2 minutes)
4. **Test deployment** (2 minutes)

**Total time: 15 minutes to live!**

---

## ✅ Post-Deployment Checklist

After deployment:

- [ ] Test all pages load
- [ ] Create test user account
- [ ] Upload test requirement
- [ ] Generate and run test
- [ ] Check email notifications
- [ ] Verify API endpoints
- [ ] Test on mobile
- [ ] Share with team!

---

## 🎉 You're Live!

Your AutoTest AI is now accessible from anywhere in the world! 🌍

Share your URL:
- `https://your-app.railway.app`
- Or your custom domain: `https://autotest.yourdomain.com`

**Congratulations on deploying to production!** 🚀

---

**Need custom deployment help?** Check `DEPLOYMENT_GUIDE.md` for more options!
