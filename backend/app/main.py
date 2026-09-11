from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import engine, Base
from app.models import platform, project, requirement, test_case, test_execution, user
from app.api.v1 import (
    agents,
    auth,
    bugs,
    chat,
    cicd,
    dashboard,
    executions,
    notifications,
    projects,
    regression,
    reports,
    repositories,
    requirements,
    tests,
    visual_tests,
)
import os
import traceback

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Error occurred: {exc}")
    print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": traceback.format_exc()}
    )

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(repositories.router, prefix="/api/v1/repositories", tags=["Repositories"])
app.include_router(requirements.router, prefix="/api/v1/requirements", tags=["Requirements"])
app.include_router(tests.router, prefix="/api/v1/tests", tags=["Tests"])
app.include_router(executions.router, prefix="/api/v1/executions", tags=["Executions"])
app.include_router(bugs.router, prefix="/api/v1/bugs", tags=["Bugs"])
app.include_router(regression.router, prefix="/api/v1/regression", tags=["Regression"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["AI Chat"])
app.include_router(cicd.router, prefix="/api/v1/cicd", tags=["CI/CD"])
app.include_router(visual_tests.router, prefix="/api/v1/visual-tests", tags=["Visual Testing"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
