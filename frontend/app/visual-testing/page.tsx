'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import VisualTestList from '@/components/VisualTestList';
import VisualTestForm from '@/components/VisualTestForm';
import VisualDiffViewer from '@/components/VisualDiffViewer';

interface Project {
  id: number;
  name: string;
}

interface VisualTest {
  id: number;
  name: string;
  url: string;
  browser: string;
  viewport_width: number;
  viewport_height: number;
  threshold: float;
  has_baseline: boolean;
  is_active: boolean;
}

interface Stats {
  total_tests: number;
  active_tests: number;
  with_baseline: number;
  recent_comparisons: {
    total: number;
    passed: number;
    failed: number;
    pass_rate: number;
  };
}

export default function VisualTestingPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<number | null>(null);
  const [visualTests, setVisualTests] = useState<VisualTest[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedTest, setSelectedTest] = useState<number | null>(null);
  const [showDiffViewer, setShowDiffViewer] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchVisualTests();
      fetchStats();
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

  const fetchVisualTests = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:8000/api/v1/visual-tests/projects/${selectedProject}/visual-tests`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      if (response.ok) {
        const data = await response.json();
        setVisualTests(data);
      }
    } catch (error) {
      console.error('Error fetching visual tests:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:8000/api/v1/visual-tests/projects/${selectedProject}/visual-tests/stats`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Visual Regression Testing</h1>
          <p className="text-gray-600">Automated screenshot comparison and visual validation</p>
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

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Total Tests</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.total_tests}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Active Tests</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">{stats.active_tests}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">With Baseline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">{stats.with_baseline}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Pass Rate</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600">
                {stats.recent_comparisons.pass_rate.toFixed(1)}%
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Quick Actions */}
      <div className="flex gap-3">
        <Button
          onClick={() => setShowCreateForm(true)}
          className="flex-1 md:flex-initial"
        >
          ➕ Create Visual Test
        </Button>
        <Button
          variant="outline"
          onClick={fetchVisualTests}
        >
          🔄 Refresh
        </Button>
        <Button
          variant="outline"
          onClick={() => setShowDiffViewer(true)}
        >
          📊 View Comparisons
        </Button>
      </div>

      {/* Create Form Modal */}
      {showCreateForm && (
        <VisualTestForm
          projectId={selectedProject!}
          onClose={() => setShowCreateForm(false)}
          onSuccess={() => {
            setShowCreateForm(false);
            fetchVisualTests();
            fetchStats();
          }}
        />
      )}

      {/* Visual Tests List */}
      <VisualTestList
        tests={visualTests}
        onTestSelect={(testId) => setSelectedTest(testId)}
        onRefresh={() => {
          fetchVisualTests();
          fetchStats();
        }}
      />

      {/* Diff Viewer Modal */}
      {showDiffViewer && selectedTest && (
        <VisualDiffViewer
          testId={selectedTest}
          onClose={() => setShowDiffViewer(false)}
        />
      )}

      {/* Getting Started */}
      {visualTests.length === 0 && !showCreateForm && (
        <Card>
          <CardHeader>
            <CardTitle>🎨 Getting Started with Visual Testing</CardTitle>
            <CardDescription>
              Visual regression testing automatically detects UI changes by comparing screenshots
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 border rounded-lg">
                <div className="text-2xl mb-2">1️⃣</div>
                <h3 className="font-semibold mb-2">Create Test</h3>
                <p className="text-sm text-gray-600">
                  Define URL, viewport, and comparison settings
                </p>
              </div>
              <div className="p-4 border rounded-lg">
                <div className="text-2xl mb-2">2️⃣</div>
                <h3 className="font-semibold mb-2">Upload Baseline</h3>
                <p className="text-sm text-gray-600">
                  Capture reference screenshot to compare against
                </p>
              </div>
              <div className="p-4 border rounded-lg">
                <div className="text-2xl mb-2">3️⃣</div>
                <h3 className="font-semibold mb-2">Compare & Approve</h3>
                <p className="text-sm text-gray-600">
                  Review differences and approve or reject changes
                </p>
              </div>
            </div>
            
            <Button onClick={() => setShowCreateForm(true)} className="w-full">
              Create Your First Visual Test
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
