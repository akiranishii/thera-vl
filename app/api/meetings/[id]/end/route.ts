"use server"

import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { meetingsTable } from "@/db/schema"
import { eq } from "drizzle-orm"

export async function PUT(
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

    // End the meeting
    const [updatedMeeting] = await db
      .update(meetingsTable)
      .set({ status: "completed" })
      .where(eq(meetingsTable.id, meetingId))
      .returning()

    if (!updatedMeeting) {
      return NextResponse.json(
        { isSuccess: false, message: "Meeting not found", data: null },
        { status: 404 }
      )
    }

    return NextResponse.json({
      isSuccess: true,
      message: "Meeting ended successfully",
      data: updatedMeeting
    })
  } catch (error) {
    console.error("Error ending meeting:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to end meeting", data: null },
      { status: 500 }
    )
  }
} 