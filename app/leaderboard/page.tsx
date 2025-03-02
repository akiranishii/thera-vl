import { Suspense } from "react"
import { getTopVotedSessionsAction } from "@/actions/db/sessions-actions"
import LeaderboardList from "./_components/leaderboard-list"

export default async function LeaderboardPage() {
  return (
    <div className="container py-8 max-w-7xl">
      <Suspense fallback={<div>Loading leaderboard...</div>}>
        <LeaderboardContent />
      </Suspense>
    </div>
  )
}

async function LeaderboardContent() {
  const { isSuccess, data = [] } = await getTopVotedSessionsAction(50)
  
  return (
    <div className="pl-10">
      <LeaderboardList sessions={data} />
      
      {!isSuccess && (
        <div className="text-center mt-8 p-6 border rounded-lg bg-muted/20">
          <p className="text-muted-foreground">
            There was an issue loading the leaderboard. Please try again later.
          </p>
        </div>
      )}
      
      {isSuccess && data.length === 0 && (
        <div className="text-center mt-8 p-6 border rounded-lg bg-muted/20">
          <p className="text-muted-foreground">
            No sessions found. Be the first to create and share a session!
          </p>
        </div>
      )}
    </div>
  )
} 