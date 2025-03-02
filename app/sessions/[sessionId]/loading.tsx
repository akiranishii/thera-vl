"use server"

import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Avatar } from "@/components/ui/avatar"
import { ThumbsUp, ThumbsDown, MessageSquare, CalendarDays, Clock, Users } from "lucide-react"

export default async function SessionTranscriptSkeleton() {
  return (
    <div className="space-y-8">
      {/* Session header loading state */}
      <div>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <Skeleton className="h-10 w-3/4 max-w-md" />
          <div className="flex items-center space-x-2">
            <Skeleton className="h-6 w-20" />
            <Skeleton className="h-8 w-24" />
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-4">
          <Skeleton className="h-5 w-36" />
          <Skeleton className="h-5 w-32" />
          <Skeleton className="h-5 w-40" />
          <Skeleton className="h-5 w-36" />
        </div>

        <div className="mt-4">
          <Skeleton className="h-16 w-full" />
        </div>
      </div>

      {/* Vote buttons loading state */}
      <div className="flex justify-center py-4 gap-4">
        <Skeleton className="h-10 w-28 rounded-full" />
        <Skeleton className="h-10 w-28 rounded-full" />
      </div>

      <div className="h-px w-full bg-border" />

      {/* Transcript loading state */}
      <div className="space-y-6">
        {Array.from({ length: 5 }).map((_, i) => (
          <Card key={i} className="shadow-sm">
            <CardHeader className="p-4 flex flex-row gap-4 items-start">
              <Skeleton className="h-10 w-10 rounded-full" />
              <div className="space-y-2 flex-1">
                <Skeleton className="h-5 w-32" />
                <Skeleton className="h-4 w-24" />
              </div>
            </CardHeader>
            <CardContent className="p-4 pt-0 space-y-3">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Feedback section loading state */}
      <div className="h-px w-full bg-border" />
      
      <div className="space-y-4">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-10 w-28" />
      </div>
    </div>
  )
} 