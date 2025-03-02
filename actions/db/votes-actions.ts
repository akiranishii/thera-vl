/*
<ai_context>
Contains server actions related to votes in the DB.
</ai_context>
*/

"use server"

import { db } from "@/db/db"
import { sessionsTable } from "@/db/schema/sessions-schema"
import { InsertVote, SelectVote, votesTable } from "@/db/schema/votes-schema"
import { ActionState } from "@/types"
import { auth } from "@clerk/nextjs/server"
import { and, count, eq, sql, sum } from "drizzle-orm"

export async function createOrUpdateVoteAction(
  sessionId: string,
  value: number
): Promise<ActionState<SelectVote>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // Ensure the session exists and is public or owned by the user
    const session = await db.query.sessions.findFirst({
      where: eq(sessionsTable.id, sessionId)
    })

    if (!session) {
      return { isSuccess: false, message: "Session not found" }
    }

    if (!session.isPublic && session.userId !== userId) {
      return { isSuccess: false, message: "Cannot vote on a private session you don't own" }
    }

    // Limit value to -1, 0, or 1
    const limitedValue = Math.max(-1, Math.min(1, value))

    // Check if user has already voted on this session
    const existingVote = await db.query.votes.findFirst({
      where: and(
        eq(votesTable.sessionId, sessionId),
        eq(votesTable.userId, userId)
      )
    })

    let result: SelectVote

    if (existingVote) {
      // Update existing vote
      const [updatedVote] = await db
        .update(votesTable)
        .set({ value: limitedValue, updatedAt: new Date() })
        .where(
          and(
            eq(votesTable.sessionId, sessionId),
            eq(votesTable.userId, userId)
          )
        )
        .returning()
      
      result = updatedVote
    } else {
      // Create new vote
      const [newVote] = await db
        .insert(votesTable)
        .values({
          sessionId,
          userId,
          value: limitedValue
        })
        .returning()
      
      result = newVote
    }

    return {
      isSuccess: true,
      message: `Vote ${existingVote ? 'updated' : 'created'} successfully`,
      data: result
    }
  } catch (error) {
    console.error("Error creating/updating vote:", error)
    return { isSuccess: false, message: "Failed to create/update vote" }
  }
}

export async function getVoteAction(
  sessionId: string
): Promise<ActionState<SelectVote | null>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    const vote = await db.query.votes.findFirst({
      where: and(
        eq(votesTable.sessionId, sessionId),
        eq(votesTable.userId, userId)
      )
    })

    return {
      isSuccess: true,
      message: vote ? "Vote retrieved successfully" : "No vote found",
      data: vote || null
    }
  } catch (error) {
    console.error("Error getting vote:", error)
    return { isSuccess: false, message: "Failed to get vote" }
  }
}

export async function getVoteCountAction(
  sessionId: string
): Promise<ActionState<{ upvotes: number; downvotes: number; total: number }>> {
  try {
    // Ensure the session exists
    const session = await db.query.sessions.findFirst({
      where: eq(sessionsTable.id, sessionId)
    })

    if (!session) {
      return { isSuccess: false, message: "Session not found" }
    }

    // Get upvotes count (value = 1)
    const [upvotesResult] = await db
      .select({ count: count() })
      .from(votesTable)
      .where(and(
        eq(votesTable.sessionId, sessionId),
        eq(votesTable.value, 1)
      ))

    // Get downvotes count (value = -1)
    const [downvotesResult] = await db
      .select({ count: count() })
      .from(votesTable)
      .where(and(
        eq(votesTable.sessionId, sessionId),
        eq(votesTable.value, -1)
      ))

    // Get sum of all votes
    const [totalResult] = await db
      .select({ sum: sum(votesTable.value) })
      .from(votesTable)
      .where(eq(votesTable.sessionId, sessionId))

    const upvotes = upvotesResult?.count || 0
    const downvotes = downvotesResult?.count || 0
    const total = totalResult?.sum !== null ? Number(totalResult.sum) : 0

    return {
      isSuccess: true,
      message: "Vote counts retrieved successfully",
      data: { upvotes, downvotes, total }
    }
  } catch (error) {
    console.error("Error getting vote count:", error)
    return { isSuccess: false, message: "Failed to get vote count" }
  }
} 