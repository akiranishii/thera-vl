import { Metadata } from "next"

export const metadata: Metadata = {
  title: "Leaderboard | Thera VL",
  description: "View the top-voted research and brainstorming sessions on Thera Virtual Lab"
}

export default async function LeaderboardLayout({
  children
}: {
  children: React.ReactNode
}) {
  return (
    <div>
      <div className="bg-background py-12 border-b">
        <div className="container max-w-7xl">
          <h1 className="text-4xl font-bold">Leaderboard</h1>
          <p className="text-muted-foreground mt-2">
            Discover the most popular research and brainstorming sessions as voted by our community
          </p>
        </div>
      </div>
      
      {children}
    </div>
  )
} 