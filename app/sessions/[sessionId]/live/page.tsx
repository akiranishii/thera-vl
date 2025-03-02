"use server"

import { Suspense } from "react"
import { notFound, redirect } from "next/navigation"
import { auth } from "@clerk/nextjs/server"
import { getSessionAction } from "@/actions/db/sessions-actions"
import { getMeetingsAction } from "@/actions/db/meetings-actions"
import { getTranscriptsForMeetingAction } from "@/actions/db/transcripts-actions"
import RealTimeTranscript from "@/components/transcript/real-time-transcript"
import LiveIndicator from "./_components/live-indicator"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export default async function LiveSessionPage({
  params
}: {
  params: Promise<{ sessionId: string }>
}) {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LiveSessionPageContent params={params} />
    </Suspense>
  )
}

async function LiveSessionPageContent({
  params
}: {
  params: Promise<{ sessionId: string }>
}) {
  const { sessionId } = await params
  const { userId } = await auth()
  
  // Get session data
  const { isSuccess, data: session } = await getSessionAction(sessionId)
  
  if (!isSuccess || !session) {
    notFound()
  }
  
  // Check if user has access to the session
  if (!session.isPublic && session.userId !== userId) {
    redirect("/sessions")
  }
  
  // Get meetings for this session
  const { isSuccess: meetingsSuccess, data: meetings = [] } = await getMeetingsAction(sessionId)
  
  if (!meetingsSuccess || meetings.length === 0) {
    // If no meetings found, show a message
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Link href={`/sessions/${sessionId}`}>
              <Button variant="outline" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Session
              </Button>
            </Link>
            <h1 className="text-2xl font-bold">Live Updates</h1>
          </div>
          <LiveIndicator isLive={false} />
        </div>
        
        <div className="rounded-lg border bg-background p-4">
          <div className="flex items-center gap-2 mb-4">
            <h2 className="font-semibold text-lg">{session.title}</h2>
            {session.isPublic ? (
              <span className="text-xs text-muted-foreground">Public Session</span>
            ) : (
              <span className="text-xs text-muted-foreground">Private Session</span>
            )}
          </div>
          <p className="text-sm text-muted-foreground">
            {session.description || "No description provided for this session."}
          </p>
        </div>
        
        <div className="text-center p-8">
          <p className="text-muted-foreground">No meetings found for this session.</p>
        </div>
      </div>
    )
  }
  
  // Get the most recent meeting
  const latestMeeting = meetings.reduce((latest, meeting) => {
    if (!latest) return meeting
    return new Date(meeting.createdAt) > new Date(latest.createdAt) ? meeting : latest
  }, meetings[0])
  
  // Check if session is live
  // In a real app, you might have a proper field or determine by last activity
  const twoHoursAgo = new Date()
  twoHoursAgo.setHours(twoHoursAgo.getHours() - 2)
  const isLive = new Date(latestMeeting.createdAt) > twoHoursAgo
  
  // Get initial transcripts for the latest meeting
  const { data: initialTranscripts = [] } = await getTranscriptsForMeetingAction(latestMeeting.id)
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-3">
          <Link href={`/sessions/${sessionId}`}>
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Session
            </Button>
          </Link>
          <h1 className="text-2xl font-bold">Live Updates</h1>
        </div>
        <LiveIndicator isLive={isLive} />
      </div>
      
      <div className="rounded-lg border bg-background p-4">
        <div className="flex items-center gap-2 mb-4">
          <h2 className="font-semibold text-lg">{session.title}</h2>
          {session.isPublic ? (
            <span className="text-xs text-muted-foreground">Public Session</span>
          ) : (
            <span className="text-xs text-muted-foreground">Private Session</span>
          )}
        </div>
        <p className="text-sm text-muted-foreground">
          {session.description || "No description provided for this session."}
        </p>
      </div>
      
      <RealTimeTranscript
        meetingId={latestMeeting.id}
        initialTranscripts={initialTranscripts}
        className="min-h-[600px]"
        autoScroll={true}
      />
    </div>
  )
} 