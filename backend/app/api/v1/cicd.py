"""
CI/CD Integration API Endpoints
Handles GitHub Actions integration, workflow generation, and run tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user, encrypt_token, decrypt_token
from app.models.user import User
from app.models.project import Project
from app.models.cicd import CICDConfig, WorkflowRun, WorkflowTemplate
from app.api.v1.dependencies import get_owned_project
from app.services.github_service import GitHubService, validate_repo_name
from app.services.workflow_generator import WorkflowGenerator

router = APIRouter()


# ==================== REQUEST/RESPONSE MODELS ====================

class GitHubTokenRequest(BaseModel):
    github_token: str


class CICDConfigRequest(BaseModel):
    github_token: str
    repository_name: str
    default_branch: str = "main"
    python_version: str = "3.10"
    node_version: str = "20"
    test_command: str = "pytest"
    deployment_command: Optional[str] = None
    auto_trigger: bool = True


class WorkflowGenerateRequest(BaseModel):
    workflow_type: str  # test, regression, pr_test, deploy, nightly
    configuration: Dict[str, Any] = {}


class WorkflowTriggerRequest(BaseModel):
    workflow_id: str
    branch: Optional[str] = "main"
    inputs: Optional[Dict[str, str]] = None


class CICDConfigResponse(BaseModel):
    id: int
    project_id: int
    repository_name: Optional[str]
    default_branch: str
    workflows_enabled: bool
    webhook_enabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class WorkflowRunResponse(BaseModel):
    id: int
    workflow_name: str
    run_number: int
    status: str
    conclusion: Optional[str]
    branch: str
    author: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    run_url: Optional[str]
    
    class Config:
        from_attributes = True


# ==================== ENDPOINTS ====================

@router.post("/validate-token")
async def validate_github_token(
    request: GitHubTokenRequest,
    current_user: User = Depends(get_current_user)
):
    """Validate GitHub personal access token"""
    try:
        github = GitHubService(request.github_token)
        validation = github.validate_token()
        github.close()
        
        if validation["valid"]:
            return {
                "valid": True,
                "username": validation["username"],
                "name": validation["name"],
                "avatar_url": validation["avatar_url"],
                "rate_limit": validation["rate_limit"]
            }
        else:
            return {
                "valid": False,
                "error": validation["error"]
            }
            
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }


@router.get("/repositories")
async def list_repositories(
    github_token: str,
    current_user: User = Depends(get_current_user)
):
    """List repositories accessible by the GitHub token"""
    try:
        github = GitHubService(github_token)
        repos = github.list_user_repositories(limit=100)
        github.close()
        
        return {"repositories": repos}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/projects/{project_id}/config", response_model=CICDConfigResponse)
async def create_or_update_cicd_config(
    project_id: int,
    config_request: CICDConfigRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update CI/CD configuration for a project"""
    # Verify project ownership
    get_owned_project(db, project_id, current_user)
    
    # Validate repository name
    if not validate_repo_name(config_request.repository_name):
        raise HTTPException(
            status_code=400,
            detail="Invalid repository name format. Use 'owner/repo'"
        )
    
    # Validate GitHub token
    try:
        github = GitHubService(config_request.github_token)
        validation = github.validate_token()
        
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail="Invalid GitHub token")
        
        # Verify repo access
        repo = github.get_repository(config_request.repository_name)
        if not repo:
            raise HTTPException(
                status_code=404,
                detail=f"Repository {config_request.repository_name} not found or not accessible"
            )
        
        github.close()
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Encrypt token
    encrypted_token = encrypt_token(config_request.github_token)
    
    # Check if config exists
    config = db.query(CICDConfig).filter(CICDConfig.project_id == project_id).first()
    
    if config:
        # Update existing config
        config.github_token_encrypted = encrypted_token
        config.repository_name = config_request.repository_name
        config.default_branch = config_request.default_branch
        config.python_version = config_request.python_version
        config.node_version = config_request.node_version
        config.test_command = config_request.test_command
        config.deployment_command = config_request.deployment_command
        config.auto_trigger = config_request.auto_trigger
        config.workflows_enabled = True
        config.updated_at = datetime.utcnow()
    else:
        # Create new config
        config = CICDConfig(
            project_id=project_id,
            github_token_encrypted=encrypted_token,
            repository_name=config_request.repository_name,
            default_branch=config_request.default_branch,
            python_version=config_request.python_version,
            node_version=config_request.node_version,
            test_command=config_request.test_command,
            deployment_command=config_request.deployment_command,
            auto_trigger=config_request.auto_trigger,
            workflows_enabled=True
        )
        db.add(config)
    
    db.commit()
    db.refresh(config)
    
    return config


@router.get("/projects/{project_id}/config", response_model=CICDConfigResponse)
async def get_cicd_config(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get CI/CD configuration for a project"""
    get_owned_project(db, project_id, current_user)
    
    config = db.query(CICDConfig).filter(CICDConfig.project_id == project_id).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="CI/CD configuration not found")
    
    return config


@router.delete("/projects/{project_id}/config")
async def delete_cicd_config(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete CI/CD configuration"""
    get_owned_project(db, project_id, current_user)
    
    config = db.query(CICDConfig).filter(CICDConfig.project_id == project_id).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="CI/CD configuration not found")
    
    db.delete(config)
    db.commit()
    
    return {"message": "CI/CD configuration deleted successfully"}


@router.post("/projects/{project_id}/generate-workflow")
async def generate_workflow(
    project_id: int,
    request: WorkflowGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a GitHub Actions workflow file"""
    # Verify project ownership
    project = get_owned_project(db, project_id, current_user)
    
    # Get CI/CD config
    config = db.query(CICDConfig).filter(CICDConfig.project_id == project_id).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="CI/CD configuration not found. Please connect GitHub first.")
    
    # Decrypt token
    github_token = decrypt_token(config.github_token_encrypted)
    
    # Generate workflow based on type
    generator = WorkflowGenerator()
    workflow_content = None
    file_name = None
    
    try:
        if request.workflow_type == "test":
            workflow_content = generator.generate_test_workflow(
                project_name=project.name,
                python_version=config.python_version,
                node_version=config.node_version,
                test_command=config.test_command,
                deployment_url=project.deployment_url
            )
            file_name = "test.yml"
            
        elif request.workflow_type == "regression":
            workflow_content = generator.generate_regression_workflow(
                project_name=project.name,
                project_id=project_id,
                api_url=request.configuration.get("api_url", "http://localhost:8000"),
                api_token=request.configuration.get("api_token", ""),
                tags=request.configuration.get("tags", []),
                exclude_flaky=request.configuration.get("exclude_flaky", True),
                schedule_cron=request.configuration.get("schedule_cron", "0 2 * * *")
            )
            file_name = "regression.yml"
            
        elif request.workflow_type == "pr_test":
            workflow_content = generator.generate_pr_test_workflow(
                project_name=project.name,
                project_id=project_id,
                api_url=request.configuration.get("api_url", "http://localhost:8000"),
                api_token=request.configuration.get("api_token", ""),
                python_version=config.python_version
            )
            file_name = "pr-test.yml"
            
        elif request.workflow_type == "deploy":
            if not config.deployment_command:
                raise HTTPException(
                    status_code=400,
                    detail="Deployment command not configured"
                )
            workflow_content = generator.generate_deploy_workflow(
                project_name=project.name,
                deployment_command=config.deployment_command,
                environment=request.configuration.get("environment", "production"),
                requires_approval=request.configuration.get("requires_approval", True)
            )
            file_name = "deploy.yml"
            
        elif request.workflow_type == "nightly":
            workflow_content = generator.generate_nightly_workflow(
                project_name=project.name,
                project_id=project_id,
                api_url=request.configuration.get("api_url", "http://localhost:8000"),
                api_token=request.configuration.get("api_token", ""),
                schedule_cron=request.configuration.get("schedule_cron", "0 0 * * *")
            )
            file_name = "nightly.yml"
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown workflow type: {request.workflow_type}"
            )
        
        # Create/update file in GitHub
        github = GitHubService(github_token)
        result = github.create_or_update_file(
            repo_name=config.repository_name,
            file_path=f".github/workflows/{file_name}",
            content=workflow_content,
            commit_message=f"Add/Update {request.workflow_type} workflow via AutoTest AI",
            branch=config.default_branch
        )
        github.close()
        
        if result["success"]:
            return {
                "success": True,
                "workflow_type": request.workflow_type,
                "file_name": file_name,
                "file_path": f".github/workflows/{file_name}",
                "action": result["action"],
                "commit_url": result["commit_url"],
                "workflow_content": workflow_content
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/workflows")
async def list_workflows(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all workflows for a project"""
    get_owned_project(db, project_id, current_user)
    
    config = db.query(CICDConfig).filter(CICDConfig.project_id == project_id).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="CI/CD configuration not found")
    
    # Decrypt token
    github_token = decrypt_token(config.github_token_encrypted)
    
    try:
        github = GitHubService(github_token)
        workflows = github.list_workflows(config.repository_name)
        github.close()
        
        return {"workflows": workflows}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/workflow-runs", response_model=List[WorkflowRunResponse])
async def list_workflow_runs(
    project_id: int,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List workflow runs for a project"""
    get_owned_project(db, project_id, current_user)
    
    config = db.query(CICDConfig).filter(CICDConfig.project_id == project_id).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="CI/CD configuration not found")
    
    # Get from database
    runs = db.query(WorkflowRun).filter(
        WorkflowRun.config_id == config.id
    ).order_by(WorkflowRun.created_at.desc()).limit(limit).all()
    
    return runs


@router.post("/projects/{project_id}/trigger-workflow")
async def trigger_workflow(
    project_id: int,
    request: WorkflowTriggerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger a workflow run"""
    get_owned_project(db, project_id, current_user)
    
    config = db.query(CICDConfig).filter(CICDConfig.project_id == project_id).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="CI/CD configuration not found")
    
    # Decrypt token
    github_token = decrypt_token(config.github_token_encrypted)
    
    try:
        github = GitHubService(github_token)
        result = github.trigger_workflow(
            repo_name=config.repository_name,
            workflow_id=request.workflow_id,
            branch=request.branch or config.default_branch,
            inputs=request.inputs
        )
        github.close()
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Workflow {result['workflow']} triggered on branch {result['branch']}"
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow-templates")
async def list_workflow_templates():
    """List available workflow templates"""
    templates = WorkflowGenerator.list_available_templates()
    return {"templates": templates}


@router.get("/projects/{project_id}/branches")
async def list_branches(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List branches for the connected repository"""
    get_owned_project(db, project_id, current_user)
    
    config = db.query(CICDConfig).filter(CICDConfig.project_id == project_id).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="CI/CD configuration not found")
    
    # Decrypt token
    github_token = decrypt_token(config.github_token_encrypted)
    
    try:
        github = GitHubService(github_token)
        branches = github.get_branches(config.repository_name)
        github.close()
        
        return {"branches": branches}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WEBHOOK HANDLER ====================

@router.post("/webhook/github")
async def github_webhook_handler(
    payload: Dict[str, Any] = Body(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Handle GitHub webhook events
    
    Processes workflow_run events and updates database
    """
    event_type = payload.get("action")
    
    if "workflow_run" in payload:
        workflow_run = payload["workflow_run"]
        repo_full_name = payload.get("repository", {}).get("full_name")
        
        # Find config by repository name
        config = db.query(CICDConfig).filter(
            CICDConfig.repository_name == repo_full_name
        ).first()
        
        if not config:
            return {"message": "Repository not configured"}
        
        # Create or update workflow run record
        github_run_id = str(workflow_run.get("id"))
        run_record = db.query(WorkflowRun).filter(
            WorkflowRun.github_run_id == github_run_id
        ).first()
        
        if not run_record:
            run_record = WorkflowRun(
                config_id=config.id,
                github_run_id=github_run_id,
                workflow_name=workflow_run.get("name"),
                workflow_path=workflow_run.get("path"),
                run_number=workflow_run.get("run_number"),
                event=workflow_run.get("event"),
                status=workflow_run.get("status"),
                conclusion=workflow_run.get("conclusion"),
                branch=workflow_run.get("head_branch"),
                commit_sha=workflow_run.get("head_sha"),
                author=workflow_run.get("actor", {}).get("login"),
                run_url=workflow_run.get("html_url"),
                started_at=datetime.fromisoformat(workflow_run.get("run_started_at").replace("Z", "+00:00")) if workflow_run.get("run_started_at") else None,
                payload=payload
            )
            db.add(run_record)
        else:
            run_record.status = workflow_run.get("status")
            run_record.conclusion = workflow_run.get("conclusion")
            run_record.updated_at = datetime.utcnow()
            
            if workflow_run.get("status") == "completed":
                run_record.completed_at = datetime.utcnow()
                if run_record.started_at:
                    duration = (run_record.completed_at - run_record.started_at).total_seconds()
                    run_record.duration_seconds = int(duration)
        
        db.commit()
        
        return {"message": "Webhook processed successfully"}
    
    return {"message": "Event type not handled"}
