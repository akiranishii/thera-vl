"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { ThumbsDown, ThumbsUp } from "lucide-react"
import { cn } from "@/lib/utils"
import { 
  createOrUpdateVoteAction, 
  getVoteAction, 
  getVoteCountAction 
} from "@/actions/db/votes-actions"
import { useToast } from "@/components/ui/use-toast"
import { Skeleton } from "@/components/ui/skeleton"

interface VoteButtonsProps {
  sessionId: string
  className?: string
  size?: "sm" | "default" | "lg"
  showCounts?: boolean
  disabled?: boolean
}

export default function VoteButtons({
  sessionId,
  className,
  size = "default",
  showCounts = true,
  disabled = false
}: VoteButtonsProps) {
  const { toast } = useToast()
  const [currentVote, setCurrentVote] = useState<number | null>(null)
  const [voteCounts, setVoteCounts] = useState<{
    upvotes: number
    downvotes: number
    total: number
  } | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isVoting, setIsVoting] = useState(false)

  useEffect(() => {
    async function loadVoteData() {
      setIsLoading(true)
      try {
        // Load the user's vote
        const voteResult = await getVoteAction(sessionId)
        if (voteResult.isSuccess && voteResult.data) {
          setCurrentVote(voteResult.data.value)
        } else {
          setCurrentVote(null)
        }

        // Load vote counts
        if (showCounts) {
          const countsResult = await getVoteCountAction(sessionId)
          if (countsResult.isSuccess) {
            setVoteCounts(countsResult.data)
          }
        }
      } catch (error) {
        console.error("Error loading vote data:", error)
      } finally {
        setIsLoading(false)
      }
    }
    
    loadVoteData()
  }, [sessionId, showCounts])

  const handleVote = async (value: number) => {
    // If already voting or disabled, do nothing
    if (isVoting || disabled) return
    
    // If clicking on same vote value, remove vote (toggle)
    const newValue = currentVote === value ? 0 : value
    
    setIsVoting(true)
    try {
      const result = await createOrUpdateVoteAction(sessionId, newValue)
      
      if (result.isSuccess) {
        // Update local state for immediate feedback
        setCurrentVote(newValue)
        
        // Update vote counts for immediate feedback
        if (showCounts && voteCounts) {
          const oldValue = currentVote || 0
          
          // Calculate the difference for this vote change
          const difference = newValue - oldValue
          
          // Update upvotes/downvotes counts based on the change
          const newCounts = { ...voteCounts }
          
          if (oldValue === 1) newCounts.upvotes--
          if (oldValue === -1) newCounts.downvotes--
          if (newValue === 1) newCounts.upvotes++
          if (newValue === -1) newCounts.downvotes++
          
          // Update total
          newCounts.total += difference
          
          setVoteCounts(newCounts)
        }
      } else {
        toast({
          title: "Vote failed",
          description: result.message,
          variant: "destructive"
        })
      }
    } catch (error) {
      console.error("Error submitting vote:", error)
      toast({
        title: "Vote failed",
        description: "An unexpected error occurred while voting",
        variant: "destructive"
      })
    } finally {
      setIsVoting(false)
    }
  }

  // Button size styles
  const sizeStyles = {
    sm: "h-8 px-2 gap-1 text-xs",
    default: "h-9 px-3 gap-1.5",
    lg: "h-10 px-4 gap-2"
  }

  // Icon size based on button size
  const iconSize = {
    sm: "h-3.5 w-3.5",
    default: "h-4 w-4",
    lg: "h-5 w-5"
  }

  if (isLoading) {
    return (
      <div className={cn("flex items-center gap-2", className)}>
        <Skeleton className="h-9 w-20" />
        <Skeleton className="h-9 w-20" />
      </div>
    )
  }

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <Button
        variant="outline"
        size="icon"
        className={cn(
          "flex items-center border-muted-foreground/20", 
          sizeStyles[size],
          currentVote === 1 && "bg-emerald-50 border-emerald-200 text-emerald-600",
          (isVoting || disabled) && "opacity-70 pointer-events-none"
        )}
        disabled={isVoting || disabled}
        onClick={() => handleVote(1)}
      >
        <ThumbsUp className={iconSize[size]} />
        {showCounts && <span>{voteCounts?.upvotes || 0}</span>}
      </Button>
      
      <Button
        variant="outline"
        size="icon"
        className={cn(
          "flex items-center border-muted-foreground/20", 
          sizeStyles[size],
          currentVote === -1 && "bg-rose-50 border-rose-200 text-rose-600",
          (isVoting || disabled) && "opacity-70 pointer-events-none"
        )}
        disabled={isVoting || disabled}
        onClick={() => handleVote(-1)}
      >
        <ThumbsDown className={iconSize[size]} />
        {showCounts && <span>{voteCounts?.downvotes || 0}</span>}
      </Button>
    </div>
  )
} 