"use client"

import { useState } from "react"
import { SelectMeeting } from "@/db/schema"
import AddSampleTranscripts from "./add-sample-transcripts"
import { useRouter } from "next/navigation"

interface AddSampleTranscriptsWrapperProps {
  meeting: SelectMeeting
}

export default function AddSampleTranscriptsWrapper({ meeting }: AddSampleTranscriptsWrapperProps) {
  const router = useRouter()
  
  const handleComplete = () => {
    // Refresh the page to show new transcripts
    router.refresh()
  }
  
  return (
    <AddSampleTranscripts meeting={meeting} onComplete={handleComplete} />
  )
} 