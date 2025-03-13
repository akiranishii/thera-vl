/*
<ai_context>
Contains server actions related to transcripts in the DB.
</ai_context>
*/

"use server"

import { db } from "@/db/db"
import { meetingsTable, SelectMeeting, MeetingWithSession } from "@/db/schema/meetings-schema"
import { sessionsTable, SelectSession } from "@/db/schema/sessions-schema"
import { InsertTranscript, SelectTranscript, transcriptsTable } from "@/db/schema/transcripts-schema"
import { ActionState } from "@/types"
import { auth } from "@clerk/nextjs/server"
import { and, eq, desc, count, sql } from "drizzle-orm"

// Define additional types for Drizzle query results that include relations
interface TranscriptWithMeeting extends SelectTranscript {
  meeting: MeetingWithSession;
}

export async function createTranscriptAction(
  transcript: InsertTranscript
): Promise<ActionState<SelectTranscript>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // Get the meeting first to verify ownership
    const meeting = await db.query.meetings.findFirst({
      where: eq(meetingsTable.id, transcript.meetingId),
    });

    if (!meeting) {
      return { isSuccess: false, message: "Meeting not found" }
    }
    
    // Get the session to check permissions
    const session = await db.query.sessions.findFirst({
      where: eq(sessionsTable.id, meeting.sessionId)
    });
    
    if (!session) {
      return { isSuccess: false, message: "Session not found" }
    }

    if (session.userId !== userId) {
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

    // Get the transcript
    const transcript = await db.query.transcripts.findFirst({
      where: eq(transcriptsTable.id, id),
      with: {
        meeting: true
      }
    });

    if (!transcript) {
      return { isSuccess: false, message: "Transcript not found" }
    }
    
    // Get the meeting's session to check permissions
    const meeting = await db.query.meetings.findFirst({
      where: eq(meetingsTable.id, transcript.meeting.id),
      with: {
        session: true
      }
    });
    
    if (!meeting) {
      return { isSuccess: false, message: "Meeting not found" }
    }

    // Check if user has access to this transcript's session
    if (!meeting.session.isPublic && meeting.session.userId !== userId) {
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
    console.log("getTranscriptsForMeetingAction: starting, meeting ID:", meetingId);
    const { userId } = await auth()
    
    // First fetch the meeting without the session relation to avoid ORM issues
    const meeting = await db.query.meetings.findFirst({
      where: eq(meetingsTable.id, meetingId)
    });

    if (!meeting) {
      console.log("getTranscriptsForMeetingAction: Meeting not found");
      return { isSuccess: false, message: "Meeting not found" }
    }

    // Then fetch the session separately
    const session = await db.query.sessions.findFirst({
      where: eq(sessionsTable.id, meeting.sessionId)
    });

    if (!session) {
      console.log("getTranscriptsForMeetingAction: Session not found");
      return { isSuccess: false, message: "Session not found" }
    }

    // Check if user has access to this session
    if (!session.isPublic && (!userId || session.userId !== userId)) {
      console.log("getTranscriptsForMeetingAction: Unauthorized, user ID:", userId, "session public:", session.isPublic, "session user ID:", session.userId);
      return { isSuccess: false, message: "Unauthorized to access transcripts for this meeting" }
    }

    const transcripts = await db.query.transcripts.findMany({
      where: eq(transcriptsTable.meetingId, meetingId),
      orderBy: [desc(transcriptsTable.createdAt)]
    })

    console.log(`getTranscriptsForMeetingAction: Found ${transcripts.length} transcripts`);
    return {
      isSuccess: true,
      message: "Transcripts retrieved successfully",
      data: transcripts
    }
  } catch (error) {
    console.error("Error getting transcripts for meeting:", error)
    return { isSuccess: false, message: "Failed to get transcripts for meeting" }
  }
}

export async function getSessionTranscriptCountAction(
  sessionId: string
): Promise<ActionState<number>> {
  try {
    console.log("getSessionTranscriptCountAction: Starting for session:", sessionId);
    const { userId } = await auth();
    
    // Check if the session exists and if the user has access to it
    const session = await db.query.sessions.findFirst({
      where: eq(sessionsTable.id, sessionId)
    });
    
    if (!session) {
      console.log("getSessionTranscriptCountAction: Session not found");
      return { isSuccess: false, message: "Session not found" };
    }
    
    // Check user access
    if (!session.isPublic && (!userId || session.userId !== userId)) {
      console.log("getSessionTranscriptCountAction: Unauthorized access attempt");
      return { isSuccess: false, message: "Unauthorized to access this session's transcript count" };
    }
    
    // Get all meeting IDs for this session
    const meetings = await db.query.meetings.findMany({
      where: eq(meetingsTable.sessionId, sessionId),
      columns: { id: true }
    });
    
    console.log(`getSessionTranscriptCountAction: Found ${meetings.length} meetings`);
    
    if (meetings.length === 0) {
      return { 
        isSuccess: true, 
        message: "No meetings found for this session",
        data: 0
      };
    }
    
    // Count transcripts for each meeting and sum them up
    let totalCount = 0;
    for (const meeting of meetings) {
      const result = await db.select({ 
        count: count() 
      }).from(transcriptsTable)
        .where(eq(transcriptsTable.meetingId, meeting.id));
      
      totalCount += Number(result[0].count || 0);
    }
    
    console.log(`getSessionTranscriptCountAction: Total transcript count: ${totalCount}`);
    
    return {
      isSuccess: true,
      message: "Transcript count retrieved successfully",
      data: totalCount
    };
  } catch (error) {
    console.error("Error getting session transcript count:", error);
    return { isSuccess: false, message: "Failed to get session transcript count" };
  }
}

export async function createSampleTranscriptsAction(
  meetingId: string
): Promise<ActionState<SelectTranscript[]>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // First fetch the meeting without the session relation
    const meeting = await db.query.meetings.findFirst({
      where: eq(meetingsTable.id, meetingId)
    });

    if (!meeting) {
      return { isSuccess: false, message: "Meeting not found" }
    }

    // Then fetch the session separately
    const session = await db.query.sessions.findFirst({
      where: eq(sessionsTable.id, meeting.sessionId)
    });

    if (!session) {
      return { isSuccess: false, message: "Session not found" }
    }

    // Verify the user owns the meeting's session
    if (session.userId !== userId) {
      return { isSuccess: false, message: "Unauthorized to add sample transcripts to this meeting" }
    }

    // Create sample transcripts with correct schema
    const sampleTranscripts = [
      {
        meetingId,
        content: "Hello, let's start the meeting.",
        role: "user" as const,
        agentName: "Host",
        roundNumber: 1,
        sequenceNumber: 1,
      },
      {
        meetingId,
        content: "Yes, let's start by discussing our first agenda item.",
        role: "assistant" as const,
        agentName: "Participant 1",
        roundNumber: 1,
        sequenceNumber: 2,
      },
      {
        meetingId,
        content: "I think we should focus on improving our product.",
        role: "user" as const,
        agentName: "Participant 2",
        roundNumber: 1,
        sequenceNumber: 3,
      },
    ] as InsertTranscript[]

    const createdTranscripts = []
    for (const transcript of sampleTranscripts) {
      const [newTranscript] = await db
        .insert(transcriptsTable)
        .values(transcript)
        .returning()
      createdTranscripts.push(newTranscript)
    }

    return {
      isSuccess: true,
      message: "Sample transcripts created successfully",
      data: createdTranscripts,
    }
  } catch (error) {
    console.error("Error creating sample transcripts:", error)
    return { isSuccess: false, message: "Failed to create sample transcripts" }
  }
} 