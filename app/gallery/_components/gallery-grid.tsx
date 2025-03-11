"use client"

import { useState, useEffect } from "react"
import { SelectSession } from "@/db/schema/sessions-schema"
import { AnimatePresence, motion } from "framer-motion"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardFooter, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Calendar, MessageSquare, ThumbsUp } from "lucide-react"
import { cn } from "@/lib/utils"
import { formatDistanceToNow } from "date-fns"
import { getVoteCountAction } from "@/actions/db/votes-actions"
import { getSessionTranscriptCountAction } from "@/actions/db/transcripts-actions"
import Link from "next/link"

interface GalleryGridProps {
  sessions: SelectSession[]
  currentUserId: string
  className?: string
}

export default function GalleryGrid({
  sessions,
  currentUserId,
  className
}: GalleryGridProps) {
  const [hoveredId, setHoveredId] = useState<string | null>(null)
  const [sessionStats, setSessionStats] = useState<Record<string, { votes: number, messages: number }>>({})

  useEffect(() => {
    const fetchStats = async () => {
      const stats: Record<string, { votes: number, messages: number }> = {}
      
      for (const session of sessions) {
        // Fetch vote counts
        const voteResult = await getVoteCountAction(session.id)
        const votes = voteResult.isSuccess ? voteResult.data.total : 0
        
        // Fetch message counts
        const messageResult = await getSessionTranscriptCountAction(session.id)
        const messages = messageResult.isSuccess ? messageResult.data : 0
        
        stats[session.id] = { votes, messages }
      }
      
      setSessionStats(stats)
    }
    
    fetchStats()
  }, [sessions])

  return (
    <div
      className={cn(
        "grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3",
        className
      )}
    >
      <AnimatePresence>
        {sessions.map((session) => (
          <motion.div
            key={session.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="relative"
            onMouseEnter={() => setHoveredId(session.id)}
            onMouseLeave={() => setHoveredId(null)}
          >
            <Card className="h-full overflow-hidden transition-all duration-300 hover:shadow-md">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="line-clamp-1 text-lg">{session.title}</CardTitle>
                  {session.userId === currentUserId && (
                    <Badge variant="secondary" className="ml-2">Yours</Badge>
                  )}
                </div>
                <div className="flex items-center text-xs text-muted-foreground">
                  <Calendar className="mr-1 h-3 w-3" />
                  <span>
                    {new Date(session.createdAt).toLocaleDateString(undefined, {
                      month: "short",
                      day: "numeric",
                      year: "numeric"
                    })}
                  </span>
                </div>
              </CardHeader>
              <CardContent className="pb-6">
                {session.description ? (
                  <p className="line-clamp-3 text-sm text-muted-foreground">
                    {session.description}
                  </p>
                ) : (
                  <p className="text-sm italic text-muted-foreground">
                    No description provided
                  </p>
                )}
              </CardContent>
              <CardFooter className="border-t bg-muted/40 p-4">
                <div className="flex w-full items-center justify-between">
                  <div className="flex items-center">
                    <ThumbsUp className="mr-1 h-4 w-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">
                      {/* Placeholder for vote count */}
                      {sessionStats[session.id]?.votes || 0}
                    </span>
                    <MessageSquare className="ml-4 mr-1 h-4 w-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">
                      {/* Placeholder for message count */}
                      {sessionStats[session.id]?.messages || 0}
                    </span>
                  </div>
                  <Button size="sm" asChild>
                    <a href={`/sessions/${session.id}`}>View</a>
                  </Button>
                </div>
              </CardFooter>
            </Card>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
} 