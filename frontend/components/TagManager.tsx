'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { X, Plus, Tag as TagIcon } from 'lucide-react'

interface TagManagerProps {
  testId: number
  tags: string[]
  onTagsUpdate: (tags: string[]) => void
  token: string
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export function TagManager({ testId, tags, onTagsUpdate, token }: TagManagerProps) {
  const [newTag, setNewTag] = useState('')
  const [adding, setAdding] = useState(false)

  const addTag = async () => {
    if (!newTag.trim() || adding) return
    setAdding(true)

    try {
      const response = await fetch(`${API_URL}/api/v1/tests/${testId}/tags`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ tags: [newTag.trim()] })
      })

      if (response.ok) {
        const updated = await response.json()
        onTagsUpdate(updated.tags || [])
        setNewTag('')
      }
    } catch (error) {
      console.error('Error adding tag:', error)
    }

    setAdding(false)
  }

  const removeTag = async (tag: string) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/tests/${testId}/tags/${encodeURIComponent(tag)}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        onTagsUpdate(tags.filter(t => t !== tag))
      }
    } catch (error) {
      console.error('Error removing tag:', error)
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <TagIcon className="w-4 h-4 text-slate-400" />
      
      {tags && tags.length > 0 ? (
        tags.map(tag => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-900/40 text-blue-300 border border-blue-700 rounded-full"
          >
            {tag}
            <button
              onClick={() => removeTag(tag)}
              className="hover:text-blue-100 transition-colors"
            >
              <X className="w-3 h-3" />
            </button>
          </span>
        ))
      ) : (
        <span className="text-xs text-slate-500">No tags</span>
      )}

      <div className="inline-flex items-center gap-1">
        <Input
          type="text"
          value={newTag}
          onChange={(e) => setNewTag(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault()
              addTag()
            }
          }}
          placeholder="Add tag..."
          className="h-7 w-32 text-xs bg-slate-800 border-slate-700"
        />
        <Button
          size="sm"
          onClick={addTag}
          disabled={!newTag.trim() || adding}
          className="h-7 px-2 bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="w-3 h-3" />
        </Button>
      </div>
    </div>
  )
}
