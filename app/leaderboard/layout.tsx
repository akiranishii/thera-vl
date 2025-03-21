import { Metadata } from "next"
import Header from "@/components/header"

export const metadata: Metadata = {
  title: "Leaderboard | Thera VL",
  description: "View the top-voted therapy sessions on Thera Virtual Lab"
}

export default async function LeaderboardLayout({
  children
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <div className="bg-background py-12 border-b">
          <div className="container max-w-7xl">
            <h1 className="text-4xl font-bold">Leaderboard</h1>
            <p className="text-muted-foreground mt-2">
              Discover the most popular therapy sessions as voted by our community
            </p>
          </div>
        </div>
        
        {children}
      </main>
    </div>
  )
} 