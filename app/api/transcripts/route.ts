"use server"

import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { transcriptsTable } from "@/db/schema"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { meetingId, content, role, agentId, agentName, roundNumber, sequenceNumber } = body

    if (!meetingId || !content || !role) {
      return NextResponse.json(
        { isSuccess: false, message: "Missing required fields", data: null },
        { status: 400 }
      )
    }

    // Create the transcript
    const [newTranscript] = await db
      .insert(transcriptsTable)
      .values({
        meetingId,
        content,
        role,
        agentId,
        agentName,
        roundNumber,
        sequenceNumber
      })
      .returning()

    return NextResponse.json({
      isSuccess: true,
      message: "Transcript created successfully",
      data: newTranscript
    })
  } catch (error) {
    console.error("Error creating transcript:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to create transcript", data: null },
      { status: 500 }
    )
  }
} 