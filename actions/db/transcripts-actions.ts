/*
<ai_context>
Contains server actions related to transcripts in the DB.
</ai_context>
*/

"use server"

import { db } from "@/db/db"
import { meetingsTable } from "@/db/schema/meetings-schema"
import { sessionsTable } from "@/db/schema/sessions-schema"
import { InsertTranscript, SelectTranscript, transcriptsTable } from "@/db/schema/transcripts-schema"
import { ActionState } from "@/types"
import { auth } from "@clerk/nextjs/server"
import { and, eq, desc } from "drizzle-orm"

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
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // Verify the user has access to the meeting's session
    const meeting = await db.query.meetings.findFirst({
      where: eq(meetingsTable.id, meetingId),
      with: {
        session: true
      }
    })

    if (!meeting) {
      return { isSuccess: false, message: "Meeting not found" }
    }

    if (!meeting.session.isPublic && meeting.session.userId !== userId) {
      return { isSuccess: false, message: "Unauthorized to access this meeting's transcripts" }
    }

    const transcripts = await db.query.transcripts.findMany({
      where: eq(transcriptsTable.meetingId, meetingId),
      orderBy: [
        desc(transcriptsTable.roundNumber),
        desc(transcriptsTable.sequenceNumber)
      ]
    })

    return {
      isSuccess: true,
      message: "Transcripts retrieved successfully",
      data: transcripts
    }
  } catch (error) {
    console.error("Error getting transcripts:", error)
    return { isSuccess: false, message: "Failed to get transcripts" }
  }
} 