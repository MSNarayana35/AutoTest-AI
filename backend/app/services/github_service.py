"""
GitHub Service for CI/CD Integration
Handles GitHub API operations: repos, workflows, PRs, commits
"""

from github import Github, GithubException, Repository
from typing import Optional, List, Dict, Any
import base64
import yaml
from datetime import datetime
import re


class GitHubService:
    """Service for interacting with GitHub API"""
    
    def __init__(self, access_token: str):
        """
        Initialize GitHub service with access token
        
        Args:
            access_token: GitHub personal access token
        """
        self.client = Github(access_token)
        self.user = None
        try:
            self.user = self.client.get_user()
        except GithubException as e:
            raise ValueError(f"Invalid GitHub token: {str(e)}")
    
    def validate_token(self) -> Dict[str, Any]:
        """Validate GitHub token and return user info"""
        try:
            user = self.client.get_user()
            return {
                "valid": True,
                "username": user.login,
                "name": user.name,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "rate_limit": self.client.get_rate_limit().core.remaining
            }
        except GithubException as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def get_repository(self, repo_name: str) -> Optional[Repository.Repository]:
        """
        Get repository by name (format: owner/repo)
        
        Args:
            repo_name: Repository name in format 'owner/repo'
            
        Returns:
            Repository object or None
        """
        try:
            return self.client.get_repo(repo_name)
        except GithubException as e:
            print(f"Error getting repository {repo_name}: {e}")
            return None
    
    def list_user_repositories(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List repositories accessible by the user"""
        try:
            repos = self.user.get_repos(sort="updated", direction="desc")
            result = []
            
            for repo in repos[:limit]:
                result.append({
                    "id": repo.id,
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "private": repo.private,
                    "url": repo.html_url,
                    "clone_url": repo.clone_url,
                    "default_branch": repo.default_branch,
                    "language": repo.language,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
                })
            
            return result
        except GithubException as e:
            print(f"Error listing repositories: {e}")
            return []
    
    def get_branches(self, repo_name: str) -> List[Dict[str, str]]:
        """Get all branches for a repository"""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return []
            
            branches = repo.get_branches()
            return [
                {
                    "name": branch.name,
                    "sha": branch.commit.sha,
                    "protected": branch.protected
                }
                for branch in branches
            ]
        except GithubException as e:
            print(f"Error getting branches: {e}")
            return []
    
    def create_or_update_file(
        self,
        repo_name: str,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Create or update a file in the repository
        
        Args:
            repo_name: Repository name (owner/repo)
            file_path: Path to file in repo
            content: File content
            commit_message: Commit message
            branch: Branch name
            
        Returns:
            Dict with commit info
        """
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return {"success": False, "error": "Repository not found"}
            
            # Try to get existing file
            try:
                existing_file = repo.get_contents(file_path, ref=branch)
                # Update existing file
                result = repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    sha=existing_file.sha,
                    branch=branch
                )
                action = "updated"
            except GithubException:
                # File doesn't exist, create it
                result = repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    branch=branch
                )
                action = "created"
            
            return {
                "success": True,
                "action": action,
                "file_path": file_path,
                "commit_sha": result["commit"].sha,
                "commit_url": result["commit"].html_url
            }
            
        except GithubException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_file_content(
        self,
        repo_name: str,
        file_path: str,
        branch: str = "main"
    ) -> Optional[str]:
        """Get content of a file from repository"""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return None
            
            file_content = repo.get_contents(file_path, ref=branch)
            if isinstance(file_content, list):
                return None  # It's a directory
            
            # Decode base64 content
            content = base64.b64decode(file_content.content).decode('utf-8')
            return content
            
        except GithubException as e:
            print(f"Error getting file content: {e}")
            return None
    
    def list_workflows(self, repo_name: str) -> List[Dict[str, Any]]:
        """List all GitHub Actions workflows in repository"""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return []
            
            workflows = repo.get_workflows()
            return [
                {
                    "id": wf.id,
                    "name": wf.name,
                    "path": wf.path,
                    "state": wf.state,
                    "created_at": wf.created_at.isoformat() if wf.created_at else None,
                    "updated_at": wf.updated_at.isoformat() if wf.updated_at else None,
                    "url": wf.html_url
                }
                for wf in workflows
            ]
        except GithubException as e:
            print(f"Error listing workflows: {e}")
            return []
    
    def get_workflow_runs(
        self,
        repo_name: str,
        workflow_id: Optional[int] = None,
        branch: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get workflow runs for a repository"""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return []
            
            if workflow_id:
                workflow = repo.get_workflow(workflow_id)
                runs = workflow.get_runs()
            else:
                runs = repo.get_workflow_runs(branch=branch)
            
            result = []
            for run in runs[:limit]:
                result.append({
                    "id": run.id,
                    "name": run.name,
                    "head_branch": run.head_branch,
                    "head_sha": run.head_sha,
                    "status": run.status,
                    "conclusion": run.conclusion,
                    "created_at": run.created_at.isoformat() if run.created_at else None,
                    "updated_at": run.updated_at.isoformat() if run.updated_at else None,
                    "run_number": run.run_number,
                    "url": run.html_url,
                    "event": run.event,
                    "author": run.actor.login if run.actor else None
                })
            
            return result
            
        except GithubException as e:
            print(f"Error getting workflow runs: {e}")
            return []
    
    def trigger_workflow(
        self,
        repo_name: str,
        workflow_id: str,
        branch: str = "main",
        inputs: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Trigger a workflow run"""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return {"success": False, "error": "Repository not found"}
            
            workflow = repo.get_workflow(workflow_id)
            ref = repo.get_branch(branch)
            
            # Trigger workflow
            success = workflow.create_dispatch(ref=ref, inputs=inputs or {})
            
            return {
                "success": success,
                "workflow": workflow.name,
                "branch": branch
            }
            
        except GithubException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_pull_request(
        self,
        repo_name: str,
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ) -> Dict[str, Any]:
        """Create a pull request"""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return {"success": False, "error": "Repository not found"}
            
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head,
                base=base
            )
            
            return {
                "success": True,
                "pr_number": pr.number,
                "pr_url": pr.html_url,
                "state": pr.state
            }
            
        except GithubException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_pr_comment(
        self,
        repo_name: str,
        pr_number: int,
        comment: str
    ) -> Dict[str, Any]:
        """Add a comment to a pull request"""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return {"success": False, "error": "Repository not found"}
            
            pr = repo.get_pull(pr_number)
            issue_comment = pr.create_issue_comment(comment)
            
            return {
                "success": True,
                "comment_id": issue_comment.id,
                "comment_url": issue_comment.html_url
            }
            
        except GithubException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_commit_status(
        self,
        repo_name: str,
        sha: str
    ) -> Dict[str, Any]:
        """Get commit status checks"""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return {"success": False, "error": "Repository not found"}
            
            commit = repo.get_commit(sha)
            statuses = commit.get_statuses()
            
            status_list = [
                {
                    "state": status.state,
                    "description": status.description,
                    "context": status.context,
                    "target_url": status.target_url,
                    "created_at": status.created_at.isoformat() if status.created_at else None
                }
                for status in statuses
            ]
            
            return {
                "success": True,
                "sha": sha,
                "statuses": status_list
            }
            
        except GithubException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_webhook(
        self,
        repo_name: str,
        webhook_url: str,
        events: List[str] = None,
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a webhook for the repository"""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return {"success": False, "error": "Repository not found"}
            
            if events is None:
                events = ["push", "pull_request", "workflow_run"]
            
            config = {
                "url": webhook_url,
                "content_type": "json"
            }
            
            if secret:
                config["secret"] = secret
            
            hook = repo.create_hook(
                name="web",
                config=config,
                events=events,
                active=True
            )
            
            return {
                "success": True,
                "hook_id": hook.id,
                "hook_url": hook.url,
                "events": events
            }
            
        except GithubException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def close(self):
        """Close GitHub client connection"""
        if self.client:
            self.client.close()


def validate_repo_name(repo_name: str) -> bool:
    """Validate repository name format (owner/repo)"""
    pattern = r'^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$'
    return bool(re.match(pattern, repo_name))
