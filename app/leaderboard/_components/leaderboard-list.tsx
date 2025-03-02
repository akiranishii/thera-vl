"use client"

import { useState } from "react"
import { SelectSession } from "@/db/schema"
import SessionCard from "@/components/session/session-card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AnimatePresence, motion } from "framer-motion"

interface LeaderboardListProps {
  sessions: {
    session: SelectSession
    votes: {
      upvotes: number
      downvotes: number
      total: number
    }
  }[]
  className?: string
}

export default function LeaderboardList({
  sessions,
  className
}: LeaderboardListProps) {
  const [sortBy, setSortBy] = useState<"upvotes" | "total">("total")
  
  const sortedSessions = [...sessions].sort((a, b) => {
    if (sortBy === "total") {
      return b.votes.total - a.votes.total
    } else {
      return b.votes.upvotes - a.votes.upvotes
    }
  })
  
  return (
    <div className={className}>
      <Tabs defaultValue="total" onValueChange={(value) => setSortBy(value as "upvotes" | "total")}>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Leaderboard</h2>
          <TabsList>
            <TabsTrigger value="total">Net Score</TabsTrigger>
            <TabsTrigger value="upvotes">Most Upvotes</TabsTrigger>
          </TabsList>
        </div>
        
        <TabsContent value="total" className="mt-0">
          <AnimatePresence>
            <div className="space-y-6">
              {sortedSessions.length === 0 ? (
                <p className="text-muted-foreground text-center py-12">
                  No sessions found
                </p>
              ) : (
                sortedSessions.map((item, index) => (
                  <motion.div 
                    key={item.session.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                    className="relative"
                  >
                    <div className="absolute -left-10 top-1/2 -translate-y-1/2 flex items-center justify-center w-8 h-8 rounded-full bg-muted font-bold">
                      {index + 1}
                    </div>
                    <SessionCard 
                      session={item.session}
                      showVotes={false}
                    />
                    <div className="absolute right-4 top-4 flex items-center gap-2">
                      <span className="text-sm font-bold">{item.votes.total >= 0 ? '+' : ''}{item.votes.total}</span>
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </AnimatePresence>
        </TabsContent>
        
        <TabsContent value="upvotes" className="mt-0">
          <AnimatePresence>
            <div className="space-y-6">
              {sortedSessions.length === 0 ? (
                <p className="text-muted-foreground text-center py-12">
                  No sessions found
                </p>
              ) : (
                sortedSessions.map((item, index) => (
                  <motion.div 
                    key={item.session.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                    className="relative"
                  >
                    <div className="absolute -left-10 top-1/2 -translate-y-1/2 flex items-center justify-center w-8 h-8 rounded-full bg-muted font-bold">
                      {index + 1}
                    </div>
                    <SessionCard 
                      session={item.session}
                      showVotes={false}
                    />
                    <div className="absolute right-4 top-4 flex items-center gap-2">
                      <span className="text-sm font-bold text-emerald-500">+{item.votes.upvotes}</span>
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </AnimatePresence>
        </TabsContent>
      </Tabs>
    </div>
  )
} 