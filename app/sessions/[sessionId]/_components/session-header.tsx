"use client"

import { useState } from "react"
import { SelectSession } from "@/db/schema/sessions-schema"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  CalendarDays, 
  MessageCircle, 
  Clock, 
  Users, 
  ClipboardCopy, 
  CheckCircle,
  Lock,
  Globe
} from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface SessionHeaderProps {
  session: SelectSession
  messageCount: number
  totalRunTime?: string
  agentCount?: number
  className?: string
}

export default function SessionHeader({
  session,
  messageCount,
  totalRunTime = "Unknown",
  agentCount = 0,
  className
}: SessionHeaderProps) {
  const [copied, setCopied] = useState(false)
  
  const handleCopyLink = () => {
    navigator.clipboard.writeText(window.location.href)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  
  // Format the date nicely
  const formattedDate = new Date(session.createdAt).toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric"
  })
  
  return (
    <div className={className}>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <h1 className="text-3xl font-bold tracking-tight">
          {session.title}
        </h1>
        
        <div className="flex items-center space-x-2">
          <Badge variant={session.isPublic ? "default" : "secondary"}>
            {session.isPublic ? (
              <>
                <Globe className="mr-1 h-3 w-3" /> Public
              </>
            ) : (
              <>
                <Lock className="mr-1 h-3 w-3" /> Private
              </>
            )}
          </Badge>
          
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="h-8 gap-1" 
                  onClick={handleCopyLink}
                >
                  {copied ? (
                    <>
                      <CheckCircle className="h-3.5 w-3.5" />
                      <span>Copied</span>
                    </>
                  ) : (
                    <>
                      <ClipboardCopy className="h-3.5 w-3.5" />
                      <span>Copy Link</span>
                    </>
                  )}
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                Copy link to this session
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>
      
      <div className="mt-4 flex flex-wrap gap-4 text-sm text-muted-foreground">
        <div className="flex items-center">
          <CalendarDays className="mr-2 h-4 w-4" />
          <span>{formattedDate}</span>
        </div>
        
        {agentCount > 0 && (
          <div className="flex items-center">
            <Users className="mr-2 h-4 w-4" />
            <span>{agentCount} agent{agentCount !== 1 ? "s" : ""}</span>
          </div>
        )}
        
        <div className="flex items-center">
          <MessageCircle className="mr-2 h-4 w-4" />
          <span>{messageCount} message{messageCount !== 1 ? "s" : ""}</span>
        </div>
        
        {totalRunTime && (
          <div className="flex items-center">
            <Clock className="mr-2 h-4 w-4" />
            <span>Run time: {totalRunTime}</span>
          </div>
        )}
      </div>
      
      {session.description && (
        <div className="mt-4 text-muted-foreground">
          <p className="whitespace-pre-wrap">{session.description}</p>
        </div>
      )}
    </div>
  )
} 