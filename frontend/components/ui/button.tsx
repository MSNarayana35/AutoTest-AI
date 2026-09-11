import React from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

export function Button({
  className,
  variant = "default",
  size = "default",
  ...props
}: ButtonProps & { variant?: "default" | "outline" | "ghost", size?: "default" | "sm" | "icon" }) {
  const variants = {
    default: "bg-blue-600 text-white hover:bg-blue-700",
    outline: "border border-slate-700 bg-transparent hover:bg-slate-800",
    ghost: "hover:bg-slate-800 text-slate-200"
  }
  const sizes = {
    default: "h-10 px-4 py-2 rounded-md",
    sm: "h-9 px-3 rounded-md text-sm",
    icon: "h-10 w-10 rounded-md flex items-center justify-center"
  }

  return (
    <button
      className={cn(
      "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
      variants[variant as keyof typeof variants],
      sizes[size as keyof typeof sizes],
      className
    )}
      {...props}
    />
  )
}
