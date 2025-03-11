"use server"

import { SelectMeeting, SelectTranscript } from "@/db/schema"
import { notFound } from "next/navigation"
import { getTranscriptsForMeetingAction } from "@/actions/db/transcripts-actions"
import TranscriptList from "./transcript-list"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { formatDistanceToNow } from "date-fns"
import { MessageCircle } from "lucide-react"
import { auth } from "@clerk/nextjs/server"

interface SessionTranscriptsProps {
  meetings: SelectMeeting[]
}

export default async function SessionTranscripts({
  meetings
}: SessionTranscriptsProps) {
  // Debug information
  console.log(`SessionTranscripts: Found ${meetings.length} meetings`);
  if (meetings.length > 0) {
    meetings.forEach((meeting, i) => {
      console.log(`Meeting ${i+1}: ID=${meeting.id}, Status=${meeting.status}, Rounds=${meeting.currentRound}/${meeting.maxRounds}, SessionId=${meeting.sessionId}`);
    });
  } else {
    console.log("SessionTranscripts: No meetings found. This is likely because:");
    console.log("1. The meetings don't exist in the database for this session");
    console.log("2. The meetings aren't linked to this session correctly");
    console.log("3. There are permission issues preventing access to the meetings");
  }
  
  // Check if user is owner of the session to show debug tools
  const { userId } = await auth()
  
  // Is owner check (simplified for demo - in reality, we'd check if userId matches session.userId)
  const isOwner = userId != null
  
  if (!meetings || meetings.length === 0) {
    return (
      <div className="p-12 text-center">
        <MessageCircle className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
        <h3 className="text-xl font-medium mb-2">No meetings found</h3>
        <p className="text-muted-foreground">
          This session doesn't have any meetings with transcripts yet.
        </p>
        <p className="text-xs text-muted-foreground mt-4">
          Note: If you've just completed a meeting, the data might still be processing. Try refreshing the page in a few moments.
        </p>
      </div>
    )
  }
  
  // Sort meetings by creation date (newest first)
  const sortedMeetings = [...meetings].sort(
    (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  )
  
  // Fetch transcripts for the first meeting initially
  const defaultMeetingId = sortedMeetings[0].id
  console.log(`SessionTranscripts: Attempting to fetch transcripts for meeting ${defaultMeetingId}`);
  
  try {
    const { isSuccess, data: initialTranscripts = [], message } = await getTranscriptsForMeetingAction(defaultMeetingId)
    
    // Debug information
    console.log(`TranscriptsResult: isSuccess=${isSuccess}, message=${message}, count=${initialTranscripts.length}`);
    
    if (!isSuccess) {
      // This would normally redirect to an error page, but for this case
      // we'll just show a message indicating an error fetching transcripts
      return (
        <div className="p-12 text-center">
          <h3 className="text-xl font-medium mb-2">Error fetching transcripts</h3>
          <p className="text-muted-foreground">
            There was an error retrieving the conversation history: {message}
          </p>
        </div>
      )
    }
    
    // If we have no transcripts, show a helpful message
    if (initialTranscripts.length === 0) {
      return (
        <div className="p-12 text-center">
          <MessageCircle className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
          <h3 className="text-xl font-medium mb-2">No transcripts found</h3>
          <p className="text-muted-foreground">
            This meeting exists but doesn't have any transcripts yet. 
            Meeting status: {sortedMeetings[0].status}
          </p>
          
          {isOwner && (
            <div className="mt-6">
              <p className="text-sm text-muted-foreground mb-4">
                If you're coming from Discord, the meeting may not have completed properly. Try rerunning the command in Discord to generate transcripts.
              </p>
            </div>
          )}
        </div>
      )
    }
    
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-start">
          <h2 className="text-2xl font-bold tracking-tight">Conversation History</h2>
        </div>
        
        {sortedMeetings.length > 1 ? (
          <Tabs defaultValue={defaultMeetingId} className="w-full">
            <TabsList className="mb-4 w-full h-auto flex flex-wrap">
              {sortedMeetings.map((meeting, index) => (
                <TabsTrigger 
                  key={meeting.id} 
                  value={meeting.id}
                  className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
                >
                  Meeting {index + 1}
                  <span className="ml-2 text-xs opacity-70">
                    {formatDistanceToNow(new Date(meeting.createdAt), { addSuffix: true })}
                  </span>
                  <span className="ml-2 text-xs opacity-70">
                    ({meeting.status})
                  </span>
                </TabsTrigger>
              ))}
            </TabsList>
            
            {sortedMeetings.map((meeting) => (
              <TabsContent key={meeting.id} value={meeting.id} className="border rounded-md p-4">
                <div className="mb-4">
                  <h3 className="text-lg font-medium">{meeting.title || "Untitled Meeting"}</h3>
                  {meeting.agenda && (
                    <p className="text-muted-foreground mt-1">{meeting.agenda}</p>
                  )}
                  <div className="text-xs text-muted-foreground mt-2">
                    Status: {meeting.status} | Rounds: {meeting.currentRound}/{meeting.maxRounds}
                  </div>
                </div>
                
                <TranscriptList 
                  meetingId={meeting.id} 
                  initialTranscripts={meeting.id === defaultMeetingId ? initialTranscripts : []}
                />
              </TabsContent>
            ))}
          </Tabs>
        ) : (
          <div className="border rounded-md p-4">
            <div className="mb-4">
              <h3 className="text-lg font-medium">{sortedMeetings[0].title || "Untitled Meeting"}</h3>
              {sortedMeetings[0].agenda && (
                <p className="text-muted-foreground mt-1">{sortedMeetings[0].agenda}</p>
              )}
              <div className="text-xs text-muted-foreground mt-2">
                Status: {sortedMeetings[0].status} | Rounds: {sortedMeetings[0].currentRound}/{sortedMeetings[0].maxRounds}
              </div>
            </div>
            
            <TranscriptList 
              meetingId={sortedMeetings[0].id} 
              initialTranscripts={initialTranscripts}
            />
          </div>
        )}
      </div>
    )
  } catch (error) {
    console.error("Error in SessionTranscripts:", error);
    return (
      <div className="p-12 text-center">
        <h3 className="text-xl font-medium mb-2">Error loading transcripts</h3>
        <p className="text-muted-foreground">
          An unexpected error occurred: {error instanceof Error ? error.message : String(error)}
        </p>
      </div>
    );
  }
} 