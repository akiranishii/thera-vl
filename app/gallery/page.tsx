import { Suspense } from "react"
import { auth } from "@clerk/nextjs/server"
import { getPublicSessionsAction } from "@/actions/db/sessions-actions"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import GalleryClient, { GalleryGridClient } from "./_components/gallery-client"

interface GalleryPageProps {
  searchParams: Promise<{
    page?: string
    sort?: "recent" | "popular" | "trending"
    search?: string
  }>
}

function SessionsSkeleton() {
  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="overflow-hidden rounded-lg border bg-card">
            <div className="p-6">
              <Skeleton className="h-6 w-3/4" />
              <Skeleton className="mt-3 h-4 w-1/2" />
              <div className="mt-6 space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-2/3" />
              </div>
            </div>
            <div className="flex items-center justify-between border-t bg-muted/40 p-4">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-8 w-20" />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default async function GalleryPage({ searchParams }: GalleryPageProps) {
  const params = await searchParams
  
  return (
    <div>
      <div className="mb-8">
        <GalleryClient 
          initialSort={params.sort || "recent"} 
          initialSearch={params.search || ""}
        />
      </div>
      
      <Suspense fallback={<SessionsSkeleton />}>
        <SessionsContent searchParams={params} />
      </Suspense>
    </div>
  )
}

async function SessionsContent({ searchParams }: { searchParams: GalleryPageProps["searchParams"] | Awaited<GalleryPageProps["searchParams"]> }) {
  const { userId } = await auth()
  
  // Ensure searchParams is awaited
  const params = searchParams instanceof Promise ? await searchParams : searchParams
  
  const page = params.page ? parseInt(params.page) : 1
  
  const { data, isSuccess } = await getPublicSessionsAction({
    page,
    pageSize: 12,
    sort: params.sort,
    search: params.search
  })
  
  if (!isSuccess || !data) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <h3 className="mb-2 text-xl font-semibold">Failed to load sessions</h3>
        <p className="text-muted-foreground">There was an error loading the sessions.</p>
      </div>
    )
  }
  
  const { sessions, totalPages, currentPage } = data
  
  if (sessions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <h3 className="mb-2 text-xl font-semibold">No sessions found</h3>
        <p className="text-muted-foreground">Try adjusting your filters or check back later.</p>
      </div>
    )
  }
  
  return (
    <div className="space-y-8">
      <GalleryGridClient sessions={sessions} currentUserId={userId || ""} />
      
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 py-8">
          {currentPage > 1 && (
            <Button
              variant="outline"
              size="sm"
              asChild
            >
              <a href={`/gallery?page=${currentPage - 1}&sort=${params.sort || ""}&search=${params.search || ""}`}>
                Previous
              </a>
            </Button>
          )}
          
          <span className="text-sm text-muted-foreground">
            Page {currentPage} of {totalPages}
          </span>
          
          {currentPage < totalPages && (
            <Button
              variant="outline"
              size="sm"
              asChild
            >
              <a href={`/gallery?page=${currentPage + 1}&sort=${params.sort || ""}&search=${params.search || ""}`}>
                Next
              </a>
            </Button>
          )}
        </div>
      )}
    </div>
  )
} 