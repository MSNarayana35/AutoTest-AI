"""
GitHub Actions Workflow Generator
Generates YAML workflow files for CI/CD automation
"""

import yaml
from typing import Dict, List, Optional, Any
from datetime import datetime


class WorkflowGenerator:
    """Generate GitHub Actions workflow YAML files"""
    
    @staticmethod
    def generate_test_workflow(
        project_name: str,
        python_version: str = "3.10",
        node_version: str = "20",
        test_command: str = "pytest",
        deployment_url: Optional[str] = None,
        api_url: Optional[str] = None,
        trigger_on: List[str] = None
    ) -> str:
        """
        Generate a workflow for running tests
        
        Args:
            project_name: Name of the project
            python_version: Python version to use
            node_version: Node.js version to use
            test_command: Command to run tests
            deployment_url: URL of deployment to test
            api_url: AutoTest AI API URL
            trigger_on: Events that trigger the workflow
            
        Returns:
            YAML workflow content
        """
        if trigger_on is None:
            trigger_on = ["push", "pull_request"]
        
        workflow = {
            "name": f"{project_name} - Test Suite",
            "on": {
                event: {
                    "branches": ["main", "develop"]
                } if event in ["push", "pull_request"] else None
                for event in trigger_on
            },
            "jobs": {
                "test": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v5",
                            "with": {
                                "python-version": python_version
                            }
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt"
                        },
                        {
                            "name": "Run tests",
                            "run": test_command,
                            "env": {
                                "DEPLOYMENT_URL": deployment_url or "http://localhost:3000",
                                "AUTOTEST_API_URL": api_url or "http://localhost:8000"
                            }
                        },
                        {
                            "name": "Upload test results",
                            "if": "always()",
                            "uses": "actions/upload-artifact@v3",
                            "with": {
                                "name": "test-results",
                                "path": "test-results/"
                            }
                        }
                    ]
                }
            }
        }
        
        # Clean up None values
        workflow["on"] = {k: v for k, v in workflow["on"].items() if v is not None}
        
        return yaml.dump(workflow, sort_keys=False, default_flow_style=False)
    
    @staticmethod
    def generate_regression_workflow(
        project_name: str,
        project_id: int,
        api_url: str,
        api_token: str,
        tags: Optional[List[str]] = None,
        exclude_flaky: bool = True,
        schedule_cron: str = "0 2 * * *"  # Daily at 2 AM
    ) -> str:
        """
        Generate a workflow for regression testing
        
        Args:
            project_name: Name of the project
            project_id: AutoTest AI project ID
            api_url: AutoTest AI API URL
            api_token: API authentication token
            tags: Tags to filter tests
            exclude_flaky: Whether to exclude flaky tests
            schedule_cron: Cron schedule for automatic runs
            
        Returns:
            YAML workflow content
        """
        workflow = {
            "name": f"{project_name} - Regression Suite",
            "on": {
                "schedule": [
                    {"cron": schedule_cron}
                ],
                "workflow_dispatch": {
                    "inputs": {
                        "tags": {
                            "description": "Comma-separated tags to filter tests",
                            "required": False,
                            "default": ",".join(tags) if tags else ""
                        },
                        "exclude_flaky": {
                            "description": "Exclude flaky tests",
                            "required": False,
                            "default": "true" if exclude_flaky else "false",
                            "type": "boolean"
                        }
                    }
                }
            },
            "jobs": {
                "regression": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Run Regression Suite",
                            "run": f"""
curl -X POST "{api_url}/api/v1/tests/project/{project_id}/run-regression" \\
  -H "Authorization: Bearer {api_token}" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "url": "${{{{ github.server_url }}}}/${{{{ github.repository }}}}",
    "tags": "${{{{ github.event.inputs.tags || '{",".join(tags) if tags else ""}' }}}}".split(","),
    "exclude_flaky": ${{{{ github.event.inputs.exclude_flaky || '{str(exclude_flaky).lower()}' }}}}
  }}'
                            """.strip()
                        },
                        {
                            "name": "Check results",
                            "run": """
echo "Regression suite completed. Check AutoTest AI dashboard for detailed results."
echo "Dashboard: {api_url}/dashboard"
                            """.strip()
                        }
                    ]
                }
            }
        }
        
        return yaml.dump(workflow, sort_keys=False, default_flow_style=False)
    
    @staticmethod
    def generate_pr_test_workflow(
        project_name: str,
        project_id: int,
        api_url: str,
        api_token: str,
        python_version: str = "3.10"
    ) -> str:
        """
        Generate a workflow for PR testing with comment integration
        
        Args:
            project_name: Name of the project
            project_id: AutoTest AI project ID
            api_url: AutoTest AI API URL
            api_token: API authentication token
            python_version: Python version to use
            
        Returns:
            YAML workflow content
        """
        workflow = {
            "name": f"{project_name} - PR Tests",
            "on": {
                "pull_request": {
                    "types": ["opened", "synchronize", "reopened"]
                }
            },
            "jobs": {
                "test": {
                    "runs-on": "ubuntu-latest",
                    "permissions": {
                        "contents": "read",
                        "pull-requests": "write"
                    },
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Run AutoTest AI Tests",
                            "id": "autotest",
                            "run": f"""
RESPONSE=$(curl -s -X POST "{api_url}/api/v1/tests/project/{project_id}/run-all" \\
  -H "Authorization: Bearer {api_token}" \\
  -H "Content-Type: application/json" \\
  -d '{{"url": "${{{{ github.server_url }}}}/${{{{ github.repository }}}}"}}')

echo "response=$RESPONSE" >> $GITHUB_OUTPUT
                            """.strip()
                        },
                        {
                            "name": "Post PR Comment",
                            "uses": "actions/github-script@v7",
                            "with": {
                                "script": """
const response = JSON.parse('${{ steps.autotest.outputs.response }}');
const total = response.total || 0;
const passed = response.passed || 0;
const failed = response.failed || 0;
const successRate = response.success_rate || 0;

const emoji = successRate >= 90 ? '✅' : successRate >= 70 ? '⚠️' : '❌';
const status = successRate >= 90 ? 'PASSED' : successRate >= 70 ? 'WARNING' : 'FAILED';

const comment = `## ${emoji} AutoTest AI - Test Results

**Status:** ${status}
**Success Rate:** ${successRate}%

| Metric | Value |
|--------|-------|
| Total Tests | ${total} |
| ✅ Passed | ${passed} |
| ❌ Failed | ${failed} |

${failed > 0 ? `### Failed Tests
${response.results.filter(r => r.status === 'FAILED').slice(0, 5).map(r => `- ${r.title}`).join('\\n')}
${failed > 5 ? `\\n_...and ${failed - 5} more_` : ''}
` : ''}

[View Full Report](""" + api_url + """/dashboard)

---
_Powered by AutoTest AI_ 🤖
`;

github.rest.issues.createComment({
  issue_number: context.issue.number,
  owner: context.repo.owner,
  repo: context.repo.repo,
  body: comment
});
                                """.strip()
                            }
                        },
                        {
                            "name": "Fail if tests failed",
                            "run": """
if [ $(echo '${{ steps.autotest.outputs.response }}' | jq -r '.failed') -gt 0 ]; then
  echo "Tests failed!"
  exit 1
fi
                            """.strip()
                        }
                    ]
                }
            }
        }
        
        return yaml.dump(workflow, sort_keys=False, default_flow_style=False)
    
    @staticmethod
    def generate_deploy_workflow(
        project_name: str,
        deployment_command: str,
        environment: str = "production",
        requires_approval: bool = True
    ) -> str:
        """
        Generate a workflow for deployment
        
        Args:
            project_name: Name of the project
            deployment_command: Command to deploy
            environment: Deployment environment
            requires_approval: Whether to require manual approval
            
        Returns:
            YAML workflow content
        """
        workflow = {
            "name": f"{project_name} - Deploy",
            "on": {
                "push": {
                    "branches": ["main"]
                },
                "workflow_dispatch": {}
            },
            "jobs": {
                "deploy": {
                    "runs-on": "ubuntu-latest",
                    "environment": environment if requires_approval else None,
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Deploy",
                            "run": deployment_command
                        }
                    ]
                }
            }
        }
        
        # Clean up None values
        if not requires_approval:
            del workflow["jobs"]["deploy"]["environment"]
        
        return yaml.dump(workflow, sort_keys=False, default_flow_style=False)
    
    @staticmethod
    def generate_nightly_workflow(
        project_name: str,
        project_id: int,
        api_url: str,
        api_token: str,
        schedule_cron: str = "0 0 * * *"  # Daily at midnight
    ) -> str:
        """
        Generate a workflow for nightly comprehensive testing
        
        Args:
            project_name: Name of the project
            project_id: AutoTest AI project ID
            api_url: AutoTest AI API URL
            api_token: API authentication token
            schedule_cron: Cron schedule
            
        Returns:
            YAML workflow content
        """
        workflow = {
            "name": f"{project_name} - Nightly Build",
            "on": {
                "schedule": [
                    {"cron": schedule_cron}
                ],
                "workflow_dispatch": {}
            },
            "jobs": {
                "nightly": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Run Full Test Suite",
                            "run": f"""
echo "🌙 Starting nightly test suite..."
curl -X POST "{api_url}/api/v1/tests/project/{project_id}/run-all" \\
  -H "Authorization: Bearer {api_token}" \\
  -H "Content-Type: application/json" \\
  -d '{{"url": "production-url-here"}}'
                            """.strip()
                        },
                        {
                            "name": "Generate Report",
                            "run": f"""
curl -X POST "{api_url}/api/v1/reports/" \\
  -H "Authorization: Bearer {api_token}" \\
  -H "Content-Type: application/json" \\
  -d '{{"project_id": {project_id}, "report_type": "json"}}'
                            """.strip()
                        }
                    ]
                }
            }
        }
        
        return yaml.dump(workflow, sort_keys=False, default_flow_style=False)
    
    @staticmethod
    def list_available_templates() -> List[Dict[str, Any]]:
        """List all available workflow templates"""
        return [
            {
                "id": "test",
                "name": "Test Suite",
                "description": "Run tests on push and pull requests",
                "triggers": ["push", "pull_request"],
                "use_case": "Continuous testing on code changes"
            },
            {
                "id": "regression",
                "name": "Regression Suite",
                "description": "Scheduled regression testing with tag filtering",
                "triggers": ["schedule", "workflow_dispatch"],
                "use_case": "Regular comprehensive testing"
            },
            {
                "id": "pr_test",
                "name": "PR Testing",
                "description": "Test pull requests and post results as comments",
                "triggers": ["pull_request"],
                "use_case": "Review-time testing with PR integration"
            },
            {
                "id": "deploy",
                "name": "Deployment",
                "description": "Deploy application after tests pass",
                "triggers": ["push", "workflow_dispatch"],
                "use_case": "Continuous deployment"
            },
            {
                "id": "nightly",
                "name": "Nightly Build",
                "description": "Comprehensive testing during off-hours",
                "triggers": ["schedule"],
                "use_case": "Full test coverage without disrupting development"
            }
        ]
