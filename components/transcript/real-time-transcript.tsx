"use client"

import { useEffect, useState, useCallback, useRef } from "react"
import { SelectTranscript } from "@/db/schema"
import TranscriptView from "@/components/transcript/transcript-view"
import { useToast } from "@/components/ui/use-toast"
import { AlertCircle } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

interface RealTimeTranscriptProps {
  meetingId: string
  initialTranscripts?: SelectTranscript[]
  className?: string
  autoScroll?: boolean
}

export default function RealTimeTranscript({
  meetingId,
  initialTranscripts = [],
  className,
  autoScroll = true
}: RealTimeTranscriptProps) {
  const { toast } = useToast()
  const [transcripts, setTranscripts] = useState<SelectTranscript[]>(initialTranscripts)
  const [isLoading, setIsLoading] = useState(true)
  const [isConnected, setIsConnected] = useState(false)
  const [hasError, setHasError] = useState(false)
  const eventSourceRef = useRef<EventSource | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttempts = useRef(0)
  const MAX_RECONNECT_ATTEMPTS = 5
  const RECONNECT_DELAY_MS = 3000

  // Sort transcripts by creation time
  const sortedTranscripts = [...transcripts].sort(
    (a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
  )

  // Function to connect to the SSE endpoint
  const connectToStream = useCallback(() => {
    if (!meetingId) return
    
    // Close existing connection if any
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
    
    setIsLoading(true)
    setHasError(false)
    
    try {
      // Create new EventSource connection
      const eventSource = new EventSource(`/api/transcripts/${meetingId}/stream`)
      eventSourceRef.current = eventSource
      
      // Handle connection open
      eventSource.onopen = () => {
        setIsConnected(true)
        setIsLoading(false)
        reconnectAttempts.current = 0
      }
      
      // Handle messages
      eventSource.addEventListener("message", (event) => {
        try {
          const newTranscripts = JSON.parse(event.data) as SelectTranscript[]
          
          if (newTranscripts && newTranscripts.length > 0) {
            setTranscripts(prev => {
              // Merge new transcripts with existing ones (avoiding duplicates by ID)
              const existingIds = new Set(prev.map(t => t.id))
              const uniqueNewTranscripts = newTranscripts.filter(t => !existingIds.has(t.id))
              
              return [...prev, ...uniqueNewTranscripts]
            })
          }
        } catch (error) {
          console.error("Error parsing transcript data:", error)
        }
      })
      
      // Handle errors
      eventSource.onerror = (error) => {
        console.error("SSE connection error:", error)
        
        // Connection failed
        setIsConnected(false)
        
        // Close the connection
        eventSource.close()
        eventSourceRef.current = null
        
        // Attempt to reconnect if under max attempts
        if (reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttempts.current++
          
          // Show attempting to reconnect toast
          toast({
            title: "Connection lost",
            description: `Attempting to reconnect (${reconnectAttempts.current}/${MAX_RECONNECT_ATTEMPTS})...`,
            duration: 3000
          })
          
          // Set timeout for reconnection
          reconnectTimeoutRef.current = setTimeout(() => {
            connectToStream()
          }, RECONNECT_DELAY_MS)
        } else {
          // Max reconnect attempts reached
          setHasError(true)
          setIsLoading(false)
          
          toast({
            title: "Connection failed",
            description: "Could not connect to real-time updates. Please refresh the page to try again.",
            variant: "destructive",
            duration: 5000
          })
        }
      }
    } catch (error) {
      console.error("Error setting up SSE connection:", error)
      setHasError(true)
      setIsLoading(false)
    }
  }, [meetingId, toast])

  // Connect on initial load
  useEffect(() => {
    connectToStream()
    
    // Cleanup function
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
      
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
    }
  }, [connectToStream])

  // Show error state
  if (hasError) {
    return (
      <Alert variant="destructive" className="mb-4">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Connection Error</AlertTitle>
        <AlertDescription>
          Could not connect to real-time updates. Please refresh the page to try again.
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className={className}>
      <TranscriptView
        transcripts={sortedTranscripts}
        isLoading={isLoading && transcripts.length === 0}
        isLive={isConnected}
        highlightLatest={autoScroll}
      />
      
      {isConnected && (
        <div className="mt-2 text-xs text-center text-muted-foreground animate-pulse">
          Live updates connected
        </div>
      )}
    </div>
  )
} 