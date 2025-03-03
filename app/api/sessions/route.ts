"use server"

import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { sessionsTable } from "@/db/schema"
import { and, eq } from "drizzle-orm"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { userId, title, description, isPublic } = body

    if (!userId || !title) {
      return NextResponse.json(
        { isSuccess: false, message: "Missing required fields", data: null },
        { status: 400 }
      )
    }

    // First, deactivate all other active sessions for this user
    await db
      .update(sessionsTable)
      .set({ isActive: false })
      .where(and(
        eq(sessionsTable.userId, userId),
        eq(sessionsTable.isActive, true)
      ))

    // Create the new session as active
    const [newSession] = await db
      .insert(sessionsTable)
      .values({ 
        userId, 
        title, 
        description, 
        isPublic: isPublic ?? false,
        isActive: true 
      })
      .returning()

    return NextResponse.json({
      isSuccess: true,
      message: "Session created successfully",
      data: newSession
    })
  } catch (error) {
    console.error("Error creating session:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to create session", data: null },
      { status: 500 }
    )
  }
} 