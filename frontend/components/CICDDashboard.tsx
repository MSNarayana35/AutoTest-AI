'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface WorkflowRun {
  id: number;
  workflow_name: string;
  run_number: number;
  status: string;
  conclusion: string | null;
  branch: string;
  author: string | null;
  started_at: string | null;
  completed_at: string | null;
  run_url: string | null;
}

interface Workflow {
  id: number;
  name: string;
  path: string;
  state: string;
  url: string;
}

interface Props {
  projectId: number;
}

export default function CICDDashboard({ projectId }: Props) {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [workflowRuns, setWorkflowRuns] = useState<WorkflowRun[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);

  useEffect(() => {
    fetchWorkflows();
    fetchWorkflowRuns();
    // Refresh every 30 seconds
    const interval = setInterval(() => {
      fetchWorkflowRuns();
    }, 30000);
    return () => clearInterval(interval);
  }, [projectId]);

  const fetchWorkflows = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/cicd/projects/${projectId}/workflows`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setWorkflows(data.workflows || []);
      }
    } catch (error) {
      console.error('Error fetching workflows:', error);
    }
  };

  const fetchWorkflowRuns = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/cicd/projects/${projectId}/workflow-runs?limit=20`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setWorkflowRuns(data);
      }
    } catch (error) {
      console.error('Error fetching workflow runs:', error);
    }
  };

  const triggerWorkflow = async (workflowId: string, branch: string = 'main') => {
    if (!confirm(`Trigger workflow on branch ${branch}?`)) {
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/cicd/projects/${projectId}/trigger-workflow`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          workflow_id: workflowId,
          branch: branch
        })
      });

      if (response.ok) {
        const data = await response.json();
        alert(`✅ ${data.message}`);
        setTimeout(() => fetchWorkflowRuns(), 3000);
      } else {
        const error = await response.json();
        alert(`Failed to trigger workflow: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error triggering workflow:', error);
      alert('Failed to trigger workflow');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string, conclusion: string | null) => {
    if (status === 'completed') {
      if (conclusion === 'success') {
        return <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">✅ Success</span>;
      } else if (conclusion === 'failure') {
        return <span className="px-2 py-1 text-xs rounded-full bg-red-100 text-red-800">❌ Failed</span>;
      } else if (conclusion === 'cancelled') {
        return <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">⊘ Cancelled</span>;
      } else {
        return <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">{conclusion}</span>;
      }
    } else if (status === 'in_progress') {
      return <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">🔄 Running</span>;
    } else if (status === 'queued') {
      return <span className="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">⏳ Queued</span>;
    }
    return <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">{status}</span>;
  };

  const formatDuration = (startedAt: string | null, completedAt: string | null) => {
    if (!startedAt || !completedAt) return '-';
    const start = new Date(startedAt).getTime();
    const end = new Date(completedAt).getTime();
    const seconds = Math.floor((end - start) / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`;
    }
    return `${seconds}s`;
  };

  const formatTime = (timestamp: string | null) => {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      {/* Workflows Card */}
      <Card>
        <CardHeader>
          <CardTitle>Active Workflows</CardTitle>
          <CardDescription>
            GitHub Actions workflows configured for this project
          </CardDescription>
        </CardHeader>
        <CardContent>
          {workflows.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No workflows found. Generate a workflow to get started.</p>
            </div>
          ) : (
            <div className="grid gap-3">
              {workflows.map((workflow) => (
                <div
                  key={workflow.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                >
                  <div>
                    <h3 className="font-semibold">{workflow.name}</h3>
                    <p className="text-sm text-gray-600">{workflow.path}</p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => triggerWorkflow(workflow.id.toString())}
                      disabled={loading}
                    >
                      ▶️ Run
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => window.open(workflow.url, '_blank')}
                    >
                      🔗
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Workflow Runs Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Recent Runs</CardTitle>
              <CardDescription>Latest workflow executions</CardDescription>
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={fetchWorkflowRuns}
              disabled={loading}
            >
              🔄 Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {workflowRuns.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No workflow runs yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {workflowRuns.map((run) => (
                <div
                  key={run.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
                  onClick={() => run.run_url && window.open(run.run_url, '_blank')}
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className="text-lg">
                        {run.conclusion === 'success' ? '✅' :
                         run.conclusion === 'failure' ? '❌' :
                         run.status === 'in_progress' ? '🔄' :
                         run.status === 'queued' ? '⏳' : '⚪'}
                      </span>
                      <div>
                        <h4 className="font-semibold">{run.workflow_name}</h4>
                        <p className="text-sm text-gray-600">
                          #{run.run_number} · {run.branch} · {run.author || 'unknown'}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    {getStatusBadge(run.status, run.conclusion)}
                    <div className="text-right text-sm">
                      <div className="text-gray-600">
                        {formatTime(run.started_at)}
                      </div>
                      {run.status === 'completed' && (
                        <div className="text-gray-500">
                          {formatDuration(run.started_at, run.completed_at)}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Stats Card */}
      <Card>
        <CardHeader>
          <CardTitle>Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-3xl font-bold text-green-600">
                {workflowRuns.filter(r => r.conclusion === 'success').length}
              </div>
              <div className="text-sm text-green-700">Successful</div>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <div className="text-3xl font-bold text-red-600">
                {workflowRuns.filter(r => r.conclusion === 'failure').length}
              </div>
              <div className="text-sm text-red-700">Failed</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-3xl font-bold text-blue-600">
                {workflowRuns.filter(r => r.status === 'in_progress').length}
              </div>
              <div className="text-sm text-blue-700">Running</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-3xl font-bold text-gray-600">
                {workflowRuns.length}
              </div>
              <div className="text-sm text-gray-700">Total Runs</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
