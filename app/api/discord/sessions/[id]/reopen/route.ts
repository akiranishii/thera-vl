import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { sessionsTable } from "@/db/schema"
import { eq } from "drizzle-orm"

/**
 * API route for reopening a previously ended session
 * PUT /api/discord/sessions/[id]/reopen
 */
export async function PUT(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const sessionId = params.id

    if (!sessionId) {
      return NextResponse.json(
        { isSuccess: false, message: "Session ID is required", data: null },
        { status: 400 }
      )
    }

    // Check if the session exists
    const existingSession = await db.query.sessions.findFirst({
      where: eq(sessionsTable.id, sessionId),
    })

    if (!existingSession) {
      return NextResponse.json(
        { isSuccess: false, message: "Session not found", data: null },
        { status: 404 }
      )
    }

    // Update the session status to active
    const [updatedSession] = await db
      .update(sessionsTable)
      .set({
        isActive: true,
        updatedAt: new Date()
      })
      .where(eq(sessionsTable.id, sessionId))
      .returning()

    return NextResponse.json({
      isSuccess: true,
      message: "Session reopened successfully",
      data: updatedSession
    })
  } catch (error) {
    console.error("Error reopening session:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to reopen session", data: null },
      { status: 500 }
    )
  }
} 