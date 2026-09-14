# 🚀 How to Run AutoTest AI

**Quick Start Guide** - Get your app running in 5 minutes!

---

## 📋 Prerequisites

Before running, ensure you have:
- ✅ Python 3.8+ installed
- ✅ Node.js 16+ installed
- ✅ Git installed (already done)

---

## 🎯 Quick Start (Easiest Method)

### **Option 1: Use the Startup Script** ⭐ RECOMMENDED

Just double-click or run:
```bash
start.bat
```

This will automatically:
1. Start the backend on port 8000
2. Start the frontend on port 3000
3. Open your browser

**That's it!** 🎉

---

## 🔧 Manual Start (Step-by-Step)

If you prefer to run manually or need more control:

### **Step 1: Start Backend** (Terminal 1)

```powershell
# Navigate to backend folder
cd backend

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at**: http://localhost:8000

---

### **Step 2: Start Frontend** (Terminal 2)

Open a **NEW terminal** and run:

```powershell
# Navigate to frontend folder
cd frontend

# Install dependencies (first time only)
npm install

# Run the development server
npm run dev
```

**Frontend will be available at**: http://localhost:3000

---

## ✅ Verify Installation

### **Check Backend**:
Open in browser: http://localhost:8000/health

Should return:
```json
{
  "status": "healthy"
}
```

### **Check Frontend**:
Open in browser: http://localhost:3000

Should show the AutoTest AI landing page.

---

## 🎮 Full Command Reference

### **Backend Commands**:

```powershell
# Install dependencies
cd backend
pip install -r requirements.txt

# Run development server (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run production server (no reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run with specific port
uvicorn app.main:app --reload --port 8080

# Check Python version
python --version

# Test imports
python -c "import fastapi; print('FastAPI installed')"
```

### **Frontend Commands**:

```powershell
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev

# Run on different port
npm run dev -- --port 3001

# Build for production
npm run build

# Start production server
npm start

# Check Node version
node --version
npm --version
```

---

## 📦 First Time Setup

If this is your **first time** running the app:

### **1. Install Backend Dependencies**:
```powershell
cd backend
pip install -r requirements.txt
```

Wait for installation to complete (~2-5 minutes).

### **2. Install Frontend Dependencies**:
```powershell
cd frontend
npm install
```

Wait for installation to complete (~3-5 minutes).

### **3. Configure Environment** (Optional):
The `.env` file is already configured, but you can customize:

```powershell
# Edit .env file if needed
notepad .env
```

Key settings:
- `OPENAI_API_KEY` - For AI features (optional for basic testing)
- `SMTP_*` - For email notifications (already configured)

---

## 🌐 Access the Application

Once both servers are running:

### **Main Application**:
```
http://localhost:3000
```

### **API Documentation**:
```
http://localhost:8000/docs
```

### **Health Check**:
```
http://localhost:8000/health
```

---

## 🛠️ Troubleshooting

### **Problem: Port Already in Use**

**Backend (Port 8000)**:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or use different port
uvicorn app.main:app --reload --port 8080
```

**Frontend (Port 3000)**:
```powershell
# Find process using port 3000
netstat -ano | findstr :3000

# Kill the process
taskkill /PID <PID> /F

# Or use different port
npm run dev -- --port 3001
```

### **Problem: Module Not Found**

**Backend**:
```powershell
cd backend
pip install -r requirements.txt --force-reinstall
```

**Frontend**:
```powershell
cd frontend
rm -rf node_modules
npm install
```

### **Problem: Database Not Found**

The SQLite database is created automatically. But if needed:
```powershell
cd backend
python -c "from app.core.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

### **Problem: Python/Node Not Installed**

**Install Python**:
1. Download from: https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Verify: `python --version`

**Install Node.js**:
1. Download from: https://nodejs.org/
2. Install with default settings
3. Verify: `node --version`

---

## 🔥 Quick Commands Summary

### **Using Startup Script** (Easiest):
```bash
# Just run this!
start.bat
```

### **Manual Start**:
```powershell
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend (open new terminal)
cd frontend
npm run dev
```

### **Stop Servers**:
- Press `Ctrl + C` in each terminal

---

## 📊 What Happens When You Run

### **Backend (FastAPI)**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### **Frontend (Next.js)**:
```
ready - started server on 0.0.0.0:3000
✓ Compiled successfully
```

---

## 🎯 Testing the App

Once running, you can:

1. **Register a User**:
   - Go to http://localhost:3000
   - Click "Sign Up"
   - Create an account

2. **Create a Project**:
   - Login with your credentials
   - Click "New Project"
   - Enter project details

3. **Upload Requirements**:
   - Open your project
   - Go to "Requirements" tab
   - Upload a document (PDF, DOCX, or TXT)

4. **Generate Tests**:
   - Click "Generate Tests" button
   - AI will create test cases

5. **Run Tests**:
   - Go to "Test Cases" tab
   - Click "Run Test" or "Run All Tests"
   - View results in real-time

---

## 🔄 Development Workflow

### **Making Changes**:

**Backend Changes**:
- Edit Python files in `backend/app/`
- Server auto-reloads (if using `--reload`)
- Changes appear immediately

**Frontend Changes**:
- Edit React files in `frontend/app/` or `frontend/components/`
- Hot Module Replacement (HMR) updates instantly
- No need to refresh browser

### **Restart Servers**:
- Backend: Press `Ctrl + C`, then re-run uvicorn command
- Frontend: Press `Ctrl + C`, then re-run `npm run dev`

---

## 🐳 Docker Alternative (Optional)

If you prefer Docker:

```powershell
# Build and run with Docker Compose
docker-compose up --build

# Access at:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
```

---

## 📱 Production Deployment

For deploying to production servers, see:
- `DEPLOYMENT_GUIDE.md` - Complete deployment instructions
- Railway: https://railway.app
- Render: https://render.com
- Vercel: https://vercel.com

---

## ✅ Success Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Can access http://localhost:3000
- [ ] Can access http://localhost:8000/docs
- [ ] Health check returns "healthy"

---

## 🎉 You're Ready!

Your AutoTest AI application is now running locally!

**Default URLs**:
- 🌐 Application: http://localhost:3000
- 📚 API Docs: http://localhost:8000/docs
- ❤️ Health: http://localhost:8000/health

**Next Steps**:
1. Create an account
2. Create a project
3. Upload requirements
4. Generate AI tests
5. Run tests and see results!

---

## 📞 Need Help?

- Check `TESTING_GUIDE.md` for detailed testing instructions
- Check `DEPLOYMENT_GUIDE.md` for production deployment
- Review API documentation at http://localhost:8000/docs

**Happy Testing! 🚀**
