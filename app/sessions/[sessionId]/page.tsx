"use server"

import { notFound } from "next/navigation"
import { Suspense } from "react"
import { auth } from "@clerk/nextjs/server"
import { Separator } from "@/components/ui/separator"
import { getSessionAction } from "@/actions/db/sessions-actions"
import { getMeetingsAction } from "@/actions/db/meetings-actions" 
import { Button } from "@/components/ui/button"
import { Eye } from "lucide-react"
import Link from "next/link"
import SessionHeader from "./_components/session-header"
import SessionTranscriptSkeleton from "./loading"

interface SessionTranscriptPageProps {
  params: { sessionId: string }
}

export default async function SessionTranscriptPage({
  params
}: SessionTranscriptPageProps) {
  const { userId } = await auth()
  
  return (
    <div className="container py-8 max-w-7xl">
      <Suspense fallback={<SessionTranscriptSkeleton />}>
        <SessionContent sessionId={params.sessionId} userId={userId} />
      </Suspense>
    </div>
  )
}

async function SessionContent({
  sessionId,
  userId
}: {
  sessionId: string
  userId: string | null
}) {
  // Get session data
  const sessionResponse = await getSessionAction(sessionId)
  
  if (!sessionResponse.isSuccess || !sessionResponse.data) {
    notFound()
  }
  
  const session = sessionResponse.data
  
  // Check if user can access this session
  const canAccess = session.isPublic || (userId && session.userId === userId)
  
  if (!canAccess) {
    notFound()
  }
  
  // Get meetings for this session to determine if live viewing is available
  const { isSuccess: meetingsSuccess, data: meetings = [] } = await getMeetingsAction(sessionId)
  
  // Check if session is potentially live (has meetings and recent activity)
  const hasLivePotential = meetingsSuccess && meetings.length > 0
  
  // If we have meetings, check if the latest one is recent enough to be considered live
  let isRecentActivity = false
  if (hasLivePotential) {
    const latestMeeting = meetings.reduce((latest, meeting) => {
      if (!latest) return meeting
      return new Date(meeting.createdAt) > new Date(latest.createdAt) ? meeting : latest
    }, meetings[0])
    
    const twoHoursAgo = new Date()
    twoHoursAgo.setHours(twoHoursAgo.getHours() - 2)
    isRecentActivity = new Date(latestMeeting.createdAt) > twoHoursAgo
  }
  
  const isOwner = userId === session.userId
  
  return (
    <div className="space-y-8">
      <div className="flex justify-between items-start">
        <SessionHeader 
          session={session} 
          messageCount={0}
          totalRunTime="Unknown"
          agentCount={0}
          className=""
        />
        
        {(hasLivePotential && isRecentActivity) && (
          <Link href={`/sessions/${sessionId}/live`}>
            <Button variant="outline" className="flex items-center gap-2">
              <Eye className="h-4 w-4" />
              Watch Live
            </Button>
          </Link>
        )}
      </div>
      
      <div className="flex justify-center py-4">
        <div className="flex gap-4">
          <button disabled className="rounded-full px-4 py-2 bg-primary text-primary-foreground">
            Upvote (0)
          </button>
          <button disabled className="rounded-full px-4 py-2 bg-muted text-muted-foreground">
            Downvote (0)
          </button>
        </div>
      </div>
      
      <Separator className="my-6" />
      
      <div className="space-y-6">
        <div className="text-center py-12">
          <h2 className="text-xl font-medium">Messages will be displayed here</h2>
          <p className="text-muted-foreground mt-2">
            Implementation of messages functionality is coming soon.
          </p>
        </div>
      </div>
      
      {userId && !isOwner && (
        <>
          <Separator className="my-6" />
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Provide Feedback</h3>
            <textarea 
              disabled
              className="w-full h-32 p-3 rounded-md border border-input bg-background"
              placeholder="Feedback functionality coming soon..."
            />
            <button disabled className="rounded px-4 py-2 bg-primary text-primary-foreground">
              Submit Feedback
            </button>
          </div>
        </>
      )}
    </div>
  )
} 