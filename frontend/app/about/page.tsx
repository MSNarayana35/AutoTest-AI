'use client'

import { motion } from 'framer-motion'
import { ShieldCheck, Zap, Users, Activity } from 'lucide-react'
import { NavLink } from '@/components/NavLink'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const teamMembers = [
  {
    name: 'The AI Team',
    role: 'Lead Developers',
    description: 'Building the future of automated testing'
  }
]

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-slate-50">
      <nav className="flex items-center justify-between p-6 border-b border-slate-800 bg-slate-950/50 backdrop-blur-sm">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => window.location.href = '/'}>
          <ShieldCheck className="w-8 h-8 text-blue-500" />
          <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">AutoTest AI</span>
        </div>
        <div className="flex gap-4 items-center">
          <NavLink href="/">Home</NavLink>
          <NavLink href="/features">Features</NavLink>
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
          <h1 className="text-5xl lg:text-6xl font-bold mb-6">About AutoTest AI</h1>
          <p className="text-xl text-slate-400 max-w-3xl mx-auto">
            Revolutionizing software testing with AI-powered automation
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <Card className="bg-slate-900/80 border-slate-700">
            <CardContent className="p-8 text-center">
              <Zap className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
              <CardTitle>Lightning Fast</CardTitle>
              <CardDescription className="text-slate-400">
                AI-generated tests in seconds
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="bg-slate-900/80 border-slate-700">
            <CardContent className="p-8 text-center">
              <Activity className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <CardTitle>Self-Healing</CardTitle>
              <CardDescription className="text-slate-400">
                Tests fix themselves when your UI changes
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="bg-slate-900/80 border-slate-700">
            <CardContent className="p-8 text-center">
              <Users className="w-16 h-16 text-blue-500 mx-auto mb-4" />
              <CardTitle>Team Ready</CardTitle>
              <CardDescription className="text-slate-400">
                Perfect for teams of all sizes
              </CardDescription>
            </CardContent>
          </Card>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="bg-slate-900/80 border-slate-700">
            <CardHeader>
              <CardTitle>Our Mission</CardTitle>
              <CardDescription>
                To make software testing accessible, fast, and intelligent for everyone.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-slate-400">
                AutoTest AI was born out of frustration with manual testing processes. Our goal is to let AI handle the repetitive, boring work of writing and maintaining tests - so your team can focus on what really matters: building great software.
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </main>
    </div>
  )
}
