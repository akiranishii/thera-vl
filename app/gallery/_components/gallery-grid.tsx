"use client"

import { useState } from "react"
import { SelectSession } from "@/db/schema/sessions-schema"
import { AnimatePresence, motion } from "framer-motion"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Calendar, MessageSquare, ThumbsUp } from "lucide-react"
import { cn } from "@/lib/utils"

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
                      12
                    </span>
                    <MessageSquare className="ml-4 mr-1 h-4 w-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">
                      {/* Placeholder for message count */}
                      5
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