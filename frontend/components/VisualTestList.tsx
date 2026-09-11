'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface VisualTest {
  id: number;
  name: string;
  url: string;
  browser: string;
  viewport_width: number;
  viewport_height: number;
  threshold: number;
  has_baseline: boolean;
  is_active: boolean;
}

interface Props {
  tests: VisualTest[];
  onTestSelect: (testId: number) => void;
  onRefresh: () => void;
}

export default function VisualTestList({ tests, onTestSelect, onRefresh }: Props) {
  const getBrowserIcon = (browser: string) => {
    const icons: Record<string, string> = {
      chromium: '🌐',
      firefox: '🦊',
      webkit: '🧭'
    };
    return icons[browser] || '🌐';
  };

  if (tests.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Visual Tests ({tests.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {tests.map((test) => (
            <div
              key={test.id}
              className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
              onClick={() => onTestSelect(test.id)}
            >
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{getBrowserIcon(test.browser)}</span>
                  <div>
                    <h3 className="font-semibold">{test.name}</h3>
                    <p className="text-sm text-gray-600">{test.url}</p>
                    <div className="flex gap-3 mt-1">
                      <span className="text-xs text-gray-500">
                        {test.viewport_width}x{test.viewport_height}
                      </span>
                      <span className="text-xs text-gray-500">
                        Threshold: {(test.threshold * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                {test.has_baseline ? (
                  <span className="px-3 py-1 text-xs rounded-full bg-green-100 text-green-800">
                    ✅ Has Baseline
                  </span>
                ) : (
                  <span className="px-3 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">
                    ⚠️ No Baseline
                  </span>
                )}
                
                {test.is_active ? (
                  <span className="px-3 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                    Active
                  </span>
                ) : (
                  <span className="px-3 py-1 text-xs rounded-full bg-gray-100 text-gray-800">
                    Inactive
                  </span>
                )}
                
                <Button size="sm" variant="outline">
                  View Details →
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
