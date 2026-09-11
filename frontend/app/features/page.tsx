'use client'

import { motion } from 'framer-motion'
import { ShieldCheck, Zap, Users, Activity, FileText, Code, Play, TestTube, Settings, Trash2 } from 'lucide-react'
import { NavLink } from '@/components/NavLink'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const features = [
  {
    icon: <FileText className="w-10 h-10 text-blue-500" />,
    title: 'Requirement Analysis',
    description: 'AI-powered analysis of your SRS/PRD documents to extract testable requirements.'
  },
  {
    icon: <TestTube className="w-10 h-10 text-green-500" />,
    title: 'Auto Test Generation',
    description: 'Automatically generates Playwright, Selenium, and pytest scripts from your requirements.'
  },
  {
    icon: <Activity className="w-10 h-10 text-yellow-500" />,
    title: 'Self-Healing Tests',
    description: 'AI automatically fixes broken locators when your UI changes.'
  },
  {
    icon: <Code className="w-10 h-10 text-purple-500" />,
    title: 'GitHub Integration',
    description: 'Connect your repo to let the AI understand your codebase better.'
  },
  {
    icon: <Play className="w-10 h-10 text-red-500" />,
    title: 'Test Execution',
    description: 'Run your tests automatically and get real-time results.'
  },
  {
    icon: <Settings className="w-10 h-10 text-indigo-500" />,
    title: 'Project Management',
    description: 'Create, manage, and delete your testing projects with ease.'
  }
]

export default function FeaturesPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-slate-50">
      <nav className="flex items-center justify-between p-6 border-b border-slate-800 bg-slate-950/50 backdrop-blur-sm">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => window.location.href = '/'}>
          <ShieldCheck className="w-8 h-8 text-blue-500" />
          <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">AutoTest AI</span>
        </div>
        <div className="flex gap-4 items-center">
          <NavLink href="/">Home</NavLink>
          <NavLink href="/about">About</NavLink>
          <NavLink href="/dashboard" variant="default">Try Now</NavLink>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-16">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h1 className="text-5xl lg:text-6xl font-bold mb-6">Powerful Features</h1>
          <p className="text-xl text-slate-400 max-w-3xl mx-auto">
            Everything you need for AI-powered automated testing - all in one place.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: idx * 0.1 }}
            >
              <Card className="bg-slate-900/80 border-slate-700 hover:border-blue-500 transition-all">
                <CardContent className="p-8">
                  <div className="mb-4">{feature.icon}</div>
                  <CardTitle className="mb-2">{feature.title}</CardTitle>
                  <CardDescription className="text-slate-400">{feature.description}</CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </main>
    </div>
  )
}
