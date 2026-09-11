/**
 * Loading skeleton components for better perceived performance
 */

export function CardSkeleton() {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-6 animate-pulse">
      <div className="h-4 bg-slate-700 rounded w-1/3 mb-4"></div>
      <div className="h-3 bg-slate-800 rounded w-2/3 mb-2"></div>
      <div className="h-3 bg-slate-800 rounded w-1/2"></div>
    </div>
  )
}

export function StatCardSkeleton() {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 animate-pulse">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="h-3 bg-slate-800 rounded w-1/2 mb-2"></div>
          <div className="h-6 bg-slate-700 rounded w-1/3"></div>
        </div>
        <div className="h-8 w-8 bg-slate-800 rounded"></div>
      </div>
    </div>
  )
}

export function TableRowSkeleton() {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 mb-3 animate-pulse">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="h-4 bg-slate-700 rounded w-2/3 mb-2"></div>
          <div className="h-3 bg-slate-800 rounded w-1/2"></div>
        </div>
        <div className="h-6 w-16 bg-slate-800 rounded"></div>
      </div>
    </div>
  )
}

export function ListSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <TableRowSkeleton key={i} />
      ))}
    </div>
  )
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <StatCardSkeleton key={i} />
        ))}
      </div>
      <div className="grid gap-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
    </div>
  )
}

export function ProjectsGridSkeleton() {
  return (
    <div className="grid gap-4">
      {Array.from({ length: 3 }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  )
}

export function Spinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  }

  return (
    <div className="flex items-center justify-center">
      <div
        className={`${sizeClasses[size]} border-4 border-slate-700 border-t-blue-500 rounded-full animate-spin`}
      ></div>
    </div>
  )
}

export function InlineSpinner() {
  return (
    <div className="inline-block h-4 w-4 border-2 border-slate-400 border-t-blue-500 rounded-full animate-spin"></div>
  )
}
