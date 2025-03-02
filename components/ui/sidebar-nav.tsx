"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

interface SidebarNavProps {
  items: {
    href: string
    title: string
    disabled?: boolean
    external?: boolean
  }[]
  className?: string
}

export function SidebarNav({ items, className }: SidebarNavProps) {
  const pathname = usePathname()
  const searchParams = typeof window !== "undefined" 
    ? new URLSearchParams(window.location.search)
    : new URLSearchParams()
  
  const currentSort = searchParams.get("sort")
  
  const isActive = (href: string) => {
    // Extract path and query params
    const [path, query] = href.split("?")
    
    // Check if current pathname matches the path
    const pathMatches = path === pathname
    
    // If there's no query in the href, just check the path
    if (!query) return pathMatches && !currentSort
    
    // If there is a query, check if it matches current sort
    const hrefParams = new URLSearchParams(query)
    const hrefSort = hrefParams.get("sort")
    
    return pathMatches && hrefSort === currentSort
  }

  return (
    <nav className={cn("flex space-y-1 flex-col", className)}>
      {items.map((item) => {
        if (item.disabled) {
          return (
            <span
              key={item.href}
              className="group flex w-full cursor-not-allowed items-center rounded-md border border-transparent px-3 py-2 text-muted-foreground hover:text-muted-foreground"
            >
              {item.title}
            </span>
          )
        }
        
        if (item.external) {
          return (
            <a
              key={item.href}
              href={item.href}
              target="_blank"
              rel="noreferrer"
              className="group flex w-full items-center rounded-md border border-transparent px-3 py-2 hover:bg-muted hover:text-foreground"
            >
              {item.title}
            </a>
          )
        }
        
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "group flex w-full items-center rounded-md border border-transparent px-3 py-2 hover:bg-muted hover:text-foreground",
              isActive(item.href)
                ? "bg-muted font-medium text-foreground"
                : "text-muted-foreground"
            )}
          >
            {item.title}
          </Link>
        )
      })}
    </nav>
  )
} 