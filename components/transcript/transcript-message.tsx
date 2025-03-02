"use client"

import { SelectTranscript } from "@/db/schema"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"
import { MessageCircle, User, Bot } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { format } from "date-fns"
import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardContent } from "@/components/ui/card"

interface TranscriptMessageProps {
  message: SelectTranscript
  isLatest?: boolean
  className?: string
}

export default function TranscriptMessage({
  message,
  isLatest = false,
  className
}: TranscriptMessageProps) {
  const isSystemMessage = message.role === "system"
  const isUserMessage = message.role === "user"
  const isAgentMessage = message.role === "assistant"
  
  const formattedTime = format(new Date(message.createdAt), "h:mm a")
  
  // Generate initial for avatar
  const getInitials = () => {
    if (isSystemMessage) return "S"
    if (isUserMessage) return "U"
    if (message.agentName) {
      return message.agentName.substring(0, 1).toUpperCase()
    }
    return "A"
  }

  // Determine avatar icon/image
  const getAvatar = () => {
    if (isSystemMessage) {
      return <MessageCircle className="h-4 w-4" />
    }
    if (isUserMessage) {
      return <User className="h-4 w-4" />
    }
    return <Bot className="h-4 w-4" />
  }

  return (
    <div className={cn(
      "flex gap-3 py-3",
      isLatest && "animate-in fade-in-50",
      className
    )}>
      <Avatar className={cn(
        "h-8 w-8 border",
        isSystemMessage && "bg-muted border-muted-foreground/20",
        isUserMessage && "bg-blue-100 border-blue-300",
        isAgentMessage && "bg-emerald-100 border-emerald-300"
      )}>
        <AvatarFallback>
          {getAvatar()}
        </AvatarFallback>
      </Avatar>
      
      <div className="flex-1 space-y-1.5">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium leading-none">
            {isSystemMessage && "System"}
            {isUserMessage && "User"}
            {isAgentMessage && (message.agentName || "Agent")}
          </p>
          
          {message.roundNumber !== null && message.roundNumber > 0 && (
            <Badge variant="outline" className="rounded-sm h-5 text-xs px-1">
              Round {message.roundNumber}
            </Badge>
          )}
          
          <p className="text-xs text-muted-foreground">{formattedTime}</p>
        </div>
        
        <Card className="border rounded-lg overflow-hidden">
          <CardContent className="p-3">
            <div className="whitespace-pre-wrap">
              {message.content}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export function TranscriptMessageSkeleton() {
  return (
    <div className="flex gap-3 py-3">
      <Skeleton className="h-8 w-8 rounded-full" />
      <div className="flex-1 space-y-1.5">
        <div className="flex items-center gap-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-4 w-16" />
        </div>
        <Skeleton className="h-20 w-full rounded-md" />
      </div>
    </div>
  )
} 