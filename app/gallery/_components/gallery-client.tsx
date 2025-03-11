"use client"

import dynamic from "next/dynamic"
import { SelectSession } from "@/db/schema/sessions-schema"

// Dynamically import client components
const GalleryFilters = dynamic(() => import("./gallery-filters"), { ssr: false })
const GalleryGrid = dynamic(() => import("./gallery-grid"), { ssr: false })

interface GalleryClientProps {
  initialSort: string
  initialSearch: string
}

export default function GalleryClient({
  initialSort,
  initialSearch
}: GalleryClientProps) {
  return (
    <GalleryFilters
      initialSort={initialSort}
      initialSearch={initialSearch}
    />
  )
}

interface GalleryGridClientProps {
  sessions: SelectSession[]
  currentUserId: string
  className?: string
}

export function GalleryGridClient({
  sessions,
  currentUserId,
  className
}: GalleryGridClientProps) {
  return (
    <GalleryGrid
      sessions={sessions}
      currentUserId={currentUserId}
      className={className}
    />
  )
} 