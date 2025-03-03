"use server"

import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { meetingsTable } from "@/db/schema"

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