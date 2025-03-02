"use server"

import SessionTranscriptSkeleton from "../loading"
import { Skeleton } from "@/components/ui/skeleton"

export default async function LiveSessionLoading() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">
          <Skeleton className="h-8 w-64" />
        </h1>
        <Skeleton className="h-6 w-16" />
      </div>
      
      <div className="rounded-lg border bg-background p-4">
        <div className="flex items-center gap-2 mb-4">
          <Skeleton className="h-5 w-20" />
          <Skeleton className="h-5 w-40" />
        </div>
        <Skeleton className="h-4 w-full max-w-md" />
      </div>
      
      <SessionTranscriptSkeleton />
    </div>
  )
} 