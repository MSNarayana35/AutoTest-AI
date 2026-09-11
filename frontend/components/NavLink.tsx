'use client'

import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'

export function NavLink({ href, children, variant = 'ghost' }: { href: string; children: React.ReactNode; variant?: 'ghost' | 'default' | 'destructive' | 'secondary' | 'outline' | 'link' }) {
  const router = useRouter()

  return (
    <Button variant={variant} onClick={() => router.push(href)}>
      {children}
    </Button>
  )
}
