"use client"

import { useState, useEffect } from "react"
import { SelectMeeting, SelectTranscript } from "@/db/schema"
import { getMeetingAction } from "@/actions/db/meetings-actions"
import { getTranscriptsForMeetingAction } from "@/actions/db/transcripts-actions"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { format } from "date-fns"
import { CircleOff, RefreshCw, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import RealTimeTranscript from "@/components/transcript/real-time-transcript"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

interface LiveMeetingViewProps {
  meetingId: string
  className?: string
}

export default function LiveMeetingView({ 
  meetingId,
  className
}: LiveMeetingViewProps) {
  const [meeting, setMeeting] = useState<SelectMeeting | null>(null)
  const [initialTranscripts, setInitialTranscripts] = useState<SelectTranscript[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [participantCount, setParticipantCount] = useState<number | null>(null)
  
  // Load initial meeting data and transcripts
  useEffect(() => {
    async function loadMeetingData() {
      setIsLoading(true)
      setError(null)
      
      try {
        // Fetch meeting data
        const meetingResult = await getMeetingAction(meetingId)
        
        if (!meetingResult.isSuccess || !meetingResult.data) {
          setError(meetingResult.message || "Failed to load meeting")
          setIsLoading(false)
          return
        }
        
        setMeeting(meetingResult.data)
        
        // Set a random participant count for demo purposes (1-8)
        // In a real implementation, this would come from a server
        setParticipantCount(Math.floor(Math.random() * 8) + 1)
        
        // Fetch initial transcripts
        const transcriptsResult = await getTranscriptsForMeetingAction(meetingId)
        
        if (transcriptsResult.isSuccess && transcriptsResult.data) {
          setInitialTranscripts(transcriptsResult.data)
        }
      } catch (err) {
        console.error("Error loading meeting data:", err)
        setError("An unexpected error occurred while loading the meeting")
      } finally {
        setIsLoading(false)
      }
    }
    
    loadMeetingData()
  }, [meetingId])
  
  // Helper to format date
  const formatDate = (date: Date) => {
    return format(new Date(date), "MMM d, yyyy h:mm a")
  }
  
  // Handle refresh button click
  const handleRefresh = async () => {
    setIsLoading(true)
    
    try {
      const transcriptsResult = await getTranscriptsForMeetingAction(meetingId)
      
      if (transcriptsResult.isSuccess && transcriptsResult.data) {
        setInitialTranscripts(transcriptsResult.data)
      }
    } catch (error) {
      console.error("Error refreshing transcripts:", error)
    } finally {
      setIsLoading(false)
    }
  }
  
  if (isLoading && !meeting) {
    return <LiveMeetingViewSkeleton />
  }

  if (error || !meeting) {
    return (
      <Alert variant="destructive" className="mb-4">
        <CircleOff className="h-4 w-4" />
        <AlertTitle>Error loading meeting</AlertTitle>
        <AlertDescription>
          {error || "Meeting not found or unavailable"}
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className={className}>
      <Card className="mb-4">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl mb-1">{meeting.title}</CardTitle>
              <CardDescription>
                Started {formatDate(meeting.createdAt)}
              </CardDescription>
            </div>
            
            <div className="flex items-center space-x-3">
              {participantCount !== null && (
                <Badge variant="outline" className="flex items-center gap-1">
                  <Users className="h-3.5 w-3.5" />
                  <span>{participantCount} viewers</span>
                </Badge>
              )}
              
              <Button 
                size="sm" 
                variant="outline"
                className="flex items-center gap-1"
                onClick={handleRefresh}
                disabled={isLoading}
              >
                <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          <p className="text-muted-foreground mb-2">
            {meeting.taskDescription || "No description provided."}
          </p>
          
          <div className="flex flex-wrap gap-2 mt-1">
            <Badge className="bg-blue-500">Round {meeting.currentRound || 1}</Badge>
            {meeting.status === "completed" && (
              <Badge className="bg-green-500">Completed</Badge>
            )}
            {meeting.status !== "completed" && (
              <Badge className="bg-amber-500 animate-pulse">In Progress</Badge>
            )}
          </div>
        </CardContent>
      </Card>
      
      <RealTimeTranscript
        meetingId={meetingId}
        initialTranscripts={initialTranscripts}
        className="h-[600px]"
      />
    </div>
  )
}

export function LiveMeetingViewSkeleton() {
  return (
    <div>
      <Card className="mb-4">
        <CardHeader className="pb-2">
          <div className="flex justify-between">
            <div>
              <Skeleton className="h-6 w-48 mb-2" />
              <Skeleton className="h-4 w-32" />
            </div>
            <Skeleton className="h-9 w-24" />
          </div>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-4 w-full mb-2" />
          <Skeleton className="h-4 w-2/3" />
          <div className="flex gap-2 mt-3">
            <Skeleton className="h-5 w-20" />
            <Skeleton className="h-5 w-20" />
          </div>
        </CardContent>
      </Card>
      
      <Skeleton className="h-[600px] w-full rounded-md" />
    </div>
  )
} 