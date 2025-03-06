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

    // First, get the base meeting to determine its parallel group
    const baseMeeting = await db.query.meetings.findFirst({
      where: eq(meetingsTable.id, baseMeetingId)
    })

    if (!baseMeeting) {
      return NextResponse.json(
        { isSuccess: false, message: "Base meeting not found", data: null },
        { status: 404 }
      )
    }

    // If the base meeting has a parallelIndex, find all meetings in the same parallel group
    const parallelIndex = baseMeeting.parallelIndex || 0

    // Get all meetings with the same sessionId that are either:
    // 1. This base meeting itself (include it in results)
    // 2. Other parallel meetings with the same parallelIndex (if not 0)
    // 3. Parallel meetings where isParallel is true (as a fallback)
    const meetings = await db.query.meetings.findMany({
      where: and(
        eq(meetingsTable.sessionId, sessionId),
        parallelIndex === 0 
          ? eq(meetingsTable.isParallel, true) // If parallelIndex is 0, find by isParallel
          : eq(meetingsTable.parallelIndex, parallelIndex) // Otherwise find by parallelIndex
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