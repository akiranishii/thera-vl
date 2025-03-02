"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import VoteButtons from "@/components/session/vote-buttons"
import { SelectSession } from "@/db/schema"
import { formatDistanceToNow } from "date-fns"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Eye, ExternalLink } from "lucide-react"
import Link from "next/link"

interface VoteCardProps {
  session: SelectSession
  className?: string
  onVoteChange?: (value: number) => void
  currentVoteValue?: number | null
}

export default function VoteCard({
  session,
  className,
  onVoteChange,
  currentVoteValue
}: VoteCardProps) {
  const [showFeedback, setShowFeedback] = useState(false)
  
  const isVoted = currentVoteValue !== null && currentVoteValue !== 0
  
  // Calculate date string
  const dateStr = session.createdAt
    ? formatDistanceToNow(new Date(session.createdAt), { addSuffix: true })
    : "Recently"

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-xl">{session.title}</CardTitle>
            <CardDescription className="flex items-center gap-2 mt-1">
              <span>Started {dateStr}</span>
              {!session.isPublic && (
                <Badge variant="outline" className="text-xs font-normal">
                  Private
                </Badge>
              )}
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pb-4">
        <p className="text-muted-foreground line-clamp-2">
          {session.description || "No description provided"}
        </p>
      </CardContent>
      
      <CardFooter className="flex flex-col items-stretch gap-4 pt-2 border-t">
        <div className="flex justify-between items-center w-full">
          <VoteButtons 
            sessionId={session.id}
            showCounts={true}
            size="default"
          />
          
          <div className="flex gap-2">
            <Button 
              size="sm" 
              variant="outline"
              asChild
            >
              <Link href={`/session/${session.id}`}>
                <ExternalLink className="mr-1 h-4 w-4" />
                Details
              </Link>
            </Button>
            
            <Button 
              size="sm" 
              variant="default"
              asChild
            >
              <Link href={`/session/${session.id}/live`}>
                <Eye className="mr-1 h-4 w-4" />
                View Live
              </Link>
            </Button>
          </div>
        </div>
        
        {showFeedback && isVoted && (
          <div className="text-center text-sm text-muted-foreground">
            <p>
              Thanks for your feedback! Your vote helps us improve our AI agents.
            </p>
          </div>
        )}
      </CardFooter>
    </Card>
  )
} 