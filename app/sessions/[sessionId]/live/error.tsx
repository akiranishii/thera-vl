"use client"

import { useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { ArrowLeft, RefreshCcw } from "lucide-react"
import Link from "next/link"

export default function LiveSessionError({
  error,
  reset
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error)
  }, [error])

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link href={location.pathname.split("/live")[0]}>
          <Button variant="outline" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Session
          </Button>
        </Link>
        <h1 className="text-2xl font-bold">Live Updates</h1>
      </div>
      
      <Alert variant="destructive" className="my-8">
        <AlertTitle>Something went wrong</AlertTitle>
        <AlertDescription>
          <p className="mb-4">
            There was an error loading the live session data. This could be due to network issues or the session may no longer be available.
          </p>
          <Button 
            onClick={() => reset()}
            variant="outline"
            className="flex items-center gap-2"
          >
            <RefreshCcw className="h-4 w-4" />
            Try again
          </Button>
        </AlertDescription>
      </Alert>
    </div>
  )
} 