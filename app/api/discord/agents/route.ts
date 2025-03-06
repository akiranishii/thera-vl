import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { agentsTable } from "@/db/schema"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { userId, sessionId, name, role, expertise, goal, model } = body

    if (!userId || !name || !role) {
      return NextResponse.json(
        { isSuccess: false, message: "Missing required fields", data: null },
        { status: 400 }
      )
    }

    // Set default model if not provided
    const defaultModel = "openai" // Default to openai if no model specified
    
    // Create the agent
    const [newAgent] = await db
      .insert(agentsTable)
      .values({
        userId,
        name,
        role,
        expertise,
        description: goal,
        model: model || defaultModel, // Use provided model or default
        prompt: `You are ${name}, a ${role}${expertise ? ` with expertise in ${expertise}` : ''}${goal ? `. Your goal is to ${goal}` : ''}`
      })
      .returning()

    return NextResponse.json({
      isSuccess: true,
      message: "Agent created successfully",
      data: newAgent
    })
  } catch (error) {
    console.error("Error creating agent:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to create agent", data: null },
      { status: 500 }
    )
  }
} 