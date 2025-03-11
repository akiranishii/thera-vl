import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { meetingsTable } from "@/db/schema"
import { eq } from "drizzle-orm"

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const resolvedParams = await params
    const meetingId = resolvedParams.id

    if (!meetingId) {
      return NextResponse.json(
        { isSuccess: false, message: "Meeting ID is required", data: null },
        { status: 400 }
      )
    }

    const meeting = await db.query.meetings.findFirst({
      where: eq(meetingsTable.id, meetingId)
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
    console.error("Error retrieving meeting:", error)
    return NextResponse.json(
      {
        isSuccess: false,
        message: "Failed to retrieve meeting",
        data: null
      },
      { status: 500 }
    )
  }
} 