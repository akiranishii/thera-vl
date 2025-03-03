import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { sessionsTable } from "@/db/schema"
import { and, eq } from "drizzle-orm"
import { auth } from "@clerk/nextjs/server"

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const userIdParam = searchParams.get("userId")
    
    // Try to get userId from Clerk auth
    const { userId: clerkUserId } = await auth()
    
    // Use the userId from the query parameter if provided, otherwise use the Clerk userId
    const userId = userIdParam || clerkUserId
    
    if (!userId) {
      return new NextResponse(JSON.stringify({
        isSuccess: false,
        message: "UserId is required",
        data: null
      }), { 
        status: 400,
        headers: { "Content-Type": "application/json" }
      })
    }

    // Find active session for the provided userId
    const activeSession = await db.query.sessions.findFirst({
      where: and(
        eq(sessionsTable.userId, userId),
        eq(sessionsTable.isActive, true)
      ),
      with: {
        meetings: true
      }
    })

    return new NextResponse(JSON.stringify({
      isSuccess: true, 
      message: activeSession ? "Active session retrieved" : "No active session found",
      data: activeSession 
    }), { 
      status: 200,
      headers: { "Content-Type": "application/json" }
    })
  } catch (error) {
    console.error("Error checking active session:", error)
    return new NextResponse(JSON.stringify({
      isSuccess: false,
      message: "Failed to check active session",
      data: null
    }), { 
      status: 500,
      headers: { "Content-Type": "application/json" }
    })
  }
} 