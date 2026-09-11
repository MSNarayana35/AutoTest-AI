'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';

interface Props {
  projectId: number;
  onClose: () => void;
  onSuccess: () => void;
}

export default function VisualTestForm({ projectId, onClose, onSuccess }: Props) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    url: '',
    selector: '',
    viewport_width: 1920,
    viewport_height: 1080,
    browser: 'chromium',
    threshold: 0.1,
    full_page: false
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:8000/api/v1/visual-tests/projects/${projectId}/visual-tests`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(formData)
        }
      );

      if (response.ok) {
        alert('✅ Visual test created successfully!');
        onSuccess();
      } else {
        const error = await response.json();
        alert(`Failed to create visual test: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error creating visual test:', error);
      alert('Failed to create visual test');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Create Visual Test</h2>
            <Button variant="outline" onClick={onClose}>✕</Button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Test Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Homepage Header"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Visual test for homepage header section"
              rows={2}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">URL *</label>
            <input
              type="url"
              value={formData.url}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="https://example.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">CSS Selector (Optional)</label>
            <input
              type="text"
              value={formData.selector}
              onChange={(e) => setFormData({ ...formData, selector: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder=".header, #main-content"
            />
            <p className="text-xs text-gray-500 mt-1">
              Leave empty for full page screenshot
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Viewport Width</label>
              <input
                type="number"
                value={formData.viewport_width}
                onChange={(e) => setFormData({ ...formData, viewport_width: Number(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg"
                min="320"
                max="3840"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Viewport Height</label>
              <input
                type="number"
                value={formData.viewport_height}
                onChange={(e) => setFormData({ ...formData, viewport_height: Number(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg"
                min="240"
                max="2160"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Browser</label>
            <select
              value={formData.browser}
              onChange={(e) => setFormData({ ...formData, browser: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
            >
              <option value="chromium">🌐 Chromium</option>
              <option value="firefox">🦊 Firefox</option>
              <option value="webkit">🧭 WebKit (Safari)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Difference Threshold ({(formData.threshold * 100).toFixed(1)}%)
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={formData.threshold}
              onChange={(e) => setFormData({ ...formData, threshold: Number(e.target.value) })}
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              Maximum acceptable difference before test fails
            </p>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="full-page"
              checked={formData.full_page}
              onChange={(e) => setFormData({ ...formData, full_page: e.target.checked })}
              className="w-4 h-4"
            />
            <label htmlFor="full-page" className="text-sm font-medium">
              Capture full page (scroll)
            </label>
          </div>

          <div className="flex gap-3 pt-4 border-t">
            <Button type="submit" disabled={loading} className="flex-1">
              {loading ? 'Creating...' : 'Create Visual Test'}
            </Button>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
