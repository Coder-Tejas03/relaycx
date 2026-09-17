import * as React from "react"
import { cn } from "cn"

function Textarea({
  className,
  ...props
}) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        "flex field-sizing-content min-h-16 w-full rounded-lg border border-white/[0.09] bg-[#17171A] px-3 py-2 text-sm text-zinc-100 placeholder:text-zinc-500 transition-all duration-micro outline-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:border-transparent disabled:opacity-40 disabled:cursor-not-allowed aria-invalid:border-red-500 aria-invalid:ring-2 aria-invalid:ring-red-400/40",
        className
      )}
      {...props}
    />
  )
}

export { Textarea }
