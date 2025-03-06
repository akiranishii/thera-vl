import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { agentsTable } from "@/db/schema"
import { and, eq, inArray } from "drizzle-orm"

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // Await the params object before accessing its properties
    const { id } = await params
    const { searchParams } = new URL(request.url)
    const userId = searchParams.get("userId")
    const namesParam = searchParams.get("names")

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

    // Build the where conditions
    let whereConditions = [eq(agentsTable.sessionId, id)];
    
    // Add userId condition if provided
    if (userId) {
      whereConditions.push(eq(agentsTable.userId, userId));
    }
    
    // Add names condition if provided
    if (namesParam) {
      const names = namesParam.split(',');
      if (names.length > 0) {
        whereConditions.push(inArray(agentsTable.name, names));
      }
    }

    // Get agents for the specific session with additional filters
    const agents = await db.query.agents.findMany({
      where: and(...whereConditions)
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