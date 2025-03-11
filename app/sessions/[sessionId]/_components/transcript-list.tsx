"use client"

import { useEffect, useState } from "react"
import { SelectTranscript } from "@/db/schema"
import { getTranscriptsForMeetingAction } from "@/actions/db/transcripts-actions"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { format } from "date-fns"
import { MessageSquare, User, Bot, RefreshCw, Info } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"
import { Skeleton } from "@/components/ui/skeleton"

interface TranscriptListProps {
  meetingId: string
  initialTranscripts?: SelectTranscript[]
  className?: string
}

export default function TranscriptList({
  meetingId,
  initialTranscripts = [],
  className
}: TranscriptListProps) {
  const [transcripts, setTranscripts] = useState<SelectTranscript[]>(initialTranscripts)
  const [isLoading, setIsLoading] = useState(initialTranscripts.length === 0)
  const [error, setError] = useState<string | null>(null)
  const [debugInfo, setDebugInfo] = useState<string>("")

  const fetchTranscripts = async () => {
    if (!meetingId) return
    
    setIsLoading(true)
    setError(null)
    
    try {
      console.log(`TranscriptList: Fetching transcripts for meetingId ${meetingId}`)
      const result = await getTranscriptsForMeetingAction(meetingId)
      
      if (!result.isSuccess) {
        console.error(`TranscriptList: Failed to fetch transcripts: ${result.message}`)
        setError(result.message || "Failed to load transcripts")
        setDebugInfo(`API Error: ${result.message}`)
        return
      }
      
      const fetchedTranscripts = result.data || []
      console.log(`TranscriptList: Fetched ${fetchedTranscripts.length} transcripts`)
      
      if (fetchedTranscripts.length === 0) {
        setDebugInfo("API returned success but zero transcripts")
      } else {
        setDebugInfo(`${fetchedTranscripts.length} transcripts found`)
      }
      
      setTranscripts(fetchedTranscripts)
    } catch (err) {
      console.error("Error fetching transcripts:", err)
      setError("An unexpected error occurred")
      setDebugInfo(`Exception: ${err instanceof Error ? err.message : String(err)}`)
    } finally {
      setIsLoading(false)
    }
  }
  
  // Fetch transcripts if we don't have initial data
  useEffect(() => {
    if (initialTranscripts.length === 0) {
      fetchTranscripts()
    } else {
      setDebugInfo(`Using ${initialTranscripts.length} initial transcripts`)
    }
  }, [meetingId, initialTranscripts.length])
  
  // Sort transcripts by round number and sequence
  const sortedTranscripts = [...transcripts].sort((a, b) => {
    // First sort by round number
    const roundA = a.roundNumber ?? 0;
    const roundB = b.roundNumber ?? 0;
    if (roundA !== roundB) {
      return roundA - roundB;
    }
    // Then by sequence number within the same round
    const seqA = a.sequenceNumber ?? 0;
    const seqB = b.sequenceNumber ?? 0;
    return seqA - seqB;
  })
  
  // Group transcripts by round
  const groupedTranscripts: Record<number, SelectTranscript[]> = {}
  sortedTranscripts.forEach(transcript => {
    const round = transcript.roundNumber || 0
    if (!groupedTranscripts[round]) {
      groupedTranscripts[round] = []
    }
    groupedTranscripts[round].push(transcript)
  })
  
  // Get rounds in order
  const rounds = Object.keys(groupedTranscripts).map(Number).sort((a, b) => a - b)
  
  if (isLoading) {
    return <TranscriptListSkeleton />
  }
  
  if (error) {
    return (
      <div className="p-6 text-center">
        <p className="text-red-500 mb-3">{error}</p>
        <p className="text-xs text-muted-foreground mb-3">Debug: {debugInfo}</p>
        <Button 
          variant="outline" 
          onClick={fetchTranscripts}
          className="mx-auto"
        >
          <RefreshCw className="h-3.5 w-3.5 mr-2" />
          Try Again
        </Button>
      </div>
    )
  }
  
  if (sortedTranscripts.length === 0) {
    return (
      <div className="p-6 text-center">
        <p className="text-muted-foreground mb-3">No conversation history found</p>
        <p className="text-xs text-muted-foreground mb-3">Debug: {debugInfo}</p>
        <Button 
          variant="outline" 
          onClick={fetchTranscripts}
          className="mx-auto flex items-center gap-2"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Refresh
        </Button>
      </div>
    )
  }
  
  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex justify-between items-center">
        <div className="text-sm text-muted-foreground flex items-center gap-2">
          {sortedTranscripts.length} message{sortedTranscripts.length !== 1 ? "s" : ""}
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => alert(debugInfo)}
            className="h-6 w-6 p-0"
          >
            <Info className="h-3.5 w-3.5 text-muted-foreground" />
          </Button>
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={fetchTranscripts}
          className="gap-1"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Refresh
        </Button>
      </div>
      
      <ScrollArea className="h-[calc(100vh-350px)] min-h-[400px] border rounded-md">
        <div className="p-4">
          {rounds.map(round => (
            <div key={round} className="mb-8 last:mb-0">
              {round > 0 && (
                <div className="mb-4 flex items-center gap-2">
                  <Badge variant="outline" className="rounded-sm px-2 py-0.5">
                    Round {round}
                  </Badge>
                  <Separator className="flex-1" />
                </div>
              )}
              
              <div className="space-y-4">
                {groupedTranscripts[round].map((transcript) => (
                  <Card 
                    key={transcript.id} 
                    className={cn(
                      "overflow-hidden transition-all",
                      transcript.role === "assistant" ? "border-l-4 border-l-primary" : ""
                    )}
                  >
                    <CardContent className="p-4">
                      <div className="flex gap-3">
                        <Avatar className="h-8 w-8">
                          <AvatarFallback className={cn(
                            transcript.role === "assistant" ? "bg-primary text-primary-foreground" : "bg-muted"
                          )}>
                            {transcript.role === "assistant" ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                          </AvatarFallback>
                        </Avatar>
                        
                        <div className="space-y-1.5 flex-1">
                          <div className="flex items-center gap-1.5">
                            <span className="font-semibold text-sm">
                              {transcript.agentName || (transcript.role === "assistant" ? "AI Assistant" : "User")}
                            </span>
                            <span className="text-xs text-muted-foreground">
                              {format(new Date(transcript.createdAt), "MMM d, h:mm a")}
                            </span>
                            <span className="text-xs text-muted-foreground">
                              (Seq: {transcript.sequenceNumber})
                            </span>
                          </div>
                          
                          <div className="space-y-2">
                            {transcript.content.split('\n').map((paragraph, i) => (
                              <p key={i} className={cn(
                                paragraph.trim() === '' ? 'h-4' : '',
                                "text-sm"
                              )}>
                                {paragraph}
                              </p>
                            ))}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  )
}

export function TranscriptListSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div className="w-24 h-5">
          <Skeleton className="h-full w-full" />
        </div>
        <div className="w-20 h-8">
          <Skeleton className="h-full w-full" />
        </div>
      </div>
      
      <div className="border rounded-md p-4 space-y-4">
        {Array.from({ length: count }).map((_, i) => (
          <div key={i} className="flex gap-3">
            <Skeleton className="h-8 w-8 rounded-full" />
            <div className="space-y-2 flex-1">
              <div className="flex gap-2">
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-4 w-32" />
              </div>
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
} 