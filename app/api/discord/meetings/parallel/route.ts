import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { meetingsTable } from "@/db/schema"
import { and, eq } from "drizzle-orm"

/**
 * API route for getting parallel meetings for a session
 * GET /api/discord/meetings/parallel?sessionId=xyz&baseMeetingId=abc
 */
export async function GET(req: NextRequest) {
  try {
    const url = new URL(req.url)
    const sessionId = url.searchParams.get("sessionId")
    const baseMeetingId = url.searchParams.get("baseMeetingId")

    if (!sessionId) {
      return NextResponse.json(
        { isSuccess: false, message: "Session ID is required", data: null },
        { status: 400 }
      )
    }

    if (!baseMeetingId) {
      return NextResponse.json(
        { isSuccess: false, message: "Base meeting ID is required", data: null },
        { status: 400 }
      )
    }

    // Get parallel meetings for the session
    const meetings = await db.query.meetings.findMany({
      where: and(
        eq(meetingsTable.sessionId, sessionId),
        eq(meetingsTable.isParallel, true)
      ),
    })

    return NextResponse.json({
      isSuccess: true,
      message: "Parallel meetings retrieved successfully",
      data: meetings
    })
  } catch (error) {
    console.error("Error getting parallel meetings:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to get parallel meetings", data: null },
      { status: 500 }
    )
  }
} 