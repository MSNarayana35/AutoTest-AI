'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface Template {
  id: string;
  name: string;
  description: string;
  triggers: string[];
  use_case: string;
}

interface Props {
  projectId: number;
  onClose: () => void;
  onGenerated: () => void;
}

export default function WorkflowTemplateSelector({ projectId, onClose, onGenerated }: Props) {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [configuration, setConfiguration] = useState<any>({
    api_url: 'http://localhost:8000',
    api_token: '',
    tags: [],
    exclude_flaky: true,
    schedule_cron: '0 2 * * *',
    environment: 'production',
    requires_approval: true
  });
  const [generatedWorkflow, setGeneratedWorkflow] = useState<string | null>(null);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/cicd/workflow-templates', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const generateWorkflow = async () => {
    if (!selectedTemplate) {
      alert('Please select a template');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/cicd/projects/${projectId}/generate-workflow`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          workflow_type: selectedTemplate,
          configuration: configuration
        })
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedWorkflow(data.workflow_content);
        alert(`✅ Workflow created: ${data.file_path}\n\nCommit: ${data.commit_url}`);
        onGenerated();
      } else {
        const error = await response.json();
        alert(`Failed to generate workflow: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error generating workflow:', error);
      alert('Failed to generate workflow');
    } finally {
      setLoading(false);
    }
  };

  const getTemplateIcon = (id: string) => {
    const icons: Record<string, string> = {
      test: '🧪',
      regression: '🔄',
      pr_test: '💬',
      deploy: '🚀',
      nightly: '🌙'
    };
    return icons[id] || '📄';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">Generate Workflow</h2>
              <p className="text-gray-600">Choose a template to create a GitHub Actions workflow</p>
            </div>
            <Button variant="outline" onClick={onClose}>✕</Button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Template Selection */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Select Template</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {templates.map((template) => (
                <div
                  key={template.id}
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    selectedTemplate === template.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedTemplate(template.id)}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-3xl">{getTemplateIcon(template.id)}</span>
                    <div className="flex-1">
                      <h4 className="font-semibold text-lg">{template.name}</h4>
                      <p className="text-sm text-gray-600 mb-2">{template.description}</p>
                      <div className="flex flex-wrap gap-1 mb-2">
                        {template.triggers.map((trigger) => (
                          <span
                            key={trigger}
                            className="text-xs px-2 py-1 bg-gray-100 rounded"
                          >
                            {trigger}
                          </span>
                        ))}
                      </div>
                      <p className="text-xs text-gray-500">💡 {template.use_case}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Configuration Options */}
          {selectedTemplate && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold mb-3">Configuration</h3>
              <div className="space-y-4">
                {(selectedTemplate === 'regression' || selectedTemplate === 'pr_test' || selectedTemplate === 'nightly') && (
                  <>
                    <div>
                      <label className="block text-sm font-medium mb-1">API URL</label>
                      <input
                        type="text"
                        value={configuration.api_url}
                        onChange={(e) => setConfiguration({ ...configuration, api_url: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg"
                        placeholder="http://localhost:8000"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        API Token
                        <span className="text-xs text-gray-500 ml-2">(Create in Settings → API Keys)</span>
                      </label>
                      <input
                        type="password"
                        value={configuration.api_token}
                        onChange={(e) => setConfiguration({ ...configuration, api_token: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg"
                        placeholder="Your AutoTest AI API token"
                      />
                    </div>
                  </>
                )}

                {selectedTemplate === 'regression' && (
                  <>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Tags (comma-separated)
                      </label>
                      <input
                        type="text"
                        value={configuration.tags.join(',')}
                        onChange={(e) => setConfiguration({
                          ...configuration,
                          tags: e.target.value.split(',').map(t => t.trim()).filter(Boolean)
                        })}
                        className="w-full px-3 py-2 border rounded-lg"
                        placeholder="regression, critical, smoke"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">Schedule (Cron)</label>
                      <input
                        type="text"
                        value={configuration.schedule_cron}
                        onChange={(e) => setConfiguration({ ...configuration, schedule_cron: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg"
                        placeholder="0 2 * * * (Daily at 2 AM)"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        <a
                          href="https://crontab.guru"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          Cron expression helper
                        </a>
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={configuration.exclude_flaky}
                        onChange={(e) => setConfiguration({ ...configuration, exclude_flaky: e.target.checked })}
                        id="exclude-flaky"
                        className="w-4 h-4"
                      />
                      <label htmlFor="exclude-flaky" className="text-sm font-medium">
                        Exclude flaky tests
                      </label>
                    </div>
                  </>
                )}

                {selectedTemplate === 'deploy' && (
                  <>
                    <div>
                      <label className="block text-sm font-medium mb-1">Environment</label>
                      <select
                        value={configuration.environment}
                        onChange={(e) => setConfiguration({ ...configuration, environment: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg"
                      >
                        <option value="production">Production</option>
                        <option value="staging">Staging</option>
                        <option value="development">Development</option>
                      </select>
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={configuration.requires_approval}
                        onChange={(e) => setConfiguration({ ...configuration, requires_approval: e.target.checked })}
                        id="requires-approval"
                        className="w-4 h-4"
                      />
                      <label htmlFor="requires-approval" className="text-sm font-medium">
                        Require manual approval
                      </label>
                    </div>
                  </>
                )}

                {selectedTemplate === 'nightly' && (
                  <div>
                    <label className="block text-sm font-medium mb-1">Schedule (Cron)</label>
                    <input
                      type="text"
                      value={configuration.schedule_cron}
                      onChange={(e) => setConfiguration({ ...configuration, schedule_cron: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg"
                      placeholder="0 0 * * * (Daily at midnight)"
                    />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Generated Workflow Preview */}
          {generatedWorkflow && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold mb-3">Generated Workflow</h3>
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                {generatedWorkflow}
              </pre>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t">
            <Button
              onClick={generateWorkflow}
              disabled={!selectedTemplate || loading}
              className="flex-1"
            >
              {loading ? '⏳ Generating...' : '✨ Generate & Commit Workflow'}
            </Button>
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
