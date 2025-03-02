"use server"

import { Skeleton } from "@/components/ui/skeleton"
import { Filter } from "lucide-react"

export default async function GalleryLoading() {
  return (
    <div className="space-y-8">
      <div className="mb-8">
        <div className="flex flex-wrap gap-2 items-center">
          <div className="flex flex-1 items-center space-x-2">
            <Skeleton className="h-10 w-full max-w-xs flex-1" />
          </div>
          <Skeleton className="h-10 w-24" />
          <Skeleton className="h-10 w-10 flex items-center justify-center">
            <Filter className="h-4 w-4 text-muted-foreground/30" />
          </Skeleton>
        </div>
      </div>
      
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="overflow-hidden rounded-lg border bg-card">
            <div className="p-6">
              <Skeleton className="h-6 w-3/4" />
              <Skeleton className="mt-3 h-4 w-1/2" />
              <div className="mt-6 space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-2/3" />
              </div>
            </div>
            <div className="flex items-center justify-between border-t bg-muted/40 p-4">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-8 w-20" />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
} 