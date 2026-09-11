'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Play, RefreshCw, AlertTriangle, CheckCircle, XCircle, Filter } from 'lucide-react'
import { toast } from '@/components/ui/use-toast'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface RegressionSuiteProps {
  projectId: number
  token: string
  deploymentUrl?: string
}

export function RegressionSuite({ projectId, token, deploymentUrl }: RegressionSuiteProps) {
  const [allTags, setAllTags] = useState<string[]>([])
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [excludeFlaky, setExcludeFlaky] = useState(true)
  const [tests, setTests] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState<any>(null)

  useEffect(() => {
    fetchAllTags()
    fetchRegressionTests()
  }, [projectId])

  const fetchAllTags = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/tests/project/${projectId}/tags`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setAllTags(data.tags || [])
      }
    } catch (error) {
      console.error('Error fetching tags:', error)
    }
  }

  const fetchRegressionTests = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (selectedTags.length > 0) {
        params.append('tags', selectedTags.join(','))
      }
      if (excludeFlaky) {
        params.append('exclude_flaky', 'true')
      }

      const response = await fetch(`${API_URL}/api/v1/tests/project/${projectId}/regression?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setTests(data)
      }
    } catch (error) {
      console.error('Error fetching regression tests:', error)
    }
    setLoading(false)
  }

  const runRegressionSuite = async () => {
    setRunning(true)
    setResult(null)

    try {
      const response = await fetch(`${API_URL}/api/v1/tests/project/${projectId}/run-regression`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          url: deploymentUrl || 'http://localhost:3000',
          tags: selectedTags.length > 0 ? selectedTags : null,
          exclude_flaky: excludeFlaky
        })
      })

      if (response.ok) {
        const data = await response.json()
        setResult(data)
        toast({ 
          title: `Regression Complete: ${data.passed}/${data.total} passed`,
          description: `${data.success_rate}% success rate`
        })
      } else {
        toast({ title: 'Regression run failed' })
      }
    } catch (error) {
      console.error('Error running regression:', error)
      toast({ title: 'Error running regression suite' })
    }

    setRunning(false)
  }

  const toggleTag = (tag: string) => {
    setSelectedTags(prev => 
      prev.includes(tag) 
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Regression Suite Configuration</CardTitle>
          <CardDescription>Filter and run tests based on tags and flaky status</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Tag Filter */}
          <div>
            <label className="text-sm font-medium text-slate-200 mb-2 flex items-center gap-2">
              <Filter className="w-4 h-4" />
              Filter by Tags
            </label>
            <div className="flex flex-wrap gap-2 mt-2">
              {allTags.length > 0 ? (
                allTags.map(tag => (
                  <button
                    key={tag}
                    onClick={() => toggleTag(tag)}
                    className={`px-3 py-1 text-sm rounded-full transition-colors ${
                      selectedTags.includes(tag)
                        ? 'bg-blue-600 text-white border-2 border-blue-400'
                        : 'bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700'
                    }`}
                  >
                    {tag}
                  </button>
                ))
              ) : (
                <p className="text-sm text-slate-500">No tags available. Add tags to test cases first.</p>
              )}
            </div>
          </div>

          {/* Flaky Test Filter */}
          <div className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg">
            <input
              type="checkbox"
              id="exclude-flaky"
              checked={excludeFlaky}
              onChange={(e) => setExcludeFlaky(e.target.checked)}
              className="w-4 h-4 rounded bg-slate-700 border-slate-600 text-blue-600 focus:ring-2 focus:ring-blue-500"
            />
            <label htmlFor="exclude-flaky" className="text-sm text-slate-200 cursor-pointer flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-yellow-500" />
              Exclude Flaky Tests
            </label>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              onClick={fetchRegressionTests}
              disabled={loading}
              variant="outline"
              className="flex-1"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh Tests
            </Button>
            <Button
              onClick={runRegressionSuite}
              disabled={running || tests.length === 0}
              className="flex-1 bg-emerald-600 hover:bg-emerald-700"
            >
              {running ? (
                <><RefreshCw className="w-4 h-4 mr-2 animate-spin" />Running...</>
              ) : (
                <><Play className="w-4 h-4 mr-2" />Run Regression</>
              )}
            </Button>
          </div>

          {/* Test Count */}
          <div className="pt-2 border-t border-slate-700">
            <p className="text-sm text-slate-400">
              {selectedTags.length > 0 && `Filtered by: ${selectedTags.join(', ')} • `}
              {excludeFlaky && 'Flaky tests excluded • '}
              <span className="font-semibold text-slate-200">{tests.length} test{tests.length !== 1 ? 's' : ''}</span> will run
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {result && (
        <Card className="border-emerald-800">
          <CardHeader>
            <CardTitle>Regression Results</CardTitle>
            <CardDescription>Last run summary</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="bg-slate-800 rounded p-3">
                <p className="text-slate-400 text-xs">Total</p>
                <p className="text-2xl font-bold">{result.total}</p>
              </div>
              <div className="bg-slate-800 rounded p-3">
                <p className="text-slate-400 text-xs flex items-center gap-1">
                  <CheckCircle className="w-3 h-3 text-emerald-400" />
                  Passed
                </p>
                <p className="text-2xl font-bold text-emerald-400">{result.passed}</p>
              </div>
              <div className="bg-slate-800 rounded p-3">
                <p className="text-slate-400 text-xs flex items-center gap-1">
                  <XCircle className="w-3 h-3 text-red-400" />
                  Failed
                </p>
                <p className="text-2xl font-bold text-red-400">{result.failed}</p>
              </div>
              <div className="bg-slate-800 rounded p-3">
                <p className="text-slate-400 text-xs">Success Rate</p>
                <p className={`text-2xl font-bold ${
                  result.success_rate >= 70 ? 'text-emerald-400' : 
                  result.success_rate >= 40 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {result.success_rate}%
                </p>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-slate-800 rounded-full h-3 mb-4">
              <div 
                className={`h-3 rounded-full transition-all ${
                  result.success_rate >= 70 ? 'bg-emerald-500' : 
                  result.success_rate >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${result.success_rate}%` }}
              />
            </div>

            {/* Failed Tests */}
            {result.failed > 0 && result.results && (
              <div className="mt-4">
                <h4 className="text-sm font-semibold text-red-400 mb-2">Failed Tests:</h4>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {result.results
                    .filter((r: any) => r.status === 'failed' || r.status === 'FAILED')
                    .map((r: any, i: number) => (
                      <div key={i} className="bg-red-950/30 border border-red-900 rounded p-2">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1">
                            <p className="text-sm font-medium text-slate-200">{r.title}</p>
                            {r.message && (
                              <p className="text-xs text-slate-400 mt-1">{r.message}</p>
                            )}
                          </div>
                          {r.is_flaky && (
                            <span className="text-xs px-2 py-1 bg-yellow-900/40 text-yellow-300 border border-yellow-700 rounded">
                              Flaky
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Test List */}
      <Card>
        <CardHeader>
          <CardTitle>Tests in Regression Suite ({tests.length})</CardTitle>
          <CardDescription>Matching tests based on current filters</CardDescription>
        </CardHeader>
        <CardContent>
          {tests.length > 0 ? (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {tests.map((test: any) => (
                <div
                  key={test.id}
                  className="flex items-center justify-between p-3 bg-slate-800/50 rounded hover:bg-slate-800 transition-colors"
                >
                  <div className="flex-1">
                    <p className="text-sm font-medium">{test.title}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs px-2 py-0.5 rounded bg-slate-700 text-slate-300">
                        {test.test_type}
                      </span>
                      {test.tags && test.tags.length > 0 && (
                        <div className="flex gap-1">
                          {test.tags.map((tag: string) => (
                            <span
                              key={tag}
                              className="text-xs px-2 py-0.5 rounded bg-blue-900/40 text-blue-300 border border-blue-700"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  {test.is_flaky && (
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-yellow-500" />
                      <span className="text-xs text-yellow-500">Flaky</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-slate-500 py-8">
              No tests match the current filters. Adjust your tag selection or disable flaky exclusion.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
