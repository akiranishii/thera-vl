/*
<ai_context>
Contains server actions related to sessions in the DB.
</ai_context>
*/

"use server"

import { db } from "@/db/db"
import { InsertSession, SelectSession, sessionsTable } from "@/db/schema/sessions-schema"
import { ActionState } from "@/types"
import { auth } from "@clerk/nextjs/server"
import { and, desc, eq, ilike, or, sql } from "drizzle-orm"

export async function createSessionAction(
  session: Omit<InsertSession, "userId">
): Promise<ActionState<SelectSession>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    const [newSession] = await db
      .insert(sessionsTable)
      .values({ ...session, userId })
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
    const sessions = await db.query.sessions.findMany({
      where: and(...conditions),
      limit: pageSize,
      offset: (page - 1) * pageSize,
      orderBy: sort === 'recent' 
        ? [desc(sessionsTable.createdAt)] 
        : [desc(sessionsTable.createdAt)] // For now use same sort for all options
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