'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  ShieldCheck, Home, FileText, TestTube, Settings, Plus, Upload,
  Play, Trash2, Bug, BarChart2, History, RefreshCw, CheckCircle,
  XCircle, Clock, AlertTriangle, ChevronDown, ChevronUp, Bell, X, Target
} from 'lucide-react'
import { motion } from 'framer-motion'
import { toast } from '@/components/ui/use-toast'
import { formatISTDateTime, formatISTDate, formatISTDisplay, formatISTShort } from '@/lib/datetime'
import { TagManager } from '@/components/TagManager'
import { RegressionSuite } from '@/components/RegressionSuite'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// ─── TYPES ────────────────────────────────────────────────────────────────────
type Project    = { id: number; name: string; description: string; repository_url?: string; deployment_url?: string; created_at: string }
type Requirement= { id: number; project_id: number; title: string; content: string; status: string; structured_data?: any; created_at: string }
type TestCase   = { id: number; project_id: number; requirement_id?: number; title: string; description?: string; test_type: string; script?: string; status: string; tags?: string[]; is_flaky?: boolean; failure_count?: number; total_runs?: number; last_failure_date?: string; created_at: string }
type Execution  = { id: number; project_id: number; test_case_id: number; status: string; logs?: string; execution_time?: number; created_at: string }
type BugItem    = { id: number; project_id: number; test_case_id?: number; execution_id?: number; title: string; description?: string; severity: string; status: string; test_case_title?: string; created_at: string; updated_at?: string }
type DashStats  = { projects: number; requirements: number; test_cases: number; executions: number; passed_executions: number; failed_executions: number; success_rate: number; bugs: number }
type NotificationItem = { id: number; user_id: number; channel: string; title: string; message?: string; status: string; created_at: string }

// ─── HELPER COMPONENTS ────────────────────────────────────────────────────────
function StatCard({ label, value, icon, color = 'text-slate-50' }: { label: string; value: any; icon: React.ReactNode; color?: string }) {
  return (
    <Card>
      <CardContent className="pt-4 pb-4">
        <div className="flex items-center justify-between">
          <div><p className="text-xs text-slate-400">{label}</p><p className={`text-2xl font-bold mt-0.5 ${color}`}>{value}</p></div>
          {icon}
        </div>
      </CardContent>
    </Card>
  )
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    analyzed: 'bg-green-900 text-green-300', analyzing: 'bg-yellow-900 text-yellow-300',
    error: 'bg-red-900 text-red-300', ready: 'bg-blue-900 text-blue-300',
    passed: 'bg-emerald-900 text-emerald-300', failed: 'bg-red-900 text-red-300',
    pending: 'bg-slate-700 text-slate-300', running: 'bg-yellow-900 text-yellow-300',
  }
  return <span className={`text-xs px-2 py-0.5 rounded ${map[status] || 'bg-slate-700 text-slate-300'}`}>{status}</span>
}

function SeverityBadge({ severity }: { severity: string }) {
  const map: Record<string, string> = {
    critical: 'bg-red-900 text-red-300', high: 'bg-orange-900 text-orange-300',
    medium: 'bg-yellow-900 text-yellow-300', low: 'bg-slate-700 text-slate-300',
  }
  return <span className={`text-xs px-2 py-0.5 rounded ${map[severity] || 'bg-slate-700 text-slate-300'}`}>{severity}</span>
}

function BugStatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    open: 'bg-red-900 text-red-300',
    in_progress: 'bg-yellow-900 text-yellow-300',
    resolved: 'bg-green-900 text-green-300',
    closed: 'bg-slate-700 text-slate-300',
  }
  const label = status.replace('_', ' ')
  return <span className={`text-xs px-2 py-0.5 rounded capitalize ${map[status] || 'bg-slate-700 text-slate-300'}`}>{label}</span>
}

function NotificationDropdown({ token, onClose }: { token: string; onClose: () => void }) {
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchNotifications()
  }, [])

  const fetchNotifications = async () => {
    try {
      const r = await fetch(`${API_URL}/api/v1/notifications/`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (r.ok) {
        const data = await r.json()
        setNotifications(data)
      }
    } catch (e) {
      console.error('Error fetching notifications:', e)
    }
  }

  const markAsRead = async (id: number) => {
    setLoading(true)
    try {
      const r = await fetch(`${API_URL}/api/v1/notifications/${id}/read`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (r.ok) {
        setNotifications(prev => prev.map(n => n.id === id ? { ...n, status: 'read' } : n))
      }
    } catch (e) {
      console.error('Error marking as read:', e)
    }
    setLoading(false)
  }

  const markAllAsRead = async () => {
    setLoading(true)
    try {
      const r = await fetch(`${API_URL}/api/v1/notifications/read-all`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (r.ok) {
        setNotifications(prev => prev.map(n => ({ ...n, status: 'read' })))
        toast({ title: '✅ All notifications marked as read' })
      }
    } catch (e) {
      console.error('Error marking all as read:', e)
    }
    setLoading(false)
  }

  const deleteNotification = async (id: number) => {
    setLoading(true)
    try {
      const r = await fetch(`${API_URL}/api/v1/notifications/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (r.ok) {
        setNotifications(prev => prev.filter(n => n.id !== id))
      }
    } catch (e) {
      console.error('Error deleting notification:', e)
    }
    setLoading(false)
  }

  const unreadCount = notifications.filter(n => n.status === 'unread').length

  return (
    <div className="absolute top-14 right-4 w-96 bg-slate-900 border border-slate-700 rounded-lg shadow-xl z-50 max-h-[600px] flex flex-col">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between sticky top-0 bg-slate-900">
        <div>
          <h3 className="text-lg font-semibold">Notifications</h3>
          {unreadCount > 0 && <p className="text-xs text-slate-400">{unreadCount} unread</p>}
        </div>
        <div className="flex gap-2">
          {unreadCount > 0 && (
            <Button size="sm" variant="ghost" onClick={markAllAsRead} disabled={loading} className="text-xs">
              Mark all read
            </Button>
          )}
          <Button size="sm" variant="ghost" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        {notifications.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            <Bell className="w-12 h-12 mx-auto mb-3 text-slate-600" />
            <p>No notifications yet</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {notifications.map(notif => (
              <div
                key={notif.id}
                className={`p-4 hover:bg-slate-800/50 cursor-pointer transition-colors ${
                  notif.status === 'unread' ? 'bg-blue-950/20' : ''
                }`}
                onClick={() => notif.status === 'unread' && markAsRead(notif.id)}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-medium text-sm">{notif.title}</p>
                      {notif.status === 'unread' && (
                        <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                      )}
                    </div>
                    {notif.message && (
                      <p className="text-xs text-slate-400 mb-2">{notif.message}</p>
                    )}
                    <p className="text-xs text-slate-500">{formatISTShort(notif.created_at)}</p>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={(e) => {
                      e.stopPropagation()
                      deleteNotification(notif.id)
                    }}
                    disabled={loading}
                    className="text-slate-500 hover:text-red-400"
                  >
                    <X className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function StructuredList({ label, items, color }: { label: string; items?: string[]; color: string }) {
  if (!items || items.length === 0) return null
  return (
    <div>
      <p className={`text-xs font-semibold mb-1 ${color}`}>{label}</p>
      <ul className="space-y-1">{items.map((item, i) => <li key={i} className="text-xs text-slate-300 flex gap-1"><span className="text-slate-500">•</span>{item}</li>)}</ul>
    </div>
  )
}

function NoProject() {
  return (
    <div className="text-center py-16">
      <AlertTriangle className="w-10 h-10 text-yellow-500 mx-auto mb-3" />
      <p className="text-slate-400">No project selected. Go to <strong>Projects</strong> and click a project card to activate it.</p>
    </div>
  )
}

function ReportsPanel({ projectId, token, onGenerate, loading, executions, testCases, requirements, bugs }: any) {
  const [reports, setReports] = useState<any[]>([])
  const [expandedReport, setExpandedReport] = useState<number | null>(null)
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    if (!projectId || !token) return
    fetch(`${API_URL}/api/v1/reports/project/${projectId}`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : []).then(setReports).catch(() => {})
  }, [projectId, token])

  const downloadPDF = async () => {
    if (!projectId || !token) return
    setDownloading(true)
    try {
      const response = await fetch(`${API_URL}/api/v1/reports/project/${projectId}/pdf`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `TestReport_${Date.now()}.pdf`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Error downloading PDF:', error)
    }
    setDownloading(false)
  }

  const total = executions.length
  const passed = executions.filter((e: any) => e.status === 'passed').length
  const failed = executions.filter((e: any) => e.status === 'failed').length
  const rate = total > 0 ? Math.round((passed / total) * 100) : 0

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center flex-wrap gap-3">
            <div><CardTitle>Project Summary</CardTitle><CardDescription>Live stats for the active project</CardDescription></div>
            <div className="flex gap-2">
              <Button onClick={downloadPDF} disabled={downloading || total === 0} size="sm" className="bg-blue-600 hover:bg-blue-700">
                <FileText className="w-4 h-4 mr-2" />{downloading ? 'Generating...' : 'Download PDF'}
              </Button>
              <Button onClick={onGenerate} disabled={loading} size="sm" className="bg-purple-600 hover:bg-purple-700">
                <BarChart2 className="w-4 h-4 mr-2" />Save Report
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <StatCard label="Requirements" value={requirements.length} icon={<FileText className="w-4 h-4 text-green-400" />} />
            <StatCard label="Test Cases" value={testCases.length} icon={<TestTube className="w-4 h-4 text-yellow-400" />} />
            <StatCard label="Bugs Logged" value={bugs.length} icon={<Bug className="w-4 h-4 text-red-400" />} />
            <StatCard label="Pass Rate" value={`${rate}%`} icon={<CheckCircle className="w-4 h-4 text-emerald-400" />} color={rate >= 70 ? 'text-emerald-400' : rate >= 40 ? 'text-yellow-400' : 'text-red-400'} />
          </div>
          {total > 0 ? (
            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-1"><span>{passed} passed</span><span>{failed} failed</span><span>{total} total</span></div>
              <div className="w-full bg-slate-800 rounded-full h-3">
                <div className={`h-3 rounded-full transition-all ${rate >= 70 ? 'bg-emerald-500' : rate >= 40 ? 'bg-yellow-500' : 'bg-red-500'}`} style={{ width: `${rate}%` }} />
              </div>
            </div>
          ) : <p className="text-slate-500 text-sm mt-2">No executions yet. Run tests from the Test Cases tab.</p>}
        </CardContent>
      </Card>

      {reports.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-3">Saved Reports ({reports.length})</h3>
          <div className="space-y-3">
            {reports.map((r: any) => (
              <Card key={r.id}>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <div><CardTitle className="text-base">Report #{r.id}</CardTitle><CardDescription>{formatISTDisplay(r.created_at)} · {r.report_type}</CardDescription></div>
                    <Button size="sm" variant="outline" onClick={() => setExpandedReport(expandedReport === r.id ? null : r.id)}>
                      {expandedReport === r.id ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </Button>
                  </div>
                </CardHeader>
                {expandedReport === r.id && r.payload && (
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm mb-3">
                      <div className="bg-slate-800 rounded p-3"><p className="text-slate-400 text-xs">Total</p><p className="text-xl font-bold">{r.payload.total_executions}</p></div>
                      <div className="bg-slate-800 rounded p-3"><p className="text-slate-400 text-xs">Passed</p><p className="text-xl font-bold text-emerald-400">{r.payload.passed}</p></div>
                      <div className="bg-slate-800 rounded p-3"><p className="text-slate-400 text-xs">Failed</p><p className="text-xl font-bold text-red-400">{r.payload.failed}</p></div>
                      <div className="bg-slate-800 rounded p-3"><p className="text-slate-400 text-xs">Success Rate</p><p className="text-xl font-bold text-blue-400">{r.payload.success_rate}%</p></div>
                    </div>
                    {r.payload.recommendations && <div className="text-xs text-slate-400 bg-slate-900 rounded p-3"><strong>Recommendations:</strong> {r.payload.recommendations.join(', ')}</div>}
                  </CardContent>
                )}
              </Card>
            ))}
          </div>
        </div>
      )}
      {reports.length === 0 && <p className="text-slate-500 text-center py-4">No saved reports yet. Click &quot;Save Report&quot; to create one.</p>}
    </div>
  )
}

// ─── MAIN DASHBOARD ───────────────────────────────────────────────────────────
export default function Dashboard() {
  const [token, setToken] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('projects')
  const [projects, setProjects] = useState<Project[]>([])
  const [requirements, setRequirements] = useState<Requirement[]>([])
  const [testCases, setTestCases] = useState<TestCase[]>([])
  const [executions, setExecutions] = useState<Execution[]>([])
  const [bugs, setBugs] = useState<BugItem[]>([])
  const [stats, setStats] = useState<DashStats | null>(null)
  const [selectedProject, setSelectedProject] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [initialLoading, setInitialLoading] = useState(true)
  const [bulkRunning, setBulkRunning] = useState(false)
  const [bulkResult, setBulkResult] = useState<any>(null)
  const [expandedReqs, setExpandedReqs] = useState<Set<number>>(new Set())
  const [expandedTests, setExpandedTests] = useState<Set<number>>(new Set())
  const [bugFormData, setBugFormData] = useState<{ test_case_id?: number; execution_id?: number; title?: string; description?: string } | null>(null)
  const [showNotifications, setShowNotifications] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)
  const router = useRouter()

  const authH = useCallback((t: string) => ({ Authorization: `Bearer ${t}` }), [])

  useEffect(() => {
    const t = localStorage.getItem('token')
    if (!t) { router.push('/'); return }
    setToken(t)
    fetchProjects(t)
    fetchDashStats(t)
    fetchUnreadCount(t)
    
    // Poll for new notifications every 30 seconds
    const interval = setInterval(() => fetchUnreadCount(t), 30000)
    return () => clearInterval(interval)
  }, [router])

  const fetchDashStats = async (t: string) => {
    try {
      const r = await fetch(`${API_URL}/api/v1/dashboard/`, { headers: authH(t) })
      if (r.ok) { const d = await r.json(); setStats(d.analytics) }
    } catch (_e) { /* silent */ }
  }

  const fetchUnreadCount = async (t: string) => {
    try {
      const r = await fetch(`${API_URL}/api/v1/notifications/unread/count`, { headers: authH(t) })
      if (r.ok) { const d = await r.json(); setUnreadCount(d.count) }
    } catch (_e) { /* silent */ }
  }

  const fetchProjects = async (t: string) => {
    try {
      const r = await fetch(`${API_URL}/api/v1/projects/`, { headers: authH(t) })
      if (r.ok) {
        const data: Project[] = await r.json()
        setProjects(data)
        if (data.length > 0) selectProject(data[0].id, t)
      }
    } catch (_e) { /* silent */ }
    finally { setInitialLoading(false) }
  }

  const selectProject = (id: number, t: string) => {
    setSelectedProject(id); setBulkResult(null)
    fetchRequirements(id, t); fetchTestCases(id, t); fetchExecutions(id, t); fetchBugs(id, t)
  }

  const fetchRequirements = async (pid: number, t: string) => {
    try { const r = await fetch(`${API_URL}/api/v1/requirements/project/${pid}`, { headers: authH(t) }); if (r.ok) setRequirements(await r.json()) } catch (_e) { /* silent */ }
  }
  const fetchTestCases = async (pid: number, t: string) => {
    try { const r = await fetch(`${API_URL}/api/v1/tests/project/${pid}`, { headers: authH(t) }); if (r.ok) setTestCases(await r.json()) } catch (_e) { /* silent */ }
  }
  const fetchExecutions = async (pid: number, t: string) => {
    try { const r = await fetch(`${API_URL}/api/v1/executions/project/${pid}`, { headers: authH(t) }); if (r.ok) setExecutions(await r.json()) } catch (_e) { /* silent */ }
  }
  const fetchBugs = async (pid: number, t: string) => {
    try { const r = await fetch(`${API_URL}/api/v1/bugs/project/${pid}`, { headers: authH(t) }); if (r.ok) setBugs(await r.json()) } catch (_e) { /* silent */ }
  }

  const createProject = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); if (!token) return; setLoading(true)
    const fd = new FormData(e.currentTarget)
    try {
      const r = await fetch(`${API_URL}/api/v1/projects/`, {
        method: 'POST', headers: { 'Content-Type': 'application/json', ...authH(token) },
        body: JSON.stringify({ name: fd.get('name'), description: fd.get('description'), repository_url: fd.get('github_url'), deployment_url: fd.get('deployment_url') })
      })
      if (r.ok) { toast({ title: '✅ Project created!' }); (e.currentTarget as HTMLFormElement).reset(); fetchProjects(token); fetchDashStats(token) }
      else { const err = await r.json().catch(() => null); toast({ title: err?.detail || 'Error creating project' }) }
    } catch { toast({ title: 'Error creating project' }) }
    setLoading(false)
  }

  const deleteProject = async (pid: number) => {
    if (!token || !confirm('Delete this project and all its data?')) return
    setLoading(true)
    try {
      const r = await fetch(`${API_URL}/api/v1/projects/${pid}`, { method: 'DELETE', headers: authH(token) })
      if (r.ok) { toast({ title: '🗑️ Project deleted' }); fetchProjects(token); fetchDashStats(token) }
    } catch { toast({ title: 'Error deleting project' }) }
    setLoading(false)
  }

  const uploadRequirement = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); if (!token || !selectedProject) return; setLoading(true)
    const formElem = e.currentTarget; const fd = new FormData()
    fd.append('project_id', selectedProject.toString())
    fd.append('title', (formElem.querySelector('[name="title"]') as HTMLInputElement).value)
    const content = (formElem.querySelector('[name="content"]') as HTMLTextAreaElement).value
    if (content) fd.append('content', content)
    const fileInput = formElem.querySelector('[name="file"]') as HTMLInputElement
    if (fileInput?.files?.[0]) fd.append('file', fileInput.files[0])
    try {
      const r = await fetch(`${API_URL}/api/v1/requirements/`, { method: 'POST', headers: authH(token), body: fd })
      if (r.ok) { toast({ title: '✅ Requirement analyzed &amp; test cases generated!' }); formElem.reset(); fetchRequirements(selectedProject, token); fetchTestCases(selectedProject, token); fetchDashStats(token) }
      else { const err = await r.json().catch(() => null); toast({ title: err?.detail || 'Error uploading' }) }
    } catch { toast({ title: 'Error uploading requirement' }) }
    setLoading(false)
  }

  const generateTests = async (reqId: number) => {
    if (!token) return; setLoading(true)
    try {
      const r = await fetch(`${API_URL}/api/v1/tests/generate/${reqId}`, { method: 'POST', headers: authH(token) })
      if (r.ok && selectedProject) { toast({ title: '✅ Test cases generated!' }); fetchTestCases(selectedProject, token); fetchDashStats(token) }
    } catch { toast({ title: 'Error generating tests' }) }
    setLoading(false)
  }

  const runAllTests = async () => {
    if (!token || !selectedProject) return; setBulkRunning(true); setBulkResult(null)
    try {
      const deployUrl = projects.find(p => p.id === selectedProject)?.deployment_url || 'http://localhost:3000'
      const r = await fetch(`${API_URL}/api/v1/tests/project/${selectedProject}/run-all`, {
        method: 'POST', headers: { 'Content-Type': 'application/json', ...authH(token) },
        body: JSON.stringify({ url: deployUrl })
      })
      if (r.ok) {
        const data = await r.json(); setBulkResult(data)
        toast({ title: `Run complete — ${data.passed}/${data.total} passed` })
        fetchExecutions(selectedProject, token); fetchDashStats(token)
      } else { const err = await r.json().catch(() => null); toast({ title: err?.detail || 'Run failed' }) }
    } catch { toast({ title: 'Error running tests' }) }
    setBulkRunning(false)
  }

  const createBug = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); if (!token || !selectedProject) return; setLoading(true)
    const fd = new FormData(e.currentTarget)
    const payload: any = { 
      project_id: selectedProject, 
      title: fd.get('title'), 
      description: fd.get('description'), 
      severity: fd.get('severity') || 'medium' 
    }
    if (bugFormData?.test_case_id) payload.test_case_id = bugFormData.test_case_id
    if (bugFormData?.execution_id) payload.execution_id = bugFormData.execution_id
    
    try {
      const r = await fetch(`${API_URL}/api/v1/bugs/`, {
        method: 'POST', headers: { 'Content-Type': 'application/json', ...authH(token) },
        body: JSON.stringify(payload)
      })
      if (r.ok) { 
        toast({ title: '🐛 Bug reported!' }); 
        (e.currentTarget as HTMLFormElement).reset(); 
        setBugFormData(null)
        fetchBugs(selectedProject, token); 
        fetchDashStats(token) 
      }
    } catch { toast({ title: 'Error reporting bug' }) }
    setLoading(false)
  }

  const updateBugStatus = async (bugId: number, status: string) => {
    if (!token || !selectedProject) return; setLoading(true)
    try {
      const r = await fetch(`${API_URL}/api/v1/bugs/${bugId}`, {
        method: 'PUT', headers: { 'Content-Type': 'application/json', ...authH(token) },
        body: JSON.stringify({ status })
      })
      if (r.ok) { 
        toast({ title: '✅ Bug status updated!' }); 
        fetchBugs(selectedProject, token); 
        fetchDashStats(token) 
      }
    } catch { toast({ title: 'Error updating bug' }) }
    setLoading(false)
  }

  const deleteBug = async (bugId: number) => {
    if (!token || !selectedProject || !confirm('Delete this bug report?')) return; setLoading(true)
    try {
      const r = await fetch(`${API_URL}/api/v1/bugs/${bugId}`, { method: 'DELETE', headers: authH(token) })
      if (r.ok) { 
        toast({ title: '🗑️ Bug deleted' }); 
        fetchBugs(selectedProject, token); 
        fetchDashStats(token) 
      }
    } catch { toast({ title: 'Error deleting bug' }) }
    setLoading(false)
  }

  const createBugFromExecution = (execution: Execution) => {
    const testCase = testCases.find(tc => tc.id === execution.test_case_id)
    setBugFormData({
      test_case_id: execution.test_case_id,
      execution_id: execution.id,
      title: `Test Failed: ${testCase?.title || `TC-${execution.test_case_id}`}`,
      description: `Failed test case: ${testCase?.title || `TC-${execution.test_case_id}`}\n\nError logs:\n${execution.logs || 'No logs available'}`
    })
    setActiveTab('bugs')
    setTimeout(() => {
      const titleInput = document.querySelector('[name="title"]') as HTMLInputElement
      if (titleInput) titleInput.focus()
    }, 100)
  }

  const generateReport = async () => {
    if (!token || !selectedProject) return; setLoading(true)
    try {
      const r = await fetch(`${API_URL}/api/v1/reports/`, {
        method: 'POST', headers: { 'Content-Type': 'application/json', ...authH(token) },
        body: JSON.stringify({ project_id: selectedProject, report_type: 'json' })
      })
      if (r.ok) { toast({ title: '📊 Report saved!' }); setActiveTab('reports') }
    } catch { toast({ title: 'Error generating report' }) }
    setLoading(false)
  }

  const handleLogout = () => { localStorage.removeItem('token'); toast({ title: 'Logged out' }); router.push('/') }
  const toggleReq = (id: number) => setExpandedReqs(prev => { const s = new Set(prev); s.has(id) ? s.delete(id) : s.add(id); return s })
  const toggleTest = (id: number) => setExpandedTests(prev => { const s = new Set(prev); s.has(id) ? s.delete(id) : s.add(id); return s })

  const activeProject = projects.find(p => p.id === selectedProject)

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-800 p-4 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-8 h-8 text-blue-500" />
          <span className="text-xl font-bold">AutoTest AI</span>
          {activeProject && <span className="text-sm text-slate-400 ml-2 hidden md:block">/ {activeProject.name}</span>}
        </div>
        <div className="flex items-center gap-3">
          {selectedProject && (
            <Button onClick={generateReport} disabled={loading} size="sm" className="bg-purple-600 hover:bg-purple-700">
              <BarChart2 className="w-4 h-4 mr-1" />Report
            </Button>
          )}
          
          {/* Notification Bell */}
          <div className="relative">
            <Button 
              onClick={() => { 
                setShowNotifications(!showNotifications); 
                if (!showNotifications && token) fetchUnreadCount(token) 
              }} 
              variant="outline" 
              size="sm"
              className="relative"
            >
              <Bell className="w-4 h-4" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </Button>
            {showNotifications && token && (
              <NotificationDropdown 
                token={token} 
                onClose={() => {
                  setShowNotifications(false)
                  if (token) fetchUnreadCount(token)
                }} 
              />
            )}
          </div>
          
          <Button onClick={handleLogout} variant="outline" size="sm">Logout</Button>
        </div>
      </header>

      <div className="flex flex-1">
        {/* Sidebar */}
        <aside className="w-52 bg-slate-900 border-r border-slate-800 p-3 flex flex-col gap-1">
          {[
            { id: 'projects',     icon: <Home className="w-4 h-4" />,      label: 'Projects' },
            { id: 'requirements', icon: <FileText className="w-4 h-4" />,   label: 'Requirements' },
            { id: 'tests',        icon: <TestTube className="w-4 h-4" />,   label: 'Test Cases' },
            { id: 'bugs',         icon: <Bug className="w-4 h-4" />,        label: 'Bug Tracker' },
            { id: 'regression',   icon: <Target className="w-4 h-4" />,     label: 'Regression' },
            { id: 'history',      icon: <History className="w-4 h-4" />,    label: 'Exec History' },
            { id: 'reports',      icon: <BarChart2 className="w-4 h-4" />,  label: 'Reports' },
            { id: 'settings',     icon: <Settings className="w-4 h-4" />,   label: 'Settings' },
          ].map(item => (
            <button key={item.id} onClick={() => setActiveTab(item.id)}
              className={`flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm transition-all ${activeTab === item.id ? 'bg-blue-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'}`}>
              {item.icon}{item.label}
            </button>
          ))}
        </aside>

        {/* Main content */}
        <main className="flex-1 p-6 overflow-auto">

          {/* Global Stats (from dashboard API) */}
          {stats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <StatCard label="Total Projects"    value={stats.projects}    icon={<Home className="w-4 h-4 text-blue-400" />} />
              <StatCard label="Requirements"      value={stats.requirements} icon={<FileText className="w-4 h-4 text-green-400" />} />
              <StatCard label="Test Cases"        value={stats.test_cases}  icon={<TestTube className="w-4 h-4 text-yellow-400" />} />
              <StatCard label="Global Pass Rate"  value={`${stats.success_rate}%`} icon={<CheckCircle className="w-4 h-4 text-emerald-400" />} color={stats.success_rate >= 70 ? 'text-emerald-400' : 'text-red-400'} />
            </div>
          )}

          {/* ── PROJECTS ── */}
          {activeTab === 'projects' && (
            <div>
              <Card className="mb-6">
                <CardHeader><CardTitle>Create New Project</CardTitle><CardDescription>Define your app for the AI tester</CardDescription></CardHeader>
                <CardContent>
                  <form onSubmit={createProject} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-1"><Label>Project Name *</Label><Input name="name" placeholder="My App" required /></div>
                    <div className="space-y-1"><Label>Description</Label><Input name="description" placeholder="Short description" /></div>
                    <div className="space-y-1"><Label>GitHub URL</Label><Input name="github_url" placeholder="https://github.com/user/repo" /></div>
                    <div className="space-y-1"><Label>Deployment URL</Label><Input name="deployment_url" placeholder="https://myapp.com" /></div>
                    <div className="md:col-span-2"><Button disabled={loading} className="bg-blue-600 hover:bg-blue-700"><Plus className="w-4 h-4 mr-2" />Create Project</Button></div>
                  </form>
                </CardContent>
              </Card>
              {initialLoading ? (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="bg-slate-900 border border-slate-700 rounded-lg p-6 animate-pulse">
                      <div className="h-5 bg-slate-700 rounded w-2/3 mb-3"></div>
                      <div className="h-3 bg-slate-800 rounded w-full mb-2"></div>
                      <div className="h-3 bg-slate-800 rounded w-3/4"></div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {projects.map(p => (
                    <motion.div key={p.id} whileHover={{ scale: 1.02 }}>
                      <Card className={`cursor-pointer ${selectedProject === p.id ? 'ring-2 ring-blue-500' : ''}`}>
                        <CardHeader>
                          <div className="flex justify-between items-start">
                            <div className="flex-1" onClick={() => token && selectProject(p.id, token)}>
                              <CardTitle className="text-lg">{p.name}</CardTitle>
                              <CardDescription className="mt-1">{p.description || 'No description'}</CardDescription>
                              {p.deployment_url && <p className="text-xs text-blue-400 mt-1 truncate">{p.deployment_url}</p>}
                              <p className="text-xs text-slate-500 mt-1">{formatISTDate(p.created_at)}</p>
                              {selectedProject === p.id && <span className="text-xs text-blue-400 mt-1 block">● Active</span>}
                            </div>
                            <Button variant="ghost" size="icon" onClick={e => { e.stopPropagation(); deleteProject(p.id) }} disabled={loading} className="text-red-400 hover:text-red-300 hover:bg-red-950">
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </CardHeader>
                      </Card>
                    </motion.div>
                  ))}
                  {projects.length === 0 && <p className="text-slate-500 col-span-3 py-8 text-center">No projects yet. Create one above.</p>}
                </div>
              )}
            </div>
          )}

          {/* ── REQUIREMENTS ── */}
          {activeTab === 'requirements' && (
            <div>
              {!selectedProject ? <NoProject /> : (
                <>
                  <Card className="mb-6">
                    <CardHeader><CardTitle>Upload Requirement</CardTitle><CardDescription>AI analyzes it and auto-generates test cases</CardDescription></CardHeader>
                    <CardContent>
                      <form onSubmit={uploadRequirement} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-1"><Label>Title *</Label><Input name="title" placeholder="e.g. User Authentication Flow" required /></div>
                          <div className="space-y-1"><Label>File (optional)</Label><Input name="file" type="file" /></div>
                        </div>
                        <div className="space-y-1">
                          <Label>Requirement Content</Label>
                          <textarea name="content" placeholder="Describe the requirement in detail. AI will extract functional reqs, risks, and generate test cases..." className="w-full min-h-[100px] bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y" />
                        </div>
                        <Button disabled={loading} className="bg-blue-600 hover:bg-blue-700"><Upload className="w-4 h-4 mr-2" />{loading ? 'Analyzing...' : 'Upload &amp; Analyze'}</Button>
                      </form>
                    </CardContent>
                  </Card>
                  <div className="space-y-3">
                    {requirements.map(req => (
                      <Card key={req.id}>
                        <CardHeader>
                          <div className="flex justify-between items-start gap-4 flex-wrap">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 flex-wrap">
                                <CardTitle className="text-base">{req.title}</CardTitle>
                                <StatusBadge status={req.status} />
                                {req.structured_data?.complexity && <span className="text-xs px-2 py-0.5 rounded bg-slate-700 text-slate-300">complexity: {req.structured_data.complexity}</span>}
                              </div>
                              <CardDescription className="mt-1 line-clamp-2">{req.content}</CardDescription>
                            </div>
                            <div className="flex gap-2">
                              <Button size="sm" variant="outline" onClick={() => toggleReq(req.id)}>{expandedReqs.has(req.id) ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}</Button>
                              <Button size="sm" onClick={() => generateTests(req.id)} disabled={req.status !== 'analyzed' || loading}><TestTube className="w-4 h-4 mr-1" />Tests</Button>
                            </div>
                          </div>
                        </CardHeader>
                        {expandedReqs.has(req.id) && req.structured_data && (
                          <CardContent>
                            <div className="grid md:grid-cols-2 gap-4 text-sm">
                              <StructuredList label="Functional Requirements" items={req.structured_data.functional_requirements} color="text-green-400" />
                              <StructuredList label="Non-Functional Requirements" items={req.structured_data.non_functional_requirements} color="text-yellow-400" />
                              <StructuredList label="Test Objectives" items={req.structured_data.test_objectives} color="text-blue-400" />
                              <StructuredList label="Risks" items={req.structured_data.risks} color="text-red-400" />
                            </div>
                          </CardContent>
                        )}
                      </Card>
                    ))}
                    {requirements.length === 0 && <p className="text-slate-500 text-center py-8">No requirements yet. Upload one above.</p>}
                  </div>
                </>
              )}
            </div>
          )}

          {/* ── TEST CASES ── */}
          {activeTab === 'tests' && (
            <div>
              {!selectedProject ? <NoProject /> : (
                <>
                  <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
                    <h2 className="text-xl font-semibold">Test Cases ({testCases.length})</h2>
                    <Button onClick={runAllTests} disabled={bulkRunning || testCases.length === 0} className="bg-emerald-600 hover:bg-emerald-700">
                      {bulkRunning ? <><RefreshCw className="w-4 h-4 mr-2 animate-spin" />Running...</> : <><Play className="w-4 h-4 mr-2" />Run All Tests</>}
                    </Button>
                  </div>
                  {bulkResult && (
                    <Card className="mb-4 border-emerald-800">
                      <CardContent className="pt-4">
                        <div className="flex items-center gap-6 flex-wrap mb-2">
                          <span className="font-bold">Run Summary</span>
                          <span className="text-emerald-400 flex items-center gap-1"><CheckCircle className="w-4 h-4" />{bulkResult.passed} Passed</span>
                          <span className="text-red-400 flex items-center gap-1"><XCircle className="w-4 h-4" />{bulkResult.failed} Failed</span>
                          <span className="text-slate-300">{bulkResult.success_rate}% Success Rate</span>
                        </div>
                        <div className="w-full bg-slate-800 rounded-full h-2">
                          <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${bulkResult.success_rate}%` }} />
                        </div>
                      </CardContent>
                    </Card>
                  )}
                  <div className="space-y-3">
                    {testCases.map(tc => (
                      <Card key={tc.id}>
                        <CardHeader>
                          <div className="flex justify-between items-start gap-4 flex-wrap">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 flex-wrap">
                                <CardTitle className="text-base">{tc.title}</CardTitle>
                                <span className="text-xs px-2 py-0.5 rounded bg-slate-700 text-slate-300">{tc.test_type}</span>
                                <StatusBadge status={tc.status} />
                              </div>
                              {tc.description && <CardDescription className="mt-1">{tc.description}</CardDescription>}
                            </div>
                            <Button size="sm" variant="outline" onClick={() => toggleTest(tc.id)}>
                              {expandedTests.has(tc.id) ? <ChevronUp className="w-4 h-4" /> : <><ChevronDown className="w-4 h-4 mr-1" />Script</>}
                            </Button>
                          </div>
                        </CardHeader>
                        {expandedTests.has(tc.id) && tc.script && (
                          <CardContent>
                            <pre className="text-xs bg-slate-950 p-4 rounded overflow-auto max-h-72 border border-slate-800">{tc.script}</pre>
                          </CardContent>
                        )}
                      </Card>
                    ))}
                    {testCases.length === 0 && <p className="text-slate-500 text-center py-8">No test cases yet. Upload a requirement to generate them automatically.</p>}
                  </div>
                </>
              )}
            </div>
          )}

          {/* ── BUG TRACKER ── */}
          {activeTab === 'bugs' && (
            <div>
              {!selectedProject ? <NoProject /> : (
                <>
                  <Card className="mb-6">
                    <CardHeader><CardTitle>Report a Bug</CardTitle><CardDescription>Log bugs found during testing</CardDescription></CardHeader>
                    <CardContent>
                      <form onSubmit={createBug} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-1"><Label>Bug Title *</Label><Input name="title" placeholder="e.g. Login fails with valid credentials" defaultValue={bugFormData?.title || ''} required /></div>
                          <div className="space-y-1">
                            <Label>Severity</Label>
                            <select name="severity" className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-sm text-slate-100">
                              <option value="low">Low</option>
                              <option value="medium">Medium</option>
                              <option value="high">High</option>
                              <option value="critical">Critical</option>
                            </select>
                          </div>
                        </div>
                        <div className="space-y-1">
                          <Label>Description</Label>
                          <textarea name="description" placeholder="Steps to reproduce, expected vs actual..." defaultValue={bugFormData?.description || ''} className="w-full min-h-[80px] bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y" />
                        </div>
                        {bugFormData && (
                          <div className="bg-blue-900/20 border border-blue-700 rounded p-3 text-sm">
                            <p className="text-blue-300">📎 Linked to Test Case #{bugFormData.test_case_id}</p>
                            <Button type="button" size="sm" variant="ghost" onClick={() => setBugFormData(null)} className="mt-2 text-xs">Clear Link</Button>
                          </div>
                        )}
                        <Button disabled={loading} className="bg-red-600 hover:bg-red-700"><Bug className="w-4 h-4 mr-2" />Report Bug</Button>
                      </form>
                    </CardContent>
                  </Card>
                  <div className="space-y-3">
                    {bugs.map(bug => (
                      <Card key={bug.id} className={`border-l-4 ${bug.severity === 'critical' ? 'border-l-red-500' : bug.severity === 'high' ? 'border-l-orange-500' : bug.severity === 'medium' ? 'border-l-yellow-500' : 'border-l-slate-600'}`}>
                        <CardHeader>
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 flex-wrap">
                                <CardTitle className="text-base">{bug.title}</CardTitle>
                                <SeverityBadge severity={bug.severity} />
                                <BugStatusBadge status={bug.status} />
                              </div>
                              {bug.description && <CardDescription className="mt-1">{bug.description}</CardDescription>}
                              {bug.test_case_title && (
                                <p className="text-xs text-blue-400 mt-1 flex items-center gap-1">
                                  <TestTube className="w-3 h-3" />
                                  Linked to: {bug.test_case_title}
                                </p>
                              )}
                              <p className="text-xs text-slate-500 mt-1">{formatISTDisplay(bug.created_at)}</p>
                            </div>
                            <div className="flex flex-col gap-2">
                              <select 
                                value={bug.status} 
                                onChange={(e) => updateBugStatus(bug.id, e.target.value)}
                                disabled={loading}
                                className="text-xs bg-slate-800 border border-slate-700 rounded px-2 py-1 text-slate-100"
                              >
                                <option value="open">Open</option>
                                <option value="in_progress">In Progress</option>
                                <option value="resolved">Resolved</option>
                                <option value="closed">Closed</option>
                              </select>
                              <Button size="sm" variant="ghost" onClick={() => deleteBug(bug.id)} disabled={loading} className="text-red-400 hover:text-red-300 hover:bg-red-950">
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </CardHeader>
                      </Card>
                    ))}
                    {bugs.length === 0 && <p className="text-slate-500 text-center py-8">No bugs reported. All clear! 🎉</p>}
                  </div>
                </>
              )}
            </div>
          )}

          {/* ── REGRESSION SUITE ── */}
          {activeTab === 'regression' && (
            <div>
              {!selectedProject || !token ? <NoProject /> : (
                <RegressionSuite 
                  projectId={selectedProject} 
                  token={token}
                  deploymentUrl={activeProject?.deployment_url}
                />
              )}
            </div>
          )}

          {/* ── EXECUTION HISTORY ── */}
          {activeTab === 'history' && (
            <div>
              {!selectedProject ? <NoProject /> : (
                <>
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold">Execution History ({executions.length})</h2>
                    <Button size="sm" variant="outline" onClick={() => token && fetchExecutions(selectedProject, token)}><RefreshCw className="w-4 h-4 mr-1" />Refresh</Button>
                  </div>
                  {executions.length > 0 && (
                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <StatCard label="Total Runs" value={executions.length} icon={<Clock className="w-4 h-4 text-slate-400" />} />
                      <StatCard label="Passed" value={executions.filter(e => e.status === 'passed').length} icon={<CheckCircle className="w-4 h-4 text-emerald-400" />} color="text-emerald-400" />
                      <StatCard label="Failed" value={executions.filter(e => e.status === 'failed').length} icon={<XCircle className="w-4 h-4 text-red-400" />} color="text-red-400" />
                    </div>
                  )}
                  <Card>
                    <CardContent className="pt-4">
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead><tr className="border-b border-slate-800 text-slate-400 text-left">
                            <th className="py-2 px-3">ID</th><th className="py-2 px-3">Test Case</th><th className="py-2 px-3">Status</th><th className="py-2 px-3">Logs</th><th className="py-2 px-3">Run At</th><th className="py-2 px-3">Actions</th>
                          </tr></thead>
                          <tbody>
                            {executions.map(ex => {
                              const testCase = testCases.find(tc => tc.id === ex.test_case_id)
                              return (
                                <tr key={ex.id} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                                  <td className="py-2 px-3 text-slate-400">#{ex.id}</td>
                                  <td className="py-2 px-3">
                                    <div className="flex flex-col">
                                      <span>TC-{ex.test_case_id}</span>
                                      {testCase && <span className="text-xs text-slate-500">{testCase.title}</span>}
                                    </div>
                                  </td>
                                  <td className="py-2 px-3"><StatusBadge status={ex.status} /></td>
                                  <td className="py-2 px-3 text-slate-400 max-w-xs truncate">{ex.logs || '—'}</td>
                                  <td className="py-2 px-3 text-slate-400 whitespace-nowrap">{formatISTShort(ex.created_at)}</td>
                                  <td className="py-2 px-3">
                                    {ex.status === 'failed' && (
                                      <Button 
                                        size="sm" 
                                        variant="outline" 
                                        onClick={() => createBugFromExecution(ex)}
                                        className="text-red-400 hover:text-red-300 hover:bg-red-950/20 border-red-800"
                                      >
                                        <Bug className="w-3 h-3 mr-1" />
                                        Report Bug
                                      </Button>
                                    )}
                                  </td>
                                </tr>
                              )
                            })}
                          </tbody>
                        </table>
                        {executions.length === 0 && <p className="text-slate-500 text-center py-8">No executions yet. Use &quot;Run All Tests&quot; from the Test Cases tab.</p>}
                      </div>
                    </CardContent>
                  </Card>
                </>
              )}
            </div>
          )}

          {/* ── REPORTS ── */}
          {activeTab === 'reports' && (
            <div>
              {!selectedProject ? <NoProject /> : (
                <ReportsPanel projectId={selectedProject} token={token!} onGenerate={generateReport} loading={loading} executions={executions} testCases={testCases} requirements={requirements} bugs={bugs} />
              )}
            </div>
          )}

          {/* ── SETTINGS ── */}
          {activeTab === 'settings' && (
            <Card>
              <CardHeader><CardTitle>Settings</CardTitle><CardDescription>AutoTest AI workspace configuration</CardDescription></CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-1"><Label>Backend API URL</Label><Input readOnly value={API_URL} className="bg-slate-800 text-slate-300" /></div>
                <div className="space-y-1"><Label>AI Model</Label><Input readOnly value="llama3 (configured in .env → DEFAULT_MODEL)" className="bg-slate-800 text-slate-300" /></div>
                <div className="p-4 bg-slate-800 rounded-lg space-y-2">
                  <p className="text-sm font-medium">Ollama Setup (Required for AI features)</p>
                  <p className="text-xs text-slate-400">If requirement analysis shows &quot;error&quot; status, Ollama is not running. Fix:</p>
                  <code className="text-xs bg-slate-950 px-3 py-1.5 rounded block text-green-400">ollama serve</code>
                  <code className="text-xs bg-slate-950 px-3 py-1.5 rounded block text-green-400">ollama pull llama3.2</code>
                  <p className="text-xs text-slate-500 mt-1">Without Ollama, the app uses smart keyword-based fallback analysis.</p>
                </div>
              </CardContent>
            </Card>
          )}

        </main>
      </div>
    </div>
  )
}
