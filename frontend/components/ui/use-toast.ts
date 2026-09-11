"use client"

import * as React from "react"

export interface Toast {
  id: string
  title?: string
  description?: string
  action?: React.ReactNode
}

// Simple in-memory toast store
const listeners: ((toasts: Toast[]) => void)[] = []
let toasts: Toast[] = []

function dispatch() {
  for (const listener of listeners) {
    listener(toasts)
  }
}

export function toast({ title, description, action }: Omit<Toast, "id">) {
  const id = Math.random().toString(36).substring(2, 9)
  toasts = [...toasts, { id, title, description, action }]
  dispatch()
  // Auto-remove after 5 seconds
  setTimeout(() => {
    toasts = toasts.filter(t => t.id !== id)
    dispatch()
  }, 5000)
}

export function useToast() {
  const [toastList, setToastList] = React.useState<Toast[]>(toasts)

  React.useEffect(() => {
    const listener = (newToasts: Toast[]) => {
      setToastList(newToasts)
    }
    listeners.push(listener)
    return () => {
      const index = listeners.indexOf(listener)
      if (index > -1) listeners.splice(index, 1)
    }
  }, [])

  return { toasts: toastList, toast }
}
