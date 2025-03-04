import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { sessionsTable } from "@/db/schema"
import { and, eq } from "drizzle-orm"

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const userId = searchParams.get("userId")
    
    if (!userId) {
      return NextResponse.json({
        isSuccess: false,
        message: "User ID is required",
        data: null
      }, { status: 400 })
    }

    console.log(`Fetching active session for userId: ${userId}`)

    try {
      // Find active session for the provided userId
      const activeSession = await db.query.sessions.findFirst({
        where: and(
          eq(sessionsTable.userId, userId),
          eq(sessionsTable.isActive, true)
        )
      })

      console.log(`Active session result:`, activeSession)

      return NextResponse.json({
        isSuccess: true, 
        message: activeSession ? "Active session retrieved" : "No active session found",
        data: activeSession || null
      })
    } catch (dbError) {
      console.error("Database error:", dbError)
      return NextResponse.json({
        isSuccess: false,
        message: `Database error: ${dbError instanceof Error ? dbError.message : String(dbError)}`,
        data: null
      }, { status: 500 })
    }
  } catch (error) {
    console.error("Error checking active session:", error)
    return NextResponse.json({
      isSuccess: false,
      message: `Failed to check active session: ${error instanceof Error ? error.message : String(error)}`,
      data: null
    }, { status: 500 })
  }
} 