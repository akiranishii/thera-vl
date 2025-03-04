import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { agentsTable } from "@/db/schema"
import { eq } from "drizzle-orm"

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // Await the params object before accessing its properties
    const { id } = await params
    const { searchParams } = new URL(request.url)
    const userId = searchParams.get("userId")

    if (!id) {
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