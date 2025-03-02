import { SessionCardSkeleton } from "@/components/session/session-card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"

export default function LeaderboardLoading() {
  return (
    <div className="container py-8 max-w-7xl">
      <Tabs defaultValue="total">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Leaderboard</h2>
          <TabsList>
            <TabsTrigger value="total" disabled>Net Score</TabsTrigger>
            <TabsTrigger value="upvotes" disabled>Most Upvotes</TabsTrigger>
          </TabsList>
        </div>
        
        <TabsContent value="total" className="mt-0">
          <div className="space-y-6 pl-10">
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="relative">
                <div className="absolute -left-10 top-1/2 -translate-y-1/2 flex items-center justify-center w-8 h-8 rounded-full bg-muted">
                  <Skeleton className="h-4 w-4" />
                </div>
                <SessionCardSkeleton />
              </div>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
} 