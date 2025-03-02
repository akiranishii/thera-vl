"use client"

import { SelectSession } from "@/db/schema"
import { getVoteCountAction } from "@/actions/db/votes-actions"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { formatDistanceToNow } from "date-fns"
import { CalendarClock, Eye, Lock, MessageSquare, ThumbsDown, ThumbsUp } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

interface SessionCardProps {
  session: SelectSession
  className?: string
  showVotes?: boolean
  showControls?: boolean
  isLink?: boolean
}

export default function SessionCard({
  session,
  className,
  showVotes = true,
  showControls = true,
  isLink = true
}: SessionCardProps) {
  const router = useRouter()
  const [votes, setVotes] = useState<{ upvotes: number; downvotes: number; total: number } | null>(null)
  const [isLoading, setIsLoading] = useState(showVotes)

  useEffect(() => {
    async function loadVotes() {
      if (showVotes) {
        setIsLoading(true)
        try {
          const result = await getVoteCountAction(session.id)
          if (result.isSuccess) {
            setVotes(result.data)
          }
        } catch (error) {
          console.error("Error loading votes:", error)
        } finally {
          setIsLoading(false)
        }
      }
    }
    loadVotes()
  }, [session.id, showVotes])

  const handleCardClick = () => {
    if (isLink) {
      router.push(`/sessions/${session.id}`)
    }
  }

  const cardContent = (
    <Card className={cn("overflow-hidden transition-all hover:shadow-md", 
      isLink && "cursor-pointer hover:border-primary/50", 
      className)}>
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <CardTitle className="line-clamp-1">{session.title}</CardTitle>
          {!session.isPublic && (
            <Badge variant="outline" className="gap-1">
              <Lock className="h-3 w-3" />
              Private
            </Badge>
          )}
        </div>
        <CardDescription className="line-clamp-2">
          {session.description || "No description provided"}
        </CardDescription>
      </CardHeader>
      <CardContent className="pb-2">
        <div className="flex items-center text-sm text-muted-foreground">
          <CalendarClock className="mr-1 h-4 w-4" />
          <span>
            {formatDistanceToNow(new Date(session.createdAt), { addSuffix: true })}
          </span>
        </div>
      </CardContent>
      <CardFooter className="flex justify-between pt-1">
        {showVotes && (
          <div className="flex items-center gap-3">
            {isLoading ? (
              <div className="flex items-center gap-2">
                <Skeleton className="h-4 w-16" />
              </div>
            ) : (
              <>
                <div className="flex items-center gap-1 text-emerald-500">
                  <ThumbsUp className="h-4 w-4" />
                  <span className="text-xs font-medium">{votes?.upvotes || 0}</span>
                </div>
                <div className="flex items-center gap-1 text-rose-500">
                  <ThumbsDown className="h-4 w-4" />
                  <span className="text-xs font-medium">{votes?.downvotes || 0}</span>
                </div>
              </>
            )}
          </div>
        )}
        {showControls && (
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              className="flex items-center gap-1"
              onClick={(e) => {
                e.stopPropagation()
                router.push(`/sessions/${session.id}/live`)
              }}
            >
              <Eye className="h-3.5 w-3.5" />
              Live
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="flex items-center gap-1"
              onClick={(e) => {
                e.stopPropagation()
                router.push(`/sessions/${session.id}`)
              }}
            >
              <MessageSquare className="h-3.5 w-3.5" />
              View
            </Button>
          </div>
        )}
      </CardFooter>
    </Card>
  )

  if (isLink) {
    return (
      <div onClick={handleCardClick}>
        {cardContent}
      </div>
    )
  }

  return cardContent
}

export function SessionCardSkeleton() {
  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-2">
        <Skeleton className="h-6 w-2/3 mb-2" />
        <Skeleton className="h-4 w-full" />
      </CardHeader>
      <CardContent className="pb-2">
        <Skeleton className="h-4 w-1/2" />
      </CardContent>
      <CardFooter className="flex justify-between pt-1">
        <div className="flex items-center gap-3">
          <Skeleton className="h-4 w-16" />
        </div>
        <div className="flex space-x-2">
          <Skeleton className="h-8 w-16" />
          <Skeleton className="h-8 w-16" />
        </div>
      </CardFooter>
    </Card>
  )
} 