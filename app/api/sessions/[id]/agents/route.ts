"use server"

import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { agentsTable } from "@/db/schema"
import { eq } from "drizzle-orm"

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const resolvedParams = await params
    const sessionId = resolvedParams.id
    const { searchParams } = new URL(req.url)
    const userId = searchParams.get("userId")

    if (!sessionId) {
      return NextResponse.json(
        { isSuccess: false, message: "Session ID is required", data: null },
        { status: 400 }
      )
    }

    if (!userId) {
      return NextResponse.json(
        { isSuccess: false, message: "User ID is required", data: null },
        { status: 400 }
      )
    }

    // Get agents for the user
    // In a real implementation, you would filter by session ID if that relationship exists
    const agents = await db.query.agents.findMany({
      where: eq(agentsTable.userId, userId)
    })

    return NextResponse.json({
      isSuccess: true,
      message: "Agents retrieved successfully",
      data: agents
    })
  } catch (error) {
    console.error("Error getting session agents:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to get session agents", data: null },
      { status: 500 }
    )
  }
} 