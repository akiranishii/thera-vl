"use client"

import { useEffect, useRef } from "react"
import { SelectTranscript } from "@/db/schema"
import { ScrollArea } from "@/components/ui/scroll-area"
import TranscriptMessage, { TranscriptMessageSkeleton } from "./transcript-message"
import { cn } from "@/lib/utils"
import { Skeleton } from "@/components/ui/skeleton"

interface TranscriptViewProps {
  transcripts: SelectTranscript[]
  isLoading?: boolean
  isLive?: boolean
  className?: string
  loadingCount?: number
  highlightLatest?: boolean
}

export default function TranscriptView({
  transcripts,
  isLoading = false,
  isLive = false,
  className,
  loadingCount = 3,
  highlightLatest = false
}: TranscriptViewProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current && (isLive || highlightLatest)) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [transcripts, isLive, highlightLatest])

  return (
    <div className={cn("relative w-full h-full overflow-hidden rounded-md border", className)}>
      <ScrollArea
        ref={scrollRef}
        className="h-full w-full px-4"
      >
        {transcripts.length === 0 && !isLoading ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-center text-sm text-muted-foreground">
              No messages to display
            </p>
          </div>
        ) : (
          <div className="pt-4 pb-12">
            {transcripts.map((message, index) => (
              <TranscriptMessage
                key={message.id}
                message={message}
                isLatest={highlightLatest && index === transcripts.length - 1}
              />
            ))}
            
            {isLoading && Array.from({ length: loadingCount }).map((_, i) => (
              <TranscriptMessageSkeleton key={`loading-${i}`} />
            ))}
          </div>
        )}
      </ScrollArea>
      
      {isLive && (
        <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-background to-transparent pointer-events-none" />
      )}
    </div>
  )
}

export function TranscriptViewSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="w-full h-full overflow-hidden rounded-md border">
      <div className="h-full w-full px-4 py-4">
        <Skeleton className="h-6 w-1/3 mb-6" />
        {Array.from({ length: count }).map((_, i) => (
          <TranscriptMessageSkeleton key={`skeleton-${i}`} />
        ))}
      </div>
    </div>
  )
} 