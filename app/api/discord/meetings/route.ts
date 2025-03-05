import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { meetingsTable } from "@/db/schema"
import { eq } from "drizzle-orm"

/**
 * API route for getting meetings for a session
 * GET /api/discord/meetings?sessionId=xyz
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

    // Get meetings for the session
    const meetings = await db.query.meetings.findMany({
      where: eq(meetingsTable.sessionId, sessionId),
    })

    return NextResponse.json({
      isSuccess: true,
      message: "Meetings retrieved successfully",
      data: meetings
    })
  } catch (error) {
    console.error("Error getting meetings:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to get meetings", data: null },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { sessionId, title, agenda, taskDescription, maxRounds } = body

    if (!sessionId || !title) {
      return NextResponse.json(
        { isSuccess: false, message: "Missing required fields", data: null },
        { status: 400 }
      )
    }

    // Create the meeting
    const [newMeeting] = await db
      .insert(meetingsTable)
      .values({
        sessionId,
        title,
        agenda,
        taskDescription,
        maxRounds
      })
      .returning()

    return NextResponse.json({
      isSuccess: true,
      message: "Meeting created successfully",
      data: newMeeting
    })
  } catch (error) {
    console.error("Error creating meeting:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to create meeting", data: null },
      { status: 500 }
    )
  }
} 