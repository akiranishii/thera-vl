/*
<ai_context>
Contains server actions related to transcripts in the DB.
</ai_context>
*/

"use server"

import { db } from "@/db/db"
import { meetingsTable } from "@/db/schema/meetings-schema"
import { sessionsTable, SelectSession } from "@/db/schema/sessions-schema"
import { InsertTranscript, SelectTranscript, transcriptsTable } from "@/db/schema/transcripts-schema"
import { ActionState } from "@/types"
import { auth } from "@clerk/nextjs/server"
import { and, eq, desc, count, sql } from "drizzle-orm"

export async function createTranscriptAction(
  transcript: InsertTranscript
): Promise<ActionState<SelectTranscript>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // Verify the user owns the meeting's session
    const meeting = await db.query.meetings.findFirst({
      where: eq(meetingsTable.id, transcript.meetingId),
      with: {
        session: true
      }
    })

    if (!meeting) {
      return { isSuccess: false, message: "Meeting not found" }
    }

    if (meeting.session.userId !== userId) {
      return { isSuccess: false, message: "Unauthorized to add transcript to this meeting" }
    }

    const [newTranscript] = await db
      .insert(transcriptsTable)
      .values(transcript)
      .returning()

    return {
      isSuccess: true,
      message: "Transcript created successfully",
      data: newTranscript
    }
  } catch (error) {
    console.error("Error creating transcript:", error)
    return { isSuccess: false, message: "Failed to create transcript" }
  }
}

export async function getTranscriptAction(
  id: string
): Promise<ActionState<SelectTranscript>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    const transcript = await db.query.transcripts.findFirst({
      where: eq(transcriptsTable.id, id),
      with: {
        meeting: {
          with: {
            session: true
          }
        }
      }
    })

    if (!transcript) {
      return { isSuccess: false, message: "Transcript not found" }
    }

    // Check if user has access to this transcript's session
    if (!transcript.meeting.session.isPublic && transcript.meeting.session.userId !== userId) {
      return { isSuccess: false, message: "Unauthorized to access this transcript" }
    }

    return {
      isSuccess: true,
      message: "Transcript retrieved successfully",
      data: transcript
    }
  } catch (error) {
    console.error("Error getting transcript:", error)
    return { isSuccess: false, message: "Failed to get transcript" }
  }
}

export async function getTranscriptsForMeetingAction(
  meetingId: string
): Promise<ActionState<SelectTranscript[]>> {
  try {
    console.log(`getTranscriptsForMeetingAction: Starting fetch for meeting ${meetingId}`)
    const { userId } = await auth()
    
    console.log(`getTranscriptsForMeetingAction: Auth check - userId: ${userId || 'null'}`);
    
    // First fetch the meeting without the relation
    const meeting = await db.query.meetings.findFirst({
      where: eq(meetingsTable.id, meetingId)
    })

    if (!meeting) {
      console.log(`getTranscriptsForMeetingAction: Meeting not found for ID ${meetingId}`)
      return { isSuccess: false, message: "Meeting not found" }
    }
    
    // Separately fetch the session to avoid ORM relationship issues
    const session = await db.query.sessions.findFirst({
      where: eq(sessionsTable.id, meeting.sessionId)
    })
    
    if (!session) {
      console.log(`getTranscriptsForMeetingAction: Session not found for meeting ${meetingId}`)
      return { isSuccess: false, message: "Session not found for this meeting" }
    }

    // Allow access if the session is public, even without authentication
    if (!session.isPublic && userId !== session.userId) {
      console.log(`getTranscriptsForMeetingAction: User ${userId || 'anonymous'} not authorized to access meeting ${meetingId}`)
      return { isSuccess: false, message: "Unauthorized to access this meeting's transcripts" }
    }
    
    console.log(`getTranscriptsForMeetingAction: Fetching transcripts for meeting ${meetingId}, status: ${meeting.status}`)

    // Fetch all transcripts, don't filter by any status
    const transcripts = await db.query.transcripts.findMany({
      where: eq(transcriptsTable.meetingId, meetingId)
    })
    
    console.log(`getTranscriptsForMeetingAction: Found ${transcripts.length} transcripts for meeting ${meetingId}`)
    
    // If no transcripts found, log some additional debug info
    if (transcripts.length === 0) {
      console.log(`getTranscriptsForMeetingAction: No transcripts found. Meeting details:`, {
        id: meeting.id,
        title: meeting.title,
        status: meeting.status,
        currentRound: meeting.currentRound,
        maxRounds: meeting.maxRounds
      })
    }

    return {
      isSuccess: true,
      message: "Transcripts retrieved successfully",
      data: transcripts
    }
  } catch (error) {
    console.error("Error getting transcripts:", error)
    return { isSuccess: false, message: `Failed to get transcripts: ${error instanceof Error ? error.message : String(error)}` }
  }
}

export async function getSessionTranscriptCountAction(
  sessionId: string
): Promise<ActionState<number>> {
  try {
    const { userId } = await auth()
    
    // First check if the session exists and if the user has access to it
    const session = await db.query.sessions.findFirst({
      where: eq(sessionsTable.id, sessionId)
    })

    if (!session) {
      return { isSuccess: false, message: "Session not found" }
    }

    // Check if the user has access to this session
    if (!session.isPublic && userId !== session.userId) {
      return { isSuccess: false, message: "Unauthorized to access this session's transcripts" }
    }

    // Use count directly instead of complex joins
    // First, get all meeting IDs for this session
    const meetings = await db.query.meetings.findMany({
      where: eq(meetingsTable.sessionId, sessionId),
      columns: {
        id: true
      }
    })
    
    if (meetings.length === 0) {
      return {
        isSuccess: true,
        message: "No meetings found for this session",
        data: 0
      }
    }
    
    // Then count transcripts for each meeting and sum them up
    let totalCount = 0;
    for (const meeting of meetings) {
      const result = await db.select({ count: count() }).from(transcriptsTable).where(eq(transcriptsTable.meetingId, meeting.id));
      totalCount += result[0]?.count || 0;
    }

    return {
      isSuccess: true,
      message: "Transcript count retrieved successfully",
      data: totalCount
    }
  } catch (error) {
    console.error("Error getting session transcript count:", error)
    return { isSuccess: false, message: "Failed to get session transcript count" }
  }
}

export async function createSampleTranscriptsAction(
  meetingId: string,
  roundCount: number = 2,
  messagesPerRound: number = 3
): Promise<ActionState<{ created: number }>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // First fetch the meeting without the relation
    const meeting = await db.query.meetings.findFirst({
      where: eq(meetingsTable.id, meetingId)
    })

    if (!meeting) {
      return { isSuccess: false, message: "Meeting not found" }
    }
    
    // Separately fetch the session to avoid ORM relationship issues
    const session = await db.query.sessions.findFirst({
      where: eq(sessionsTable.id, meeting.sessionId)
    })
    
    if (!session) {
      return { isSuccess: false, message: "Session not found for this meeting" }
    }

    if (session.userId !== userId) {
      return { isSuccess: false, message: "Unauthorized to add sample transcripts to this meeting" }
    }

    // Create sample transcripts
    const sampleRoles = ["user", "assistant"] as const
    const sampleAgentNames = ["Dr. Smith", "Dr. Johnson", "Dr. Williams", "Dr. Brown", "Dr. Miller"]
    let created = 0

    for (let round = 1; round <= roundCount; round++) {
      for (let seq = 1; seq <= messagesPerRound; seq++) {
        // Alternate between user and assistant
        const role = sampleRoles[seq % 2]
        const agentName = role === "assistant" ? sampleAgentNames[seq % sampleAgentNames.length] : "User"
        
        const content = role === "assistant" 
          ? `This is a sample assistant message in round ${round}, sequence ${seq}.\n\nIt contains multiple paragraphs to demonstrate formatting.`
          : `This is a sample user message in round ${round}, sequence ${seq}.`

        const transcript: InsertTranscript = {
          meetingId,
          role,
          agentName,
          content,
          roundNumber: round,
          sequenceNumber: seq,
          createdAt: new Date(),
          updatedAt: new Date()
        }

        await db.insert(transcriptsTable).values(transcript)
        created++
      }
    }

    // Update the meeting to reflect the number of rounds
    await db.update(meetingsTable)
      .set({ 
        currentRound: roundCount,
        status: "completed" 
      })
      .where(eq(meetingsTable.id, meetingId))

    return {
      isSuccess: true,
      message: `Created ${created} sample transcripts`,
      data: { created }
    }
  } catch (error) {
    console.error("Error creating sample transcripts:", error)
    return { isSuccess: false, message: "Failed to create sample transcripts" }
  }
} 