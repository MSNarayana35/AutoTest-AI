'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ShieldCheck, Zap, Users, Activity, FileText, Code } from 'lucide-react'
import { motion } from 'framer-motion'
import { toast } from '@/components/ui/use-toast'
import { NavLink } from '@/components/NavLink'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
    const formData = new FormData(e.currentTarget)
    const email = formData.get('email') as string
    const password = formData.get('password') as string

    // #region debug-point A:login-submit
    fetch('http://127.0.0.1:7777/event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId: 'app-flow-error',
        runId: 'pre-fix',
        hypothesisId: 'A',
        location: 'frontend/app/page.tsx:25',
        msg: '[DEBUG] login submit handler fired',
        data: { emailLength: email?.length ?? 0 },
        ts: Date.now()
      })
    }).catch(() => {})
    // #endregion

    try {
      const body = new URLSearchParams({ username: email, password })
      const res = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body
      })
      // #region debug-point B:login-response
      fetch('http://127.0.0.1:7777/event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: 'app-flow-error',
          runId: 'pre-fix',
          hypothesisId: 'B',
          location: 'frontend/app/page.tsx:44',
          msg: '[DEBUG] login response received',
          data: { ok: res.ok, status: res.status },
          ts: Date.now()
        })
      }).catch(() => {})
      // #endregion
      if (res.ok) {
        const data = await res.json()
        localStorage.setItem('token', data.access_token)
        setIsAuthenticated(true)
        toast({ title: 'Logged in!', description: 'Redirecting to dashboard...' })
        // Redirect after a small delay to let the toast show
        setTimeout(() => {
          router.push('/dashboard')
        }, 1000)
      } else {
        toast({ title: 'Error logging in', description: 'Please check your credentials' })
      }
    } catch {
      // #region debug-point C:login-error
      fetch('http://127.0.0.1:7777/event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: 'app-flow-error',
          runId: 'pre-fix',
          hypothesisId: 'C',
          location: 'frontend/app/page.tsx:65',
          msg: '[DEBUG] login request threw',
          data: {},
          ts: Date.now()
        })
      }).catch(() => {})
      // #endregion
      toast({ title: 'Connection error', description: 'Make sure backend is running' })
    }
    setLoading(false)
  }

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
    const formData = new FormData(e.currentTarget)
    const email = formData.get('email') as string
    const password = formData.get('password') as string
    const fullName = formData.get('fullName') as string

    try {
      const res = await fetch(`${API_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: fullName })
      })
      if (res.ok) {
        toast({ title: 'Registered!', description: 'Now login to continue' })
      } else {
        toast({ title: 'Registration failed', description: 'Email might already exist' })
      }
    } catch {
      toast({ title: 'Connection error', description: 'Make sure backend is running' })
    }
    setLoading(false)
  }

  if (isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-slate-50">
      <nav className="flex items-center justify-between p-6 border-b border-slate-800 bg-slate-950/50 backdrop-blur-sm">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => window.location.href = '/'}>
          <ShieldCheck className="w-8 h-8 text-blue-500" />
          <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">AutoTest AI</span>
        </div>
        <div className="flex gap-4 items-center">
          <NavLink href="/features">Features</NavLink>
          <NavLink href="/about">About</NavLink>
          <NavLink href="/dashboard" variant="default">Try Now</NavLink>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-16">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-8"
          >
            <h1 className="text-5xl lg:text-6xl font-bold leading-tight">
              Automate. Validate. <br/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">Accelerate.</span>
            </h1>
            <p className="text-xl text-slate-400">
              AI-powered multi-agent autonomous testing platform for modern software development.
            </p>
            <div className="grid md:grid-cols-2 gap-4 text-slate-300">
              <div className="flex items-center gap-3">
                <Zap className="w-5 h-5 text-yellow-400" />
                Smart Test Generation
              </div>
              <div className="flex items-center gap-3">
                <Activity className="w-5 h-5 text-green-400" />
                Self-Healing Tests
              </div>
              <div className="flex items-center gap-3">
                <Users className="w-5 h-5 text-blue-400" />
                Multi-Agent System
              </div>
              <div className="flex items-center gap-3">
                <Code className="w-5 h-5 text-purple-400" />
                Playwright/Selenium Support
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Card className="backdrop-blur-xl bg-slate-900/80 border-slate-700 shadow-2xl">
              <CardHeader>
                <CardTitle className="text-white text-2xl">Get Started</CardTitle>
                <CardDescription>Create an account or sign in</CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="login" className="w-full">
                  <TabsList className="w-full grid grid-cols-2 bg-slate-800">
                    <TabsTrigger value="login">Login</TabsTrigger>
                    <TabsTrigger value="register">Register</TabsTrigger>
                  </TabsList>
                  <TabsContent value="login">
                    <form onSubmit={handleLogin} className="space-y-4 pt-4">
                      <div className="space-y-2">
                        <Label>Email</Label>
                        <Input name="email" type="email" placeholder="you@example.com" required />
                      </div>
                      <div className="space-y-2">
                        <Label>Password</Label>
                        <Input name="password" type="password" placeholder="••••••••" required />
                      </div>
                      <Button className="w-full bg-blue-600 hover:bg-blue-700" disabled={loading}>
                        {loading ? 'Logging in...' : 'Login'}
                      </Button>
                    </form>
                  </TabsContent>
                  <TabsContent value="register">
                    <form onSubmit={handleRegister} className="space-y-4 pt-4">
                      <div className="space-y-2">
                        <Label>Full Name</Label>
                        <Input name="fullName" placeholder="John Doe" required />
                      </div>
                      <div className="space-y-2">
                        <Label>Email</Label>
                        <Input name="email" type="email" placeholder="you@example.com" required />
                      </div>
                      <div className="space-y-2">
                        <Label>Password</Label>
                        <Input name="password" type="password" placeholder="••••••••" required />
                      </div>
                      <Button className="w-full bg-blue-600 hover:bg-blue-700" disabled={loading}>
                        {loading ? 'Registering...' : 'Register'}
                      </Button>
                    </form>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        <div className="mt-20">
          <h2 className="text-3xl font-bold text-center text-white mb-12">Powerful Features</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<FileText className="w-8 h-8" />}
              title="Requirement Analysis"
              description="AI agents analyze PRDs, SRS, and user stories to extract testable requirements."
            />
            <FeatureCard
              icon={<Code className="w-8 h-8" />}
              title="Test Generation"
              description="Automatically generate Playwright, Selenium, and pytest scripts from requirements."
            />
            <FeatureCard
              icon={<Activity className="w-8 h-8" />}
              title="Self-Healing"
              description="AI automatically fixes broken locators when your UI changes."
            />
          </div>
        </div>
      </main>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <Card className="backdrop-blur-xl bg-slate-900/50 border-slate-700 hover:bg-slate-800/50 transition-all">
      <CardContent className="p-8">
        <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center mb-4 text-white">
          {icon}
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
        <p className="text-slate-400">{description}</p>
      </CardContent>
    </Card>
  )
}
