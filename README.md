# AutoTest AI

**AutoTest AI** is an AI-powered multi-agent autonomous software testing platform built with modern web technologies. It automates requirement analysis, test generation, test execution, and self-healing for web applications.

---

## 🌍 Live Demo
You can test the deployed version of AutoTest AI here:
**[Your Deployment URL]** (e.g., https://autotest-ai.yourdomain.com)

---

## ✨ Features

- **Requirement Analysis**: AI agents analyze PRDs, SRS documents, and user stories
- **Test Generation**: Automatically generate Playwright, Selenium, and pytest scripts
- **Self-Healing Tests**: AI automatically fixes broken locators when UI changes
- **Beautiful UI**: Modern SaaS interface with dark mode
- **Dockerized**: Full Docker Compose support for easy deployment
- **Free & Open Source**: Uses Ollama for local AI inference (no API costs needed!)

## � Installation (First Time)
Please read `INSTALL_GUIDE.md` for step-by-step setup! It has everything you need to install Node.js, Python, and Ollama.

## �🚀 Quick Start - One-Click Launch!

### Windows (Easiest)
1. **Install Prerequisites**:
   - **Python 3.10+**: Download from https://www.python.org/downloads/ (IMPORTANT: Check "Add Python to PATH"!)
   - **Node.js 20+**: Download from https://nodejs.org/ (LTS version recommended)
   - (Optional) Ollama for AI features: Install from https://ollama.com/ and run `ollama pull llama3` in terminal
2. **Double-click `start.bat`** in the main "AutoTest AI" folder!

### macOS/Linux
1. **Install Prerequisites**: Python 3.10+, Node.js 20+, (optional) Ollama
2. **Run in Terminal**:
   ```bash
   chmod +x start.sh && ./start.sh
   ```

## 📱 Access the App
Once running:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger UI)**: http://localhost:8000/docs

## 🛠️ Manual Setup (If you prefer not to use scripts)

### Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
mkdir -p uploads
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

## 📖 Usage Guide
1. **Register/Login**: Create an account to get started
2. **Create a Project**: Add a new project and give it a name
3. **Add Requirements**: Upload your PRD, SRS, or paste requirements directly
4. **Generate Tests**: The AI will automatically create comprehensive test cases with Playwright scripts
5. **Execute Tests**: Run your tests and see results in real-time
6. **Self Healing**: Broken locators are automatically fixed by the AI!

## 📝 Tech Stack

### Backend
- FastAPI (Modern web framework)
- SQLite (Default for local dev; PostgreSQL for production)
- SQLAlchemy (ORM)
- LangChain + CrewAI (Multi-agent AI)
- Playwright (Browser automation)

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- ShadCN UI Components
- Framer Motion (Animations)
- Lucide Icons

## 📂 Project Structure
```
AutoTest AI/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── agents/       # AI testing agents
│   │   ├── api/v1/       # REST API endpoints
│   │   ├── core/         # Config, DB, security
│   │   └── models/       # SQLAlchemy models
│   ├── uploads/          # File upload storage
│   └── requirements.txt
├── frontend/             # Next.js + Tailwind frontend
│   ├── app/
│   └── components/ui/
├── start.bat             # Windows startup script
├── start.sh              # macOS/Linux startup script
└── README.md
```

## 🐳 Docker & Cloud Deployment

### Local Docker (Test Deploy Locally)
To run the full stack in Docker containers:
```bash
docker-compose up --build
```

### Cloud Deployment Options (Free/Cheap Tiers)

#### 1. Vercel (Frontend) + Render (Backend)
**Best for simple deployment**
- **Frontend**: Deploy Next.js app on Vercel (free)
- **Backend**: Deploy FastAPI on Render (free tier available)
- **Database**: Use Render's free PostgreSQL

#### 2. Railway (All-in-One)
- Easiest all-in-one platform
- Deploy full stack with Docker
- Free tier available

#### 3. DigitalOcean App Platform
- $200 credit for new users
- Supports Docker and Node.js/Python apps

---

### Environment Variables for Deployment
Set these variables in your cloud provider's dashboard:

```env
# Backend
SECRET_KEY=your_very_secret_key_here
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://... (optional)
OLLAMA_HOST=... (optional, for AI features)

# Frontend
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

## 🎯 Future Enhancements
- [ ] Full CI/CD integration (GitHub Actions, GitLab CI)
- [ ] Advanced report generation (PDF, Excel)
- [ ] Grafana dashboards for test analytics
- [ ] Kubernetes deployment files
- [ ] Team collaboration features
- [ ] Browser plugin for recording manual tests

## 📄 License
MIT License - feel free to use for your projects!
