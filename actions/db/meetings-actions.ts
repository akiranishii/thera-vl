/*
<ai_context>
Contains server actions related to meetings in the DB.
</ai_context>
*/

"use server"

import { db } from "@/db/db"
import { InsertMeeting, MeetingWithSession, SelectMeeting, meetingsTable, meetingStatusEnum } from "@/db/schema/meetings-schema"
import { sessionsTable } from "@/db/schema/sessions-schema"
import { ActionState } from "@/types"
import { auth } from "@clerk/nextjs/server"
import { and, eq } from "drizzle-orm"

export async function createMeetingAction(
  meeting: InsertMeeting
): Promise<ActionState<SelectMeeting>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // Verify the user owns the session
    const session = await db.query.sessions.findFirst({
      where: and(
        eq(sessionsTable.id, meeting.sessionId),
        eq(sessionsTable.userId, userId)
      )
    })

    if (!session) {
      return { isSuccess: false, message: "Session not found or unauthorized" }
    }

    const [newMeeting] = await db
      .insert(meetingsTable)
      .values(meeting)
      .returning()

    return {
      isSuccess: true,
      message: "Meeting created successfully",
      data: newMeeting
    }
  } catch (error) {
    console.error("Error creating meeting:", error)
    return { isSuccess: false, message: "Failed to create meeting" }
  }
}

export async function getMeetingsAction(
  sessionId: string
): Promise<ActionState<SelectMeeting[]>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // Verify the user owns the session or it's public
    const session = await db.query.sessions.findFirst({
      where: eq(sessionsTable.id, sessionId)
    })

    if (!session) {
      return { isSuccess: false, message: "Session not found" }
    }

    if (!session.isPublic && session.userId !== userId) {
      return { isSuccess: false, message: "Unauthorized to access this session" }
    }

    const meetings = await db.query.meetings.findMany({
      where: eq(meetingsTable.sessionId, sessionId)
    })

    return {
      isSuccess: true,
      message: "Meetings retrieved successfully",
      data: meetings
    }
  } catch (error) {
    console.error("Error getting meetings:", error)
    return { isSuccess: false, message: "Failed to get meetings" }
  }
}

export async function getMeetingAction(
  id: string
): Promise<ActionState<MeetingWithSession>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    const meeting = await db.query.meetings.findFirst({
      where: eq(meetingsTable.id, id),
      with: {
        session: true
      }
    }) as MeetingWithSession | null

    if (!meeting) {
      return { isSuccess: false, message: "Meeting not found" }
    }

    // Check if user has access to this meeting's session
    if (!meeting.session.isPublic && meeting.session.userId !== userId) {
      return { isSuccess: false, message: "Unauthorized to access this meeting" }
    }

    return {
      isSuccess: true,
      message: "Meeting retrieved successfully",
      data: meeting
    }
  } catch (error) {
    console.error("Error getting meeting:", error)
    return { isSuccess: false, message: "Failed to get meeting" }
  }
}

export async function updateMeetingAction(
  id: string,
  data: Partial<InsertMeeting>
): Promise<ActionState<SelectMeeting>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // Get the meeting with its session
    const meeting = await db.query.meetings.findFirst({
      where: eq(meetingsTable.id, id),
      with: {
        session: true
      }
    }) as MeetingWithSession | null

    if (!meeting) {
      return { isSuccess: false, message: "Meeting not found" }
    }

    // Check if user owns the meeting's session
    if (meeting.session.userId !== userId) {
      return { isSuccess: false, message: "Unauthorized to update this meeting" }
    }

    const [updatedMeeting] = await db
      .update(meetingsTable)
      .set(data)
      .where(eq(meetingsTable.id, id))
      .returning()

    return {
      isSuccess: true,
      message: "Meeting updated successfully",
      data: updatedMeeting
    }
  } catch (error) {
    console.error("Error updating meeting:", error)
    return { isSuccess: false, message: "Failed to update meeting" }
  }
}

export async function deleteMeetingAction(
  id: string
): Promise<ActionState<void>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // Get the meeting with its session
    const meeting = await db.query.meetings.findFirst({
      where: eq(meetingsTable.id, id),
      with: {
        session: true
      }
    }) as MeetingWithSession | null

    if (!meeting) {
      return { isSuccess: false, message: "Meeting not found" }
    }

    // Check if user owns the meeting's session
    if (meeting.session.userId !== userId) {
      return { isSuccess: false, message: "Unauthorized to delete this meeting" }
    }

    await db.delete(meetingsTable).where(eq(meetingsTable.id, id))

    return {
      isSuccess: true,
      message: "Meeting deleted successfully",
      data: undefined
    }
  } catch (error) {
    console.error("Error deleting meeting:", error)
    return { isSuccess: false, message: "Failed to delete meeting" }
  }
}

/**
 * Ends a team meeting by marking it as completed
 */
export async function endMeetingAction(
  id: string
): Promise<ActionState<SelectMeeting>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // Get the meeting with its session
    const meeting = await db.query.meetings.findFirst({
      where: eq(meetingsTable.id, id),
      with: {
        session: true
      }
    }) as MeetingWithSession | null

    if (!meeting) {
      return { isSuccess: false, message: "Meeting not found" }
    }

    // Check if user owns the meeting's session
    if (meeting.session.userId !== userId) {
      return { isSuccess: false, message: "Unauthorized to end this meeting" }
    }

    // If meeting is already completed, return early
    if (meeting.status === "completed") {
      return {
        isSuccess: true,
        message: "Meeting is already completed",
        data: meeting
      }
    }

    // Update meeting to completed status
    const [updatedMeeting] = await db
      .update(meetingsTable)
      .set({
        status: "completed",
        completedAt: new Date()
      })
      .where(eq(meetingsTable.id, id))
      .returning()

    return {
      isSuccess: true,
      message: "Meeting ended successfully",
      data: updatedMeeting
    }
  } catch (error) {
    console.error("Error ending meeting:", error)
    return { isSuccess: false, message: "Failed to end meeting" }
  }
}

/**
 * Ends all active meetings for a session
 */
export async function endAllSessionMeetingsAction(
  sessionId: string
): Promise<ActionState<number>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // Ensure the user owns the session
    const session = await db.query.sessions.findFirst({
      where: and(
        eq(sessionsTable.id, sessionId),
        eq(sessionsTable.userId, userId)
      )
    })

    if (!session) {
      return { isSuccess: false, message: "Session not found or unauthorized" }
    }

    // Get all active meetings for this session
    const activeMeetings = await db.query.meetings.findMany({
      where: and(
        eq(meetingsTable.sessionId, sessionId),
        eq(meetingsTable.status, "in_progress")
      )
    })

    if (activeMeetings.length === 0) {
      return {
        isSuccess: true,
        message: "No active meetings to end",
        data: 0
      }
    }

    // End all active meetings
    const result = await db
      .update(meetingsTable)
      .set({
        status: "completed",
        completedAt: new Date()
      })
      .where(
        and(
          eq(meetingsTable.sessionId, sessionId),
          eq(meetingsTable.status, "in_progress")
        )
      )

    return {
      isSuccess: true,
      message: `${activeMeetings.length} meetings ended successfully`,
      data: activeMeetings.length
    }
  } catch (error) {
    console.error("Error ending all session meetings:", error)
    return { isSuccess: false, message: "Failed to end session meetings" }
  }
} 