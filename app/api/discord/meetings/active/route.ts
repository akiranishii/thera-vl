import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { meetingsTable } from "@/db/schema"
import { and, eq, not, or } from "drizzle-orm"

/**
 * API route for getting active meetings for a session
 * GET /api/discord/meetings/active?sessionId=xyz
 */
export async function GET(req: NextRequest) {
  try {
    const url = new URL(req.url)
    const sessionId = url.searchParams.get("sessionId")

    if (!sessionId) {
      return NextResponse.json(
        { isSuccess: false, message: "Session ID is required", data: null },
        { status: 400 }
      )
    }

    // Get active meetings for the session
    // We determine a meeting is active if status is 'pending' or 'in_progress'
    const meetings = await db.query.meetings.findMany({
      where: and(
        eq(meetingsTable.sessionId, sessionId),
        or(
          eq(meetingsTable.status, "pending"),
          eq(meetingsTable.status, "in_progress")
        )
      ),
    })

    return NextResponse.json({
      isSuccess: true,
      message: "Active meetings retrieved successfully",
      data: meetings
    })
  } catch (error) {
    console.error("Error getting active meetings:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to get active meetings", data: null },
      { status: 500 }
    )
  }
} 