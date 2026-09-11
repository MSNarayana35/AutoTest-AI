'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { ShieldCheck, ArrowLeft, Bell } from 'lucide-react'
import { RegressionSuite } from '@/components/RegressionSuite'
import { toast } from '@/components/ui/use-toast'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

type Project = { 
  id: number
  name: string
  description: string
  repository_url?: string
  deployment_url?: string
  created_at: string
}

export default function RegressionPage() {
  const [token, setToken] = useState<string | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProject, setSelectedProject] = useState<number | null>(null)
  const router = useRouter()

  useEffect(() => {
    const t = localStorage.getItem('token')
    if (!t) {
      router.push('/')
      return
    }
    setToken(t)
    fetchProjects(t)
  }, [router])

  const fetchProjects = async (t: string) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/projects/`, {
        headers: { Authorization: `Bearer ${t}` }
      })
      if (response.ok) {
        const data: Project[] = await response.json()
        setProjects(data)
        if (data.length > 0) {
          setSelectedProject(data[0].id)
        }
      }
    } catch (error) {
      console.error('Error fetching projects:', error)
      toast({ title: 'Error loading projects' })
    }
  }

  const activeProject = projects.find(p => p.id === selectedProject)

  const handleLogout = () => {
    localStorage.removeItem('token')
    toast({ title: 'Logged out' })
    router.push('/')
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-800 p-4 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-4">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => router.push('/dashboard')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Dashboard
          </Button>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-8 h-8 text-blue-500" />
            <span className="text-xl font-bold">AutoTest AI</span>
            <span className="text-sm text-slate-400">/ Regression Suite</span>
          </div>
        </div>
        <Button onClick={handleLogout} variant="outline" size="sm">
          Logout
        </Button>
      </header>

      <div className="flex-1 p-6">
        {/* Project Selector */}
        {projects.length > 0 && (
          <div className="mb-6">
            <label className="text-sm font-medium text-slate-300 mb-2 block">
              Select Project
            </label>
            <select
              value={selectedProject || ''}
              onChange={(e) => setSelectedProject(Number(e.target.value))}
              className="w-full md:w-96 bg-slate-800 border border-slate-700 rounded-md px-4 py-2 text-slate-100"
            >
              {projects.map(project => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Regression Suite Component */}
        {selectedProject && token ? (
          <RegressionSuite
            projectId={selectedProject}
            token={token}
            deploymentUrl={activeProject?.deployment_url}
          />
        ) : (
          <div className="text-center py-16 text-slate-500">
            {projects.length === 0 ? (
              <p>No projects found. Create a project in the dashboard first.</p>
            ) : (
              <p>Select a project to view regression suite</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
