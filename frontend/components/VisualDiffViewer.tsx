'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface Comparison {
  id: number;
  difference_percentage: number;
  passed: boolean;
  status: string;
  screenshot_path: string;
  diff_path: string;
  ssim_score: number;
  created_at: string;
  extra_data: any;
}

interface Props {
  testId: number;
  onClose: () => void;
}

export default function VisualDiffViewer({ testId, onClose }: Props) {
  const [comparisons, setComparisons] = useState<Comparison[]>([]);
  const [selectedComparison, setSelectedComparison] = useState<Comparison | null>(null);
  const [viewMode, setViewMode] = useState<'side-by-side' | 'overlay' | 'diff'>('side-by-side');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchComparisons();
  }, [testId]);

  const fetchComparisons = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:8000/api/v1/visual-tests/visual-tests/${testId}/comparisons`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      if (response.ok) {
        const data = await response.json();
        setComparisons(data);
        if (data.length > 0) {
          setSelectedComparison(data[0]);
        }
      }
    } catch (error) {
      console.error('Error fetching comparisons:', error);
    } finally {
      setLoading(false);
    }
  };

  const reviewComparison = async (action: string, notes: string = '') => {
    if (!selectedComparison) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:8000/api/v1/visual-tests/comparisons/${selectedComparison.id}/review`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ action, notes })
        }
      );

      if (response.ok) {
        alert(`✅ Comparison ${action} successfully!`);
        fetchComparisons();
      } else {
        alert('Failed to review comparison');
      }
    } catch (error) {
      console.error('Error reviewing comparison:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-7xl w-full max-h-[95vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="border-b p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">Visual Comparison Viewer</h2>
              <p className="text-gray-600">Review screenshot differences and approve changes</p>
            </div>
            <Button variant="outline" onClick={onClose}>✕</Button>
          </div>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Comparison List Sidebar */}
          <div className="w-80 border-r overflow-y-auto">
            <div className="p-4 space-y-2">
              <h3 className="font-semibold mb-3">Comparison History</h3>
              {comparisons.map((comp) => (
                <div
                  key={comp.id}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    selectedComparison?.id === comp.id
                      ? 'bg-blue-50 border-blue-500'
                      : 'hover:bg-gray-50'
                  }`}
                  onClick={() => setSelectedComparison(comp)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">
                      {comp.passed ? '✅' : '❌'} {comp.difference_percentage.toFixed(2)}% diff
                    </span>
                  </div>
                  <div className="text-xs text-gray-500">
                    {new Date(comp.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
              
              {comparisons.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <p>No comparisons yet</p>
                </div>
              )}
            </div>
          </div>

          {/* Main Viewer */}
          <div className="flex-1 overflow-y-auto">
            {selectedComparison ? (
              <div className="p-6 space-y-6">
                {/* Metrics */}
                <div className="grid grid-cols-4 gap-4">
                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-2xl font-bold text-center">
                        {selectedComparison.difference_percentage.toFixed(2)}%
                      </div>
                      <div className="text-sm text-gray-600 text-center mt-1">Difference</div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-2xl font-bold text-center">
                        {selectedComparison.ssim_score?.toFixed(3) || 'N/A'}
                      </div>
                      <div className="text-sm text-gray-600 text-center mt-1">SSIM Score</div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="pt-6">
                      <div className={`text-2xl font-bold text-center ${
                        selectedComparison.passed ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {selectedComparison.passed ? '✅ PASS' : '❌ FAIL'}
                      </div>
                      <div className="text-sm text-gray-600 text-center mt-1">Status</div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-lg font-bold text-center">
                        {selectedComparison.status.toUpperCase()}
                      </div>
                      <div className="text-sm text-gray-600 text-center mt-1">Review Status</div>
                    </CardContent>
                  </Card>
                </div>

                {/* View Mode Selector */}
                <div className="flex gap-2">
                  <Button
                    variant={viewMode === 'side-by-side' ? 'default' : 'outline'}
                    onClick={() => setViewMode('side-by-side')}
                    size="sm"
                  >
                    Side by Side
                  </Button>
                  <Button
                    variant={viewMode === 'overlay' ? 'default' : 'outline'}
                    onClick={() => setViewMode('overlay')}
                    size="sm"
                  >
                    Overlay
                  </Button>
                  <Button
                    variant={viewMode === 'diff' ? 'default' : 'outline'}
                    onClick={() => setViewMode('diff')}
                    size="sm"
                  >
                    Diff Only
                  </Button>
                </div>

                {/* Image Viewer */}
                <div className="border rounded-lg overflow-hidden">
                  {viewMode === 'side-by-side' && (
                    <div className="grid grid-cols-2 gap-4 p-4">
                      <div>
                        <h4 className="font-semibold mb-2">Baseline</h4>
                        <img
                          src={`http://localhost:8000/${selectedComparison.screenshot_path}`}
                          alt="Baseline"
                          className="w-full border rounded"
                        />
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2">Current</h4>
                        <img
                          src={`http://localhost:8000/${selectedComparison.screenshot_path}`}
                          alt="Current"
                          className="w-full border rounded"
                        />
                      </div>
                    </div>
                  )}

                  {viewMode === 'diff' && (
                    <div className="p-4">
                      <h4 className="font-semibold mb-2">Difference Highlight</h4>
                      <img
                        src={`http://localhost:8000/${selectedComparison.extra_data?.highlighted_diff_path || selectedComparison.diff_path}`}
                        alt="Diff"
                        className="w-full border rounded"
                      />
                    </div>
                  )}

                  {viewMode === 'overlay' && (
                    <div className="p-4">
                      <h4 className="font-semibold mb-2">Overlay Comparison</h4>
                      <div className="relative">
                        <img
                          src={`http://localhost:8000/${selectedComparison.screenshot_path}`}
                          alt="Overlay"
                          className="w-full border rounded"
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                  <Button
                    onClick={() => reviewComparison('approve_change')}
                    className="flex-1"
                    variant="default"
                  >
                    ✅ Approve Change
                  </Button>
                  <Button
                    onClick={() => reviewComparison('update_baseline')}
                    className="flex-1"
                  >
                    🔄 Update Baseline
                  </Button>
                  <Button
                    onClick={() => reviewComparison('reject')}
                    className="flex-1"
                    variant="destructive"
                  >
                    ❌ Reject
                  </Button>
                  <Button
                    onClick={() => reviewComparison('ignore')}
                    variant="outline"
                  >
                    ⊘ Ignore
                  </Button>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                <p>Select a comparison to view details</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
