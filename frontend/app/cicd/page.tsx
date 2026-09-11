'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import CICDDashboard from '@/components/CICDDashboard';
import WorkflowTemplateSelector from '@/components/WorkflowTemplateSelector';

interface Project {
  id: number;
  name: string;
  description: string;
}

interface CICDConfig {
  id: number;
  project_id: number;
  repository_name: string;
  default_branch: string;
  workflows_enabled: boolean;
  webhook_enabled: boolean;
}

interface Repository {
  id: number;
  name: string;
  full_name: string;
  description: string;
  private: boolean;
  url: string;
  default_branch: string;
  language: string;
}

export default function CICDPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<number | null>(null);
  const [cicdConfig, setCicdConfig] = useState<CICDConfig | null>(null);
  const [loading, setLoading] = useState(false);
  
  // GitHub connection state
  const [showGitHubConnect, setShowGitHubConnect] = useState(false);
  const [githubToken, setGithubToken] = useState('');
  const [tokenValid, setTokenValid] = useState<boolean | null>(null);
  const [githubUser, setGithubUser] = useState<any>(null);
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [selectedRepo, setSelectedRepo] = useState<string>('');
  
  // Workflow generation state
  const [showWorkflowGenerator, setShowWorkflowGenerator] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchCICDConfig();
    }
  }, [selectedProject]);

  const fetchProjects = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/projects/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setProjects(data);
        if (data.length > 0) {
          setSelectedProject(data[0].id);
        }
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const fetchCICDConfig = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/cicd/projects/${selectedProject}/config`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setCicdConfig(data);
      } else if (response.status === 404) {
        setCicdConfig(null);
      }
    } catch (error) {
      console.error('Error fetching CI/CD config:', error);
    }
  };

  const validateGitHubToken = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/cicd/validate-token', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ github_token: githubToken })
      });
      
      const data = await response.json();
      
      if (data.valid) {
        setTokenValid(true);
        setGithubUser(data);
        await fetchRepositories();
      } else {
        setTokenValid(false);
        alert(`Invalid token: ${data.error}`);
      }
    } catch (error) {
      console.error('Error validating token:', error);
      setTokenValid(false);
    } finally {
      setLoading(false);
    }
  };

  const fetchRepositories = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:8000/api/v1/cicd/repositories?github_token=${encodeURIComponent(githubToken)}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setRepositories(data.repositories);
      }
    } catch (error) {
      console.error('Error fetching repositories:', error);
    }
  };

  const connectRepository = async () => {
    if (!selectedRepo) {
      alert('Please select a repository');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/cicd/projects/${selectedProject}/config`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          github_token: githubToken,
          repository_name: selectedRepo,
          default_branch: 'main',
          python_version: '3.10',
          node_version: '20',
          test_command: 'pytest',
          auto_trigger: true
        })
      });

      if (response.ok) {
        const data = await response.json();
        setCicdConfig(data);
        setShowGitHubConnect(false);
        alert('✅ Repository connected successfully!');
      } else {
        const error = await response.json();
        alert(`Failed to connect repository: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error connecting repository:', error);
      alert('Failed to connect repository');
    } finally {
      setLoading(false);
    }
  };

  const disconnectRepository = async () => {
    if (!confirm('Are you sure you want to disconnect the GitHub repository?')) {
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/cicd/projects/${selectedProject}/config`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        setCicdConfig(null);
        alert('✅ Repository disconnected successfully!');
      }
    } catch (error) {
      console.error('Error disconnecting repository:', error);
      alert('Failed to disconnect repository');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">CI/CD Integration</h1>
          <p className="text-gray-600">Automate testing with GitHub Actions</p>
        </div>
        
        {projects.length > 0 && (
          <select
            value={selectedProject || ''}
            onChange={(e) => setSelectedProject(Number(e.target.value))}
            className="px-4 py-2 border rounded-lg"
          >
            {projects.map(project => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Connection Status Card */}
      <Card>
        <CardHeader>
          <CardTitle>GitHub Connection</CardTitle>
          <CardDescription>
            Connect your GitHub repository to enable automated testing
          </CardDescription>
        </CardHeader>
        <CardContent>
          {cicdConfig ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">✅</span>
                    <div>
                      <h3 className="font-semibold text-green-900">Connected to GitHub</h3>
                      <p className="text-sm text-green-700">
                        Repository: <code className="bg-green-100 px-2 py-1 rounded">{cicdConfig.repository_name}</code>
                      </p>
                      <p className="text-sm text-green-700">
                        Branch: <code className="bg-green-100 px-2 py-1 rounded">{cicdConfig.default_branch}</code>
                      </p>
                    </div>
                  </div>
                </div>
                <Button
                  variant="outline"
                  onClick={disconnectRepository}
                  disabled={loading}
                >
                  Disconnect
                </Button>
              </div>

              <div className="flex gap-3">
                <Button
                  onClick={() => setShowWorkflowGenerator(true)}
                  className="flex-1"
                >
                  📄 Generate Workflow
                </Button>
                <Button
                  variant="outline"
                  onClick={() => window.open(`https://github.com/${cicdConfig.repository_name}/actions`, '_blank')}
                  className="flex-1"
                >
                  🔗 View on GitHub
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {!showGitHubConnect ? (
                <div className="text-center py-8">
                  <div className="text-6xl mb-4">🔌</div>
                  <p className="text-gray-600 mb-4">No repository connected</p>
                  <Button onClick={() => setShowGitHubConnect(true)}>
                    Connect GitHub Repository
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      GitHub Personal Access Token
                    </label>
                    <input
                      type="password"
                      value={githubToken}
                      onChange={(e) => setGithubToken(e.target.value)}
                      placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                      className="w-full px-3 py-2 border rounded-lg"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Create a token at{' '}
                      <a
                        href="https://github.com/settings/tokens/new"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        github.com/settings/tokens
                      </a>
                      {' '}with <code>repo</code> and <code>workflow</code> scopes
                    </p>
                  </div>

                  <Button
                    onClick={validateGitHubToken}
                    disabled={!githubToken || loading}
                    className="w-full"
                  >
                    {loading ? 'Validating...' : 'Validate Token'}
                  </Button>

                  {tokenValid && githubUser && (
                    <div className="space-y-3">
                      <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                        <p className="text-sm text-green-800">
                          ✅ Authenticated as <strong>{githubUser.username}</strong>
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">
                          Select Repository
                        </label>
                        <select
                          value={selectedRepo}
                          onChange={(e) => setSelectedRepo(e.target.value)}
                          className="w-full px-3 py-2 border rounded-lg"
                        >
                          <option value="">-- Select a repository --</option>
                          {repositories.map(repo => (
                            <option key={repo.id} value={repo.full_name}>
                              {repo.full_name} {repo.private && '🔒'}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="flex gap-2">
                        <Button
                          onClick={connectRepository}
                          disabled={!selectedRepo || loading}
                          className="flex-1"
                        >
                          {loading ? 'Connecting...' : 'Connect Repository'}
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => {
                            setShowGitHubConnect(false);
                            setGithubToken('');
                            setTokenValid(null);
                          }}
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Workflow Generator Modal */}
      {showWorkflowGenerator && cicdConfig && (
        <WorkflowTemplateSelector
          projectId={selectedProject!}
          onClose={() => setShowWorkflowGenerator(false)}
          onGenerated={() => {
            setShowWorkflowGenerator(false);
            // Refresh dashboard
          }}
        />
      )}

      {/* CI/CD Dashboard */}
      {cicdConfig && selectedProject && (
        <CICDDashboard projectId={selectedProject} />
      )}
    </div>
  );
}
