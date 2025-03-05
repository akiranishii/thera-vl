import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { transcriptsTable } from "@/db/schema"
import { eq, desc } from "drizzle-orm"

/**
 * API route for getting transcripts for a meeting
 * GET /api/discord/transcripts?meetingId=xyz&limit=10
 */
export async function GET(req: NextRequest) {
  try {
    const url = new URL(req.url)
    const meetingId = url.searchParams.get("meetingId")
    const limitParam = url.searchParams.get("limit")
    const limit = limitParam ? parseInt(limitParam, 10) : undefined

    if (!meetingId) {
      return NextResponse.json(
        { isSuccess: false, message: "Meeting ID is required", data: null },
        { status: 400 }
      )
    }

    // Query for transcripts
    let query = db.query.transcripts.findMany({
      where: eq(transcriptsTable.meetingId, meetingId),
      orderBy: [desc(transcriptsTable.createdAt)]
    })

    // Apply limit if provided
    if (limit && !isNaN(limit)) {
      query = db.query.transcripts.findMany({
        where: eq(transcriptsTable.meetingId, meetingId),
        orderBy: [desc(transcriptsTable.createdAt)],
        limit
      })
    }

    const transcripts = await query

    return NextResponse.json({
      isSuccess: true,
      message: "Transcripts retrieved successfully",
      data: transcripts
    })
  } catch (error) {
    console.error("Error getting transcripts:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to get transcripts", data: null },
      { status: 500 }
    )
  }
}

/**
 * API route for adding a message to a meeting transcript
 * POST /api/discord/transcripts
 * 
 * Body: {
 *   meetingId: string,
 *   content: string,
 *   role: string,
 *   agentId?: string,
 *   agentName?: string,
 *   roundNumber?: number,
 *   sequenceNumber?: number
 * }
 */
export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const { 
      meetingId, 
      content, 
      role, 
      agentId, 
      agentName, 
      roundNumber, 
      sequenceNumber 
    } = body

    if (!meetingId || !content || !role) {
      return NextResponse.json(
        { 
          isSuccess: false, 
          message: "Meeting ID, content, and role are required", 
          data: null 
        },
        { status: 400 }
      )
    }

    // Insert the transcript message
    const [transcript] = await db
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
      message: "Transcript message added successfully",
      data: transcript
    })
  } catch (error) {
    console.error("Error adding transcript message:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to add transcript message", data: null },
      { status: 500 }
    )
  }
} 