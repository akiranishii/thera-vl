import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { meetingsTable } from "@/db/schema"
import { eq } from "drizzle-orm"

/**
 * API route for getting a specific meeting by ID
 * GET /api/discord/meetings/[id]
 */
export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const meetingId = params.id

    if (!meetingId) {
      return NextResponse.json(
        { isSuccess: false, message: "Meeting ID is required", data: null },
        { status: 400 }
      )
    }

    // Get the meeting
    const meeting = await db.query.meetings.findFirst({
      where: eq(meetingsTable.id, meetingId),
    })

    if (!meeting) {
      return NextResponse.json(
        { isSuccess: false, message: "Meeting not found", data: null },
        { status: 404 }
      )
    }

    return NextResponse.json({
      isSuccess: true,
      message: "Meeting retrieved successfully",
      data: meeting
    })
  } catch (error) {
    console.error("Error getting meeting:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to get meeting", data: null },
      { status: 500 }
    )
  }
} 