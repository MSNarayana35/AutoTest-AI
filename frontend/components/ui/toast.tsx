import * as React from "react"
import { cn } from "@/lib/utils"

export function Toast({
  className,
  title,
  description,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & { title?: string; description?: string }) {
  return (
    <div
      className={cn(
        "pointer-events-auto relative flex w-full flex-col space-y-2 overflow-hidden rounded-lg border border-slate-700 bg-slate-900 p-4 text-slate-50 shadow-lg",
        className
      )}
      {...props}
    >
      <div className="flex items-center justify-between">
        {title && <div className="font-semibold">{title}</div>}
      </div>
      {description && <div className="text-sm text-slate-400">{description}</div>}
    </div>
  )
}
