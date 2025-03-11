"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Beaker, CheckCircle } from "lucide-react"
import { createSampleTranscriptsAction } from "@/actions/db/transcripts-actions"
import { SelectMeeting } from "@/db/schema"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"

interface AddSampleTranscriptsProps {
  meeting: SelectMeeting
  onComplete: () => void
}

export default function AddSampleTranscripts({ meeting, onComplete }: AddSampleTranscriptsProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [rounds, setRounds] = useState(2)
  const [messagesPerRound, setMessagesPerRound] = useState(3)
  const [result, setResult] = useState<string | null>(null)
  
  const handleAddSamples = async () => {
    setIsLoading(true)
    setResult(null)
    
    try {
      const response = await createSampleTranscriptsAction(
        meeting.id,
        rounds,
        messagesPerRound
      )
      
      if (response.isSuccess) {
        setResult(`Success! Created ${response.data.created} sample transcripts`)
        // Refresh parent component
        setTimeout(() => {
          onComplete()
          setIsOpen(false)
        }, 2000)
      } else {
        setResult(`Error: ${response.message}`)
      }
    } catch (error) {
      setResult(`Error: ${error instanceof Error ? error.message : String(error)}`)
    } finally {
      setIsLoading(false)
    }
  }
  
  const meetingTitle = meeting.title || "Untitled Meeting"
  
  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button 
          variant="outline" 
          size="sm" 
          className="gap-2 mb-2"
          onClick={() => setIsOpen(true)}
        >
          <Beaker className="h-4 w-4" />
          Add Sample Transcripts
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add Sample Transcripts</DialogTitle>
          <DialogDescription>
            This will generate sample transcripts for testing purposes.
            Adding to: <span className="font-medium">{meetingTitle}</span>
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="rounds" className="text-right">
              Rounds
            </Label>
            <Input
              id="rounds"
              type="number"
              min={1}
              max={10}
              value={rounds}
              onChange={(e) => setRounds(parseInt(e.target.value))}
              className="col-span-3"
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="messagesPerRound" className="text-right">
              Messages per round
            </Label>
            <Input
              id="messagesPerRound"
              type="number"
              min={1}
              max={10}
              value={messagesPerRound}
              onChange={(e) => setMessagesPerRound(parseInt(e.target.value))}
              className="col-span-3"
            />
          </div>
          {result && (
            <div className={`p-3 rounded-md mt-2 text-sm ${result.startsWith('Success') ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
              {result.startsWith('Success') && (
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4" />
                  <span>{result}</span>
                </div>
              )}
              {!result.startsWith('Success') && (
                <span>{result}</span>
              )}
            </div>
          )}
        </div>
        <DialogFooter>
          <Button type="submit" onClick={handleAddSamples} disabled={isLoading}>
            {isLoading ? "Adding..." : "Add Samples"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
} 