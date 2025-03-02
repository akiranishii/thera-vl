import { NextRequest, NextResponse } from "next/server"
import { headers } from "next/headers"
import { auth } from "@clerk/nextjs/server"
import { db } from "@/db/db"
import { getTranscriptsForMeetingAction } from "@/actions/db/transcripts-actions"
import { getMeetingAction } from "@/actions/db/meetings-actions"
import { getSessionAction } from "@/actions/db/sessions-actions"

// Stream response encoder helper
function streamResponse(res: ReadableStream) {
  return new NextResponse(res, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      "Connection": "keep-alive",
    },
  })
}

export async function GET(
  req: NextRequest,
  { params }: { params: { meetingId: string } }
) {
  // Get the meeting ID from the URL
  const { meetingId } = params
  
  if (!meetingId) {
    return NextResponse.json(
      { error: "Meeting ID is required" },
      { status: 400 }
    )
  }

  // Authenticate the request
  const { userId } = await auth()
  
  if (!userId) {
    return NextResponse.json(
      { error: "Unauthorized" },
      { status: 401 }
    )
  }

  // Verify the meeting exists and user has access to it
  const meetingResult = await getMeetingAction(meetingId)
  
  if (!meetingResult.isSuccess || !meetingResult.data) {
    return NextResponse.json(
      { error: "Meeting not found" },
      { status: 404 }
    )
  }
  
  // Get session to check permissions
  const sessionResult = await getSessionAction(meetingResult.data.sessionId)
  
  if (!sessionResult.isSuccess || !sessionResult.data) {
    return NextResponse.json(
      { error: "Session not found" },
      { status: 404 }
    )
  }
  
  // Check if user has access to this session
  const session = sessionResult.data
  if (!session.isPublic && session.userId !== userId) {
    return NextResponse.json(
      { error: "Unauthorized to access this session" },
      { status: 403 }
    )
  }

  // Get the last event ID if available
  const lastEventId = req.headers.get("Last-Event-ID") || "0"
  const lastTimestamp = new Date(parseInt(lastEventId) || 0)

  // Set up the SSE stream
  const encoder = new TextEncoder()
  let isClosed = false
  
  const readableStream = new ReadableStream({
    start: async (controller) => {
      // Send initial data when connecting
      await sendInitialTranscripts(controller, meetingId, lastTimestamp)
      
      // Poll for updates every 2 seconds
      const intervalId = setInterval(async () => {
        if (isClosed) {
          clearInterval(intervalId)
          return
        }
        
        // Get new transcripts
        await sendTranscriptUpdates(controller, meetingId, lastTimestamp)
      }, 2000)
      
      // Handle client disconnect
      req.signal.addEventListener("abort", () => {
        isClosed = true
        clearInterval(intervalId)
        controller.close()
      })
    }
  })

  return streamResponse(readableStream)

  // Helper function to send initial transcripts
  async function sendInitialTranscripts(
    controller: ReadableStreamDefaultController,
    meetingId: string,
    since: Date
  ) {
    const transcriptsResult = await getTranscriptsForMeetingAction(meetingId)
    
    if (transcriptsResult.isSuccess && transcriptsResult.data) {
      // Filter transcripts newer than the last event ID if provided
      const transcripts = transcriptsResult.data.filter(
        t => new Date(t.createdAt) > since
      )
      
      // Send the transcripts as a JSON array
      if (transcripts.length > 0) {
        const message = `data: ${JSON.stringify(transcripts)}\n\n`
        controller.enqueue(encoder.encode(message))
        
        // Send the latest timestamp as the event ID
        const latestDate = new Date(
          Math.max(...transcripts.map(t => new Date(t.createdAt).getTime()))
        )
        const eventId = `id: ${latestDate.getTime()}\n\n`
        controller.enqueue(encoder.encode(eventId))
      } else {
        // Send an empty array if no new transcripts
        const message = `data: []\n\n`
        controller.enqueue(encoder.encode(message))
      }
    } else {
      // Send an empty array if error fetching transcripts
      const message = `data: []\n\n`
      controller.enqueue(encoder.encode(message))
    }
  }

  // Helper function to send transcript updates
  async function sendTranscriptUpdates(
    controller: ReadableStreamDefaultController,
    meetingId: string,
    since: Date
  ) {
    const transcriptsResult = await getTranscriptsForMeetingAction(meetingId)
    
    if (transcriptsResult.isSuccess && transcriptsResult.data) {
      // Filter for only new transcripts
      const newTranscripts = transcriptsResult.data.filter(
        t => new Date(t.createdAt) > since
      )
      
      // Only send updates if there are new transcripts
      if (newTranscripts.length > 0) {
        const message = `data: ${JSON.stringify(newTranscripts)}\n\n`
        controller.enqueue(encoder.encode(message))
        
        // Update the latest timestamp
        const latestDate = new Date(
          Math.max(...newTranscripts.map(t => new Date(t.createdAt).getTime()))
        )
        const eventId = `id: ${latestDate.getTime()}\n\n`
        controller.enqueue(encoder.encode(eventId))
      }
    }
  }
} 