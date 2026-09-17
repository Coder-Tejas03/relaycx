import * as React from "react"
import { cn } from "cn"

function Input({
  className,
  type,
  ...props
}) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "h-10 sm:h-9 min-h-[44px] sm:min-h-0 w-full min-w-0 rounded-lg border border-white/[0.09] bg-[#17171A] px-3 py-2 text-sm text-zinc-100 placeholder:text-zinc-500 transition-all duration-micro outline-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:border-transparent disabled:opacity-40 disabled:cursor-not-allowed aria-invalid:border-red-500 aria-invalid:ring-2 aria-invalid:ring-red-400/40",
        className
      )}
      {...props}
    />
  )
}

export { Input }
