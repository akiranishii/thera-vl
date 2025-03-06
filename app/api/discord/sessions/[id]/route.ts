import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { sessionsTable } from "@/db/schema"
import { eq } from "drizzle-orm"

/**
 * API route for getting a specific session by ID
 * GET /api/discord/sessions/[id]
 */
export async function GET(
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

    // Get the session
    const session = await db.query.sessions.findFirst({
      where: eq(sessionsTable.id, sessionId),
    })

    if (!session) {
      return NextResponse.json(
        { isSuccess: false, message: "Session not found", data: null },
        { status: 404 }
      )
    }

    // Transform the session to include a status field for Python client compatibility
    const transformedSession = {
      ...session,
      status: session.isActive ? "active" : "ended",
      is_public: session.isPublic // Add snake_case version for Python compatibility
    };

    return NextResponse.json({
      isSuccess: true,
      message: "Session retrieved successfully",
      data: transformedSession
    })
  } catch (error) {
    console.error("Error getting session:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to get session", data: null },
      { status: 500 }
    )
  }
}

/**
 * Update a session by ID
 * PUT /api/discord/sessions/[id]
 * 
 * Body example:
 * {
 *   "isPublic": true,
 *   "title": "Updated Title",
 *   "description": "Updated Description"
 * }
 */
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params
    const body = await request.json()
    
    if (!id) {
      return NextResponse.json(
        { isSuccess: false, message: "Session ID is required", data: null },
        { status: 400 }
      )
    }

    // Extract updatable fields from the request body
    const updates: any = {}
    
    // Handle all possible fields that can be updated
    if (body.isPublic !== undefined) updates.isPublic = body.isPublic
    if (body.title) updates.title = body.title
    if (body.description !== undefined) updates.description = body.description
    if (body.is_public !== undefined) updates.isPublic = body.is_public // Handle snake_case variant
    
    if (Object.keys(updates).length === 0) {
      return NextResponse.json(
        { isSuccess: false, message: "No valid fields to update", data: null },
        { status: 400 }
      )
    }

    // Update the session
    const [updatedSession] = await db
      .update(sessionsTable)
      .set(updates)
      .where(eq(sessionsTable.id, id))
      .returning()

    if (!updatedSession) {
      return NextResponse.json(
        { isSuccess: false, message: "Session not found", data: null },
        { status: 404 }
      )
    }

    return NextResponse.json({
      isSuccess: true,
      message: "Session updated successfully",
      data: updatedSession
    })
  } catch (error) {
    console.error("Error updating session:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to update session", data: null },
      { status: 500 }
    )
  }
} 