import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { sessionsTable } from "@/db/schema"
import { and, eq, desc } from "drizzle-orm"

/**
 * Get sessions for a user
 * GET /api/discord/sessions?userId=123
 */
export async function GET(request: NextRequest) {
  try {
    const url = new URL(request.url)
    const userId = url.searchParams.get("userId")

    if (!userId) {
      return NextResponse.json(
        { isSuccess: false, message: "User ID is required", data: null },
        { status: 400 }
      )
    }

    // Get all sessions for the user, ordered by createdAt descending (newest first)
    const sessions = await db.query.sessions.findMany({
      where: eq(sessionsTable.userId, userId),
      orderBy: [desc(sessionsTable.createdAt)]
    })

    // Transform the sessions to include a status field for Python client compatibility
    const transformedSessions = sessions.map(session => ({
      ...session,
      status: session.isActive ? "active" : "ended",
      is_public: session.isPublic // Add snake_case version for Python compatibility
    }))

    return NextResponse.json({
      isSuccess: true,
      message: "Sessions retrieved successfully",
      data: transformedSessions
    })
  } catch (error) {
    console.error("Error getting user sessions:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to get user sessions", data: null },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { userId, title, description, isPublic } = body

    if (!userId || !title) {
      return NextResponse.json(
        { isSuccess: false, message: "Missing required fields", data: null },
        { status: 400 }
      )
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
      .values({ 
        userId, 
        title, 
        description, 
        isPublic: isPublic ?? false,
        isActive: true 
      })
      .returning()

    return NextResponse.json({
      isSuccess: true,
      message: "Session created successfully",
      data: newSession
    })
  } catch (error) {
    console.error("Error creating session:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to create session", data: null },
      { status: 500 }
    )
  }
} 