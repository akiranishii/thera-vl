"use client"

import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { motion } from "framer-motion"

interface LiveIndicatorProps {
  isLive?: boolean
  className?: string
}

export default function LiveIndicator({ 
  isLive = true, 
  className 
}: LiveIndicatorProps) {
  const [isPulsing, setIsPulsing] = useState(false)
  
  // Alternate between pulsing and not pulsing
  useEffect(() => {
    if (!isLive) return
    
    const interval = setInterval(() => {
      setIsPulsing(prev => !prev)
    }, 2000)
    
    return () => clearInterval(interval)
  }, [isLive])
  
  if (!isLive) {
    return (
      <Badge 
        variant="outline" 
        className={cn(
          "text-muted-foreground border-muted-foreground/20 bg-muted",
          className
        )}
      >
        Ended
      </Badge>
    )
  }
  
  return (
    <Badge 
      variant="outline" 
      className={cn(
        "flex items-center gap-1.5 font-medium uppercase",
        "border-red-500/20 text-red-500",
        className
      )}
    >
      <motion.div 
        className="h-2 w-2 rounded-full bg-red-500"
        animate={{
          scale: isPulsing ? [1, 1.5, 1] : 1,
          opacity: isPulsing ? [1, 0.8, 1] : 1
        }}
        transition={{ 
          duration: 2,
          ease: "easeInOut",
          times: [0, 0.5, 1]
        }}
      />
      Live
    </Badge>
  )
} 