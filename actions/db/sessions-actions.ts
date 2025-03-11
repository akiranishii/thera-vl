/*
<ai_context>
Contains server actions related to sessions in the DB.
</ai_context>
*/

"use server"

import { db } from "@/db/db"
import { InsertSession, SelectSession, sessionsTable } from "@/db/schema/sessions-schema"
import { votesTable } from "@/db/schema/votes-schema"
import { meetingsTable, meetingStatusEnum } from "@/db/schema/meetings-schema"
import { ActionState } from "@/types"
import { auth } from "@clerk/nextjs/server"
import { and, desc, eq, ilike, or, sql, sum, count, not, isNull } from "drizzle-orm"

export async function createSessionAction(
  session: Omit<InsertSession, "userId">
): Promise<ActionState<SelectSession>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // First, deactivate all other active sessions for this user
    await db
      .update(sessionsTable)
      .set({ isActive: false })
      .where(and(
        eq(sessionsTable.userId, userId),
        eq(sessionsTable.isActive, true)
      ))

    // Create the new session as active
    const [newSession] = await db
      .insert(sessionsTable)
      .values({ ...session, userId, isActive: true })
      .returning()

    return {
      isSuccess: true,
      message: "Session created successfully",
      data: newSession
    }
  } catch (error) {
    console.error("Error creating session:", error)
    return { isSuccess: false, message: "Failed to create session" }
  }
}

export async function getSessionsAction(): Promise<ActionState<SelectSession[]>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    const sessions = await db.query.sessions.findMany({
      where: eq(sessionsTable.userId, userId)
    })

    return {
      isSuccess: true,
      message: "Sessions retrieved successfully",
      data: sessions
    }
  } catch (error) {
    console.error("Error getting sessions:", error)
    return { isSuccess: false, message: "Failed to get sessions" }
  }
}

export async function getPublicSessionsAction(
  params?: {
    page?: number
    pageSize?: number
    sort?: 'recent' | 'popular' | 'trending'
    search?: string
    agentType?: string
  }
): Promise<ActionState<{
  sessions: SelectSession[],
  totalPages: number,
  currentPage: number
}>> {
  try {
    const {
      page = 1,
      pageSize = 12,
      sort = 'recent',
      search,
      agentType
    } = params || {}
    
    // Build the query conditions
    const conditions = [eq(sessionsTable.isPublic, true)];
    
    // Add search condition if provided
    if (search && search.trim() !== '') {
      conditions.push(ilike(sessionsTable.title, `%${search}%`));
    }
    
    // Add agent type condition if provided
    // if (agentType) {
    //   conditions.push(eq(sessionsTable.agentType, agentType));
    // }
    
    // Count total sessions for pagination
    const totalSessions = await db.query.sessions.findMany({
      where: and(...conditions),
    });
    
    const totalCount = totalSessions.length;
    const totalPages = Math.ceil(totalCount / pageSize);
    
    // Get the paginated and sorted sessions
    let orderByClause;
    
    switch (sort) {
      case 'popular':
        // For popular, we would ideally sort by number of votes or views
        // This is a placeholder - in a real app, you'd join with votes table and count
        orderByClause = [desc(sessionsTable.createdAt)]; // Placeholder
        break;
      case 'trending':
        // For trending, we'd ideally sort by recent activity or engagement
        // This is a placeholder - in a real app, you'd likely use a more complex algorithm
        orderByClause = [desc(sessionsTable.createdAt)]; // Placeholder
        break;
      case 'recent':
      default:
        orderByClause = [desc(sessionsTable.createdAt)];
        break;
    }
    
    const sessions = await db.query.sessions.findMany({
      where: and(...conditions),
      limit: pageSize,
      offset: (page - 1) * pageSize,
      orderBy: orderByClause
    });
    
    return {
      isSuccess: true,
      message: "Public sessions retrieved successfully",
      data: {
        sessions,
        totalPages,
        currentPage: page
      }
    }
  } catch (error) {
    console.error("Error getting public sessions:", error)
    return { isSuccess: false, message: "Failed to get public sessions" }
  }
}

export async function getSessionAction(
  id: string
): Promise<ActionState<SelectSession>> {
  try {
    const session = await db.query.sessions.findFirst({
      where: eq(sessionsTable.id, id)
    })

    if (!session) {
      return { isSuccess: false, message: "Session not found" }
    }

    return {
      isSuccess: true,
      message: "Session retrieved successfully",
      data: session
    }
  } catch (error) {
    console.error("Error getting session:", error)
    return { isSuccess: false, message: "Failed to get session" }
  }
}

export async function updateSessionAction(
  id: string,
  data: Partial<InsertSession>
): Promise<ActionState<SelectSession>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // Ensure the user owns the session
    const sessionToUpdate = await db.query.sessions.findFirst({
      where: and(
        eq(sessionsTable.id, id),
        eq(sessionsTable.userId, userId)
      )
    })

    if (!sessionToUpdate) {
      return { isSuccess: false, message: "Session not found or unauthorized" }
    }

    const [updatedSession] = await db
      .update(sessionsTable)
      .set(data)
      .where(eq(sessionsTable.id, id))
      .returning()

    return {
      isSuccess: true,
      message: "Session updated successfully",
      data: updatedSession
    }
  } catch (error) {
    console.error("Error updating session:", error)
    return { isSuccess: false, message: "Failed to update session" }
  }
}

export async function deleteSessionAction(
  id: string
): Promise<ActionState<void>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // Ensure the user owns the session
    const sessionToDelete = await db.query.sessions.findFirst({
      where: and(
        eq(sessionsTable.id, id),
        eq(sessionsTable.userId, userId)
      )
    })

    if (!sessionToDelete) {
      return { isSuccess: false, message: "Session not found or unauthorized" }
    }

    await db.delete(sessionsTable).where(eq(sessionsTable.id, id))

    return {
      isSuccess: true,
      message: "Session deleted successfully",
      data: undefined
    }
  } catch (error) {
    console.error("Error deleting session:", error)
    return { isSuccess: false, message: "Failed to delete session" }
  }
}

export async function checkSessionAccessAction(
  id: string
): Promise<ActionState<{ hasAccess: boolean }>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { 
        isSuccess: true, 
        message: "Access check completed", 
        data: { hasAccess: false } 
      }
    }

    const session = await db.query.sessions.findFirst({
      where: eq(sessionsTable.id, id)
    })

    if (!session) {
      return { 
        isSuccess: true, 
        message: "Session not found", 
        data: { hasAccess: false } 
      }
    }

    // User has access if the session is public or if they own it
    const hasAccess = session.isPublic || session.userId === userId

    return {
      isSuccess: true,
      message: "Access check completed",
      data: { hasAccess }
    }
  } catch (error) {
    console.error("Error checking session access:", error)
    return { 
      isSuccess: false, 
      message: "Failed to check session access"
    }
  }
}

export async function getTopVotedSessionsAction(
  limit: number = 20
): Promise<ActionState<{
  session: SelectSession,
  votes: {
    upvotes: number,
    downvotes: number,
    total: number
  }
}[]>> {
  try {
    // Get all public sessions
    const publicSessions = await db.query.sessions.findMany({
      where: eq(sessionsTable.isPublic, true)
    })
    
    // For each session, get the vote counts
    const sessionsWithVotes = await Promise.all(
      publicSessions.map(async (session) => {
        // Get vote counts for this session
        const voteResult = await db
          .select({
            upvotes: sql<number>`COALESCE(SUM(CASE WHEN ${votesTable.value} = 1 THEN 1 ELSE 0 END), 0)`,
            downvotes: sql<number>`COALESCE(SUM(CASE WHEN ${votesTable.value} = -1 THEN 1 ELSE 0 END), 0)`,
            total: sql<number>`COALESCE(SUM(${votesTable.value}), 0)`
          })
          .from(votesTable)
          .where(eq(votesTable.sessionId, session.id))
          .then(res => res[0])
        
        return {
          session,
          votes: {
            upvotes: voteResult.upvotes || 0,
            downvotes: voteResult.downvotes || 0,
            total: voteResult.total || 0
          }
        }
      })
    )
    
    // Sort by total votes (can be sorted differently on the client)
    const sortedSessions = sessionsWithVotes
      .sort((a, b) => b.votes.total - a.votes.total)
      .slice(0, limit)
    
    return {
      isSuccess: true,
      message: "Top voted sessions retrieved successfully",
      data: sortedSessions
    }
  } catch (error) {
    console.error("Error getting top voted sessions:", error)
    return { isSuccess: false, message: "Failed to get top voted sessions" }
  }
}

/**
 * Activates a session and deactivates all other sessions for the user.
 * This supports the one-at-a-time session model.
 */
export async function activateSessionAction(
  id: string
): Promise<ActionState<SelectSession>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // Ensure the user owns the session
    const sessionToActivate = await db.query.sessions.findFirst({
      where: and(
        eq(sessionsTable.id, id),
        eq(sessionsTable.userId, userId)
      )
    })

    if (!sessionToActivate) {
      return { isSuccess: false, message: "Session not found or unauthorized" }
    }

    // First, deactivate all sessions for this user
    await db
      .update(sessionsTable)
      .set({ isActive: false })
      .where(and(
        eq(sessionsTable.userId, userId),
        eq(sessionsTable.isActive, true)
      ))

    // Then, activate the requested session
    const [activatedSession] = await db
      .update(sessionsTable)
      .set({ isActive: true })
      .where(eq(sessionsTable.id, id))
      .returning()

    return {
      isSuccess: true,
      message: "Session activated successfully",
      data: activatedSession
    }
  } catch (error) {
    console.error("Error activating session:", error)
    return { isSuccess: false, message: "Failed to activate session" }
  }
}

/**
 * Deactivates a session.
 */
export async function deactivateSessionAction(
  id: string
): Promise<ActionState<SelectSession>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // Ensure the user owns the session
    const sessionToDeactivate = await db.query.sessions.findFirst({
      where: and(
        eq(sessionsTable.id, id),
        eq(sessionsTable.userId, userId)
      )
    })

    if (!sessionToDeactivate) {
      return { isSuccess: false, message: "Session not found or unauthorized" }
    }

    // Deactivate the session
    const [deactivatedSession] = await db
      .update(sessionsTable)
      .set({ isActive: false })
      .where(eq(sessionsTable.id, id))
      .returning()

    return {
      isSuccess: true,
      message: "Session deactivated successfully",
      data: deactivatedSession
    }
  } catch (error) {
    console.error("Error deactivating session:", error)
    return { isSuccess: false, message: "Failed to deactivate session" }
  }
}

/**
 * Gets the currently active session for the user, if any.
 */
export async function getActiveSessionAction(): Promise<ActionState<SelectSession | null>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    const activeSession = await db.query.sessions.findFirst({
      where: and(
        eq(sessionsTable.userId, userId),
        eq(sessionsTable.isActive, true)
      )
    })

    return {
      isSuccess: true,
      message: activeSession ? "Active session retrieved" : "No active session found",
      data: activeSession || null
    }
  } catch (error) {
    console.error("Error getting active session:", error)
    return { isSuccess: false, message: "Failed to get active session" }
  }
}

/**
 * Reopens an ended session by activating it and creating a new meeting.
 */
export async function reopenSessionAction(
  id: string,
  meetingParams?: Partial<{
    title: string;
    agenda: string;
    taskDescription: string;
    maxRounds: number;
  }>
): Promise<ActionState<{
  session: SelectSession;
  meetingId: string;
}>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // Ensure the user owns the session
    const sessionToReopen = await db.query.sessions.findFirst({
      where: and(
        eq(sessionsTable.id, id),
        eq(sessionsTable.userId, userId)
      )
    })

    if (!sessionToReopen) {
      return { isSuccess: false, message: "Session not found or unauthorized" }
    }

    // Activate this session and deactivate others
    await db
      .update(sessionsTable)
      .set({ isActive: false })
      .where(and(
        eq(sessionsTable.userId, userId),
        eq(sessionsTable.isActive, true)
      ))

    const [reopenedSession] = await db
      .update(sessionsTable)
      .set({ isActive: true })
      .where(eq(sessionsTable.id, id))
      .returning()

    // Create a new meeting for this session
    const [newMeeting] = await db
      .insert(meetingsTable)
      .values({
        sessionId: id,
        title: meetingParams?.title || `Reopened: ${reopenedSession.title}`,
        agenda: meetingParams?.agenda || '',
        taskDescription: meetingParams?.taskDescription || '',
        maxRounds: meetingParams?.maxRounds || 3,
        status: 'pending',
        currentRound: 0
      })
      .returning()

    return {
      isSuccess: true,
      message: "Session reopened successfully",
      data: {
        session: reopenedSession,
        meetingId: newMeeting.id
      }
    }
  } catch (error) {
    console.error("Error reopening session:", error)
    return { isSuccess: false, message: "Failed to reopen session" }
  }
} 