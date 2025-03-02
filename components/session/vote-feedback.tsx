"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import VoteButtons from "@/components/session/vote-buttons"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/components/ui/use-toast"
import { StarIcon } from "lucide-react"

interface VoteFeedbackProps {
  sessionId: string
  className?: string
  title?: string
  description?: string
}

export default function VoteFeedback({
  sessionId,
  className,
  title = "How was this session?",
  description = "Your feedback helps us improve our AI agents and conversations."
}: VoteFeedbackProps) {
  const { toast } = useToast()
  const [feedback, setFeedback] = useState("")
  const [hasVoted, setHasVoted] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showFeedbackForm, setShowFeedbackForm] = useState(false)
  
  const handleSubmitFeedback = async () => {
    if (!feedback.trim()) return
    
    setIsSubmitting(true)
    try {
      // This is a placeholder for a future action that would save feedback
      // You would need to create this action and schema in the future
      // const result = await createFeedbackAction({
      //   sessionId,
      //   content: feedback
      // })
      
      // For now, just simulate success
      const result = { isSuccess: true }
      
      if (result.isSuccess) {
        toast({
          title: "Thank you for your feedback!",
          description: "Your comments have been submitted successfully.",
        })
        setFeedback("")
        setShowFeedbackForm(false)
      } else {
        toast({
          title: "Feedback submission failed",
          description: "There was a problem submitting your feedback. Please try again.",
          variant: "destructive"
        })
      }
    } catch (error) {
      console.error("Error submitting feedback:", error)
      toast({
        title: "Error",
        description: "An unexpected error occurred. Please try again later.",
        variant: "destructive"
      })
    } finally {
      setIsSubmitting(false)
    }
  }
  
  return (
    <Card className={cn("w-full", className)}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <StarIcon className="h-5 w-5 text-yellow-500" />
          {title}
        </CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="flex flex-col items-center gap-4">
          <VoteButtons 
            sessionId={sessionId}
            showCounts={false}
            size="lg"
          />
          
          {!showFeedbackForm && (
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => setShowFeedbackForm(true)}
              className="text-primary hover:text-primary/80"
            >
              Add written feedback
            </Button>
          )}
        </div>
        
        {showFeedbackForm && (
          <div className="space-y-3 mt-4">
            <Textarea
              placeholder="Tell us what you liked or didn't like about this session..."
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              className="min-h-[100px] resize-none"
            />
            
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setShowFeedbackForm(false)
                  setFeedback("")
                }}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              
              <Button
                variant="default"
                size="sm"
                onClick={handleSubmitFeedback}
                disabled={isSubmitting || !feedback.trim()}
              >
                Submit Feedback
              </Button>
            </div>
          </div>
        )}
      </CardContent>
      
      <CardFooter className="flex justify-center text-sm text-muted-foreground">
        <p>Your feedback remains anonymous and helps improve our systems</p>
      </CardFooter>
    </Card>
  )
} 